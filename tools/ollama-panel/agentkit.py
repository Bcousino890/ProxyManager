#!/usr/bin/env python3
"""agentkit: herramientas y controlador del agente del Panel del Pod (solo biblioteca estándar).

Contiene lo que hace fiable al agente en sesiones largas:
  · ejecución de comandos con timeout, cancelación, stdout/stderr/código separados y límite de salida
  · herramientas de archivos/Git/pruebas/procesos con esquemas claros
  · detector de secretos (commits, escrituras y logs) y censura
  · memoria de proyecto en disco (TASK/PLAN/PROGRESS/DECISIONS/TEST_RESULTS/BLOCKERS)
  · plan con estados verificables, detector de estancamiento, presupuesto de tiempo real
  · compactación determinista del contexto
Uso como script:  python3 agentkit.py --scan-staged   (hook pre-commit)
"""
import difflib, hashlib, json, math, os, re, signal, subprocess, sys, tempfile, threading, time, urllib.error, urllib.parse, urllib.request
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

HOME = Path(os.environ.get("PANEL_HOME", Path.home() / ".pod-panel"))
ENV = SimpleNamespace(repo=Path(os.environ.get("PANEL_REPO", "/ProxyManager")), workdir=None, branch=os.environ.get("PANEL_BRANCH", "pod-sync"),
                      token=lambda: "", extra_secrets=lambda: [], home=HOME)
ENV.workdir = ENV.repo / "pod-work"
MEMORY_FILES = ["TASK.md", "PLAN.md", "PROGRESS.md", "DECISIONS.md", "TEST_RESULTS.md", "BLOCKERS.md", "ACCEPTANCE.md"]
STATUS_ES = {"pending": "PENDIENTE", "running": "EJECUTANDO", "done": "COMPLETADO", "failed": "FALLIDO", "blocked": "BLOQUEADO"}
PROTECTED = {"main", "master"}

def now_s(): return time.strftime("%Y-%m-%d %H:%M:%S")
def tmp_dir():
    d = ENV.home / "tmp"; d.mkdir(parents=True, exist_ok=True); return d
def out_dir():
    d = ENV.home / "toollog" / "out"; d.mkdir(parents=True, exist_ok=True); return d

