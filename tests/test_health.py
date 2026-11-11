import socket
import httpx
from fastapi.testclient import TestClient
from proxymanager.app import create_app
from proxymanager.config import Settings


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
        history=c.get(route, headers={'X-API-Key':'eval'}).json()
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
        r=c.get(route,headers=h)
        assert 'private-password' not in r.text
        assert r.json()[0]['success'] is False
