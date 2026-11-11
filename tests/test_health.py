import socket
import httpx
from fastapi.testclient import TestClient
from proxymanager.app import create_app
from proxymanager.config import Settings
import time


def wait_done(client, route, headers):
    for _ in range(100):
        history = client.get(route, headers=headers).json()
        if history and history[0]['state'] in ('completed', 'failed'):
            return history
        time.sleep(0.05)
    raise AssertionError('el worker no terminó la comprobación')


def test_proxy_check_records_result_and_requires_admin(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [(2, 1, 6, '', ('8.8.8.8', 443))])
    settings = Settings(db_path=str(tmp_path/'db'), admin_key='admin', evaluator_key='eval', allowed_hosts=('lab.example',), expected_text='expected')
    with TestClient(create_app(settings, transport=httpx.MockTransport(lambda r: httpx.Response(200, text='expected')))) as c:
        p = c.post('/v1/proxies', headers={'X-API-Key':'admin'}, json={'provider':'lab','host':'proxy.example','port':8080,'kind':'unknown','country':'ZZ'}).json()
        route=f"/v1/proxies/{p['id']}/checks"
        assert c.post(route, headers={'X-API-Key':'eval'}, json={'url':'https://lab.example/'}).status_code == 403
        assert c.post(route, headers={'X-API-Key':'admin'}, json={'url':'https://other.example/'}).status_code == 422
        result=c.post(route, headers={'X-API-Key':'admin'}, json={'url':'https://lab.example/'})
        assert result.status_code == 202
        history=wait_done(c, route, {'X-API-Key':'eval'})
        assert history[0]['state']=='completed'
        assert history[0]['success'] is True


def test_transport_failure_is_redacted(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [(2, 1, 6, '', ('8.8.8.8', 443))])
    def broken(request):
        raise httpx.ConnectError('private-password')
    settings=Settings(db_path=str(tmp_path/'db'),admin_key='admin',allowed_hosts=('lab.example',))
    with TestClient(create_app(settings,transport=httpx.MockTransport(broken))) as c:
        h={'X-API-Key':'admin'}
        p=c.post('/v1/proxies',headers=h,json={'provider':'lab','host':'proxy.example','port':8080,'kind':'unknown','country':'ZZ'}).json()
        route=f"/v1/proxies/{p['id']}/checks"
        c.post(route,headers=h,json={'url':'https://lab.example/'})
        history=wait_done(c,route,h)
        assert 'private-password' not in str(history)
        assert history[0]['success'] is False


def _service(tmp_path, **kw):
    from proxymanager.health import ProxyHealth
    from proxymanager.proxies import ProxyStore
    settings=Settings(db_path=str(tmp_path/'db'),**kw)
    return ProxyHealth(ProxyStore(settings.db_path),settings), settings


def test_claim_is_atomic_and_ordered(tmp_path):
    service,_=_service(tmp_path)
    first=service.queue('p1'); second=service.queue('p2')
    assert service.claim()[0]==first
    assert service.claim()[0]==second
    assert service.claim() is None


def test_crashed_worker_job_is_requeued_then_failed_after_max_attempts(tmp_path):
    service,_=_service(tmp_path,health_lease_seconds=0.001,health_max_attempts=2)
    job=service.queue('p')
    assert service.claim()[0]==job          # intento 1, el worker "muere"
    time.sleep(0.01); service.recover()
    assert service.history('p')[0]['state']=='queued'
    assert service.claim()[0]==job          # intento 2, muere otra vez
    time.sleep(0.01); service.recover()
    item=service.history('p')[0]
    assert item['state']=='failed' and item['error']['type']=='max_attempts'


def test_live_lease_is_not_stolen(tmp_path):
    service,_=_service(tmp_path,health_lease_seconds=60)
    service.queue('p'); service.claim(); service.recover()
    assert service.history('p')[0]['state']=='running'


def test_worker_completes_queued_job_after_restart(tmp_path):
    service,settings=_service(tmp_path)
    job=service.queue('missing-proxy')   # encolado antes del arranque
    with TestClient(create_app(settings)):
        for _ in range(50):
            if service.history('missing-proxy')[0]['state']=='completed': break
            time.sleep(0.05)
        item=service.history('missing-proxy')[0]
    assert item['id']==job and item['state']=='completed' and item['success'] is False


def test_queue_capacity_is_configurable(tmp_path):
    import pytest
    from proxymanager.health import ProxyHealth, QueueFull
    from proxymanager.proxies import ProxyStore
    settings=Settings(db_path=str(tmp_path/'db'),health_queue_limit=1)
    service=ProxyHealth(ProxyStore(settings.db_path),settings)
    service.queue('first')
    with pytest.raises(QueueFull):
        service.queue('second')


def test_history_omits_query_secrets(tmp_path):
    from proxymanager.health import ProxyHealth
    from proxymanager.proxies import ProxyStore
    settings=Settings(db_path=str(tmp_path/'db'))
    service=ProxyHealth(ProxyStore(settings.db_path),settings)
    service.queue('example','https://lab.example/path?token=private')
    assert service.history('example')[0]['target']=='https://lab.example/path'
