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
    assert ag.exec("plan", {"action": "update", "index": 1, "status": "done", "evidence": "run_tests: 1 passed"})[0]

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
        self.send_response(200); self.send_header("Content-Type", "application/x-ndjson"); self.end_headers()
        msg = {"role": "assistant", "content": "" if item == "empty" else item.get("content", ""), **({"tool_calls": item["tool_calls"]} if item != "empty" and item.get("tool_calls") else {})}
        self.wfile.write((json.dumps({"message": msg, "done": True, "eval_count": 5, "eval_duration": 1e8, "prompt_eval_count": 100}) + "\n").encode())

@pytest.fixture(scope="module", autouse=True)
def fake_ollama():
    srv.OLLAMA = f"http://127.0.0.1:{FAKE_PORT}"; srv.LIMIT_H = 10 ** 6   # el reloj real del pod no debe afectar a las pruebas
    s = ThreadingHTTPServer(("127.0.0.1", FAKE_PORT), Fake); threading.Thread(target=s.serve_forever, daemon=True).start()
    yield; s.shutdown()

def run_turn(conv=None, mode="agent"):
    conv = conv or {"id": "f%d" % int(time.time() * 1000), "messages": [{"role": "user", "content": "haz algo"}], "title": "t", "created": 0, "updated": 0}
    ev = []; time.sleep(0.01)
    out = srv.agent_turn(conv, ev.append, threading.Event(), mode, "m")
    return out, conv, ev

def call(name, **a): return {"tool_calls": [{"function": {"name": name, "arguments": a}}]}

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
