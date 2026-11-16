"""Prueba de humo de un despliegue real: `python -m proxymanager.smoke --base-url https://… --target https://…`.

Usa solo destinos que controles o tengas autorizados. Con --api-key reutiliza una clave existente;
sin ella crea una cuenta de prueba (consume créditos gratuitos y deja un usuario en la base).
"""
import argparse
import os
import secrets
import sys

import httpx


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base-url", required=True)
    p.add_argument("--target", required=True, help="URL https autorizada")
    p.add_argument("--expected-text", default=None)
    p.add_argument("--api-key", default=os.getenv("PM_API_KEY"))
    p.add_argument("--country", default=None, help="Prueba también el enrutado por proxy de ese país")
    p.add_argument("--ca-bundle", default=None)
    args = p.parse_args()
    base = args.base_url.rstrip("/")
    client = httpx.Client(timeout=90, verify=args.ca_bundle or True)
    failures = []

    def check(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    r = client.get(base + "/health")
    check("health", r.status_code == 200 and r.json().get("status") == "ok")
    for path in ("/app/", "/docs/", "/admin/"):
        check(f"página {path}", client.get(base + path).status_code == 200)
    key = args.api_key
    if not key:
        r = client.post(base + "/v1/account/signup", json={"email": f"smoke-{secrets.token_hex(4)}@smoke.test", "password": secrets.token_urlsafe(16)})
        check("alta de cuenta de prueba", r.status_code == 201, str(r.status_code))
        key = r.json().get("api_key") if r.status_code == 201 else None
    if not key:
        sys.exit("Sin clave API: no se puede continuar")
    h = {"X-API-Key": key}
    check("clave inválida → 401", client.post(base + "/scrape", headers={"X-API-Key": "pm_live_x"}, json={"url": args.target}).status_code == 401)
    body = {"url": args.target, **({"expected_text": args.expected_text} if args.expected_text else {})}
    r = client.post(base + "/scrape", headers=h, json=body)
    data = r.json() if r.status_code == 200 else {}
    check("scrape directo", r.status_code == 200 and data.get("success") is True,
          f"http={r.status_code} destino={data.get('status_code')} validación={data.get('validation')} {data.get('duration_ms')} ms créditos={data.get('credits_charged')}")
    if args.country:
        sid = client.post(base + "/v1/sessions", headers=h).json().get("session_id")
        ids = []
        for _ in range(2):
            r = client.post(base + "/scrape", headers=h, json={**body, "country": args.country, "session_id": sid})
            d = r.json() if r.status_code == 200 else {}
            ids.append(d.get("proxy_id"))
            check(f"scrape por proxy {args.country}", d.get("success") is True, f"http={r.status_code} destino={d.get('status_code')} proxy={d.get('proxy_id')} error={d.get('error') or r.text[:80] if not d.get('success') else ''}")
        check("misma IP durante la sesión", ids[0] is not None and ids[0] == ids[1])
        client.delete(base + f"/v1/sessions/{sid}", headers=h)
    print("\nRESULTADO:", "TODO OK" if not failures else f"{len(failures)} fallo(s): " + ", ".join(failures))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
