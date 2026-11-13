#!/usr/bin/env python3
"""Panel del Pod: chat agéntico con Ollama + estado del pod + sincronización con GitHub.

Solo biblioteca estándar. Se ejecuta EN el pod:  python3 server.py
Variables (todas opcionales):
  PANEL_PORT=8787  PANEL_HOST=127.0.0.1  OLLAMA_URL=http://127.0.0.1:11434
  PANEL_MODEL=qwen2.5-coder:14b  PANEL_REPO=/ProxyManager  PANEL_WORKDIR=<repo>/pod-work
  PANEL_BRANCH=pod-sync  GITHUB_TOKEN=...  POD_HOURLY_USD=0.245  POD_LIMIT_H=3
"""
import base64, json, os, re, subprocess, threading, time, uuid, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).parent
STATIC = HERE / "static"
HOME = Path(os.environ.get("PANEL_HOME", Path.home() / ".pod-panel"))
CONV_DIR = HOME / "conversations"
CONV_DIR.mkdir(parents=True, exist_ok=True)
TOKEN_FILE = HOME / "github-token"
STATE_FILE = HOME / "state.json"

OLLAMA = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.environ.get("PANEL_MODEL", "qwen2.5-coder:14b")
REPO = Path(os.environ.get("PANEL_REPO", "/ProxyManager"))
WORKDIR = Path(os.environ.get("PANEL_WORKDIR", REPO / "pod-work"))
BRANCH = os.environ.get("PANEL_BRANCH", "pod-sync")
HOURLY = float(os.environ.get("POD_HOURLY_USD", "0.245"))
LIMIT_H = float(os.environ.get("POD_LIMIT_H", "3"))
NUM_CTX = int(os.environ.get("PANEL_NUM_CTX", "16384"))
MAX_STEPS = int(os.environ.get("PANEL_MAX_STEPS", "25"))
WORKDIR.mkdir(parents=True, exist_ok=True)

SYSTEM = f"""Eres un agente de programación que trabaja DENTRO de un pod Linux con GPU. Respondes en español.
Tienes herramientas reales: bash, read_file, write_file, list_dir, web_search y web_fetch (acceso a internet). Tu directorio de trabajo es {WORKDIR}.
Reglas:
- SÍ tienes internet y SÍ puedes ejecutar comandos: nunca digas que no tienes acceso ni que no puedes; usa la herramienta.
- Si no sabes algo o puede haber cambiado (versiones, APIs, documentación), compruébalo en internet antes de responder. web_search solo cubre GitHub, Wikipedia, Stack Overflow y Hacker News; para la última versión de un proyecto usa web_fetch con https://api.github.com/repos/DUEÑO/REPO/releases/latest (campo tag_name); para documentación usa web_fetch con la URL directa.
- Actúa, no supongas. Si necesitas saber algo del entorno, ejecútalo con una herramienta y lee la salida real.
- Nunca inventes salidas de comandos ni digas "ejecuta esto y dime el resultado": ejecútalo tú.
- Haz los pasos uno a uno; tras cada herramienta lee el resultado y decide el siguiente paso.
- Verifica tu trabajo (ejecuta el programa o las pruebas) antes de dar por terminada una tarea.
- Todo lo que crees o modifiques debe quedar dentro de {WORKDIR}; el panel lo guarda en GitHub (rama {BRANCH}) al terminar.
- Nunca escribas secretos ni tokens en archivos. Sé breve en el texto final: qué hiciste y qué comprobaste."""

