"""Bounded, durable proxy checks. Workers claim jobs atomically from SQLite and
requeue them if a worker dies (lease expiry), so several processes can share one database."""
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
    def __init__(self, store, settings, transport=None, metrics=None, alerts=None):
        self.store, self.settings, self.transport, self.metrics, self.alerts = store, settings, transport, metrics, alerts
        with sqlite3.connect(store.db_path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS proxy_checks (id TEXT PRIMARY KEY, proxy_id TEXT, created REAL, state TEXT, result TEXT)')
            columns = {r[1] for r in db.execute('PRAGMA table_info(proxy_checks)')}
            for name, ddl in (('target', "TEXT NOT NULL DEFAULT ''"), ('attempts', 'INTEGER NOT NULL DEFAULT 0'), ('started', 'REAL')):
                if name not in columns:
                    db.execute(f"ALTER TABLE proxy_checks ADD COLUMN {name} {ddl}")

    def recover(self):
        """Requeue running jobs whose lease expired; fail those out of attempts."""
        cutoff = time.time() - self.settings.health_lease_seconds
        dead = json.dumps({"success": False, "error": {"type": "max_attempts"}})
        with sqlite3.connect(self.store.db_path) as db:
            db.execute("UPDATE proxy_checks SET state='failed', result=? WHERE state='running' AND started<=? AND attempts>=?", (dead, cutoff, self.settings.health_max_attempts))
            db.execute("UPDATE proxy_checks SET state='queued' WHERE state='running' AND started<=?", (cutoff,))

    def claim(self):
        with sqlite3.connect(self.store.db_path, isolation_level=None) as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute("SELECT id, proxy_id, target FROM proxy_checks WHERE state='queued' ORDER BY created LIMIT 1").fetchone()
            if row:
                db.execute("UPDATE proxy_checks SET state='running', started=?, attempts=attempts+1 WHERE id=?", (time.time(), row[0]))
            db.execute('COMMIT')
        return row

    async def worker(self):
        while True:
            try:
                await asyncio.to_thread(self.recover)
                job = await asyncio.to_thread(self.claim)
            except sqlite3.Error:
                job = None
            if job is None:
                await asyncio.sleep(self.settings.health_poll_seconds)
                continue
            await self.process(*job)

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

    async def process(self, job_id, proxy_id, url):
        try:
            proxy_url = self.connection(proxy_id)
            _, hostname = guard_url(url, self.settings)
            transport = self.transport or PinnedProxyTransport(proxy_url, hostname)
            result = await fetch(url, self.settings, transport)
            result.pop('html', None)
            if self.metrics:
                if self.alerts:
                    await self.alerts.record_proxy(self.metrics, proxy_id, 'check', result.get('status_code') is not None, result.get('duration_ms'))
                else:
                    self.metrics.record(proxy_id, 'check', result.get('status_code') is not None, result.get('duration_ms'))
            if 'error' in result:
                result['error'] = {'type': 'transport_error'}
        except Exception:
            result = {'success': False, 'error': {'type': 'check_failed'}}
            if self.metrics:
                if self.alerts:
                    await self.alerts.record_proxy(self.metrics, proxy_id, 'check', False)
                else:
                    self.metrics.record(proxy_id, 'check', False)
        with sqlite3.connect(self.store.db_path) as db:
            db.execute("UPDATE proxy_checks SET state='completed', result=? WHERE id=? AND state='running'", (json.dumps(result), job_id))

    def history(self, proxy_id):
        with sqlite3.connect(self.store.db_path) as db:
            rows = db.execute('SELECT id, created, state, result, target FROM proxy_checks WHERE proxy_id=? ORDER BY created DESC LIMIT 100', (proxy_id,)).fetchall()
        return [{'id': r[0], 'created_at': r[1], 'state': r[2], 'target': r[4], **json.loads(r[3])} for r in rows]
