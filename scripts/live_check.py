"""Prueba real contra un destino PROPIO o autorizado (por defecto zinto.app/robots.txt).

Requiere un lote ya importado (python -m proxymanager.importer ...) y las variables
PROXYMANAGER_DB_PATH y PROXYMANAGER_CREDENTIAL_KEY. Imprime solo resultados, nunca credenciales.
Uso: PROXYMANAGER_LIVE_URL=https://tu-destino/ruta PROXYMANAGER_LIVE_EXPECTED='texto' python scripts/live_check.py
"""
import json, os, time
from urllib.parse import urlsplit

from proxymanager.config import Settings
from proxymanager.app import create_app
from fastapi.testclient import TestClient
URL = os.environ.get("PROXYMANAGER_LIVE_URL", "https://zinto.app/robots.txt")
st = Settings(db_path=os.environ["PROXYMANAGER_DB_PATH"], credential_key=os.environ["PROXYMANAGER_CREDENTIAL_KEY"], admin_key="a"*20, evaluator_key="e"*20, allowed_hosts=(urlsplit(URL).hostname,), expected_text=os.environ.get("PROXYMANAGER_LIVE_EXPECTED", "User-agent"), health_concurrency=2)
A={"X-API-Key":"a"*20}
with TestClient(create_app(st)) as c:
    ids=[p["id"] for p in c.get("/v1/proxies",headers=A).json()]
    print("proxies:",len(ids))
    for i in ids: c.post(f"/v1/proxies/{i}/checks",headers=A,json={"url":URL})
    for _ in range(300):
        h=[c.get(f"/v1/proxies/{i}/checks",headers=A).json()[0]["state"] for i in ids]
        if all(x in("completed","failed") for x in h): break
        time.sleep(0.2)
    for i in ids:
        r=c.get(f"/v1/proxies/{i}/checks",headers=A).json()[0]
        print(r["state"], r.get("success"), r.get("status_code"), r.get("duration_ms"), r.get("error"))
    sess=c.post("/v1/sessions",headers=A).json()["session_id"]
    r=c.post("/scrape",headers=A,json={"url":URL,"use_proxy":True,"session_id":sess}).json()
    print({k:r.get(k) for k in("success","status_code","proxy_id","duration_ms","detail")})
    print(json.dumps(c.get(f"/v1/proxies/{ids[0]}/stats",headers=A).json()))