TOOLS = [
    {"type": "function", "function": {"name": "bash", "description": "Ejecuta un comando bash en el pod y devuelve stdout+stderr y el código de salida.",
        "parameters": {"type": "object", "properties": {"command": {"type": "string", "description": "Comando a ejecutar"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Lee un archivo de texto.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Crea o sobrescribe un archivo con el contenido dado.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "web_search", "description": "Busca en internet y devuelve título, URL y fragmento de los primeros resultados.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "web_fetch", "description": "Descarga una URL y devuelve su texto (HTML limpiado).",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "list_dir", "description": "Lista los archivos de un directorio.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": []}}},
]

REFUSAL = re.compile(r"no (tengo|dispongo de) acceso|no puedo (acceder|ejecutar|buscar|navegar|conectarme)|no tengo la capacidad|sin acceso a internet|ejecuta (estos|este|los siguientes) comandos?", re.I)
DANGEROUS = re.compile(r"(\brm\s+-[a-z]*r|\bmkfs|\bdd\s+if=|:\(\)\s*\{|\bshutdown|\breboot|git\s+push\s+.*(--force|-f\b)|git\s+reset\s+--hard|>\s*/dev/sd|\bchmod\s+-R\s+777\s+/|curl[^|]*\|\s*(sudo\s+)?(ba)?sh|wget[^|]*\|\s*(sudo\s+)?(ba)?sh|\bkill\s+-9\s+1\b|\bpkill\s+ollama)")

# ---------------------------------------------------------------- helpers
def jload(p, default):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return default

def jsave(p, data):
    tmp = Path(str(p) + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False))
    tmp.replace(p)

def run(cmd, cwd=None, timeout=120, env=None):
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd or WORKDIR, capture_output=True, text=True,
                           timeout=timeout, env={**os.environ, **(env or {})}, executable="/bin/bash" if isinstance(cmd, str) else None)
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""))
        return 124, out + f"\n[tiempo agotado tras {timeout}s]"
    except Exception as e:
        return 1, f"[error] {e}"

def clip(s, n=8000):
    return s if len(s) <= n else s[: n // 2] + f"\n…[{len(s) - n} caracteres omitidos]…\n" + s[-n // 2:]

def safe_path(p):
    q = Path(os.path.expanduser(p or "."))
    q = q if q.is_absolute() else WORKDIR / q
    q = q.resolve()
    if REPO.resolve() not in q.parents and q != REPO.resolve() and WORKDIR.resolve() not in q.parents:
        raise ValueError(f"ruta fuera del repositorio: {q}")
    return q

def token():
    return os.environ.get("GITHUB_TOKEN") or (TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else "")

def git(*args, auth=False, timeout=120):
    cmd = ["git", "-c", "user.name=Pod Agent", "-c", "user.email=pod-agent@users.noreply.github.com"]
    if auth and token():
        b = base64.b64encode(f"x-access-token:{token()}".encode()).decode()
        cmd += ["-c", "credential.helper=", "-c", f"http.extraheader=Authorization: Basic {b}"]
    return run(cmd + list(args), cwd=REPO, timeout=timeout, env={"GIT_TERMINAL_PROMPT": "0"})

# ---------------------------------------------------------------- estado
def pod_clock():
    st = jload(STATE_FILE, {})
    _, out = run(["ps", "-o", "etimes=", "-p", "1"])
    try:
        boot = time.time() - int(out.strip())
    except ValueError:
        boot = time.time()
    start = max(boot, st.get("clock_reset", 0))
    secs = max(0, time.time() - start)
    return {"seconds": int(secs), "usd": round(secs / 3600 * HOURLY, 3), "limit_h": LIMIT_H,
            "pod_id": os.environ.get("RUNPOD_POD_ID", "")}

def gpu_info():
    code, out = run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu",
                     "--format=csv,noheader,nounits"])
    if code:
        return None
    n, u, t, ut, tp = [x.strip() for x in out.strip().splitlines()[0].split(",")]
    return {"name": n.replace("NVIDIA GeForce ", ""), "mem_used": int(u), "mem_total": int(t), "util": int(ut), "temp": int(tp)}

def ollama_info():
    info = {"up": False, "loaded": None}
    try:
        with urllib.request.urlopen(OLLAMA + "/api/ps", timeout=2) as r:
            ps = json.load(r)
        info["up"] = True
        if ps.get("models"):
            m = ps["models"][0]
            info["loaded"] = {"name": m["name"], "gb": round(m.get("size_vram", m.get("size", 0)) / 1e9, 1)}
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=2) as r:
            info["models"] = [m["name"] for m in json.load(r).get("models", [])]
    except Exception:
        pass
    return info

