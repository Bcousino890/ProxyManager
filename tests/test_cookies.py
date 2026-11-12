from cryptography.fernet import Fernet
import sqlite3

from proxymanager.cookies import CookieStore
from proxymanager.storage import SessionStore


def test_encrypted_cookie_matches_only_authorized_scope(tmp_path):
    db_path = str(tmp_path / 'cookies.db')
    sessions = SessionStore(db_path)
    owner = sessions.owner_id('owner-key')
    sid = sessions.create(owner, 3600)['session_id']
    cookies = CookieStore(db_path, Fernet.generate_key().decode(), sessions, ('lab.example', 'sub.lab.example'))
    cookies.record(sid, owner, 'https://lab.example/account/login', [
        'sid=private-value; Path=/account; Secure; HttpOnly',
        'other=visible-only-here; Path=/account',
    ])
    assert 'private-value' not in (tmp_path / 'cookies.db').read_bytes().decode('latin1')
    assert cookies.header(sid, owner, 'https://lab.example/account/orders') == 'sid=private-value; other=visible-only-here'
    assert cookies.header(sid, owner, 'https://lab.example/accountant') == ''
    assert cookies.header(sid, owner, 'https://sub.lab.example/account/orders') == ''
    assert cookies.header(sid, 'different-owner', 'https://lab.example/account/orders') == ''
    assert CookieStore(db_path, cookies.key, sessions, ('lab.example', 'sub.lab.example')).header(sid, owner, 'https://lab.example/account/orders') == 'sid=private-value; other=visible-only-here'


def test_expiry_domain_and_session_deletion(tmp_path):
    db_path = str(tmp_path / 'cookies.db')
    sessions = SessionStore(db_path)
    owner = sessions.owner_id('owner-key')
    sid = sessions.create(owner, 3600)['session_id']
    cookies = CookieStore(db_path, Fernet.generate_key().decode(), sessions, ('lab.example', 'sub.lab.example'))
    cookies.record(sid, owner, 'https://lab.example/', [
        'shared=ok; Domain=lab.example; Path=/; Secure',
        'expired=gone; Max-Age=0; Path=/',
        'unsafe=no; Domain=example; Path=/',
    ])
    assert cookies.header(sid, owner, 'https://sub.lab.example/') == 'shared=ok'
    assert cookies.header(sid, owner, 'http://lab.example/') == ''
    assert cookies.header(sid, owner, 'https://lab.example/') == 'shared=ok'
    cookies.record(sid, owner, 'https://lab.example/', ['shared=deleted; Domain=lab.example; Path=/; Max-Age=0'])
    assert cookies.header(sid, owner, 'https://sub.lab.example/') == ''
    assert sessions.delete(sid, owner)
    assert cookies.header(sid, owner, 'https://lab.example/') == ''
    with sqlite3.connect(db_path) as db:
        assert db.execute('SELECT count(*) FROM session_cookies WHERE session_id=?', (sid,)).fetchone()[0] == 0


def test_cookie_size_and_count_limits(tmp_path):
    from proxymanager.cookies import CookieStore, MAX_COOKIES_PER_SESSION
    from proxymanager.storage import SessionStore
    from cryptography.fernet import Fernet
    db = str(tmp_path / "c.db")
    sessions = SessionStore(db)
    store = CookieStore(db, Fernet.generate_key().decode(), sessions, ("lab.example",))
    sid = sessions.create("o", 3600)["session_id"]
    url = "https://lab.example/"
    store.record(sid, "o", url, ["big=" + "x" * 5000])
    assert store.header(sid, "o", url) == ""
    store.record(sid, "o", url, [f"c{i}=v" for i in range(MAX_COOKIES_PER_SESSION + 10)])
    assert len(store.header(sid, "o", url).split("; ")) == MAX_COOKIES_PER_SESSION
    store.record(sid, "o", url, ["c0=new"])  # reemplazar uno existente sigue permitido
    assert "c0=new" in store.header(sid, "o", url)