# ------------------------------------------------------------------ secretos
_PLACE = re.compile(r"^(pass(word)?|pwd|secret|xxx+|\*+|changeme|clave|contrase.a|example|your.*|token|user|usuario|tu_.*|redacted|\.\.\.)$", re.I)
HARD = [  # (tipo, regex) — alta confianza: bloquean escritura y commit
    ("token de GitHub", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|github_pat_[A-Za-z0-9_]{40,}")),
    ("clave privada", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("clave AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("clave de API (sk-)", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{32,}")),
    ("clave Tavily", re.compile(r"\btvly-[A-Za-z0-9]{20,}")),
    ("token de Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
]
URL_CRED = re.compile(r"\b([a-z][a-z0-9+.\-]*)://([^\s/:@\"'<>]+):([^\s/@\"'<>]{3,})@([^\s/\"'<>]+)", re.I)
GENERIC = re.compile(r"(?i)\b(password|passwd|pwd|secret|api[_\-]?key|access[_\-]?token|auth[_\-]?token|token)\b\s*[:=]\s*[\"']?([A-Za-z0-9/+_\-.]{16,})")
SENSITIVE_NAME = re.compile(r"(^|/)(\.env(\.(?!example$|sample$|template$)[\w.\-]*)?|\.netrc|\.npmrc|\.pypirc|id_(rsa|ed25519|ecdsa|dsa)|github-token|tavily-key|"
                            r"cookies?\.(txt|json|sqlite3?)|credentials?\.json|service[_\-]?account[\w\-]*\.json|proxies?\.(txt|csv|list)|[^/]*\.(pem|key|p12|pfx|jks|sqlite3?|db))$", re.I)

def _entropy(s):
    c = Counter(s); n = len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())

def find_secrets(text):
    """Devuelve lista de tipos de secreto hallados (sin incluir el valor)."""
    found = []
    for kind, rx in HARD:
        if rx.search(text): found.append(kind)
    for m in URL_CRED.finditer(text):
        if m.group(2).lower() in ("x-access-token", "user", "usuario", "username") and _PLACE.match(m.group(3)): continue
        if _PLACE.match(m.group(3)) or re.search(r"[<{$*]", m.group(2) + m.group(3)): continue
        found.append("credenciales en URL/proxy"); break
    for m in GENERIC.finditer(text):
        v = m.group(2)
        if not _PLACE.match(v) and _entropy(v) >= 3.3 and re.search(r"\d", v) and re.search(r"[A-Za-z]", v):
            found.append("contraseña/token literal"); break
    return found

def redact(text):
    if not text: return text
    t = str(text)
    for s in [ENV.token(), *ENV.extra_secrets()]:
        if s and len(s) >= 8: t = t.replace(s, "***")
    for _, rx in HARD: t = rx.sub("***", t)
    t = URL_CRED.sub(lambda m: f"{m.group(1)}://{m.group(2)}:***@{m.group(4)}" if not _PLACE.match(m.group(3)) else m.group(0), t)
    t = re.sub(r"(?i)(authorization:\s*(?:basic|bearer)\s+)\S+", r"\1***", t)
    return t

def scan_staged(repo=None):
    """Revisa lo que hay en el índice de Git. Devuelve [(archivo, motivo)]."""
    repo = str(repo or ENV.repo); bad = []
    r = subprocess.run(["git", "-C", repo, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], capture_output=True, text=True)
    for f in [x for x in r.stdout.split("\0") if x]:
        if SENSITIVE_NAME.search(f): bad.append((f, "archivo sensible por su nombre"))

    d = subprocess.run(["git", "-C", repo, "diff", "--cached", "-U0", "--no-color", "--diff-filter=ACMR"], capture_output=True, text=True, errors="replace").stdout
    cur = None
    for line in d.splitlines():
        if line.startswith("+++ b/"): cur = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            k = find_secrets(line[1:])
            if k and (cur, k[0]) not in bad: bad.append((cur, k[0]))
    return bad

# ------------------------------------------------------------------ rutas y salida
def safe_path(p, must_exist=False):
    q = Path(os.path.expanduser(p or "."))
    q = q if q.is_absolute() else ENV.workdir / q
    q = Path(os.path.realpath(q))
    roots = [Path(os.path.realpath(x)) for x in (ENV.repo, ENV.workdir, ENV.home / "procs", ENV.home / "toollog")]
    if not any(q == r or r in q.parents for r in roots):
        raise ValueError(f"ruta fuera del repositorio: {q}")
    if must_exist and not q.exists(): raise FileNotFoundError(f"no existe: {q}")
    return q

def clip(s, n=8000):
    return s if len(s) <= n else s[: n // 2] + f"\n…[{len(s) - n} caracteres omitidos]…\n" + s[-n // 2:]

def _read_tail(path, limit):
    try:
        with open(path, "rb") as f:
            size = os.fstat(f.fileno()).st_size
            if size <= limit: return f.read().decode("utf-8", "replace"), size
            head = f.read(limit // 2); f.seek(size - limit // 2); tail = f.read()
        return head.decode("utf-8", "replace") + f"\n…[{size - limit} bytes omitidos]…\n" + tail.decode("utf-8", "replace"), size
    except OSError:
        return "", 0

def _kill(p):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try: os.killpg(p.pid, sig)
        except (ProcessLookupError, PermissionError): return
        try: p.wait(timeout=3); return
        except subprocess.TimeoutExpired: continue

def run_cmd(cmd, cwd=None, timeout=120, env=None, stop=None, limit=6000, max_bytes=50_000_000):
    """Ejecuta un comando en su propio grupo de procesos. Devuelve dict(code, stdout, stderr, status, duration, full)."""
    t0 = time.time(); cwd = str(cwd or ENV.workdir)
    fo, po = tempfile.mkstemp(prefix="o-", dir=tmp_dir()); fe, pe = tempfile.mkstemp(prefix="e-", dir=tmp_dir())
    status = "ok"; code = -1
    try:
        with os.fdopen(fo, "wb") as so, os.fdopen(fe, "wb") as se:
            try:
                p = subprocess.Popen(["/bin/bash", "-c", cmd] if isinstance(cmd, str) else list(cmd), cwd=cwd, stdout=so, stderr=se, stdin=subprocess.DEVNULL,
                                     start_new_session=True, env={**os.environ, "PYTHONUNBUFFERED": "1", "GIT_TERMINAL_PROMPT": "0", "PIP_NO_INPUT": "1",
                                                                  "DEBIAN_FRONTEND": "noninteractive", "PIP_DISABLE_PIP_VERSION_CHECK": "1", **(env or {})})
            except Exception as e:
                return {"code": 127, "stdout": "", "stderr": f"[no se pudo iniciar: {e}]", "status": "error", "duration": 0, "full": None}
            while True:
                try: code = p.wait(timeout=0.2); break
                except subprocess.TimeoutExpired: pass
                if stop is not None and stop.is_set(): status, code = "cancelled", 130; _kill(p); break
                if time.time() - t0 > timeout: status, code = "timeout", 124; _kill(p); break
                if os.path.getsize(po) + os.path.getsize(pe) > max_bytes: status, code = "output_limit", 125; _kill(p); break
        so_t, so_n = _read_tail(po, limit); se_t, se_n = _read_tail(pe, limit)
        full = None
        if so_n + se_n > limit:
            full = out_dir() / f"{int(t0)}-{hashlib.md5((str(cmd) + str(t0)).encode()).hexdigest()[:6]}.txt"
            full.write_text(f"$ {redact(str(cmd))}\n--- stdout ---\n" + Path(po).read_bytes()[-2_000_000:].decode("utf-8", "replace") + "\n--- stderr ---\n" + Path(pe).read_bytes()[-2_000_000:].decode("utf-8", "replace"))
        return {"code": code, "stdout": so_t, "stderr": se_t, "status": status, "duration": round(time.time() - t0, 2), "full": str(full) if full else None}
    finally:
        for x in (po, pe):
            try: os.unlink(x)
            except OSError: pass

def fmt_result(r, timeout=None):
    """Texto que ve el modelo: stdout, stderr, código y estado, siempre explícitos."""
    parts = []
    if r["stdout"].strip(): parts.append("[stdout]\n" + r["stdout"].rstrip())
    if r["stderr"].strip(): parts.append("[stderr]\n" + r["stderr"].rstrip())
    if not parts: parts.append("(sin salida)")
    tail = f"[código de salida {r['code']}]"
    if r["status"] == "timeout": tail += f" [TIEMPO AGOTADO tras {timeout}s: el proceso se mató. Si es un servicio o algo largo usa proc_start y luego proc_inspect/logs]"
    elif r["status"] == "cancelled": tail += " [CANCELADO por el usuario]"
    elif r["status"] == "output_limit": tail += " [SALIDA DEMASIADO GRANDE: proceso detenido; redirige a un archivo y léelo por partes]"
    tail += f" [{r['duration']}s]"
    if r.get("full"): tail += f"\n[salida completa guardada en {r['full']}; léela con read_file offset/limit]"
    return redact("\n".join(parts)) + "\n" + tail

# ------------------------------------------------------------------ git
def git(*args, cwd=None, auth=False, timeout=120):
    cmd = ["git", "-c", "user.name=Pod Agent", "-c", "user.email=pod-agent@users.noreply.github.com"]
    if auth and ENV.token():
        import base64
        b = base64.b64encode(f"x-access-token:{ENV.token()}".encode()).decode()
        cmd += ["-c", "credential.helper=", "-c", f"http.extraheader=Authorization: Basic {b}"]
    r = run_cmd(cmd + list(args), cwd=cwd or ENV.repo, timeout=timeout, limit=20000)
    return r["code"], redact(r["stdout"] + r["stderr"])

def remote_hash(branch):
    code, out = git("ls-remote", "--heads", "origin", f"refs/heads/{branch}", auth=True, timeout=60)
    if code: return None, out.strip()
    line = out.strip().split("\n")[0].split()
    return (line[0] if line else ""), ""

def commit_paths(message, paths=None):
    """Commit seguro: añade solo lo pedido, revisa secretos, nunca commitea archivos sensibles."""
    paths = paths or [str(ENV.workdir)]
    git("reset", "-q")  # índice limpio: solo entra lo que añadimos ahora
    code, out = git("add", "-A", "--", *paths)
    if code: return False, f"git add falló: {out.strip()}"
    bad = scan_staged()
    if bad:
        for f, _ in bad: git("reset", "-q", "--", f)
        lst = "; ".join(f"{f} ({k})" for f, k in bad)
        return False, f"COMMIT BLOQUEADO: posibles secretos o archivos sensibles → {lst}. Se han sacado del índice. Quita el secreto (usa variables de entorno / .env ignorado por git) y vuelve a intentarlo."
    if git("diff", "--cached", "--quiet")[0] == 0: return True, "Nada que commitear (sin cambios)."
    code, out = git("commit", "-m", message[:200])
    if code: return False, f"git commit falló: {out.strip()}"
    return True, "Commit creado: " + git("log", "-1", "--format=%h %s")[1].strip()

def push_branch(branch=None, retry=True):
    """Push normal (nunca force) de HEAD a refs/heads/<branch> y verificación del hash remoto."""
    branch = branch or ENV.branch
    if not ENV.token(): return {"ok": False, "msg": "Falta el token de GitHub (botón 🔑 del panel)."}
    code, head = git("rev-parse", "HEAD")
    head = head.strip()
    code, out = git("push", "-u", "origin", f"HEAD:refs/heads/{branch}", auth=True)
    if code and retry and re.search(r"rejected|non-fast-forward|fetch first", out):
        c2, o2 = git("pull", "--rebase", "--autostash", "origin", branch, auth=True)
        if c2:
            git("rebase", "--abort"); return {"ok": False, "msg": "Push rechazado y el rebase automático tuvo conflictos (abortado, nada perdido). Resuélvelo a mano: " + clip(o2.strip(), 400)}
        return push_branch(branch, retry=False)
    if code: return {"ok": False, "msg": clip(out.strip(), 600)}
    rh, err = remote_hash(branch)
    ok = rh == head
    return {"ok": ok, "branch": branch, "local": head, "remote": rh, "msg": f"Rama {branch} en GitHub = {rh[:10] if rh else '?'} ({'coincide con el commit local' if ok else 'NO coincide con ' + head[:10]})"}

# ------------------------------------------------------------------ procesos persistentes
def proc_dir():
    d = ENV.home / "procs"; d.mkdir(parents=True, exist_ok=True); return d

def _alive(pid):
    try:
        st = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
        return st not in ("Z", "X")
    except Exception: return False

def proc_start(name, command, cwd=None):
    name = re.sub(r"[^\w.\-]", "_", name)[:40] or "proc"
    meta = proc_dir() / f"{name}.json"
    if meta.exists() and _alive(json.loads(meta.read_text()).get("pid", 0)):
        return False, f"Ya hay un proceso '{name}' en marcha (pid {json.loads(meta.read_text())['pid']}). Páralo con proc_inspect(action='stop') o usa otro nombre."
    log, exitf = proc_dir() / f"{name}.log", proc_dir() / f"{name}.exit"
    exitf.unlink(missing_ok=True)
    wrapper = f'( {command}\n) ; echo $? > {exitf}'
    p = subprocess.Popen(["/bin/bash", "-c", wrapper], cwd=str(cwd or ENV.workdir), stdout=open(log, "wb"), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    threading.Thread(target=p.wait, daemon=True).start()
    meta.write_text(json.dumps({"name": name, "pid": p.pid, "command": redact(command), "cwd": str(cwd or ENV.workdir), "started": time.time(), "log": str(log), "exit_file": str(exitf)}))
    time.sleep(1.0)
    st = proc_status(name)
    return True, f"Proceso '{name}' iniciado en segundo plano (pid {p.pid}, desacoplado de la terminal). Log: {log}\nEstado tras 1s: {st['state']}" + (f" (código {st['exit']})" if st.get("exit") is not None else "") + \
        ("\nÚltimas líneas:\n" + redact(_read_tail(log, 1500)[0]) if st["state"] != "en marcha" else "")

def proc_status(name):
    meta = proc_dir() / f"{name}.json"
    if not meta.exists(): return {"state": "desconocido"}
    m = json.loads(meta.read_text()); exitf = Path(m["exit_file"])
    alive = _alive(m["pid"]); ex = None
    if exitf.exists():
        try: ex = int(exitf.read_text().strip())
        except ValueError: pass
    return {**m, "state": "en marcha" if alive and ex is None else "terminado", "exit": ex, "uptime_s": int(time.time() - m["started"])}

def proc_list():
    return [proc_status(p.stem) for p in sorted(proc_dir().glob("*.json"))]

def proc_stop(name):
    m = proc_status(name)
    if m["state"] != "en marcha": return f"'{name}' no está en marcha ({m['state']})."
    try: os.killpg(m["pid"], signal.SIGTERM)
    except Exception as e: return f"No pude detenerlo: {e}"
    time.sleep(1)
    if _alive(m["pid"]):
        try: os.killpg(m["pid"], signal.SIGKILL)
        except Exception: pass
    return f"Proceso '{name}' detenido."

# ------------------------------------------------------------------ esquemas de herramientas
def _t(name, desc, props, req=()):
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": {"type": "object", "properties": props, "required": list(req)}}}
S = lambda d: {"type": "string", "description": d}
I = lambda d: {"type": "integer", "description": d}
SCHEMAS = [
    _t("bash", "Ejecuta un comando bash y devuelve [stdout], [stderr] y el código de salida. Con timeout (120 s por defecto, máx. 1800). NO lo uses para servicios o procesos que no terminan: usa proc_start.",
       {"command": S("Comando a ejecutar"), "cwd": S("Directorio de trabajo (por defecto el directorio del proyecto)"), "timeout": I("Segundos máximos")}, ["command"]),
    _t("read_file", "Lee un archivo de texto por partes (400 líneas por defecto). Indica el total de líneas; usa offset/limit para seguir leyendo.",
       {"path": S("Ruta"), "offset": I("Primera línea (1 = inicio)"), "limit": I("Número de líneas (máx. 800)")}, ["path"]),
    _t("write_file", "Crea o sobrescribe un archivo. Para cambios pequeños en uno existente usa edit_file.", {"path": S("Ruta"), "content": S("Contenido completo")}, ["path", "content"]),
    _t("edit_file", "Edita un archivo reemplazando un fragmento EXACTO (old_string debe aparecer una sola vez; incluye algo de contexto).",
       {"path": S("Ruta"), "old_string": S("Texto exacto a reemplazar"), "new_string": S("Texto nuevo"), "replace_all": {"type": "boolean", "description": "Reemplazar todas las apariciones"}}, ["path", "old_string", "new_string"]),
    _t("list_dir", "Lista el contenido de un directorio (archivos con tamaño).", {"path": S("Ruta (por defecto el directorio de trabajo)")}),
    _t("search_files", "Busca texto/regex en archivos (como grep -rn) y devuelve archivo:línea:texto (máx. 80 resultados).",
       {"pattern": S("Expresión regular"), "path": S("Directorio donde buscar"), "glob": S("Filtro de archivos, p. ej. *.py")}, ["pattern"]),
    _t("git_status", "Estado de Git: rama, remoto y cambios sin commitear.", {}),
    _t("git_diff", "Muestra el diff de cambios (sin commitear, o los ya añadidos con staged=true).", {"path": S("Ruta opcional"), "staged": {"type": "boolean"}}),
    _t("git_commit", "Crea un commit con revisión automática de secretos (rechaza .env, tokens, claves, credenciales de proxies). Por defecto incluye todo el directorio de trabajo.",
       {"message": S("Mensaje del commit"), "paths": {"type": "array", "items": {"type": "string"}, "description": "Rutas a incluir (opcional)"}}, ["message"]),
    _t("git_push", "Sube el commit actual a una RAMA de GitHub (nunca force) y verifica que el hash remoto coincide. main/master requieren aprobación del usuario.",
       {"branch": S("Rama de destino (por defecto la rama de sincronización configurada)")}),
    _t("run_tests", "Ejecuta las pruebas del proyecto y devuelve un resumen aprobadas/falladas más la salida. Registra el resultado en TEST_RESULTS.md. Sin comando, detecta pytest/npm test.",
       {"path": S("Directorio del proyecto"), "command": S("Comando de pruebas (opcional)"), "timeout": I("Segundos máximos (por defecto 600)")}),
    _t("proc_start", "Inicia un proceso/servicio de larga duración en segundo plano (desacoplado, con log consultable). Ej.: uvicorn, docker compose up -d, workers.",
       {"name": S("Nombre corto"), "command": S("Comando"), "cwd": S("Directorio")}, ["name", "command"]),
    _t("proc_inspect", "Consulta o detiene procesos iniciados con proc_start. action: list | status | stop.", {"action": S("list|status|stop"), "name": S("Nombre del proceso")}, ["action"]),
    _t("inspect_logs", "Lee el final del log de un proceso (proc_start) o de cualquier archivo de log; admite filtro regex.",
       {"name": S("Nombre del proceso o ruta del log"), "tail": I("Líneas finales (por defecto 80)"), "grep": S("Regex para filtrar")}, ["name"]),
    _t("plan", "Plan de trabajo con estados verificables. action=set crea la lista de tareas (tasks=[texto,...]); action=update cambia una tarea: index (1..n), status (running|done|failed|blocked) y evidence (obligatoria para done: qué comando/prueba lo demuestra).",
       {"action": S("set|update|show"), "tasks": {"type": "array", "items": {"type": "string"}}, "index": I("Número de tarea"), "status": S("running|done|failed|blocked"), "evidence": S("Evidencia (obligatoria para done)")}, ["action"]),
    _t("project_init", "Crea la carpeta del proyecto con sus archivos de memoria persistente (TASK, PLAN, PROGRESS, DECISIONS, TEST_RESULTS, BLOCKERS). Hazlo al empezar un proyecto grande.",
       {"name": S("Nombre de la carpeta del proyecto"), "task": S("Descripción completa de la tarea y restricciones")}, ["name", "task"]),
    _t("memory_update", "Actualiza un archivo de memoria del proyecto (sobrevive a la compactación del contexto). Registra decisiones en DECISIONES.md, bloqueos en BLOCKERS.md, etc.",
       {"file": S("TASK.md|PLAN.md|PROGRESS.md|DECISIONS.md|TEST_RESULTS.md|BLOCKERS.md"), "content": S("Texto"), "mode": S("append (por defecto) | replace")}, ["file", "content"]),
    _t("http_check", "Hace una petición HTTP REAL desde el pod y devuelve estado, tiempo y un fragmento de la respuesta. Es la ÚNICA forma válida de demostrar que una URL/servicio funciona (localhost o pública). Un 403/captcha (p. ej. DataDome) se informa tal cual.",
       {"url": S("URL completa"), "method": S("GET (por defecto) o HEAD/POST"), "contains": S("Texto que debe aparecer en la respuesta (opcional)"), "timeout": I("Segundos (por defecto 15)")}, ["url"]),
    _t("notify", "Envía un aviso al usuario (notificación del navegador). Úsala cuando el usuario lo pida y al terminar una tarea larga.",
       {"title": S("Título"), "message": S("Mensaje")}, ["message"]),
]
NEW_TOOLS = {s["function"]["name"] for s in SCHEMAS}
READONLY = {"http_check", "read_file", "list_dir", "search_files", "git_status", "git_diff", "inspect_logs", "proc_inspect", "plan", "web_search", "web_fetch", "describe_image"}
RO_CMD = re.compile(r"^\s*(ls|cat|head|tail|grep|rg|echo|pwd|which|wc|find|stat|df|du|ps|nvidia-smi|git\s+(status|diff|log|show|branch|remote)|pip\s+(list|show|freeze)|python3?\s+--version|docker\s+(ps|images|logs|inspect))\b")


# ------------------------------------------------------------------ evidencia y criterios de aceptación
URL_RX = re.compile(r"https?://[^\s)\]>\"'`,;]+")
LOCAL_HOST = re.compile(r"^(localhost|127\.\d+\.\d+\.\d+|0\.0\.0\.0|\[?::1\]?|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)$")
IGNORE_TARGET = re.compile(r"(^|\.)(github\.com|githubusercontent\.com|pypi\.org|python\.org|readthedocs\.io|docs\.|npmjs\.com|stackoverflow\.com|wikipedia\.org|runpod\.io)$")
HTTP_CLIENT = re.compile(r"\b(curl|wget|httpx|requests\.(get|post|request)|urllib|aiohttp|http\.client|playwright|fetch\(|http_check)\b")
SITE_HOSTS = {"idealista": "idealista.com", "fotocasa": "fotocasa.es", "habitaclia": "habitaclia.com", "amazon": "amazon.", "zalando": "zalando.", "crawio": "crawio.com"}
VERIFY_RX = re.compile(r"\b(pru[eé]ba(lo|la|s)?|probar|pru[eé]balo|comprueba|comprobar|verifica|verificar|testea|test|run it|try it|check)\b", re.I)
DEPLOY_RX = re.compile(r"\b(publica(r)?|despliega(r)?|desplegad[oa]|deploy|poner? en (producci[oó]n|marcha)|pon(lo|la)? en (l[ií]nea|marcha)|lev[aá]nta(lo|la)|arranca(lo|la)?)\b", re.I)
PUBLIC_RX = re.compile(r"(url|enlace|link|direcci[oó]n)\s+(p[uú]blic[ao]|https(?!:)|accesible)|p[uú]blic[ao]\s+(url|https(?!:))|https(?!:)\s+accesible|accesible\s+desde\s+internet", re.I)
GIT_RX = re.compile(r"\b(github|git\b|commit|push|rama|branch|main)\b", re.I)
SCRAPE_RX = re.compile(r"\b(scrap\w*|extra[ec]\w*|crawl\w*|prueba\w*|probar|ejecuta\w*|run|test\w*|comprueba\w*|verifica\w*|descarga\w*|obt[eé]n\w*)\b", re.I)

def url_host(u):
    try: return (urllib.parse.urlparse(u).hostname or "").lower()
    except Exception: return ""

def is_local(host): return bool(LOCAL_HOST.match(host or ""))

def extract_requirements(text):
    """Criterios de aceptación verificables que se deducen de lo que pide el usuario (sin usar el modelo)."""
    reqs, seen = [], set()
    def add(kind, key, txt):
        if (kind, key) not in seen: seen.add((kind, key)); reqs.append({"kind": kind, "key": key, "text": txt})
    t = text or ""
    urls = [u.rstrip(".") for u in URL_RX.findall(urllib.parse.unquote(t))]
    wants_run = bool(SCRAPE_RX.search(t))
    for u in urls:
        h = url_host(u)
        if h and not is_local(h) and not IGNORE_TARGET.search(h) and wants_run:
            add("target", h, f"Ejecutar una petición real contra {u} (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)")
    for tok in re.findall(r"(?:url|enlace|link|p[aá]gina|sitio|web)\s+de\s+([A-Za-z0-9\-]{3,})", t, re.I):
        k = SITE_HOSTS.get(tok.lower())
        if k and wants_run: add("target", k, f"Ejecutar una petición/extracción real contra una URL de {tok} y reportar el resultado REAL")
    if VERIFY_RX.search(t): add("verify", "run", "Ejecutar una prueba REAL ahora (run_tests o http_check/ejecución) y mostrar su salida")
    dep = DEPLOY_RX.search(t)
    if dep:
        git_ctx = bool(re.search(r"\b(github|rama|branch|commit|push|main)\b", t, re.I))
        if re.search(r"\b(despleg\w*|deploy|url|https|servicio|app|aplicaci[oó]n|producci[oó]n|panel)\b", t, re.I) or not git_ctx:
            add("deploy", "service", "Servicio ejecutándose y comprobado con una petición HTTP real DESPUÉS del último cambio")
        if git_ctx or dep.group(0).lower().startswith("publica"):
            add("git", "push", "Commit + push verificado (hash remoto == local) DESPUÉS del último cambio")
    if PUBLIC_RX.search(t): add("public", "url", "URL pública (no localhost) comprobada con http_check y estado 2xx/3xx")
    return reqs

CLAIM_URL = re.compile(r"(funciona\w*|responde\w*|accesible\w*|disponible\w*|operativ\w*|en l[ií]nea|live|working|up\b|activ[oa]|probad\w*|200)", re.I)
CLAIM_DEPLOY = re.compile(r"(desplegad[oa]s?|deployed|en producci[oó]n|servicio (activo|corriendo|en marcha)|servidor (activo|corriendo|en marcha)|running|publicad[oa] en (producci[oó]n|la url))", re.I)
CLAIM_PUBLIC = re.compile(r"(url|enlace|link|direcci[oó]n)\s+p[uú]blic[ao]|p[uú]blic[ao]mente|accesible desde (internet|fuera)|public url", re.I)
CLAIM_TESTS = re.compile(r"(pruebas?|tests?)\s+(pasan|pasaron|aprobad\w+|ok|correct\w+|exitos\w+)|(todas las|all) (pruebas|tests)|tests? pass", re.I)
CLAIM_GIT = re.compile(r"(push|subid[oa]|publicad[oa]|commit\w*).{0,60}(github|rama|main|remoto)|(github|rama|main).{0,60}(push|subid[oa]|publicad[oa])", re.I)

def http_probe(url, method="GET", timeout=15, headers=None, contains=None, max_bytes=200_000):
    """Petición HTTP real desde el pod. Devuelve dict(status, ok, seconds, bytes, final_url, snippet, error, server)."""
    t0 = time.time(); out = {"url": url, "status": None, "ok": False, "seconds": 0, "bytes": 0, "final_url": url, "snippet": "", "error": None, "server": ""}
    try:
        req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) pod-agent-check/1.0", "Accept": "*/*", **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read(max_bytes); out.update(status=r.status, final_url=r.geturl(), server=r.headers.get("Server", ""))
        except urllib.error.HTTPError as e:
            body = e.read(max_bytes) if hasattr(e, "read") else b""; out.update(status=e.code, final_url=url, server=e.headers.get("Server", "") if e.headers else "")
        txt = body.decode("utf-8", "replace"); out.update(bytes=len(body), snippet=redact(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", txt)).strip()[:300]))
        out["ok"] = out["status"] is not None and out["status"] < 400 and (contains is None or contains in txt)
        if contains is not None and contains not in txt: out["error"] = f"la respuesta no contiene {contains!r}"
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"[:200]
    out["seconds"] = round(time.time() - t0, 2)
    return out

# ------------------------------------------------------------------ estancamiento
class Stagnation:
    """Detecta bucles sin progreso. record() devuelve un motivo (str) cuando hay estancamiento."""
    def __init__(self):
        self.sig = {}; self.world = 0; self.err_sig = None; self.err_n = 0; self.writes = Counter(); self.strikes = 0
        self.empty = 0; self.noaction = 0; self.parsefail = 0; self.blocked = Counter(); self.seen_ok = set(); self.last_key = None; self.consec = 0; self.consec_world = 0; self.fs_world = 0

    def record(self, name, args, ok, out, blocked=False):
        key = json.dumps([name, args], sort_keys=True, default=str)
        osig = hashlib.md5(re.sub(r"\d+(\.\d+)?|0x[0-9a-f]+", "#", out or "")[-600:].encode()).hexdigest()
        if key == self.last_key and self.consec_world == self.fs_world and name not in ("plan", "notify"):
            self.consec += 1
        else:
            self.consec = 1
        self.last_key, self.consec_world = key, self.fs_world
        if name in ("write_file", "edit_file", "git_commit", "proc_start") and ok: self.fs_world += 1
        mutating = name in ("write_file", "edit_file", "git_commit", "proc_start") or (name == "bash" and ok and not RO_CMD.match(str(args.get("command", ""))))
        reason = None
        if blocked:
            self.blocked[key] += 1
            if self.blocked[key] >= 2: reason = f"el comando {name} fue bloqueado/rechazado {self.blocked[key]} veces"
        else:
            prev = self.sig.get(key)
            if self.consec >= 3 and not blocked:
                reason = f"has ejecutado {name} con los mismos argumentos {self.consec} veces seguidas sin cambiar nada entre medias (aunque la salida parezca distinta)"
            if prev and prev == (osig, self.world) and name not in ("plan", "notify", "proc_inspect"):
                reason = reason or f"repites {name} con los mismos argumentos y el resultado no ha cambiado"
            self.sig[key] = (osig, self.world)
            if not ok:
                self.err_n = self.err_n + 1 if self.err_sig == osig else 1; self.err_sig = osig
                if self.err_n >= 3: reason = reason or f"el MISMO error se repitió {self.err_n} veces seguidas"
            else:
                self.err_sig, self.err_n = None, 0
                if key not in self.seen_ok and name not in READONLY: self.strikes = 0
                self.seen_ok.add(key)
            if name in ("write_file", "edit_file"):
                self.writes[str(args.get("path"))] += 1
                if self.writes[str(args.get("path"))] >= 5: reason = reason or f"has reescrito {args.get('path')} {self.writes[str(args.get('path'))]} veces sin pruebas intermedias"
            if name in ("run_tests",) or (name == "bash" and re.search(r"pytest|npm (run )?test|go test|cargo test", str(args.get("command", "")))):
                self.writes.clear()
        if mutating and ok: self.world += 1
        if reason: self.strikes += 1
        return reason

    def reset_counters(self): self.empty = self.noaction = self.parsefail = 0

# ------------------------------------------------------------------ agente
class Agent:
    def __init__(self, conv, emit, stop, legacy, budget_s=None, pod_remaining_s=None, mode="agent"):
        self.conv, self.emit, self.stop, self.legacy, self.mode = conv, emit, stop, legacy, mode
        r = conv.get("run") or {}
        self.tasks = r.get("tasks", []); self.project = Path(r["project"]) if r.get("project") else None
        c = r.get("counts", {})
        self.n_calls, self.n_valid, self.n_invalid, self.n_err = c.get("calls", 0), c.get("valid", 0), c.get("invalid", 0), c.get("errors", 0)
        self.tool_time = Counter(c.get("tool_time", {})); self.tool_n = Counter(c.get("tool_n", {}))
        self.files = set(r.get("files", [])); self.last_test = r.get("last_test"); self.n_compact = r.get("compactions", 0)
        self.strag = Stagnation(); self.world_steps = 0
        self.start = time.time()
        rem = pod_remaining_s if pod_remaining_s is not None else 10 ** 9
        total = min(budget_s or 10 ** 9, rem)
        self.total = total; self.deadline = self.start + total
        self.reserve = min(max(total * 0.15, 180), 900) if total < 10 ** 8 else 0
        self.phase = r.get("phase", "PLANIFICAR" if not self.tasks else "EJECUTAR"); self.last_tool = None
        self.final_notified = False; self.tps = []; self.ctx_tokens = 0; self.nudges = 0
        self.ledger = list(r.get("ledger", [])); self.seq = max([e["seq"] for e in self.ledger] + [0]); self.reqs = list(r.get("reqs", []))
        self.last_mut = r.get("last_mut", 0); self.need_plan = False; self.plan_set_turn = False; self._http = None

    # ---- estado / tiempo
    def elapsed(self): return time.time() - self.start
    def remaining(self): return max(0, self.deadline - time.time())
    def in_reserve(self): return self.reserve and self.remaining() <= self.reserve

    def current_task(self):
        for t in self.tasks:
            if t["status"] == "running": return t["text"]
        for t in self.tasks:
            if t["status"] == "pending": return t["text"]
        return None

    def pending(self): return [t for t in self.tasks if t["status"] in ("pending", "running")]

    def status(self):
        return {"phase": self.phase, "task": self.current_task(), "tasks": self.tasks, "elapsed": int(self.elapsed()), "remaining": None if self.total > 10 ** 8 else int(self.remaining()),
                "calls": self.n_calls, "valid": self.n_valid, "invalid": self.n_invalid, "errors": self.n_err, "files": sorted(self.files)[-12:], "n_files": len(self.files),
                "last_test": self.last_test, "last_tool": self.last_tool, "ctx": self.ctx_tokens, "compactions": self.n_compact, "tps": round(sum(self.tps[-5:]) / len(self.tps[-5:]), 1) if self.tps else None,
                "strikes": self.strag.strikes, "project": str(self.project) if self.project else None,
                "unmet": [r["text"] for r, _ in self.unmet()][:6], "reqs": len(self.reqs)}

    def state(self):
        return {"tasks": self.tasks, "project": str(self.project) if self.project else None, "phase": self.phase, "files": sorted(self.files), "last_test": self.last_test, "compactions": self.n_compact,
                "counts": {"calls": self.n_calls, "valid": self.n_valid, "invalid": self.n_invalid, "errors": self.n_err, "tool_time": dict(self.tool_time), "tool_n": dict(self.tool_n)},
                "ledger": self.ledger[-150:], "reqs": self.reqs, "last_mut": self.last_mut,
                "elapsed_total": self.conv.get("run", {}).get("elapsed_total", 0) + int(self.elapsed())}

    def push_status(self): self.emit({"type": "status", **self.status()})

    def budget_note(self):
        s = f"[ESTADO REAL · fase {self.phase}"
        if self.total < 10 ** 8:
            s += f" · transcurrido {int(self.elapsed() // 60)} min · restante {int(self.remaining() // 60)} min"
            if self.in_reserve(): s += " · ⚠ FASE FINAL: no empieces nada nuevo; prueba, revisa secretos, commit, push y verifica"
        pend = self.pending()
        s += f" · tareas pendientes {len(pend)}/{len(self.tasks)}" if self.tasks else " · sin plan (usa plan action=set)"
        if self.last_test: s += f" · última prueba: {'OK' if self.last_test['ok'] else 'FALLÓ'}"
        return s + "]"

    # ---- memoria de proyecto
    def mem(self, name):
        return (self.project / name) if self.project else None

    def init_project(self, name, task, session=False):
        slug = re.sub(r"[^\w\-]+", "-", name.strip().lower()).strip("-")[:40] or "proyecto"
        old = self.project if (self.project and self.project.parent.name == ".sessions") else None
        d = safe_path((".sessions/" + self.conv["id"]) if session else slug)
        d.mkdir(parents=True, exist_ok=True)
        if old and old != d:   # la memoria de sesión pasa a la carpeta real del proyecto
            for f in MEMORY_FILES:
                if (old / f).exists(): (d / f).write_text((old / f).read_text())
            import shutil; shutil.rmtree(old, ignore_errors=True)
        for f in MEMORY_FILES:
            p = d / f
            if not p.exists():
                p.write_text({"TASK.md": f"# Tarea\n\n{task}\n", "PLAN.md": "# Plan\n\n(sin plan todavía)\n", "PROGRESS.md": f"# Progreso\n\n- {now_s()} proyecto creado\n",
                              "DECISIONS.md": "# Decisiones\n\n", "TEST_RESULTS.md": "# Resultados de pruebas\n\n", "BLOCKERS.md": "# Bloqueos\n\n", "ACCEPTANCE.md": "# Criterios de aceptación (verificados por el controlador)\n\n"}[f])
        self.project = d; self.phase = "PLANIFICAR"
        return d

    def log(self, file, line):
        if not self.project: return
        try:
            with open(self.project / file, "a") as f: f.write(f"- {now_s()} {redact(line)}\n")
        except OSError: pass

    def write_plan_md(self):
        if not self.project: return
        mark = {"pending": " ", "running": "~", "done": "x", "failed": "!", "blocked": "B"}
        lines = ["# Plan", "", "Leyenda: [ ] pendiente · [~] ejecutando · [x] completado (con evidencia) · [!] fallido · [B] bloqueado", ""]
        for i, t in enumerate(self.tasks, 1):
            lines.append(f"{i}. [{mark[t['status']]}] {t['text']}" + (f"  — evidencia: {t['evidence']}" if t.get("evidence") else ""))
        try: (self.project / "PLAN.md").write_text("\n".join(lines) + "\n")
        except OSError: pass

    def memory_snapshot(self, n=5000):
        if not self.project: return ""
        out = []
        for f in ("TASK.md", "ACCEPTANCE.md", "PLAN.md", "PROGRESS.md", "BLOCKERS.md"):
            try:
                t = (self.project / f).read_text()
                out.append(f"--- {f} ---\n" + (t[:n] if f == "TASK.md" else t[-n:]))
            except OSError: pass
        return "\n".join(out)

    # ---- herramientas
    def exec(self, name, args):
        t0 = time.time(); ok, out = True, ""
        try:
            fn = getattr(self, "t_" + name, None)
            if fn: ok, out = fn(args)
            else: ok, out = self.legacy(name, args)
        except Exception as e:
            ok, out = False, f"[error] {type(e).__name__}: {e}"
        dt = time.time() - t0
        out = redact(out)
        self.n_calls += 1; self.n_valid += 1; self.tool_time[name] += dt; self.tool_n[name] += 1
        if not ok: self.n_err += 1
        self.last_tool = {"name": name, "ok": ok, "seconds": round(dt, 2)}
        try: self._ledger_from_call(name, args, ok, out)
        except Exception: pass
        self._log_jsonl(name, args, ok, out, dt)
        return ok, out

    def _log_jsonl(self, name, args, ok, out, dt):
        try:
            d = ENV.home / "toollog"; d.mkdir(parents=True, exist_ok=True)
            a = {k: (redact(str(v))[:300]) for k, v in args.items() if k != "content"}
            with open(d / f"{self.conv['id']}.jsonl", "a") as f:
                f.write(json.dumps({"t": time.time(), "tool": name, "args": a, "ok": ok, "seconds": round(dt, 2), "out": redact(out)[:200]}, ensure_ascii=False) + "\n")
        except OSError: pass

    def t_bash(self, a):
        cmd = str(a.get("command", ""))
        if not cmd.strip(): return False, "command vacío"
        timeout = min(int(a.get("timeout") or 120), 1800)
        cwd = safe_path(a["cwd"]) if a.get("cwd") else (self.project or ENV.workdir)
        r = run_cmd(cmd, cwd=cwd, timeout=timeout, stop=self.stop)
        self.phase = "CORREGIR" if r["code"] and self.phase == "VERIFICAR" else self.phase
        if re.search(r"pytest|npm (run )?test|go test|cargo test|unittest", cmd) and not re.search(r"\b(pip3?|npm|apt-get|apt)\s+install\b|venv", cmd): self._note_test(cmd, r)
        elif r["code"] == 0 and re.search(r"\b(pip|npm|apt-get|apt)\s+install\b", cmd): self.log("PROGRESS.md", f"instalación: {cmd[:100]}")
        return r["code"] == 0, fmt_result(r, timeout)

    def _note_test(self, cmd, r):
        text = r["stdout"] + "\n" + r["stderr"]
        m_p, m_f = re.search(r"(\d+) passed", text), re.search(r"(\d+) (?:failed|error)", text)
        summ = f"{m_p.group(1) if m_p else 0} aprobadas, {m_f.group(1) if m_f else 0} falladas/errores (exit {r['code']})"
        ok = r["code"] == 0
        self.last_test = {"ok": ok, "summary": summ, "cmd": redact(cmd)[:120], "t": time.time()}
        self.phase = "VERIFICAR" if ok else "CORREGIR"
        self.log("TEST_RESULTS.md", f"`{redact(cmd)[:100]}` → {'OK' if ok else 'FALLÓ'}: {summ}" + ("" if ok else "\n  " + redact(clip(text.strip(), 600)).replace("\n", "\n  ")))
        self.log("PROGRESS.md", f"pruebas {'OK' if ok else 'FALLARON'}: {summ}")

    def t_run_tests(self, a):
        base = safe_path(a["path"]) if a.get("path") else (self.project or ENV.workdir)
        cmd = a.get("command")
        if not cmd:
            py = base / ".venv/bin/python"
            if (base / "package.json").exists() and not (base / "tests").exists(): cmd = "npm test --silent"
            else: cmd = f"{py if py.exists() else 'python3'} -m pytest -q -x --tb=short"
        timeout = min(int(a.get("timeout") or 600), 1800)
        r = run_cmd(cmd, cwd=base, timeout=timeout, stop=self.stop, limit=7000)
        self._note_test(cmd, r)
        lt = self.last_test
        return r["code"] == 0, f"RESULTADO DE PRUEBAS: {'APROBADAS' if lt['ok'] else 'FALLARON'} — {lt['summary']}\n" + fmt_result(r, timeout)

    def t_read_file(self, a):
        p = safe_path(a.get("path"), must_exist=True)
        if p.is_dir(): return False, f"{p} es un directorio; usa list_dir"
        if b"\0" in p.read_bytes()[:4096]: return False, f"{p} parece binario ({p.stat().st_size} bytes)"
        lines = p.read_text(errors="replace").splitlines()
        off = max(1, int(a.get("offset") or 1)); lim = min(max(1, int(a.get("limit") or 400)), 800)
        chunk = lines[off - 1: off - 1 + lim]
        body = clip("\n".join(f"{off + i}: {l}" for i, l in enumerate(chunk)), 14000)
        end = off + len(chunk) - 1
        return True, f"{p} · líneas {off}-{end} de {len(lines)}" + (f" · SIGUE: usa offset={end + 1}" if end < len(lines) else " · (fin)") + "\n" + body

    def _guard_write(self, p, content):
        bad = [k for k in find_secrets(content) if k not in ("contraseña/token literal",)]
        if bad and not p.name.endswith((".example", ".sample", ".md")):
            return f"ESCRITURA BLOQUEADA: el contenido parece incluir un secreto ({', '.join(bad)}). Usa variables de entorno o un archivo .env (ignorado por git) y referencia el nombre de la variable."
        if SENSITIVE_NAME.search(str(p)) and p.suffix not in (".example",):
            return None  # se permite escribir .env locales; el commit los bloquea
        return None

    def t_write_file(self, a):
        p = safe_path(a.get("path")); content = a.get("content", "")
        if not isinstance(content, str): content = json.dumps(content, indent=2, ensure_ascii=False)
        err = self._guard_write(p, content)
        if err: return False, err
        existed = p.exists()
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content)
        if p.read_text() != content: return False, f"La escritura de {p} no se verificó (contenido distinto al leerlo)"
        self.files.add(str(p)); self.phase = "EJECUTAR" if self.phase != "CORREGIR" else self.phase
        self.log("PROGRESS.md", f"{'reescrito' if existed else 'creado'} {p.name} ({len(content)} car.)")
        return True, f"{'Reescrito' if existed else 'Creado'} {p} ({len(content)} caracteres, {content.count(chr(10)) + 1} líneas)"

    def t_edit_file(self, a):
        p = safe_path(a.get("path"), must_exist=True); old, new = a.get("old_string", ""), a.get("new_string", "")
        txt = p.read_text(); n = txt.count(old) if old else 0
        if not old: return False, "old_string vacío"
        if n == 0:
            first = old.strip().splitlines()[0].strip() if old.strip() else ""
            hints = [f"{i + 1}: {l}" for i, l in enumerate(txt.splitlines()) if first and first[:40] in l][:3]
            return False, "old_string no aparece en el archivo (debe coincidir EXACTO, incluida la indentación)." + ("\nLíneas parecidas:\n" + "\n".join(hints) if hints else " Lee el archivo con read_file y copia el fragmento.")
        if n > 1 and not a.get("replace_all"): return False, f"old_string aparece {n} veces; añade más contexto o usa replace_all=true."
        err = self._guard_write(p, new)
        if err: return False, err
        p.write_text(txt.replace(old, new) if a.get("replace_all") else txt.replace(old, new, 1))
        self.files.add(str(p)); self.log("PROGRESS.md", f"editado {p.name}")
        return True, f"Editado {p} ({n if a.get('replace_all') else 1} reemplazo/s)"

    def t_list_dir(self, a):
        p = safe_path(a.get("path") or ".", must_exist=True)
        items = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
        return True, f"{p}\n" + ("\n".join(("📁 " + i.name + "/") if i.is_dir() else f"   {i.name}  ({i.stat().st_size} B)" for i in items[:200]) or "(vacío)")

    def t_search_files(self, a):
        base = safe_path(a.get("path") or ".", must_exist=True)
        cmd = ["grep", "-rnIE", "--exclude-dir=.git", "--exclude-dir=node_modules", "--exclude-dir=.venv", "--exclude-dir=__pycache__"]
        if a.get("glob"): cmd += [f"--include={a['glob']}"]
        r = run_cmd(cmd + ["-m", "20", "--", str(a.get("pattern", "")), str(base)], cwd=base, timeout=30, limit=20000)
        lines = r["stdout"].splitlines()
        if r["code"] == 1 and not lines: return True, "(sin coincidencias)"
        if r["code"] > 1: return False, r["stderr"].strip() or "error de grep"
        return True, "\n".join(lines[:80]) + (f"\n…[{len(lines) - 80} más]" if len(lines) > 80 else "")

    def t_git_status(self, a):
        _, br = git("rev-parse", "--abbrev-ref", "HEAD"); _, st = git("status", "--short", "--branch")
        _, remote = git("remote", "get-url", "origin")
        return True, f"Remoto: {re.sub(r'https://[^@]+@', 'https://', remote.strip())}\nRama configurada de publicación: {ENV.branch}\n{st.strip()}"

    def t_git_diff(self, a):
        args = ["diff", "--no-color", "--stat", "-p"] + (["--cached"] if a.get("staged") else []) + (["--", str(safe_path(a["path"]))] if a.get("path") else [])
        _, out = git(*args)
        return True, clip(out.strip() or "(sin cambios)", 9000)

    def t_git_commit(self, a):
        paths = [str(safe_path(x)) for x in a.get("paths") or []] or None
        ok, msg = commit_paths(str(a.get("message", "")).strip() or "pod: cambios del agente", paths)
        self.log("PROGRESS.md", ("commit: " if ok else "COMMIT BLOQUEADO: ") + msg[:150])
        if not ok: self.log("BLOCKERS.md", msg[:300])
        if ok: self.phase = "PUBLICAR"
        return ok, msg

    def t_git_push(self, a):
        r = push_branch(str(a.get("branch") or ENV.branch))
        self.log("PROGRESS.md", ("push OK: " if r["ok"] else "push FALLÓ: ") + r["msg"][:150])
        return r["ok"], r["msg"]

    def t_proc_start(self, a):
        return proc_start(str(a.get("name", "proc")), str(a.get("command", "")), safe_path(a["cwd"]) if a.get("cwd") else (self.project or ENV.workdir))

    def t_proc_inspect(self, a):
        act, name = str(a.get("action", "list")), re.sub(r"[^\w.\-]", "_", str(a.get("name", "")))
        if act == "list":
            L = proc_list()
            return True, "\n".join(f"{m['name']}: {m['state']}" + (f" (código {m['exit']})" if m.get("exit") is not None else "") + f" · pid {m.get('pid')} · {m.get('uptime_s', 0)}s · {m.get('command', '')[:80]}" for m in L) or "(ningún proceso gestionado)"
        if act == "stop": return True, proc_stop(name)
        m = proc_status(name)
        if m["state"] == "desconocido": return False, f"No existe el proceso '{name}'"
        return True, json.dumps({k: m.get(k) for k in ("name", "state", "exit", "pid", "uptime_s", "command", "log")}, ensure_ascii=False)

    def t_inspect_logs(self, a):
        n = str(a.get("name", "")); tail = min(int(a.get("tail") or 80), 400)
        p = proc_dir() / f"{re.sub(r'[^\w.\-]', '_', n)}.log"
        if not p.exists(): p = safe_path(n, must_exist=True)
        lines = p.read_text(errors="replace").splitlines()
        if a.get("grep"):
            rx = re.compile(str(a["grep"]), re.I); lines = [l for l in lines if rx.search(l)]
        return True, f"{p} ({len(lines)} líneas{' filtradas' if a.get('grep') else ''})\n" + clip("\n".join(lines[-tail:]), 9000)

    def t_notify(self, a):
        self.emit({"type": "notify", "title": str(a.get("title") or "Panel del Pod"), "text": str(a.get("message", ""))})
        return True, "Aviso enviado al usuario."

    def t_project_init(self, a):
        d = self.init_project(str(a.get("name", "proyecto")), str(a.get("task", "")))
        return True, f"Proyecto en {d} con {', '.join(MEMORY_FILES)}. Actualiza PROGRESS/DECISIONS con memory_update y define el plan con plan(action='set')."

    def t_memory_update(self, a):
        if not self.project: return False, "No hay proyecto: llama primero a project_init."
        f = str(a.get("file", "")).strip()
        if f not in MEMORY_FILES: return False, f"file debe ser uno de {MEMORY_FILES}"
        txt = redact(str(a.get("content", "")))
        if str(a.get("mode", "append")) == "replace": (self.project / f).write_text(txt.rstrip() + "\n")
        else:
            with open(self.project / f, "a") as fh: fh.write(f"\n- {now_s()} {txt.strip()}\n")
        return True, f"{f} actualizado."

    def t_plan(self, a):
        act = str(a.get("action", "show"))
        if act == "set":
            ts = [str(x).strip() for x in (a.get("tasks") or []) if str(x).strip()]
            if not ts: return False, "tasks vacío"
            self.tasks = [{"text": t, "status": "pending", "evidence": ""} for t in ts[:30]]
            self.phase = "EJECUTAR"; self.plan_set_turn = True; self.need_plan = False
            for t in self.tasks: t["since_seq"] = self.seq
            self.write_plan_md(); self.log("PROGRESS.md", f"plan creado con {len(self.tasks)} tareas")
        elif act == "update":
            i = int(a.get("index") or 0); st = str(a.get("status", "")).lower(); ev = str(a.get("evidence", "")).strip()
            if not 1 <= i <= len(self.tasks): return False, f"index fuera de rango (1..{len(self.tasks)})"
            if st not in ("running", "done", "failed", "blocked", "pending"): return False, "status inválido"
            if st == "done":
                if len(ev) < 25: return False, "COMPLETADO exige evidencia concreta (comando ejecutado, salida/estado HTTP, resultado de pruebas, hash) de al menos una frase."
                miss = self.task_evidence_missing(self.tasks[i - 1]["text"], self.tasks[i - 1].get("since_seq", 0))
                if miss: return False, "No se puede marcar COMPLETADO: " + miss
                if self.world_steps_since(i) == 0: return False, "No hay ninguna herramienta ejecutada con éxito desde que empezó esta tarea: no se puede marcar COMPLETADO sin evidencia real."
            self.tasks[i - 1].update(status=st, evidence=ev if ev else self.tasks[i - 1].get("evidence", ""))
            if st == "running": self.tasks[i - 1]["since"] = self.n_valid
            self.write_plan_md(); self.log("PROGRESS.md", f"tarea {i} → {STATUS_ES[st]}: {self.tasks[i - 1]['text'][:80]}")
            if st in ("failed", "blocked"): self.log("BLOCKERS.md", f"tarea {i} {STATUS_ES[st]}: {ev[:200]}")
        self.emit({"type": "plan", "tasks": self.tasks})
        return True, "\n".join(f"{i}. [{STATUS_ES[t['status']]}] {t['text']}" for i, t in enumerate(self.tasks, 1)) or "(sin plan)"

    def task_evidence_missing(self, text, since):
        """Evidencia que el tipo de tarea exige antes de poder darla por completada (None = suficiente)."""
        t = text.lower()
        if re.search(r"(ejecut|corr|pas|aprob|verific|valid)\w*.{0,25}(prueba|test)|run_tests|pytest", t) and not (self.after_last_change(("test",), True, since) or self.after_last_change(("http",), True, since)):
            return "la tarea implica pruebas y no hay un run_tests (o http_check) exitoso posterior al último cambio."
        if re.search(r"(prueb\w*|prob\w*|verific\w*|comprob\w*|valid\w*).{0,30}(http|url|endpoint|servicio|responde|health)|(http|url|endpoint).{0,30}(funciona|responde|accesible)", t) and not self.after_last_change(("http",), True, since):
            return "la tarea implica una URL/endpoint y no hay ninguna petición HTTP exitosa (http_check) posterior al último cambio."
        if re.search(r"url p[uú]blica|p[uú]blic\w* (la )?(url|app)|https p[uú]blic", t) and not self.after_last_change(("http",), True, since, local=False):
            return "la tarea es una URL PÚBLICA y no hay una comprobación HTTP exitosa a un host no local (localhost no cuenta; una variable de configuración no cuenta)."
        if re.search(r"despleg|deploy|levantar (el )?servicio|arrancar (el )?servicio|poner en (marcha|producci)", t) and not self.service_ok(since):
            return "la tarea es un despliegue y no hay un servicio vivo comprobado con HTTP."
        if re.search(r"(commit|push|publicar).{0,30}(github|rama|main)|verificar.{0,15}hash", t) and not self.after_last_change(("git_push",), True, since):
            return "la tarea es publicar en GitHub y no hay un git_push con hash remoto verificado."
        if re.search(r"scrap|extra[ec]\w* (de|desde)|idealista|crawl", t) and re.search(r"(ejecut|prob|real)", t) and not self.after_last_change(("http",), False, since):
            return "la tarea es ejecutar scraping real y no hay ninguna petición ejecutada."
        return None

    def world_steps_since(self, i):
        since = self.tasks[i - 1].get("since", 0)
        return self.n_valid - since - 1 if self.n_valid > since else 0


    # ---- evidencia real (libro de pruebas) y criterios de aceptación
    def _ev(self, kind, ok, **kw):
        self.seq += 1
        e = {"seq": self.seq, "kind": kind, "ok": bool(ok), "t": time.time(), **kw}
        self.ledger.append(e); self.ledger = self.ledger[-300:]
        if kind == "mutation": self.last_mut = self.seq
        return e

    def _ledger_from_call(self, name, args, ok, out):
        if name in ("write_file", "edit_file") and ok:
            p = str(args.get("path", ""))
            if Path(p).name not in MEMORY_FILES and ".sessions" not in p: self._ev("mutation", True, path=p)
        elif name == "run_tests":
            self._ev("test", ok, detail=(self.last_test or {}).get("summary", ""))
        elif name == "http_check" and self._http:
            h = self._http; self._ev("http", h["ok"], url=h["url"], host=url_host(h["url"]), local=is_local(url_host(h["url"])), status=h["status"], error=h.get("error"))
        elif name == "bash":
            cmd = urllib.parse.unquote(str(args.get("command", "")))
            if re.search(r"pytest|npm (run )?test|go test|cargo test", cmd) and not re.search(r"\b(pip3?|npm)\s+install\b", cmd) and self.last_test:
                self._ev("test", self.last_test["ok"], detail=self.last_test["summary"])
            if HTTP_CLIENT.search(cmd):
                m = re.search(r"\b([1-5]\d\d)\b", out.split("[código")[0][-400:]) if ok else None
                for u in list(dict.fromkeys(URL_RX.findall(cmd)))[:4]:
                    self._ev("http", ok, url=u, host=url_host(u), local=is_local(url_host(u)), status=int(m.group(1)) if m and ok else None, via="bash")
            if ok and re.search(r"docker( compose|-compose)?\s+(compose\s+)?(up|run)\b", cmd): self._ev("service", True, detail="docker up")
            if ok and re.search(r"\bpkill|kill\b", cmd): pass
        elif name == "proc_start":
            time.sleep(0.1); nm = re.sub(r"[^\w.\-]", "_", str(args.get("name", "proc")))[:40]
            self._ev("service", ok and proc_status(nm)["state"] == "en marcha", detail=f"proc {nm}")
        elif name == "git_commit" and ok: self._ev("git_commit", True)
        elif name == "git_push": self._ev("git_push", ok, detail=out[:120])

    def t_http_check(self, a):
        url = str(a.get("url", "")).strip()
        if not re.match(r"https?://", url): return False, "url debe empezar por http:// o https://"
        h = http_probe(url, str(a.get("method") or "GET").upper(), min(int(a.get("timeout") or 15), 60), contains=a.get("contains"))
        self._http = h
        local = is_local(url_host(url))
        txt = (f"HTTP {h['status']} · {h['seconds']}s · {h['bytes']} bytes · servidor: {h['server'] or '?'}" if h["status"] is not None else f"SIN RESPUESTA: {h['error']}")
        if h["final_url"] != url: txt += f"\nRedirigido a: {h['final_url']}"
        txt += f"\nOrigen de la comprobación: {'LOCAL (localhost/red privada: NO demuestra una URL pública)' if local else 'URL externa/pública'}"
        if h["error"] and h["status"] is not None: txt += f"\n{h['error']}"
        if h["snippet"]: txt += "\nFragmento: " + h["snippet"]
        if h["status"] in (401, 403, 429, 503): txt += "\n[Posible bloqueo/antibot: infórmalo tal cual; no lo presentes como éxito]"
        return h["ok"], txt

    def after_last_change(self, kinds, ok=True, since=0, local=None, host=None):
        lim = max(self.last_mut, since)
        for e in reversed(self.ledger):
            if e["seq"] <= lim: break
            if e["kind"] in kinds and (e["ok"] or not ok) and (local is None or e.get("local") == local) and (host is None or host in (e.get("host") or "")):
                return e
        return None

    def service_ok(self, since=0):
        if self.after_last_change(("http",), True, since, local=True) or self.after_last_change(("http",), True, since, local=False): return True
        e = self.after_last_change(("service",), True, since)
        if e and any(m["state"] == "en marcha" for m in proc_list()): return True
        return bool(e and e.get("detail") == "docker up")

    def unmet(self):
        """[(requisito, acción concreta)] de los criterios todavía sin evidencia."""
        out = []
        for r in self.reqs:
            if r.get("done"): continue
            since, k = r.get("since", 0), r["kind"]
            if k == "target":
                e = next((x for x in self.ledger if x["seq"] > since and x["kind"] == "http" and r["key"] in (x.get("host") or "")), None)
                if not e: out.append((r, f"ejecuta http_check sobre la URL objetivo ({r['key']}) o llama a tu servicio con esa URL y muestra el resultado real"))
            elif k == "verify":
                has_target = any(x["kind"] == "target" for x in self.reqs)
                blocked_attempt = has_target and any(e["seq"] > max(since, self.last_mut) and e["kind"] == "http" and e.get("status") for e in self.ledger)   # 403/captcha reportado = intento real
                if not (self.after_last_change(("test",), True, since) or self.after_last_change(("http",), True, since) or blocked_attempt):
                    out.append((r, "ejecuta run_tests y/o http_check AHORA (la evidencia anterior no vale: es previa a tu último cambio o a esta petición)"))
            elif k == "deploy":
                if not self.service_ok(since): out.append((r, "arranca el servicio con proc_start y compruébalo con http_check (la URL debe responder 2xx/3xx)"))
            elif k == "public":
                if not self.after_last_change(("http",), True, since, local=False): out.append((r, "comprueba con http_check la URL PÚBLICA (https://<POD_ID>-<puerto>.proxy.runpod.net o la que corresponda); localhost no cuenta"))
            elif k == "git":
                if not self.after_last_change(("git_push",), True, since): out.append((r, "git_commit y git_push a la rama (verifica el hash remoto)"))
        return out

    def add_requirements(self, text):
        new = []
        have = {(r["kind"], r["key"]) for r in self.reqs if not r.get("done")}
        for r in extract_requirements(text):
            if (r["kind"], r["key"]) not in have:
                r.update(since=self.seq, added=now_s()); self.reqs.append(r); new.append(r)
        self.reqs = self.reqs[-30:]
        return new

    def settle(self):
        """Marca como cumplidos los criterios con evidencia (se llama antes de evaluar)."""
        pend = {id(r) for r, _ in self.unmet()}
        for r in self.reqs:
            if id(r) not in pend and not r.get("done"): r["done"] = True
        return self.reqs

    def claim_problems(self, content):
        """Cosas que el modelo AFIRMA en su respuesta final sin que haya prueba ejecutada."""
        out = []; txt = content or ""
        if not txt.strip(): return out
        for m in URL_RX.finditer(txt):
            u = m.group(0).rstrip(".,"); h = url_host(u)
            ctx = txt[max(0, m.start() - 140): m.end() + 140]
            if not (CLAIM_URL.search(ctx) or CLAIM_PUBLIC.search(ctx)) or IGNORE_TARGET.search(h): continue
            if not self.after_last_change(("http",), True, 0, host=h):
                out.append(f"Afirmas que {u} funciona/responde pero NO hay ninguna petición HTTP exitosa ejecutada contra ese host después de tu último cambio. Usa http_check({u}).")
            if CLAIM_PUBLIC.search(ctx) and is_local(h):
                out.append(f"Llamas «URL pública» a {u}, que es local (localhost/red privada). Una URL pública exige un host accesible desde internet y comprobado con http_check; añadir una variable `public_url` NO basta.")
        if CLAIM_PUBLIC.search(txt) and not self.after_last_change(("http",), True, 0, local=False):
            out.append("Declaras una URL pública pero no existe ninguna comprobación HTTP exitosa a un host NO local. Comprueba la URL pública real con http_check o di claramente que NO está publicada.")
        if CLAIM_DEPLOY.search(txt) and not self.service_ok():
            out.append("Declaras la aplicación desplegada/en marcha pero no hay evidencia de servicio vivo (proc_start + http_check exitoso después del último cambio).")
        if CLAIM_TESTS.search(txt) and not self.after_last_change(("test",), True, 0):
            out.append("Declaras que las pruebas pasan pero no hay un run_tests exitoso posterior a tu último cambio.")
        if CLAIM_GIT.search(txt) and not self.after_last_change(("git_push",), True, 0) and not re.search(r"(no (se )?(ha|he)? ?(publicad|subid)|sin publicar|pendiente de publicar)", txt, re.I):
            out.append("Declaras publicación en GitHub pero no hay git_push con hash remoto verificado después del último cambio.")
        return out

    def completion_problems(self, content, prev_final=None):
        """Motivos por los que NO se puede cerrar la tarea ahora (lista vacía = se puede cerrar)."""
        self.settle(); out = []
        if self.need_plan and not self.plan_set_turn and self.unmet():
            out.append("Hay una instrucción nueva y no has creado un plan nuevo. Haz plan(action='set') con tareas que cubran lo pedido (y ejecútalas).")
        for r, hint in self.unmet(): out.append(f"Requisito sin evidencia: «{r['text']}» → {hint}.")
        out += self.claim_problems(content)
        if prev_final and content and len(content) > 80 and difflib.SequenceMatcher(None, prev_final[:700], content[:700]).ratio() > 0.85 and (self.unmet() or self.need_plan):
            out.append("Estás repitiendo tu resumen anterior en vez de ejecutar lo que el usuario acaba de pedir. Usa herramientas.")
        return out

    def on_user_message(self, text):
        """Cada instrucción nueva crea criterios nuevos y obliga a un plan nuevo si el anterior estaba completo."""
        new = self.add_requirements(text)
        if self.tasks and all(t["status"] in ("done", "failed", "blocked") for t in self.tasks):
            self.log("PROGRESS.md", f"plan anterior archivado ({len(self.tasks)} tareas); nueva instrucción recibida"); self.tasks = []
        self.need_plan = bool(new) or self.need_plan
        self.plan_set_turn = False
        if self.project:
            try:
                with open(self.project / "TASK.md", "a") as f: f.write(f"\n\n## Instrucción del usuario ({now_s()})\n\n{redact(text)[:8000]}\n")
            except OSError: pass
        self.write_acceptance()
        return new

    def write_acceptance(self):
        if not self.project: return
        unmet = {id(r) for r, _ in self.unmet()}
        lines = ["# Criterios de aceptación (verificados por el controlador con evidencia real)", ""]
        for r in self.reqs: lines.append(f"- [{'x' if r.get('done') or id(r) not in unmet else ' '}] ({r['kind']}) {r['text']}")
        try: (self.project / "ACCEPTANCE.md").write_text("\n".join(lines) + "\n")
        except OSError: pass

    def verified_report(self):
        """Estado REAL, separado: GIT vs APLICACIÓN vs PRUEBAS vs REQUISITOS. Lo calcula el controlador, no el modelo."""
        L = ["**Estado verificado por el controlador** (comprobaciones reales, no el resumen del modelo)"]
        _, br = git("rev-parse", "--abbrev-ref", "HEAD"); _, head = git("rev-parse", "HEAD"); head = head.strip()
        rh, err = remote_hash(ENV.branch); _, dirty = git("status", "--porcelain")
        n_dirty = len([l for l in dirty.splitlines() if l.strip()])
        L.append(f"- **Git**: rama local `{br.strip()}` @{head[:8]} · rama de publicación `{ENV.branch}` en GitHub: " + (f"@{rh[:8]} ({'COINCIDE' if rh == head else 'DIFIERE del commit local'})" if rh else "no existe/no consultable") + f" · {n_dirty} archivos sin commitear")
        procs = proc_list()
        L.append("- **Aplicación (procesos)**: " + ("; ".join(f"{p['name']}: {p['state']}" for p in procs) if procs else "ninguno gestionado por el panel"))
        https = [e for e in self.ledger if e["kind"] == "http"][-4:]
        if https:
            for e in https:
                live = http_probe(e["url"], timeout=6) if e["seq"] > self.last_mut else None
                L.append(f"- **HTTP** {e['url']}: {'OK' if e['ok'] else 'FALLÓ'}" + (f" (estado {e.get('status')})" if e.get("status") else "") + (" · local" if e.get("local") else " · externa") +
                         (f" · ahora: {live['status'] if live['status'] is not None else live['error']}" if live else " · evidencia anterior al último cambio"))
        else: L.append("- **HTTP**: ninguna petición ejecutada")
        L.append("- **Pruebas**: " + (f"{'OK' if self.last_test['ok'] else 'FALLARON'} — {self.last_test['summary']}" if self.last_test else "no ejecutadas"))
        self.settle(); un = self.unmet()
        if un: L.append("- **⚠ Requisitos SIN cumplir**: " + "; ".join(r["text"] for r, _ in un))
        elif self.reqs: L.append("- Requisitos del usuario: todos con evidencia")
        self.write_acceptance()
        return "\n".join(L)

    # ---- contexto
    def estimate_tokens(self, msgs):
        return int(sum(len(json.dumps(m, ensure_ascii=False)) for m in msgs) / 3.2)

    def compact(self, keep=8):
        """Resume de forma determinista lo antiguo sin perder instrucciones: conserva TODOS los mensajes
        del usuario, decisiones/archivos/errores/pruebas y la memoria del proyecto."""
        msgs = self.conv["messages"]; c = self.conv.setdefault("ctx", {"upto": 0, "summary": ""})
        cut = max(c["upto"], len(msgs) - keep)
        while cut < len(msgs) and msgs[cut].get("role") == "tool": cut -= 1
        if cut <= c["upto"]: return False
        digest = []
        for m in msgs[c["upto"]:cut]:
            if m["role"] == "user" and not m.get("hidden"): digest.append("USUARIO: " + clip(m.get("display") or m.get("content", ""), 12000 if not digest else 6000))
            elif m["role"] == "user": digest.append("(aviso del controlador) " + clip(m.get("content", ""), 200))
            elif m["role"] == "assistant":
                for tc in m.get("tool_calls") or []:
                    f = tc["function"]; ar = f.get("arguments") or {}
                    digest.append(f"→ {f['name']}({redact(clip(str(ar.get('command') or ar.get('path') or ar.get('query') or ar.get('message') or ar.get('pattern') or ''), 110))})")
                if m.get("content") and not m.get("tool_calls"): digest.append("AGENTE: " + clip(m["content"], 300))
            elif m["role"] == "tool":
                first = next((l for l in (m.get("content") or "").splitlines() if l.strip()), "")
                m_c = re.search(r"\[código de salida (-?\d+)\]", m.get("content", ""))
                digest.append(f"   ← {'OK' if m.get('ok', True) else 'FALLÓ'}{' exit ' + m_c.group(1) if m_c else ''}: {clip(first, 140)}")
        merged = (c["summary"] + "\n" if c["summary"] else "") + "\n".join(digest)
        if len(merged) > 24000:   # conserva el principio (tarea original) y lo más reciente
            merged = merged[:12500] + "\n…[historial antiguo omitido]…\n" + merged[-11000:]
        c["summary"], c["upto"] = merged, cut
        self.n_compact += 1
        self.log("PROGRESS.md", f"contexto compactado ({cut} mensajes resumidos)")
        self.emit({"type": "notice", "text": f"Contexto compactado: {cut} mensajes antiguos resumidos (instrucciones, decisiones, archivos y errores conservados; el proyecto sigue en sus archivos de memoria)."})
        return True

    def build_view(self, system, msgs, transient=None):
        """Mensajes que ve el modelo: sistema + resumen + cola reciente + estado real (transitorio)."""
        c = self.conv.get("ctx") or {"upto": 0, "summary": ""}
        out = [{"role": "system", "content": system}]
        if c["summary"] or self.project:
            snap = self.memory_snapshot()
            out.append({"role": "user", "content": "[CONTEXTO RECUPERADO — tu conversación anterior se compactó. Sigue con la misma tarea sin repetir trabajo hecho.]\n"
                        + (c["summary"] + "\n\n" if c["summary"] else "") + (("[MEMORIA DEL PROYECTO]\n" + snap) if snap else "")})
            out.append({"role": "assistant", "content": "Entendido. Continúo desde el estado indicado."})
        n = len(msgs)
        for i, m in enumerate(msgs[c["upto"]:], c["upto"]):
            m = {k: v for k, v in m.items() if k in ("role", "content", "tool_calls", "tool_name")}
            if m["role"] == "tool" and i < n - 8: m["content"] = clip(m["content"], 1200)
            out.append(m)
        if transient and out:
            last = dict(out[-1]); last["content"] = (last.get("content") or "") + "\n\n" + transient; out[-1] = last
        return out

def repair_history(msgs):
    """Si el servidor se interrumpió a mitad de una herramienta, añade resultados sintéticos para que el historial sea válido."""
    fixed = 0
    for i, m in enumerate(list(msgs)):
        pass
    i = 0
    while i < len(msgs):
        m = msgs[i]
        if m.get("role") == "assistant" and m.get("tool_calls"):
            ids = {c["id"] for c in m["tool_calls"]}
            have = set()
            j = i + 1
            while j < len(msgs) and msgs[j].get("role") == "tool": have.add(msgs[j].get("tool_call_id")); j += 1
            for c in m["tool_calls"]:
                if c["id"] not in have:
                    msgs.insert(j, {"role": "tool", "tool_name": c["function"]["name"], "tool_call_id": c["id"], "ok": False,
                                    "content": "[la ejecución se interrumpió (reinicio del servicio o corte); el resultado se desconoce. Comprueba el estado real antes de continuar]"}); j += 1; fixed += 1
            i = j
        else: i += 1
    return fixed

if __name__ == "__main__":
    if "--scan-staged" in sys.argv:
        bad = scan_staged(os.getcwd())
        if bad:
            print("✖ commit bloqueado por el escáner de secretos:", file=sys.stderr)
            for f, k in bad: print(f"   {f}: {k}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    print(__doc__)