def git_info():
    _, remote = git("remote", "get-url", "origin")
    _, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    _, dirty = git("status", "--porcelain", "--", str(WORKDIR))
    remote = re.sub(r"https://[^@]+@", "https://", remote.strip())
    slug = re.sub(r"^.*github\.com[:/]|\.git$", "", remote)
    _, ahead = git("rev-list", "--count", f"origin/{BRANCH}..{BRANCH}") if git("rev-parse", "--verify", BRANCH)[0] == 0 else (1, "0")
    return {"repo": slug, "branch": branch.strip(), "target_branch": BRANCH, "workdir": str(WORKDIR.relative_to(REPO)) if REPO in WORKDIR.parents else str(WORKDIR),
            "dirty": len([l for l in dirty.splitlines() if l.strip()]), "ahead": int(ahead.strip() or 0) if ahead.strip().isdigit() else 0,
            "token": bool(token())}

def ensure_branch():
    _, cur = git("rev-parse", "--abbrev-ref", "HEAD")
    if cur.strip() == BRANCH:
        return
    if git("rev-parse", "--verify", BRANCH)[0] == 0:
        git("checkout", BRANCH)
    elif git("rev-parse", "--verify", f"origin/{BRANCH}")[0] == 0:
        git("checkout", "-b", BRANCH, f"origin/{BRANCH}")
    else:
        git("checkout", "-b", BRANCH)

def git_save(message, push=True):
    """Commit de todo el workdir en la rama de sincronización y push si hay token."""
    ensure_branch()
    git("add", "-A", "--", str(WORKDIR))
    if git("diff", "--cached", "--quiet")[0] == 0:
        committed = False
    else:
        code, out = git("commit", "-m", message[:100] + "\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" if False else message[:100])
        if code:
            return {"ok": False, "msg": out.strip()}
        committed = True
    if not push:
        return {"ok": True, "committed": committed, "pushed": False}
    if not token():
        return {"ok": True, "committed": committed, "pushed": False, "msg": "Commit local hecho. Falta el token de GitHub para subir."}
    code, out = git("push", "-u", "origin", BRANCH, auth=True)
    return {"ok": code == 0, "committed": committed, "pushed": code == 0, "msg": clip(re.sub(r"https://\S+@", "https://", out.strip()), 600)}

def git_pull():
    ensure_branch()
    code, out = git("pull", "--rebase", "--autostash", "origin", BRANCH, auth=True)
    if code and "couldn't find remote ref" in out:
        return {"ok": True, "msg": "La rama aún no existe en GitHub."}
    return {"ok": code == 0, "msg": clip(out.strip(), 600)}

