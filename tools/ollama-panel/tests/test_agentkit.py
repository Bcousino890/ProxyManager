"""Pruebas del agente del panel: herramientas, secretos, estancamiento, compactación y recuperación ante fallos.
Ejecutar:  cd tools/ollama-panel && python3 -m pytest tests -q   (usa un Ollama falso: no necesita GPU)"""
import json, os, subprocess, sys, tempfile, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import pytest

TMP = Path(tempfile.mkdtemp(prefix="panel-test-"))
REPO = TMP / "repo"; BARE = TMP / "remote.git"
subprocess.run(["git", "init", "-q", "--bare", str(BARE)], check=True)
subprocess.run(["git", "init", "-q", "-b", "work", str(REPO)], check=True)
subprocess.run(["git", "-C", str(REPO), "remote", "add", "origin", str(BARE)], check=True)
(REPO / "pod-work").mkdir()
(REPO / "README").write_text("x"); subprocess.run(["git", "-C", str(REPO), "add", "."], check=True)
subprocess.run(["git", "-C", str(REPO), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"], check=True)
FAKE_PORT = 18999
os.environ.update(PANEL_HOME=str(TMP / "home"), PANEL_REPO=str(REPO), PANEL_BRANCH="work", OLLAMA_URL=f"http://127.0.0.1:{FAKE_PORT}")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import agentkit as kit
import server as srv

kit.ENV.token = lambda: "tok-test-123456"

def mk_agent(conv=None, stop=None):
    conv = conv or {"id": "abc123", "messages": [], "title": "t"}
    events = []
    ag = kit.Agent(conv, events.append, stop or threading.Event(), srv.legacy_exec)
    return ag, events

# ---------------------------------------------------------------- secretos
def test_secret_detection_and_redaction():
    assert kit.find_secrets("x = 'ghp_" + "a1B2" * 9 + "'")
    assert kit.find_secrets("proxy http://usuario1:" + "Zx9kLm3pQ" + "@10.0.0.5:8080")
    assert not kit.find_secrets("http://user:pass@host")          # marcador de posición
    assert not kit.find_secrets("proxy = os.environ['PROXY_URL']")
    assert "S3cretPw9" not in kit.redact("curl http://bob:" + "S3cretPw9" + "@1.2.3.4/")
    assert "tok-test-123456" not in kit.redact("Authorization tok-test-123456")

def test_write_file_blocks_secrets_but_allows_env_example():
    ag, _ = mk_agent()
    ok, out = ag.exec("write_file", {"path": "a.py", "content": "T='ghp_" + "Ab3d" * 9 + "'"})
    assert not ok and "BLOQUEADA" in out
    ok, _ = ag.exec("write_file", {"path": "ok.py", "content": "TOKEN = os.environ['T']"})
    assert ok

def test_commit_blocks_env_and_hook_blocks_bash_commit():
    srv.install_hooks()
    (REPO / "pod-work" / ".env").write_text("A=1\n")
    ok, msg = kit.commit_paths("x")
    assert not ok and ".env" in msg
    kit.git("reset", "-q")
    subprocess.run(["git", "-C", str(REPO), "add", "-f", "pod-work/.env"], check=True)
    r = subprocess.run(["git", "-C", str(REPO), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-m", "bypass"], capture_output=True, text=True)
    assert r.returncode != 0 and "secretos" in r.stderr           # el hook pre-commit lo frena
    subprocess.run(["git", "-C", str(REPO), "reset", "-q"]); (REPO / "pod-work" / ".env").unlink()

# ---------------------------------------------------------------- ejecución de comandos
def test_run_cmd_stdout_stderr_exit_and_timeout_and_cancel():
    r = kit.run_cmd("echo out; echo err >&2; exit 3")
    assert (r["code"], r["stdout"].strip(), r["stderr"].strip()) == (3, "out", "err")
    t = time.time(); r = kit.run_cmd("sleep 30", timeout=1)
    assert r["status"] == "timeout" and r["code"] == 124 and time.time() - t < 6
    ev = threading.Event(); threading.Timer(0.5, ev.set).start()
    r = kit.run_cmd("sleep 30", stop=ev); assert r["status"] == "cancelled"
    r = kit.run_cmd("seq 1 200000", limit=2000)
    assert r["full"] and Path(r["full"]).exists() and len(r["stdout"]) < 3000   # salida limitada y guardada completa

def test_background_process_lifecycle():
    ok, msg = kit.proc_start("t1", "echo hola; sleep 30")
    assert ok
    ag, _ = mk_agent()
    time.sleep(0.5)
    assert "en marcha" in ag.exec("proc_inspect", {"action": "status", "name": "t1"})[1]
    assert "hola" in ag.exec("inspect_logs", {"name": "t1"})[1]
    assert "detenido" in ag.exec("proc_inspect", {"action": "stop", "name": "t1"})[1]
    kit.proc_start("t2", "exit 7"); time.sleep(1.5)
    assert kit.proc_status("t2")["exit"] == 7

# ---------------------------------------------------------------- archivos
def test_file_tools():
    ag, _ = mk_agent()
    body = "\n".join(f"line{i}" for i in range(1, 1001))
    assert ag.exec("write_file", {"path": "big.txt", "content": body})[0]
    ok, out = ag.exec("read_file", {"path": "big.txt", "limit": 10})
    assert "líneas 1-10 de 1000" in out and "offset=11" in out
    assert "line500" in ag.exec("read_file", {"path": "big.txt", "offset": 500, "limit": 2})[1]
    assert ag.exec("edit_file", {"path": "big.txt", "old_string": "line7\n", "new_string": "SIETE\n"})[0]
    ok, out = ag.exec("edit_file", {"path": "big.txt", "old_string": "line", "new_string": "x"})
    assert not ok and "veces" in out
    assert not ag.exec("edit_file", {"path": "big.txt", "old_string": "nada", "new_string": "x"})[0]
    assert "big.txt:" in ag.exec("search_files", {"pattern": "SIETE", "glob": "*.txt"})[1]
    assert not ag.exec("read_file", {"path": "/etc/passwd"})[0]            # fuera del repositorio
    assert not ag.exec("read_file", {"path": "nope.txt"})[0]               # archivo que no existe

# ---------------------------------------------------------------- git
def test_git_commit_push_verify_and_no_force():
    ag, _ = mk_agent()
    kit.ENV.branch = "work"
    (REPO / "pod-work" / "f.txt").write_text("hola")
    ok, out = ag.exec("git_commit", {"message": "feat: f"}); assert ok and "Commit creado" in out
    ok, out = ag.exec("git_push", {}); assert ok and "coincide" in out
    rh, _ = kit.remote_hash("work"); assert rh == kit.git("rev-parse", "HEAD")[1].strip()
    assert srv.needs_approval("git_push", {"branch": "main"}) and not srv.needs_approval("git_push", {"branch": "work"})
    assert srv.needs_approval("bash", {"command": "git push origin main"}) and srv.needs_approval("bash", {"command": "git push -f origin x"})
    assert not any("force" in s["function"]["parameters"]["properties"] for s in kit.SCHEMAS)

def test_push_rejected_then_rebase_retry():
    other = TMP / "other"; subprocess.run(["git", "clone", "-q", str(BARE), str(other)], check=True)
    subprocess.run(["git", "-C", str(other), "checkout", "-q", "work"], check=True)
    (other / "pod-work").mkdir(exist_ok=True); (other / "pod-work" / "ajeno.txt").write_text("de otro")
    for c in (["add", "."], ["-c", "user.name=o", "-c", "user.email=o@o", "commit", "-qm", "ajeno"], ["push", "-q", "origin", "work"]):
        subprocess.run(["git", "-C", str(other)] + c, check=True)
    (REPO / "pod-work" / "mio.txt").write_text("mio")
    assert kit.commit_paths("mio")[0]
    r = kit.push_branch("work"); assert r["ok"], r
    assert (REPO / "pod-work" / "ajeno.txt").exists()                      # no se sobrescribió el trabajo ajeno

# ---------------------------------------------------------------- plan, pruebas, estancamiento, contexto
def test_plan_requires_evidence_and_run_tests_parses():
    ag, _ = mk_agent()
    ag.exec("plan", {"action": "set", "tasks": ["a", "b"]})
    ok, out = ag.exec("plan", {"action": "update", "index": 1, "status": "done", "evidence": ""})
    assert not ok and "evidencia" in out
    proj = REPO / "pod-work" / "pt"; (proj / "tests").mkdir(parents=True)
    (proj / "tests" / "test_x.py").write_text("def test_a():\n    assert 1+1 == 3\n")
    ok, out = ag.exec("run_tests", {"path": str(proj), "command": f"{sys.executable} -m pytest -q"})
    assert not ok and "FALLARON" in out and ag.last_test["ok"] is False
    (proj / "tests" / "test_x.py").write_text("def test_a():\n    assert 1+1 == 2\n")
    ok, out = ag.exec("run_tests", {"path": str(proj), "command": f"{sys.executable} -m pytest -q"})
    assert ok and "APROBADAS" in out and ag.last_test["ok"]
    assert ag.exec("plan", {"action": "update", "index": 1, "status": "done", "evidence": "run_tests devolvió 1 passed, exit 0 en este turno"})[0]

def test_stagnation_detector():
    s = kit.Stagnation()
    assert s.record("bash", {"command": "false"}, False, "error X") is None
    assert s.record("bash", {"command": "false"}, False, "error X")            # mismo comando, mismo resultado
    s2 = kit.Stagnation()
    r = [s2.record("bash", {"command": f"c{i}"}, False, "boom 12:00:0%d" % i) for i in range(3)]
    assert r[2] and "MISMO error" in r[2]
    s3 = kit.Stagnation(); rs = [s3.record("write_file", {"path": "a.py"}, True, "ok%d" % i) for i in range(5)]
    assert rs[4] and "reescrito" in rs[4]
    s4 = kit.Stagnation(); s4.record("bash", {"command": "rm -rf x"}, False, "no", blocked=True)
    assert s4.record("bash", {"command": "rm -rf x"}, False, "no", blocked=True)

def test_stagnation_same_call_changing_output():
    s = kit.Stagnation(); r = [s.record("bash", {"command": "curl health"}, True, "ok ts=%f" % (1794616018.29 + i * 1.7)) for i in range(4)]
    assert r[0] is None and r[2] and "veces seguidas" in r[2]
    s2 = kit.Stagnation(); s2.record("bash", {"command": "curl health"}, True, "ok 1"); s2.record("write_file", {"path": "a"}, True, "w")
    assert s2.record("bash", {"command": "curl health"}, True, "ok 2") is None   # hubo un cambio entre medias: no es bucle

def test_compaction_keeps_instructions_and_memory_and_repair():
    conv = {"id": "cmp1", "messages": [], "title": "t"}
    ag, ev = mk_agent(conv); ag.init_project("cmp", "TAREA ORIGINAL IMPORTANTE", session=False)
    m = conv["messages"]; m.append({"role": "user", "content": "INSTRUCCION CRITICA: no uses la red"})
    for i in range(30):
        tid = f"t{i}"
        m.append({"role": "assistant", "content": "", "tool_calls": [{"id": tid, "function": {"name": "bash", "arguments": {"command": f"echo {i}"}}}]})
        m.append({"role": "tool", "tool_name": "bash", "tool_call_id": tid, "ok": True, "content": f"[stdout]\n{i}\n[código de salida 0]"})
    assert ag.compact(keep=8)
    view = ag.build_view("SYS", m, "[ESTADO]")
    flat = json.dumps(view, ensure_ascii=False)
    assert "INSTRUCCION CRITICA" in flat and "TAREA ORIGINAL IMPORTANTE" in flat and len(view) < 20
    assert view[-1]["content"].endswith("[ESTADO]") and view[3 if view[2]["role"] == "assistant" else 2]["role"] != "tool"
    m.append({"role": "assistant", "content": "", "tool_calls": [{"id": "dangling", "function": {"name": "bash", "arguments": {}}}]})
    assert kit.repair_history(m) == 1 and m[-1]["role"] == "tool"

def test_budget_is_real_and_reserve():
    ag = kit.Agent({"id": "b", "messages": [], "title": "t"}, lambda e: None, threading.Event(), srv.legacy_exec, budget_s=600, pod_remaining_s=100000)
    assert 0 < ag.remaining() <= 600 and ag.reserve >= 180 and not ag.in_reserve()
    ag.deadline = time.time() + 100; assert ag.in_reserve() and "FASE FINAL" in ag.budget_note()

# ---------------------------------------------------------------- recuperación ante fallos (Ollama falso)
SCRIPT = []   # respuestas encoladas: dict(message=…) | "empty" | "error500" | "hang"
class Fake(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0); self.rfile.read(n)
        item = SCRIPT.pop(0) if SCRIPT else {"content": "fin"}
        if item == "error500":
            self.send_response(500); self.end_headers(); return
        if item == "parse500":
            b_ = json.dumps({"error": "XML syntax error on line 8: unexpected EOF"}).encode()
            self.send_response(500); self.send_header("Content-Length", str(len(b_))); self.end_headers(); self.wfile.write(b_); return
        self.send_response(200); self.send_header("Content-Type", "application/x-ndjson"); self.end_headers()
        msg = {"role": "assistant", "content": "" if item == "empty" else item.get("content", ""), **({"tool_calls": item["tool_calls"]} if item != "empty" and item.get("tool_calls") else {})}
        self.wfile.write((json.dumps({"message": msg, "done": True, "eval_count": 5, "eval_duration": 1e8, "prompt_eval_count": 100}) + "\n").encode())

@pytest.fixture(scope="module", autouse=True)
def fake_ollama():
    srv.OLLAMA = f"http://127.0.0.1:{FAKE_PORT}"; srv.LIMIT_H = 10 ** 6   # el reloj real del pod no debe afectar a las pruebas
    s = ThreadingHTTPServer(("127.0.0.1", FAKE_PORT), Fake); threading.Thread(target=s.serve_forever, daemon=True).start()
    yield; s.shutdown()

def run_turn(conv=None, mode="agent", resume=False):
    conv = conv or {"id": "f%d" % int(time.time() * 1000), "messages": [{"role": "user", "content": "haz algo"}], "title": "t", "created": 0, "updated": 0}
    ev = []; time.sleep(0.01)
    out = srv.agent_turn(conv, ev.append, threading.Event(), mode, "m", resume=resume)
    return out, conv, ev

def call(_tool, **a): return {"tool_calls": [{"function": {"name": _tool, "arguments": a}}]}

def test_recovery_empty_responses_then_ok(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    SCRIPT[:] = ["empty", "empty", {"content": "Listo."}]
    out, conv, ev = run_turn(); assert out == "done" and conv["messages"][-1]["content"] == "Listo."

def test_recovery_empty_three_times_is_blocked(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    SCRIPT[:] = ["empty", "empty", "empty"]
    out, _, ev = run_turn(); assert out == "blocked" and any("vacías" in e.get("text", "") for e in ev)

def test_recovery_ollama_500_retries(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    SCRIPT[:] = ["error500", {"content": "ok tras reintento"}]
    out, conv, _ = run_turn(); assert out == "done" and "reintento" in conv["messages"][-1]["content"]
    SCRIPT[:] = ["error500"] * 3
    out, _, ev = run_turn(); assert out == "error"

def test_recovery_malformed_tool_call_is_nudged(monkeypatch):
    SCRIPT[:] = [{"content": '<tool_call>{"name": "bash", "arguments": {"command": "echo hola"</tool_call>'}, call("bash", command="echo bien"), {"content": "hecho"}]
    out, conv, ev = run_turn()
    assert out == "done" and any(m.get("hidden") and "mal formada" in m["content"] for m in conv["messages"])
    assert any(m["role"] == "tool" and "bien" in m["content"] for m in conv["messages"])

def test_recovery_text_function_call_is_parsed():
    SCRIPT[:] = [{"content": "<function=bash>\n<parameter=command>\necho desde_texto\n</parameter>\n</function>"}, {"content": "hecho"}]
    out, conv, _ = run_turn(); assert any(m["role"] == "tool" and "desde_texto" in m["content"] for m in conv["messages"])

def test_recovery_failing_command_then_fix_and_stagnation_block():
    SCRIPT[:] = [call("bash", command="exit 2"), call("bash", command="echo arreglado"), {"content": "ok"}]
    out, conv, _ = run_turn(); assert out == "done"
    assert [m["ok"] for m in conv["messages"] if m["role"] == "tool"] == [False, True]
    SCRIPT[:] = [call("bash", command="false")] * 12
    out, conv, ev = run_turn(); assert out == "blocked" and any("estancamiento" in e.get("text", "").lower() for e in ev)

def test_file_disappears_and_write_failure_reported():
    ag, _ = mk_agent()
    assert not ag.exec("read_file", {"path": "desaparecido.txt"})[0]
    (REPO / "pod-work" / "rodir").mkdir(exist_ok=True); (REPO / "pod-work" / "rodir").chmod(0o500)
    ok, out = ag.exec("write_file", {"path": "rodir/x.txt", "content": "a"})
    (REPO / "pod-work" / "rodir").chmod(0o700)
    assert ok or "error" in out.lower()   # root puede escribir; si no, el error se informa sin romper el agente

def test_pending_tasks_prevent_early_completion():
    SCRIPT[:] = [call("plan", action="set", tasks=["t1", "t2"]), {"content": "Terminado."}, call("bash", command="echo x"), {"content": "Terminado."}, {"content": "Terminado."}]
    out, conv, ev = run_turn(); assert any(m.get("hidden") and "sin completar" in m["content"] for m in conv["messages"])

def test_interrupted_runs_are_marked():
    c = {"id": "aaaaaa111111", "title": "x", "messages": [], "run": {"status": "running"}}
    srv.jsave(srv.conv_path(c["id"]), c); srv.mark_interrupted()
    assert srv.jload(srv.conv_path(c["id"]), {})["run"]["status"] == "interrupted"


# ================================================================ REGRESIÓN: finalización prematura sin evidencia
def fake_probe(status=200, ok=None, calls=None, server="t", snippet="x", nbytes=10):
    def f(url, method="GET", timeout=15, headers=None, contains=None, max_bytes=200000):
        if calls is not None: calls.append(url)
        good = status < 400 if ok is None else ok
        return {"url": url, "status": status, "ok": good, "seconds": 0.1, "bytes": nbytes, "final_url": url, "snippet": snippet, "error": None, "server": server}
    return f

def prior_conv(summary="Todo listo: public_url configurada y servicio terminado."):
    return {"id": "a%011x" % int(time.time() * 1000), "title": "t", "created": 0, "updated": 0,
            "run": {"tasks": [{"text": "Crear app", "status": "done", "evidence": "ya hecho en turno anterior"}]},
            "messages": [{"role": "user", "content": "construye la app"}, {"role": "assistant", "content": summary, "stats": {}}]}

def last_user(conv, text): conv["messages"].append({"role": "user", "content": text}); return conv

def test_REGRESSION_premature_completion_config_only(monkeypatch):
    """Caso real: pidió probar una URL de Idealista y publicar; el agente solo tocó `public_url` y declaró éxito."""
    monkeypatch.setattr(kit, "http_probe", fake_probe())
    conv = last_user(prior_conv(), "Construye la alternativa. Prueba esta URL https://www.idealista.com/inmueble/123/ y PUBLICA con una URL pública HTTPS")
    claim = "Listo. La URL pública funciona: https://abc123-8000.proxy.runpod.net y el servicio está desplegado."
    SCRIPT[:] = [call("write_file", path="settings.py", content="public_url = 'https://abc123-8000.proxy.runpod.net'"), {"content": claim}] + [{"content": claim}] * 8
    out, conv, ev = run_turn(conv)
    assert out == "incomplete", out                                              # ANTES: "done"
    hidden = [m["content"] for m in conv["messages"] if m.get("hidden")]
    assert any("NO puedes cerrar la tarea" in h for h in hidden)
    assert any("idealista" in h.lower() for h in hidden)                            # el requisito de la URL objetivo se exige
    final = conv["messages"][-1]["content"]
    assert "Estado verificado por el controlador" in final and "SIN cumplir" in final and "INCOMPLETO" in final
    assert "**Git**" in final and "**Aplicación" in final                           # Git y aplicación, por separado
    assert not any(e["kind"] == "http" and e["ok"] for e in conv["run"]["ledger"])  # no había ninguna prueba HTTP

def test_REGRESSION_same_scenario_passes_with_real_evidence(monkeypatch):
    calls = []; monkeypatch.setattr(kit, "http_probe", fake_probe(200, calls=calls))
    conv = last_user(prior_conv(), "Prueba esta URL https://www.idealista.com/inmueble/123/ y PUBLICA con una URL pública HTTPS")
    SCRIPT[:] = [call("plan", action="set", tasks=["Arrancar servicio", "Probar URL objetivo", "Comprobar URL pública"]),
                 call("write_file", path="app_ok.py", content="print('hi')"),
                 call("proc_start", name="svc1", command="sleep 60"),
                 call("http_check", url="https://www.idealista.com/inmueble/123/"),
                 call("http_check", url="https://abc123-8000.proxy.runpod.net/"),
                 call("plan", action="update", index=1, status="done", evidence="proc_start svc1 en marcha y comprobado con http_check"),
                 call("plan", action="update", index=2, status="done", evidence="http_check a la URL de Idealista devolvió HTTP 200 (simulado)"),
                 call("plan", action="update", index=3, status="done", evidence="http_check a la URL pública externa devolvió HTTP 200"),
                 {"content": "Servicio activo. La URL pública https://abc123-8000.proxy.runpod.net/ responde (HTTP 200) y la URL de Idealista se probó (HTTP 200)."}]
    out, conv, ev = run_turn(conv)
    kit.proc_stop("svc1")
    assert any(u.startswith("https://www.idealista.com") for u in calls)
    assert out in ("done", "incomplete")
    unmet = [r["text"] for r in conv["run"]["reqs"] if not r.get("done")]
    assert not [u for u in unmet if "idealista" in u.lower() or "pública" in u.lower() or "Servicio" in u], unmet

def test_REGRESSION_new_instruction_pruebalo_does_not_repeat_summary(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe())
    summary = "Resumen anterior: la aplicación está terminada, hay endpoints /health y /extract y todo está configurado correctamente en el servidor local."
    conv = last_user(prior_conv(summary), "pruébalo")
    SCRIPT[:] = [{"content": summary}] * 8
    out, conv, ev = run_turn(conv)
    assert out == "incomplete"
    hidden = " ".join(m["content"] for m in conv["messages"] if m.get("hidden"))
    assert "repitiendo tu resumen" in hidden and "Requisito sin evidencia" in hidden
    # y si de verdad lo prueba, se acepta
    conv2 = last_user(prior_conv(summary), "pruébalo")
    SCRIPT[:] = [call("plan", action="set", tasks=["Ejecutar prueba real"]), call("http_check", url="http://127.0.0.1:18998/health"),
                 call("plan", action="update", index=1, status="done", evidence="http_check GET /health devolvió HTTP 200 en 0.1s"), {"content": "Probado: GET /health devolvió HTTP 200."}]
    out2, conv2, _ = run_turn(conv2)
    assert out2 == "done", out2

def test_claims_need_evidence_and_local_is_not_public(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe())
    ag, _ = mk_agent()
    assert ag.claim_problems("La URL http://127.0.0.1:9000/ funciona perfectamente")                 # sin petición HTTP
    assert ag.claim_problems("Todo desplegado y funcionando")                                      # sin servicio vivo
    ag.exec("http_check", {"url": "http://127.0.0.1:9000/"})
    assert not ag.claim_problems("La URL http://127.0.0.1:9000/ funciona perfectamente")             # con petición HTTP
    assert ag.claim_problems("Esta es la URL pública: http://127.0.0.1:9000/ y funciona")            # localhost no es pública
    assert ag.claim_problems("Todas las pruebas pasan") and ag.claim_problems("Subido a GitHub en la rama main")
    ag.exec("http_check", {"url": "https://x.example.org/"})
    assert not [p for p in ag.claim_problems("La URL pública https://x.example.org/ funciona") if "pública" in p]

def test_http_evidence_before_last_change_is_stale(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe())
    ag, _ = mk_agent(); ag.exec("http_check", {"url": "http://127.0.0.1:9001/"})
    assert not ag.claim_problems("http://127.0.0.1:9001/ funciona")
    ag.exec("write_file", {"path": "cambio.py", "content": "x=1"})
    assert ag.claim_problems("http://127.0.0.1:9001/ funciona")        # el cambio invalida la evidencia anterior

def test_plan_done_requires_real_evidence_by_task_type(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe())
    ag, _ = mk_agent(); ag.exec("plan", {"action": "set", "tasks": ["Probar la URL /health con una petición HTTP", "Poner la URL pública del servicio"]})
    ok, out = ag.exec("plan", {"action": "update", "index": 1, "status": "done", "evidence": "he modificado el campo public_url en settings.py"})
    assert not ok and "HTTP" in out
    ag.exec("http_check", {"url": "http://127.0.0.1:9002/health"})
    assert ag.exec("plan", {"action": "update", "index": 1, "status": "done", "evidence": "http_check GET /health devolvió HTTP 200 en 0.1s"})[0]
    ok, out = ag.exec("plan", {"action": "update", "index": 2, "status": "done", "evidence": "añadida la variable public_url en la configuración del servicio"})
    assert not ok and "PÚBLICA" in out                                  # una variable de configuración no es una URL pública

def test_blocked_site_is_reported_not_success(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe(403, server="DataDome", snippet="Please enable JS"))
    ag, _ = mk_agent(); ok, out = ag.exec("http_check", {"url": "https://www.idealista.com/x"})
    assert not ok and "bloqueo" in out.lower() and "403" in out
    ag2, _ = mk_agent(); ag2.add_requirements("Prueba esta URL https://www.idealista.com/x"); assert ag2.unmet()
    ag2.exec("http_check", {"url": "https://www.idealista.com/x"}); ag, _ = ag2, 0
    assert not ag.unmet()                                               # el intento real cumple «ejecutar contra la URL objetivo»...
    assert ag.claim_problems("La URL https://www.idealista.com/x funciona")   # ...pero afirmar que funciona sigue rechazado (403)

def test_long_user_requirements_survive_compaction():
    conv = {"id": "lng1", "messages": [], "title": "t"}; ag, _ = mk_agent(conv)
    big = "REQUISITO-INICIAL " + "x" * 5000 + " REQUISITO-FINAL-CRITICO"
    m = conv["messages"]; m.append({"role": "user", "content": big})
    for i in range(20):
        m.append({"role": "assistant", "content": "", "tool_calls": [{"id": f"q{i}", "function": {"name": "bash", "arguments": {"command": "echo"}}}]})
        m.append({"role": "tool", "tool_name": "bash", "tool_call_id": f"q{i}", "ok": True, "content": "ok"})
    assert ag.compact(keep=6); assert "REQUISITO-FINAL-CRITICO" in json.dumps(ag.build_view("S", m))

def test_resume_with_pending_requirements_is_not_closed_early(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe())
    conv = last_user(prior_conv(), "pruébalo y publícalo con URL pública HTTPS")
    conv["run"]["reqs"] = [{"kind": "public", "key": "url", "text": "URL pública (no localhost) comprobada con http_check y estado 2xx/3xx", "since": 0}]
    conv["messages"].append({"role": "user", "hidden": True, "content": "REANUDA la tarea"})
    SCRIPT[:] = [{"content": "Todo terminado."}] * 8
    out, conv, ev = run_turn(conv, resume=True)
    assert out == "incomplete" and any("PENDIENTE" in m["content"] for m in conv["messages"] if m.get("hidden"))
    assert "SIN cumplir" in conv["messages"][-1]["content"]

def test_notify_and_compaction_do_not_end_the_loop():
    ag, ev = mk_agent(); ok, _ = ag.exec("notify", {"message": "hola"})
    assert ok and any(e["type"] == "notify" for e in ev)               # notify solo emite el aviso; el bucle lo decide el controlador


# ================================================================ despliegue y rama main
def test_deploy_check_and_config(monkeypatch):
    assert srv.set_deploy({"pod_id": "abc123def", "app_port": 8081})["ok"]
    assert srv.public_url()[0] == "https://abc123def-8081.proxy.runpod.net"
    assert not srv.set_deploy({"pod_id": "NO VALIDO!"})["ok"] and not srv.set_deploy({"app_port": 99999})["ok"]
    monkeypatch.setattr(kit, "http_probe", fake_probe(200))
    d = srv.deploy_check(full=True); ids = {i["id"]: i for i in d["items"]}
    assert {"ollama", "gpu", "token", "branch", "hook", "pod_id", "persist"} <= set(ids) and d["public_url"] and ids["public"]["ok"]
    assert all("fix" in i for i in d["items"])

def test_main_requires_explicit_confirmation_and_agent_push_policy():
    assert not srv.set_config({"branch": "main"})["ok"]                       # sin confirmación no
    assert srv.set_config({"branch": "main", "allow_main": True})["ok"] and srv.BRANCH == "main"
    assert not srv.needs_approval("git_push", {}) and not srv.needs_approval("git_push", {"branch": "main"})   # rama configurada por el usuario
    assert srv.needs_approval("git_push", {"branch": "master"})                                              # otra protegida: aprobación
    srv.set_config({"branch": "work"}); assert srv.BRANCH == "work" and srv.needs_approval("git_push", {"branch": "main"})


def test_recovery_ollama_tool_parse_500_is_not_fatal(monkeypatch):
    """Caso real: qwen3-coder escribe un write_file enorme, Ollama responde 500 'XML syntax error'. Debe pedir contenido más pequeño y continuar."""
    monkeypatch.setattr(time, "sleep", lambda s: None)
    SCRIPT[:] = ["parse500", "parse500", "parse500", call("bash", command="echo trozo1"), {"content": "hecho"}]
    out, conv, ev = run_turn()
    assert out == "done" and any(m.get("hidden") and "NO se pudo interpretar" in m["content"] for m in conv["messages"])
    assert any(m["role"] == "tool" and "trozo1" in m["content"] for m in conv["messages"])
    SCRIPT[:] = ["parse500"] * 12
    out, conv, ev = run_turn(); assert out == "blocked" and any("4 veces" in e.get("text", "") for e in ev)


def test_user_can_steer_the_agent_while_it_runs(monkeypatch):
    """Comentarios del usuario durante la tarea: se leen en el siguiente paso y también si llegan justo al terminar."""
    seen = []
    orig = srv.stream_ollama
    def spy(view, *a, **k):
        seen.append(json.dumps(view, ensure_ascii=False)); return orig(view, *a, **k)
    monkeypatch.setattr(srv, "stream_ollama", spy)
    conv = {"id": "b%011x" % int(time.time() * 1000), "title": "t", "created": 0, "updated": 0, "messages": [{"role": "user", "content": "haz algo"}]}
    q = ["usa httpx en vez de requests"]; ev = []
    SCRIPT[:] = [call("bash", command="echo paso1"), {"content": "hecho"}, call("bash", command="echo paso2_tras_consejo"), {"content": "listo ya"}]
    real_call = srv.call_model; n = {"i": 0}
    def wrapped(*a, **k):
        n["i"] += 1
        if n["i"] == 2: q.append("ahora añade tests")      # llega justo cuando el modelo va a cerrar
        return real_call(*a, **k)
    monkeypatch.setattr(srv, "call_model", wrapped)
    out = srv.agent_turn(conv, ev.append, threading.Event(), "agent", "m", steer=q)
    users = [m for m in conv["messages"] if m.get("steer")]
    assert [m["display"] for m in users] == ["usa httpx en vez de requests", "ahora añade tests"]
    assert any("usa httpx en vez de requests" in v for v in seen[:1])                 # el modelo lo ve en la primera llamada
    assert any(m["role"] == "tool" and "paso2_tras_consejo" in m["content"] for m in conv["messages"])   # y siguió trabajando tras el 2º comentario
    assert sum(1 for e in ev if e["type"] == "user" and e.get("steer")) == 2 and not q


# ================================================================ REGRESIÓN: bucle infinito de validación / criterios obsoletos
from collections import Counter
PAD = " Contexto del proyecto: panel de frontend y backend con servicios locales. " * 5      # >300 caracteres => el controlador crea la memoria de la tarea (BLOCKERS.md, ACCEPTANCE.md)

def reqs_conv(reqs, text):
    c = prior_conv(); c["messages"][0]["content"] = "Construye la app completa del panel." + PAD; c["run"]["reqs"] = reqs; return last_user(c, text)

def pub_req(): return {"kind": "public", "key": "url", "text": "URL pública (no localhost) comprobada con http_check y estado 2xx/3xx", "since": 0, "status": "active", "epoch": 0}

def test_REGRESSION_public_url_requirement_changed_to_local_ssh(monkeypatch):
    """Escenario del usuario: la tarea exigía URL pública; no está disponible; el usuario cambia a acceso local por SSH."""
    monkeypatch.setattr(kit, "http_probe", fake_probe(200))
    conv = reqs_conv([pub_req()], "La URL pública no está disponible. Cambio el requisito: acceso local mediante SSH, ya no hace falta la URL pública. Sigue con el frontend y el backend." + PAD)
    SCRIPT[:] = [call("plan", action="set", tasks=["Crear el frontend", "Crear el backend", "Arrancar el servicio local"]),
                 call("write_file", path="front_t/index.html", content="<h1>hola</h1>"), call("write_file", path="back_t/app.py", content="print('api')"),
                 call("proc_start", name="svcssh", command="sleep 60"), call("http_check", url="http://127.0.0.1:8000/health"),
                 call("plan", action="update", index=1, status="done", evidence="write_file front_t/index.html creado correctamente"),
                 call("plan", action="update", index=2, status="done", evidence="write_file back_t/app.py creado correctamente"),
                 call("plan", action="update", index=3, status="done", evidence="proc_start svcssh y http_check local devolvió HTTP 200"),
                 {"content": "Frontend y backend listos. Accesible por SSH en http://127.0.0.1:8000/health (HTTP 200)."}]
    out, conv, ev = run_turn(conv); kit.proc_stop("svcssh")
    stat = {r["kind"]: kit.rstat(r) for r in conv["run"]["reqs"]}
    assert stat["public"] == "retired" and stat.get("local") == "done", stat          # la pública se retiró y el acceso local se cumplió
    assert out == "done", out
    allhidden = " ".join(m["content"] for m in conv["messages"] if m.get("hidden")).lower()
    assert "url pública" not in allhidden and "pública" not in allhidden               # ningún aviso vuelve a pedir la URL pública
    assert not any("pública" in (e.get("text") or "") for e in ev if e["type"] in ("notice", "blocker", "verified") and "retirad" not in e.get("text", ""))
    assert any("Criterio retirado por tu cambio" in e.get("text", "") for e in ev)      # y se avisó del cambio de criterio
    assert "Criterios retirados" in conv["messages"][-1]["content"]

def test_REGRESSION_http_403_datadome_is_blocked_not_success(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe(403, server="DataDome", snippet="Please enable JS and disable any ad blocker", nbytes=773))
    conv = reqs_conv([], "Prueba esta URL https://www.idealista.com/inmueble/1/ y extrae los datos." + PAD)
    SCRIPT[:] = [call("plan", action="set", tasks=["Intentar la extracción real de Idealista", "Documentar el resultado"]), call("http_check", url="https://www.idealista.com/inmueble/1/"),
                 call("plan", action="update", index=1, status="blocked", evidence="HTTP 403 DataDome en http_check"),
                 call("plan", action="update", index=2, status="blocked", evidence="sin datos que documentar: bloqueado por DataDome"),
                 {"content": "Idealista bloquea la petición con DataDome (HTTP 403); no se obtuvieron datos."}]
    out, conv, ev = run_turn(conv)
    assert out == "incomplete"                                                           # BLOQUEADO, no «extracción exitosa»
    tgt = [r for r in conv["run"]["reqs"] if r["kind"] == "target"][0]
    assert kit.rstat(tgt) == "blocked" and "antibot" in tgt["reason"]
    final = conv["messages"][-1]["content"]
    assert "Extracción ejecutada: SÍ" in final and "Datos útiles obtenidos: NO" in final and "DataDome" in final and "BLOQUEADOS" in final
    assert "Servicio operativo (2xx/3xx): NO" in final and "Despliegue público verificado: NO" in final
    assert sum(1 for e in ev if e["type"] == "blocker") == 1                              # aviso único
    assert sum(1 for m in conv["messages"] if m.get("hidden") and "NO puedes cerrar" in m["content"]) == 0
    pdir = Path(conv["run"]["project"]); assert (pdir / "BLOCKERS.md").read_text().count("criterio BLOQUEADO") == 1

def test_http_404_never_counts_as_available(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe(404))
    ag, _ = mk_agent(); ag.add_requirements("Pruébalo y despliégalo en el servicio")
    ok, out = ag.exec("http_check", {"url": "http://127.0.0.1:9100/health", "expect_status": 200})
    assert not ok and "404" in out and "NO cuenta" in out
    assert not ag.exec("http_check", {"url": "http://127.0.0.1:9100/"})[0]
    kinds = {r["kind"] for r, _ in ag.unmet()}; assert {"verify", "deploy"} <= kinds             # un 404 no satisface prueba ni despliegue
    lv = ag.service_levels(); assert lv["accesible"] and not lv["operativo"]                  # accesible ≠ operativo
    monkeypatch.setattr(kit, "http_probe", fake_probe(200)); assert ag.exec("http_check", {"url": "http://127.0.0.1:9100/health", "expect_status": 200})[0]
    assert not ag.exec("http_check", {"url": "http://127.0.0.1:9100/x", "expect_status": 204})[0]   # 200 != 204

def test_five_service_levels_are_distinct(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe(200, nbytes=900))
    ag, _ = mk_agent(); ag.add_requirements("Prueba https://www.ejemplo-sitio.es/p/1 y extrae")
    assert ag.service_levels()["extraccion"] == "NO" and ag.service_levels()["datos"] == "NO" and not ag.service_levels()["publico"]
    ag.exec("http_check", {"url": "https://www.ejemplo-sitio.es/p/1"})
    lv = ag.service_levels(); assert lv["extraccion"].startswith("SÍ") and lv["datos"].startswith("SÍ") and lv["publico"] and not lv["accesible"]

def test_identical_warnings_are_not_repeated_across_resumes(monkeypatch):
    """El bucle de las 100+ repeticiones: el mismo aviso, turno tras turno. Ahora hay deduplicación y límite persistentes."""
    monkeypatch.setattr(kit, "http_probe", fake_probe(200))
    claim = "Todo listo. La URL pública funciona: https://abc-8000.proxy.runpod.net y está desplegado."
    conv = reqs_conv([], "Despliega el servicio con una URL pública HTTPS y pruébalo." + PAD)
    msgs_hidden = []
    for i in range(4):                                                                  # 1 turno + 3 reanudaciones
        SCRIPT[:] = [{"content": claim}] * 14
        if i: conv["messages"].append({"role": "user", "hidden": True, "content": "REANUDA la tarea"})
        out, conv, ev = run_turn(conv, resume=bool(i))
        assert out == "incomplete"
    hidden = [m["content"] for m in conv["messages"] if m.get("hidden") and "NO puedes cerrar" in m["content"]]
    assert len(hidden) <= 4, len(hidden)                                                # antes: 12 por turno, sin fin entre turnos
    assert Counter(hidden).most_common(1)[0][1] <= 2                                    # ningún texto idéntico más de 2 veces
    ctrl = [m["content"] for m in conv["messages"] if m.get("hidden") and m["role"] == "user" and not m["content"].startswith("REANUDA")]
    assert Counter(ctrl).most_common(1)[0][1] <= 2 
    crit = [c for c in ctrl if c.startswith("CRITERIOS DE ACEPTACIÓN")]; assert len(crit) == len(set(crit))        # el resumen de criterios solo se reenvía si CAMBIÓ
    bl = (Path(conv["run"]["project"]) / "BLOCKERS.md").read_text()
    assert bl.count("criterio BLOQUEADO (public)") == 1 and bl.count("criterio BLOQUEADO (deploy)") <= 1   # cada bloqueo se registra UNA vez
    assert sum(1 for e in ev if e["type"] == "blocker") == 0                            # en las reanudaciones ya no se vuelve a avisar

def test_old_criteria_do_not_block_new_task_and_keep_old_on_continue(monkeypatch):
    monkeypatch.setattr(kit, "http_probe", fake_probe(200))
    git_req = {"kind": "git", "key": "push", "text": "Commit + push verificado", "since": 0, "status": "active", "epoch": 0}
    ag, _ = mk_agent(prior_conv()); ag.reqs = [dict(git_req)]; ag.on_user_message("pruébalo")
    assert kit.rstat(ag.reqs[0]) == "retired" and {r["kind"] for r, _ in ag.unmet()} == {"verify"}      # el criterio antiguo ya no bloquea
    ag2, _ = mk_agent(prior_conv()); ag2.reqs = [dict(git_req)]; ag2.on_user_message("continúa y pruébalo")
    assert kit.rstat(ag2.reqs[0]) == "active"                                                          # «continúa» conserva lo anterior

def test_explicit_criteria_update_replace_retire_reactivate(monkeypatch):
    conv = prior_conv(); conv["run"]["reqs"] = [pub_req(), {"kind": "git", "key": "push", "text": "Commit + push verificado", "since": 0, "status": "active", "epoch": 0}]
    srv.jsave(srv.conv_path(conv["id"]), conv)
    r = srv.criteria_op(conv["id"], "retire", 1); assert r["ok"] and r["criteria"][1]["status"] == "retired"
    r = srv.criteria_op(conv["id"], "reactivate", 1); assert r["criteria"][1]["status"] == "active"
    r = srv.criteria_op(conv["id"], "add", None, "ya no es obligatoria la URL pública; acceso local por SSH"); assert r["ok"]
    st = {c["kind"]: c["status"] for c in srv.criteria_view(conv["id"])}; assert st["public"] == "retired" and st["local"] == "active"
    r = srv.criteria_op(conv["id"], "replace", 1, "pruébalo"); assert any(c["kind"] == "verify" and c["status"] == "active" for c in r["criteria"]) and r["criteria"][1]["status"] == "retired"
    r = srv.criteria_op(conv["id"], "clear"); assert all(c["status"] in ("retired", "done") for c in r["criteria"])        # liberar: nada bloquea y nada se borra
    assert len(srv.criteria_view(conv["id"])) >= 4
    assert not srv.criteria_op("aaaaaaaaaaaa", "clear")["ok"]

def test_extract_changes_natural_language():
    c = kit.extract_changes("La URL pública no es obligatoria en esta fase, acceso local mediante SSH")
    assert "public" in c["drop"] and c["add_local"]
    assert "public" in kit.extract_changes("ya no hace falta la URL pública")["drop"]
    assert "verify" in kit.extract_changes("ignora el requisito de pruebas")["drop"] and "git" in kit.extract_changes("olvida el criterio de github")["drop"]
    assert not kit.extract_changes("Despliega el servicio con URL pública HTTPS")["drop"]           # pedir URL pública NO la retira
    assert kit.extract_changes("continúa con lo de antes")["keep_old"]

def test_user_can_stop_stuck_task_without_losing_anything(monkeypatch):
    """Cancelar una tarea atascada conserva conversación, código y progreso."""
    ev = threading.Event(); conv = reqs_conv([], "Haz algo largo." + PAD); before = len(conv["messages"])
    SCRIPT[:] = [call("write_file", path="keep_me.py", content="x=1")] + [call("bash", command=f"echo v{i}") for i in range(30)]
    n = {"i": 0}; real = srv.call_model
    def wrapped(*a, **k):
        n["i"] += 1
        if n["i"] == 4: ev.set()
        return real(*a, **k)
    monkeypatch.setattr(srv, "call_model", wrapped)
    out = srv.agent_turn(conv, lambda e: None, ev, "agent", "m")
    assert out == "stopped" and len(conv["messages"]) > before and (srv.WORKDIR / "keep_me.py").exists()
    assert srv.jload(srv.conv_path(conv["id"]), {})["run"]["status"] == "stopped"


def test_broad_kill_commands_need_approval():
    """Incidente real: `pkill -f "python.*server.py"` mató el panel y un servicio del usuario."""
    for c in ['pkill -f "python.*server.py"', "killall python3", "pkill uvicorn", "fuser -k 8002/tcp", "kill -9 $(pgrep -f server)", "ps aux | awk '{print $2}' | xargs kill"]:
        assert srv.needs_approval("bash", {"command": c}), c
    assert not srv.needs_approval("bash", {"command": "echo hola && ls"})
    assert "NUNCA uses pkill" in srv.system_base()


def test_explicit_budget_overrides_exhausted_pod_clock(monkeypatch):
    """Incidente: el reloj del pod superó el límite (3h27 > 3h) y toda tarea nueva terminaba al instante con «presupuesto agotado»."""
    monkeypatch.setattr(srv, "LIMIT_H", 1e-6)                                   # pod ya pasado del límite
    SCRIPT[:] = [call("bash", command="echo con_presupuesto"), {"content": "hecho"}]
    conv = {"id": "c%011x" % int(time.time() * 1000), "title": "t", "created": 0, "updated": 0, "messages": [{"role": "user", "content": "haz algo"}]}; ev = []
    out = srv.agent_turn(conv, ev.append, threading.Event(), "agent", "m", budget_min=120)
    assert out == "done" and any("superó el límite" in e.get("text", "") for e in ev)                # avisa, pero trabaja
    assert any(m["role"] == "tool" and "con_presupuesto" in m["content"] for m in conv["messages"])
    conv2 = {"id": "d%011x" % int(time.time() * 1000), "title": "t", "created": 0, "updated": 0, "messages": [{"role": "user", "content": "haz algo"}]}; ev2 = []
    out2 = srv.agent_turn(conv2, ev2.append, threading.Event(), "agent", "m")
    assert out2 == "budget" and any("Escribe un número de minutos" in e.get("text", "") for e in ev2)   # sin presupuesto: mensaje claro, no «agotado 0:00»
