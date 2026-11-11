"""Bounded, persistent proxy checks. Jobs run in this API process."""
import asyncio
import json
import sqlite3
import time
import uuid
from urllib.parse import quote, urlsplit, urlunsplit

import httpx
from .fetch import fetch, guard_url
from .transport import PinnedProxyTransport


class QueueFull(ValueError):
    pass


class ProxyHealth:
    def __init__(self, store, settings, transport=None):
        self.store, self.settings, self.transport = store, settings, transport
        self.limit = asyncio.Semaphore(settings.health_concurrency)
        with sqlite3.connect(store.db_path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS proxy_checks (id TEXT PRIMARY KEY, proxy_id TEXT, created REAL, state TEXT, result TEXT)')
            columns = {r[1] for r in db.execute('PRAGMA table_info(proxy_checks)')}
            if 'target' not in columns:
                db.execute("ALTER TABLE proxy_checks ADD COLUMN target TEXT NOT NULL DEFAULT ''")

    def recover(self):
        with sqlite3.connect(self.store.db_path) as db:
            db.execute("UPDATE proxy_checks SET state='interrupted', result=? WHERE state='queued'", (json.dumps({"success": False, "error": {"type": "process_restarted"}}),))

    def connection(self, proxy_id):
        with sqlite3.connect(self.store.db_path) as db:
            row = db.execute('SELECT host, port, credentials FROM proxies WHERE id=?', (proxy_id,)).fetchone()
        if row is None:
            raise LookupError('Proxy no encontrado')
        host, port, blob = row
        # Host is data, never a URL containing userinfo or path.
        if any(c in host for c in '/@?#:') or not host:
            raise ValueError('Host de proxy inválido')
        auth = ''
        if blob:
            if not self.store.cipher:
                raise ValueError('Falta clave de cifrado')
            creds = json.loads(self.store.cipher.decrypt(blob))
            auth = quote(creds['username'] or '', safe='') + ':' + quote(creds['password'] or '', safe='') + '@'
        return f'http://{auth}{host}:{port}'

    def queue(self, proxy_id, url=""):
        parts = urlsplit(url)
        target = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        job_id = uuid.uuid4().hex
        with sqlite3.connect(self.store.db_path) as db:
            db.execute('BEGIN IMMEDIATE')
            count = db.execute("SELECT count(*) FROM proxy_checks WHERE state='queued'").fetchone()[0]
            if count >= self.settings.health_queue_limit:
                raise QueueFull('Cola de comprobaciones llena')
            db.execute('INSERT INTO proxy_checks (id, proxy_id, created, state, result, target) VALUES (?, ?, ?, ?, ?, ?)', (job_id, proxy_id, time.time(), 'queued', '{}', target))
        return job_id

    async def run(self, job_id, url, proxy_url):
        async with self.limit:
            try:
                _, hostname = guard_url(url, self.settings)
                transport = self.transport or PinnedProxyTransport(proxy_url, hostname)
                result = await fetch(url, self.settings, transport)
                result.pop('html', None)
                if 'error' in result:
                    result['error'] = {'type': 'transport_error'}
            except Exception:
                result = {'success': False, 'error': {'type': 'check_failed'}}
            with sqlite3.connect(self.store.db_path) as db:
                db.execute('UPDATE proxy_checks SET state=?, result=? WHERE id=?', ('completed', json.dumps(result), job_id))

    def history(self, proxy_id):
        with sqlite3.connect(self.store.db_path) as db:
            rows = db.execute('SELECT id, created, state, result, target FROM proxy_checks WHERE proxy_id=? ORDER BY created DESC LIMIT 100', (proxy_id,)).fetchall()
        return [{'id': r[0], 'created_at': r[1], 'state': r[2], 'target': r[4], **json.loads(r[3])} for r in rows]