# ---------------------------------------------------------------- herramientas del agente
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def _get_json(url, headers=None, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "pod-panel/1.0", "Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def web_search(q, n=5):
    """Los buscadores web bloquean las IP de los pods, así que se usan APIs abiertas.
    Con TAVILY_API_KEY se usa Tavily (búsqueda web completa)."""
    import html as H, urllib.parse
    qq = urllib.parse.quote(q)
    if os.environ.get("TAVILY_API_KEY"):
        d = _get_json("https://api.tavily.com/search", {"Content-Type": "application/json"},
                      json.dumps({"api_key": os.environ["TAVILY_API_KEY"], "query": q, "max_results": 6}).encode())
        return "\n".join(f"{i}. {r['title']}\n   {r['url']}\n   {r['content'][:300]}" for i, r in enumerate(d.get("results", []), 1)) or "(sin resultados)"
    clean = lambda x: H.unescape(re.sub(r"<[^>]+>", "", x or "")).strip()
    sections, errors = [], []
    def add(title, items):
        if items: sections.append(f"## {title}\n" + "\n".join(items))
    jobs = {
        "Repositorios de GitHub": lambda: [f"- {r['full_name']} (★{r['stargazers_count']}) {r['html_url']}\n  {(r['description'] or '')[:160]}"
            for r in _get_json(f"https://api.github.com/search/repositories?q={qq}&per_page={n}").get("items", [])],
        "Wikipedia": lambda: [f"- {r['title']}: https://en.wikipedia.org/wiki/{urllib.parse.quote(r['title'].replace(' ', '_'))}\n  {clean(r['snippet'])[:200]}"
            for r in _get_json(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={qq}&format=json&srlimit={n}")["query"]["search"]],
        "Stack Overflow": lambda: [f"- {clean(r['title'])} {r['link']}" for r in _get_json(f"https://api.stackexchange.com/2.3/search/advanced?q={qq}&site=stackoverflow&pagesize={n}&order=desc&sort=relevance").get("items", [])],
        "Hacker News": lambda: [f"- {r.get('title') or r.get('story_title')}: {r.get('url') or 'https://news.ycombinator.com/item?id=' + r['objectID']}"
            for r in _get_json(f"https://hn.algolia.com/api/v1/search?query={qq}&hitsPerPage={n}").get("hits", []) if r.get("title") or r.get("story_title")],
    }
    for title, fn in jobs.items():
        try: add(title, fn())
        except Exception as e: errors.append(f"{title}: {e}")
    out = "\n\n".join(sections) or "(sin resultados)"
    return out + "\n\n[Nota: búsqueda limitada a GitHub, Wikipedia, Stack Overflow y Hacker News. Para versiones de software usa web_fetch con https://api.github.com/repos/DUEÑO/REPO/releases/latest; para docs usa web_fetch con la URL directa.]"

def web_fetch(url):
    import html as H
    if not re.match(r"https?://", url):
        raise ValueError("la URL debe empezar por http:// o https://")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=20) as r:
        ctype = r.headers.get("Content-Type", "")
        raw = r.read(600000).decode("utf-8", "replace")
    if "html" in ctype or raw.lstrip().startswith("<"):
        raw = re.sub(r"<(script|style|noscript|svg|nav|footer)[\s\S]*?</\1>|<!--[\s\S]*?-->", " ", raw)
        raw = re.sub(r"</(p|div|li|h[1-6]|tr|pre)>|<br\s*/?>", "\n", raw)
        raw = H.unescape(re.sub(r"<[^>]+>", " ", raw))
        raw = re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", raw)).strip()
    return raw


def needs_approval(name, args):
    if name == "bash":
        return bool(DANGEROUS.search(args.get("command", "")))
    return False

def exec_tool(name, args):
    try:
        if name == "bash":
            code, out = run(args.get("command", ""), timeout=int(args.get("timeout", 120)))
            return code == 0, clip(out.strip() or "(sin salida)") + f"\n[código de salida {code}]"
        if name == "read_file":
            p = safe_path(args.get("path"))
            return True, clip(p.read_text(errors="replace"), 12000)
        if name == "write_file":
            p = safe_path(args.get("path"))
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args.get("content", ""))
            return True, f"Escrito {p} ({len(args.get('content', ''))} caracteres)"
        if name == "web_search":
            return True, web_search(args.get("query", ""))
        if name == "web_fetch":
            return True, clip(web_fetch(args.get("url", "")), 9000)
        if name == "list_dir":
            p = safe_path(args.get("path") or ".")
            items = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
            return True, "\n".join(("📁 " if i.is_dir() else "   ") + i.name for i in items[:200]) or "(vacío)"
        return False, f"Herramienta desconocida: {name}"
    except Exception as e:
        return False, f"[error] {e}"

def parse_text_tool_call(text):
    """Algunos modelos escriben las llamadas como JSON en el texto (solas o tras algo de prosa).
    Devuelve (llamadas, texto_sin_las_llamadas) o None."""
    names = {x["function"]["name"] for x in TOOLS}
    dec, calls, spans = json.JSONDecoder(), [], []
    for m in re.finditer(r"\{\s*\"name\"\s*:", text):
        if spans and m.start() < spans[-1][1]:
            continue
        try:
            o, j = dec.raw_decode(text, m.start())
        except ValueError:
            continue
        if isinstance(o, dict) and o.get("name") in names:
            a = o.get("arguments", o.get("parameters", {}))
            calls.append({"function": {"name": o["name"], "arguments": a if isinstance(a, dict) else {}}})
            spans.append((m.start(), j))
    if not calls:
        return None
    rest, last = "", 0
    for st, en in spans:
        rest += text[last:st]; last = en
    rest = re.sub(r"</?tool_call>|^```(?:json)?\s*$|^```\s*$", "", rest + text[last:], flags=re.M).strip()
    return calls, rest

# ---------------------------------------------------------------- bucle agéntico
APPROVALS = {}   # call_id -> {"event", "ok"}
STOPS = {}       # conv_id -> Event
LAST_SPEED = {"tps": None}

def prep_messages(msgs):
    out = [{"role": "system", "content": SYSTEM}]
    n = len(msgs)
    for i, m in enumerate(msgs):
        m = {k: v for k, v in m.items() if k in ("role", "content", "tool_calls", "tool_name")}
        if m["role"] == "tool" and i < n - 8:
            m["content"] = clip(m["content"], 1200)
        out.append(m)
    return out

def stream_ollama(msgs, emit, stop):
    body = json.dumps({"model": MODEL, "messages": prep_messages(msgs), "tools": TOOLS, "stream": True,
                       "options": {"num_ctx": NUM_CTX, "temperature": 0.2}, "keep_alive": "2h"}).encode()
    req = urllib.request.Request(OLLAMA + "/api/chat", body, {"Content-Type": "application/json"})
    content, calls, stats = "", [], {}
    with urllib.request.urlopen(req, timeout=600) as r:
        for line in r:
            if stop.is_set():
                break
            if not line.strip():
                continue
            d = json.loads(line)
            m = d.get("message", {})
            if m.get("content"):
                content += m["content"]
                emit({"type": "token", "text": m["content"]})
            calls += m.get("tool_calls") or []
            if d.get("done"):
                ec, ed = d.get("eval_count", 0), d.get("eval_duration", 0)
                stats = {"tokens": ec, "tps": round(ec / (ed / 1e9), 1) if ed else None}
    return content, calls, stats

def agent_turn(conv, emit, stop, mode="agent"):
    msgs = conv["messages"]
    seen = {}
    refused = False
    for step in range(MAX_STEPS):
        if stop.is_set():
            emit({"type": "notice", "text": "Detenido por el usuario."}); return
        try:
            content, calls, stats = stream_ollama(msgs, emit, stop)
        except Exception as e:
            emit({"type": "error", "text": f"No pude hablar con Ollama: {e}"}); return
        if mode == "chat":
            calls = []
        elif not calls and content:
            parsed = parse_text_tool_call(content)
            calls = parsed[0] if parsed else []
            if parsed:
                emit({"type": "clear_text"})
                content = parsed[1]
                if content: emit({"type": "token", "text": content})
            if not calls and not refused and REFUSAL.search(content):
                refused = True
                msgs.append({"role": "assistant", "content": content})
                msgs.append({"role": "user", "content": "Eso es incorrecto: SÍ tienes acceso a internet y a un shell mediante tus herramientas (web_search, web_fetch, bash). Úsalas ahora para hacer lo que te pedí."})
                emit({"type": "clear_text"}); continue
        a = {"role": "assistant", "content": content, "stats": stats}
        if calls:
            a["tool_calls"] = [{"id": uuid.uuid4().hex[:8], **c} for c in calls]
        msgs.append(a)
        if stats.get("tps"):
            LAST_SPEED["tps"] = stats["tps"]
        emit({"type": "assistant_done", "stats": stats})
        if not calls:
            return
        for c in a["tool_calls"]:
            name = c["function"]["name"]; args = c["function"].get("arguments") or {}
            if isinstance(args, str):
                try: args = json.loads(args)
                except Exception: args = {}
            emit({"type": "tool_start", "id": c["id"], "name": name, "args": args})
            ok_run = True
            if needs_approval(name, args):
                ev = threading.Event(); APPROVALS[c["id"]] = {"event": ev, "ok": False}
                emit({"type": "approval", "id": c["id"], "name": name, "args": args})
                while not ev.wait(0.5):
                    if stop.is_set(): break
                ok_run = APPROVALS.pop(c["id"], {}).get("ok", False) and not stop.is_set()
            key = json.dumps([name, args], sort_keys=True)
            if ok_run and key in seen and name in ("bash", "read_file", "list_dir", "web_search", "web_fetch"):
                ok, out = True, seen[key] + "\n[AVISO: ya ejecutaste exactamente esto y el resultado es el mismo. No lo repitas: da ahora tu respuesta final al usuario.]"
            elif ok_run:
                ok, out = exec_tool(name, args); seen[key] = out
            else:
                ok, out = False, "El usuario rechazó o no aprobó este comando. Propón una alternativa más segura."
            msgs.append({"role": "tool", "tool_name": name, "content": out, "tool_call_id": c["id"], "ok": ok})
            emit({"type": "tool_result", "id": c["id"], "ok": ok, "output": out})
    emit({"type": "notice", "text": f"Alcancé el máximo de {MAX_STEPS} pasos. Escribe «continúa» para seguir."})

def title_from(text):
    t = re.sub(r"\s+", " ", text).strip()
    return (t[:44] + "…") if len(t) > 45 else t or "Nueva conversación"

def conv_path(cid):
    if not re.fullmatch(r"[a-f0-9]{6,32}", cid or ""):
        raise ValueError("id inválido")
    return CONV_DIR / f"{cid}.json"

def new_conv():
    c = {"id": uuid.uuid4().hex[:12], "title": "Nueva conversación", "created": time.time(), "updated": time.time(), "messages": []}
    jsave(conv_path(c["id"]), c)
    return c

# ---------------------------------------------------------------- HTTP
class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *a): pass

    def _json(self, data, code=200):
        b = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/status":
                return self._json({"clock": pod_clock(), "gpu": gpu_info(), "ollama": ollama_info(), "git": git_info(),
                                   "model": MODEL, "tps": LAST_SPEED["tps"]})
            if path == "/api/conversations":
                items = [jload(p, {}) for p in CONV_DIR.glob("*.json")]
                items = sorted([c for c in items if c], key=lambda c: -c.get("updated", 0))
                return self._json([{"id": c["id"], "title": c["title"], "updated": c["updated"]} for c in items])
            m = re.fullmatch(r"/api/conversations/([a-f0-9]+)", path)
            if m:
                return self._json(jload(conv_path(m.group(1)), {"error": "no existe"}))
            f = STATIC / ("index.html" if path in ("/", "") else path.lstrip("/"))
            if f.is_file() and STATIC in f.resolve().parents:
                b = f.read_bytes()
                ct = {".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".svg": "image/svg+xml"}.get(f.suffix, "application/octet-stream")
                self.send_response(200); self.send_header("Content-Type", ct + "; charset=utf-8")
                self.send_header("Cache-Control", "no-store"); self.send_header("Content-Length", str(len(b))); self.end_headers()
                return self.wfile.write(b)
            self._json({"error": "no encontrado"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def do_DELETE(self):
        m = re.fullmatch(r"/api/conversations/([a-f0-9]+)", urlparse(self.path).path)
        if m:
            conv_path(m.group(1)).unlink(missing_ok=True)
            return self._json({"ok": True})
        self._json({"error": "no encontrado"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            b = self._body()
            if path == "/api/conversations":
                return self._json(new_conv())
            if path == "/api/chat":
                return self.chat(b)
            if path == "/api/approve":
                a = APPROVALS.get(b.get("id"))
                if a: a["ok"] = bool(b.get("ok")); a["event"].set()
                return self._json({"ok": True})
            if path == "/api/stop":
                ev = STOPS.get(b.get("id"))
                if ev: ev.set()
                return self._json({"ok": True})
            if path == "/api/git/push":
                return self._json(git_save(b.get("message") or "pod: guardado manual desde el panel"))
            if path == "/api/git/pull":
                return self._json(git_pull())
            if path == "/api/git/token":
                t = (b.get("token") or "").strip()
                if t: TOKEN_FILE.write_text(t); TOKEN_FILE.chmod(0o600)
                else: TOKEN_FILE.unlink(missing_ok=True)
                return self._json({"ok": True})
            if path == "/api/clock/reset":
                st = jload(STATE_FILE, {}); st["clock_reset"] = time.time(); jsave(STATE_FILE, st)
                return self._json({"ok": True})
            if path == "/api/shell":
                code, out = run(b.get("command", ""), timeout=int(b.get("timeout", 120)))
                return self._json({"code": code, "output": clip(out)})
            self._json({"error": "no encontrado"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def chat(self, b):
        conv = jload(conv_path(b["id"]), None) or new_conv()
        text, mode = (b.get("message") or "").strip(), b.get("mode", "agent")
        self.send_response(200)
        for k, v in {"Content-Type": "text/event-stream", "Cache-Control": "no-cache", "Connection": "close"}.items():
            self.send_header(k, v)
        self.end_headers(); self.close_connection = True
        lock = threading.Lock()
        def emit(ev):
            try:
                with lock:
                    self.wfile.write(b"data: " + json.dumps(ev, ensure_ascii=False).encode() + b"\n\n"); self.wfile.flush()
            except Exception:
                stop.set()
        stop = STOPS[conv["id"]] = threading.Event()
        try:
            if conv["title"] == "Nueva conversación" and text:
                conv["title"] = title_from(text.lstrip("!/"))
            run_model = True
            if text.startswith("!"):   # comando directo en el pod
                cmd = text[1:].strip()
                emit({"type": "tool_start", "id": "sh", "name": "bash", "args": {"command": cmd}})
                code, out = run(cmd)
                emit({"type": "tool_result", "id": "sh", "ok": code == 0, "output": clip(out.strip() or "(sin salida)") + f"\n[código de salida {code}]"})
                conv["messages"].append({"role": "user", "content": f"Ejecuté en el pod: `{cmd}`\nSalida (código {code}):\n```\n{clip(out, 6000)}\n```",
                                         "shell": {"cmd": cmd, "output": clip(out), "code": code}})
                run_model = bool(b.get("send_output", True))
            elif text.startswith("/leer "):
                url = text[6:].strip()
                try:
                    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pod-panel"}), timeout=20) as r:
                        raw = r.read(400000).decode("utf-8", "replace")
                    page = re.sub(r"\s+", " ", re.sub(r"<(script|style)[\s\S]*?</\1>|<[^>]+>", " ", raw)).strip()
                except Exception as e:
                    page = f"[error al leer: {e}]"
                conv["messages"].append({"role": "user", "content": f"Contenido de {url}:\n{clip(page, 8000)}\n\n(Resume lo relevante y espera instrucciones.)", "display": text})
            elif text:
                conv["messages"].append({"role": "user", "content": text})
            if run_model:
                agent_turn(conv, emit, stop, mode)
            conv["updated"] = time.time(); jsave(conv_path(conv["id"]), conv)
            emit({"type": "title", "title": conv["title"], "id": conv["id"]})
            if mode == "agent" and not stop.is_set() and b.get("auto_push", True):
                g = git_save("pod: " + conv["title"])
                if g.get("committed") or not g.get("ok"):
                    emit({"type": "git", **g})
        except Exception as e:
            emit({"type": "error", "text": str(e)})
        finally:
            emit({"type": "done"}); STOPS.pop(conv["id"], None)

if __name__ == "__main__":
    ensure_branch()
    host, port = os.environ.get("PANEL_HOST", "127.0.0.1"), int(os.environ.get("PANEL_PORT", "8787"))
    print(f"Panel del Pod en http://{host}:{port}  ·  modelo {MODEL}  ·  workdir {WORKDIR}  ·  rama {BRANCH}")
    ThreadingHTTPServer((host, port), H).serve_forever()
