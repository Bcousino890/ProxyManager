#!/usr/bin/env python3
"""Prueba de humo de un pod recién preparado (solo biblioteca estándar). Sale con código 1 si algo crítico falla.
   python3 smoke_test.py [--chat]   (--chat hace una ronda real con el modelo: ejecuta un comando y comprueba la salida)"""
import json, sys, time, urllib.request
PANEL = "http://127.0.0.1:8787"
def get(p): return json.load(urllib.request.urlopen(PANEL + p, timeout=30))
def post(p, b): return json.load(urllib.request.urlopen(urllib.request.Request(PANEL + p, json.dumps(b).encode(), {"Content-Type": "application/json"}), timeout=60))
bad = []
def check(name, ok, detail=""):
    print(("  ✔ " if ok else "  ✖ ") + name + (f" · {detail}" if detail else "")); (None if ok else bad.append(name))
for _ in range(20):
    try: s = get("/api/status"); break
    except Exception: time.sleep(1)
else: print("  ✖ el panel no responde en", PANEL); sys.exit(1)
check("panel responde", True, f"ctx {s.get('num_ctx')}")
check("Ollama responde", s["ollama"]["up"]); check("modelo del agente descargado", s["model"] in s["ollama"].get("models", []), s["model"])
check("GPU", bool(s["gpu"]))
d = get("/api/deploy/check"); crit = [i for i in d["items"] if not i["ok"] and i["id"] in ("ollama", "gpu", "token", "hook") or (not i["ok"] and i["id"].startswith("model:"))]
for i in crit: check(i["label"], False, i.get("fix", ""))
if "--chat" in sys.argv:
    c = post("/api/conversations", {}); t0 = time.time(); ok_tool = False
    req = urllib.request.Request(PANEL + "/api/chat", json.dumps({"id": c["id"], "message": "Ejecuta con bash: echo humo_ok_123", "mode": "agent", "auto_push": False}).encode(), {"Content-Type": "application/json"})
    for line in urllib.request.urlopen(req, timeout=300):
        line = line.decode().strip()
        if line.startswith("data: "):
            ev = json.loads(line[6:])
            if ev["type"] == "tool_result" and "humo_ok_123" in ev.get("output", "") and "[código de salida 0]" in ev["output"]: ok_tool = True
    check("el modelo ejecuta herramientas reales", ok_tool, f"{time.time() - t0:.0f}s")
print("RESULTADO:", "OK" if not bad else "FALLOS: " + ", ".join(bad)); sys.exit(1 if bad else 0)
