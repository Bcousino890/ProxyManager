#!/usr/bin/env python3
"""Panel del Pod: chat agéntico con Ollama + estado del pod + sincronización con GitHub.

Solo biblioteca estándar. Se ejecuta EN el pod:  python3 server.py
Variables (todas opcionales):
  PANEL_PORT=8787  PANEL_HOST=127.0.0.1  OLLAMA_URL=http://127.0.0.1:11434
  PANEL_MODEL=qwen3-coder:30b  PANEL_REPO=/ProxyManager  PANEL_WORKDIR=<repo>/pod-work
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
MODEL = os.environ.get("PANEL_MODEL", "qwen3-coder:30b")
REPO = Path(os.environ.get("PANEL_REPO", "/ProxyManager"))
WORKDIR = Path(os.environ.get("PANEL_WORKDIR", REPO / "pod-work"))
BRANCH = os.environ.get("PANEL_BRANCH", "pod-sync")
HOURLY = float(os.environ.get("POD_HOURLY_USD", "0.245"))
LIMIT_H = float(os.environ.get("POD_LIMIT_H", "3"))
NUM_CTX = int(os.environ.get("PANEL_NUM_CTX", "24576"))
MAX_STEPS = int(os.environ.get("PANEL_MAX_STEPS", "25"))
RESEARCH_STEPS = int(os.environ.get("PANEL_RESEARCH_STEPS", "45"))
WORKDIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = WORKDIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THINK_MODEL = os.environ.get("PANEL_THINK_MODEL", "qwen3:30b")
VISION_MODEL = os.environ.get("PANEL_VISION_MODEL", "qwen2.5vl:7b")
MAX_UPLOAD = 30 * 1024 * 1024
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
TEXT_EXT = (".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".toml", ".ini", ".log", ".py", ".js", ".ts", ".html", ".css", ".sh", ".sql", ".xml", ".env.example", ".cfg", ".java", ".go", ".rs", ".c", ".cpp", ".h")

SYSTEM_BASE = f"""Eres un agente que trabaja DENTRO de un pod Linux con GPU, con herramientas reales: bash, read_file, write_file, list_dir, web_search, web_fetch (acceso a internet) y describe_image (ver imágenes) y notify (avisar al usuario). Los archivos que sube el usuario quedan en {UPLOAD_DIR}. Tu directorio de trabajo es {WORKDIR}.
IDIOMA: responde SIEMPRE en español, aunque el usuario escriba en inglés, las fuentes estén en inglés o el código tenga comentarios en inglés (traduce lo que cites). No traduzcas identificadores, comandos ni nombres de archivos.
Reglas generales:
- Eres el agente: cuando el usuario pide algo, lo haces tú con las herramientas. Nunca le pidas que ejecute algo por ti ni inventes salidas de comandos.
- SÍ tienes internet y SÍ puedes ejecutar comandos: nunca digas que no puedes; usa la herramienta.
- Actúa, no supongas: si necesitas saber algo del entorno, ejecútalo y lee la salida real. Tras cada herramienta lee el resultado y decide el siguiente paso.
- El proyecto del usuario ya está clonado en {REPO}: para analizarlo léelo ahí, NO lo vuelvas a clonar. Lo que crees nuevo va en {WORKDIR}; el panel lo guarda en GitHub (rama {BRANCH}) al terminar.
- Si el usuario pide que le avises (al terminar o después de algo), usa la herramienta notify con un resumen breve; además el panel avisa solo al terminar cada tarea. Razona los pasos antes de actuar y revisa tu propio resultado antes de darlo por bueno.
- Nunca escribas secretos ni tokens en archivos. Si algo falla, lee el error, corrígelo y reintenta; no lo ocultes.
- Texto final breve y concreto: qué hiciste, qué comprobaste y qué queda pendiente."""

SYSTEM_CODE = """
MODO PROGRAMACIÓN — trabaja como un ingeniero senior:
1. Antes de escribir, lee el código y las convenciones existentes y haz un plan de 3-5 líneas.
2. Estructura de proyecto real (Python): pod-work/NOMBRE/ con README.md (qué hace, instalar, ejecutar, probar), pyproject.toml, src/NOMBRE/__init__.py + módulos, y tests/ al mismo nivel que src/. Instala con `pip install -e .` dentro de un venv (.venv) y ejecuta `pytest`. NUNCA pongas el código del paquete suelto en la raíz del proyecto.
3. Calidad: nombres claros, funciones pequeñas con una sola responsabilidad, type hints, docstrings breves, manejo explícito de errores, validación de entradas, sin secretos ni rutas fijas, sin código muerto ni duplicado.
4. Pruebas: escribe pruebas con pytest (casos normales, bordes y errores) y EJECÚTALAS. Si faltan dependencias, crea un venv (python3 -m venv .venv && .venv/bin/pip install ...) en la carpeta del proyecto. Itera hasta que todo pase.
5. Ejecuta el programa de verdad y comprueba el resultado antes de decir que está listo. NUNCA afirmes que algo funciona o que las pruebas pasan si la última salida real dice lo contrario: informa del resultado tal cual.
6. En código existente haz cambios mínimos y coherentes con su estilo; no reescribas lo que funciona.
7. Para APIs, versiones o documentación que no conozcas con certeza, compruébalo en internet (web_fetch a la documentación oficial) en lugar de adivinar."""

SYSTEM_RESEARCH = """
MODO INVESTIGACIÓN PROFUNDA — sigue este protocolo:
1. Descompón la pregunta en 3-6 subpreguntas concretas.
2. Para cada una, lanza varias web_search con formulaciones distintas (en español y en inglés).
3. Abre con web_fetch al menos 4 fuentes distintas, priorizando las primarias (documentación oficial, papers, repositorios, normativa) sobre blogs. Lee el contenido: no cites una página que no hayas abierto.
4. Contrasta fuentes. Señala contradicciones, fechas, y qué es dato y qué es opinión. Si no encuentras algo, dilo; no rellenes huecos.
5. Escribe el informe con write_file en pod-work/investigaciones/AAAA-MM-DD-tema.md con: resumen ejecutivo, hallazgos por subpregunta con citas numeradas [n], comparativa o recomendación si procede, límites de la investigación y lista de fuentes (título + URL).
6. En el chat entrega un resumen de 6-10 líneas con las conclusiones clave y la ruta del informe.
Si web_search devuelve poco (puede estar limitada a GitHub, Wikipedia, Stack Overflow, Hacker News, arXiv y OpenAlex), ve directo con web_fetch a documentación oficial, repositorios o APIs abiertas, y menciona esa limitación en el informe."""

def system_for(mode):
    return SYSTEM_BASE + (SYSTEM_RESEARCH if mode == "research" else SYSTEM_CODE if mode == "agent" else "")

TOOLS = [
    {"type": "function", "function": {"name": "bash", "description": "Ejecuta un comando bash en el pod y devuelve stdout+stderr y el código de salida.",
        "parameters": {"type": "object", "properties": {"command": {"type": "string", "description": "Comando a ejecutar"}, "timeout": {"type": "integer", "description": "Segundos máximos (por defecto 120, máximo 1800)"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "notify", "description": "Envía un aviso al usuario (notificación del navegador). Úsala cuando el usuario pida que le avises, y al terminar una tarea larga con un resumen de una línea.",
        "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "message": {"type": "string"}}, "required": ["message"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Lee un archivo de texto.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Crea o sobrescribe un archivo con el contenido dado.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "web_search", "description": "Busca en internet y devuelve título, URL y fragmento de los primeros resultados.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "web_fetch", "description": "Descarga una URL y devuelve su texto (HTML limpiado).",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "describe_image", "description": "Mira una imagen (foto, captura, diagrama) con el modelo de visión y responde una pregunta sobre ella o la describe y transcribe su texto.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "question": {"type": "string", "description": "Qué quieres saber de la imagen (opcional)"}}, "required": ["path"]}}},
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

# ---------------------------------------------------------------- visión
def describe_image(path, question=None):
    """Interpreta una imagen con el modelo de visión (descripción + OCR) y devuelve texto en español."""
    p = safe_path(path)
    raw = p.read_bytes()
    try:   # reducir fotos grandes para que sea rápido
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(raw)); im.thumbnail((1568, 1568))
        buf = io.BytesIO(); im.convert("RGB").save(buf, "JPEG", quality=88); raw = buf.getvalue()
    except Exception:
        pass
    prompt = (question or "Describe esta imagen con detalle.") + (
        "\nSi hay texto visible, transcríbelo literalmente. Si es una captura de pantalla, un error, un diagrama o código, explica qué muestra y los datos concretos "
        "(números, nombres, mensajes). Responde SIEMPRE en español.")
    body = json.dumps({"model": VISION_MODEL, "stream": False, "keep_alive": "30s", "options": {"temperature": 0.1, "num_ctx": 8192},
                       "messages": [{"role": "user", "content": prompt, "images": [base64.b64encode(raw).decode()]}]}).encode()
    try:
        req = urllib.request.Request(OLLAMA + "/api/chat", body, {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"[No hay modelo de visión instalado. Ejecuta: ollama pull {VISION_MODEL}]"
        return f"[error del modelo de visión: {e}]"

def kind_of(name):
    n = name.lower()
    return "image" if n.endswith(IMG_EXT) else "text" if n.endswith(TEXT_EXT) else "pdf" if n.endswith(".pdf") else "file"

def attachments_block(atts, emit=None):
    """Convierte los adjuntos en texto que el modelo puede leer."""
    out = []
    for a in atts:
        p = safe_path(a["path"]); name = a.get("name") or p.name; k = kind_of(p.name)
        line = f"- {name} → {p} ({k}, {p.stat().st_size // 1024} KB)"
        if k == "image":
            if emit: emit({"type": "tool_start", "id": "v" + p.name, "name": "describe_image", "args": {"path": str(p)}})
            d = describe_image(str(p))
            if emit: emit({"type": "tool_result", "id": "v" + p.name, "ok": not d.startswith("["), "output": d})
            line += "\n  Descripción de la imagen (modelo de visión):\n  " + d.replace("\n", "\n  ")
        elif k == "text":
            txt = p.read_text(errors="replace")
            line += "\n  Contenido" + (" (primeros 6000 caracteres)" if len(txt) > 6000 else "") + ":\n```\n" + txt[:6000] + "\n```"
        elif k == "pdf":
            line += "\n  (PDF: extrae el texto con bash, p. ej. `pip install pypdf` y leyéndolo con Python.)"
        out.append(line)
    return "\n".join(out)

# ---------------------------------------------------------------- herramientas del agente
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def _get_json(url, headers=None, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "pod-panel/1.0", "Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

SEARCH_KEY_FILE = HOME / "tavily-key"
def search_key():
    return os.environ.get("TAVILY_API_KEY") or (SEARCH_KEY_FILE.read_text().strip() if SEARCH_KEY_FILE.exists() else "")

def web_search(q, n=5):
    """Los buscadores web bloquean las IP de los pods, así que se usan APIs abiertas.
    Con TAVILY_API_KEY se usa Tavily (búsqueda web completa)."""
    import html as H, urllib.parse
    qq = urllib.parse.quote(q)
    if search_key():
        d = _get_json("https://api.tavily.com/search", {"Content-Type": "application/json"},
                      json.dumps({"api_key": search_key(), "query": q, "max_results": 8, "search_depth": "advanced"}).encode())
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
        "Papers (OpenAlex)": lambda: [f"- {r['display_name']} ({r.get('publication_year')}) {r.get('doi') or r['id']}"
            for r in _get_json(f"https://api.openalex.org/works?search={qq}&per-page=3").get("results", [])],
        "arXiv": lambda: [f"- {clean(t)} {u}" for u, t in re.findall(r"<entry>[\s\S]*?<id>(.*?)</id>[\s\S]*?<title>([\s\S]*?)</title>",
            urllib.request.urlopen(urllib.request.Request(f"https://export.arxiv.org/api/query?search_query=all:{qq}&max_results=3", headers={"User-Agent": "pod-panel/1.0"}), timeout=15).read().decode())],
        "Hacker News": lambda: [f"- {r.get('title') or r.get('story_title')}: {r.get('url') or 'https://news.ycombinator.com/item?id=' + r['objectID']}"
            for r in _get_json(f"https://hn.algolia.com/api/v1/search?query={qq}&hitsPerPage={n}").get("hits", []) if r.get("title") or r.get("story_title")],
    }
    for title, fn in jobs.items():
        try: add(title, fn())
        except Exception as e: errors.append(f"{title}: {e}")
    out = "\n\n".join(sections) or "(sin resultados)"
    return out + "\n\n[Nota: búsqueda limitada a GitHub, Wikipedia, Stack Overflow, Hacker News, OpenAlex y arXiv; no hay clave de búsqueda web completa (Tavily). Para versiones de software usa web_fetch con https://api.github.com/repos/DUEÑO/REPO/releases/latest; para docs usa web_fetch con la URL directa.]"

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
            code, out = run(args.get("command", ""), timeout=min(int(args.get("timeout", 120)), 1800))
            return code == 0, clip(out.strip() or "(sin salida)") + f"\n[código de salida {code}]"
        if name == "read_file":
            p = safe_path(args.get("path"))
            return True, clip(p.read_text(errors="replace"), 12000)
        if name == "write_file":
            p = safe_path(args.get("path"))
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args.get("content", ""))
            return True, f"Escrito {p} ({len(args.get('content', ''))} caracteres)"
        if name == "describe_image":
            return True, describe_image(args.get("path", ""), args.get("question"))
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
EN_W = set("the and is are to of with this that you for it on as be by from or an at not have has can will your which".split())
ES_W = set("el la los las de que y en un una para con por se es no del al lo como más pero su sus esto esta este son ha han puede".split())
def looks_english(text):
    t = re.sub(r"```[\s\S]*?```|`[^`]*`", " ", text).lower()
    w = re.findall(r"[a-záéíóúñü]+", t)
    en, es = sum(x in EN_W for x in w), sum(x in ES_W for x in w)
    return len(w) > 25 and en > es * 1.3
CODE_EXT = (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".cpp", ".sh", ".rb", ".php")

def prep_messages(msgs, mode="agent"):
    out = [{"role": "system", "content": system_for(mode)}]
    n = len(msgs)
    for i, m in enumerate(msgs):
        m = {k: v for k, v in m.items() if k in ("role", "content", "tool_calls", "tool_name")}
        if m["role"] == "tool" and i < n - 8:
            m["content"] = clip(m["content"], 1200)
        out.append(m)
    return out

def stream_ollama(msgs, emit, stop, model, tools=True, mode="agent", think=False):
    body = json.dumps({"model": model, "messages": prep_messages(msgs, mode), **({"tools": TOOLS} if tools else {}), "stream": True,
                       "options": {"num_ctx": NUM_CTX, "temperature": 0.6 if think else 0.2}, "keep_alive": "2h", **({"think": True} if think else {})}).encode()
    req = urllib.request.Request(OLLAMA + "/api/chat", body, {"Content-Type": "application/json"})
    content, calls, stats, thinking = "", [], {}, ""
    with urllib.request.urlopen(req, timeout=600) as r:
        for line in r:
            if stop.is_set():
                break
            if not line.strip():
                continue
            d = json.loads(line)
            m = d.get("message", {})
            if m.get("thinking"):
                thinking += m["thinking"]
                emit({"type": "thinking", "text": m["thinking"]})
            if m.get("content"):
                content += m["content"]
                emit({"type": "token", "text": m["content"]})
            calls += m.get("tool_calls") or []
            if d.get("done"):
                ec, ed = d.get("eval_count", 0), d.get("eval_duration", 0)
                stats = {"tokens": ec, "tps": round(ec / (ed / 1e9), 1) if ed else None}
    stats["thinking"] = thinking
    return content, calls, stats

def agent_turn(conv, emit, stop, mode="agent", model=None, think=False):
    model = THINK_MODEL if think else (model or MODEL)
    msgs = conv["messages"]
    seen = {}
    refused = False
    st = {"wrote": False, "ran": False, "nv": False, "ne": False, "fail": None, "nf": 0}
    max_steps = RESEARCH_STEPS if mode == "research" else MAX_STEPS
    for step in range(max_steps):
        if stop.is_set():
            emit({"type": "notice", "text": "Detenido por el usuario."}); return
        try:
            content, calls, stats = stream_ollama(msgs, emit, stop, model, tools=(mode != "chat"), mode=mode, think=think)
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
        nudge = None
        if not calls and content:
            if mode != "chat" and not refused and REFUSAL.search(content):
                refused = True
                nudge = "Eso es incorrecto: SÍ tienes acceso a internet y a un shell mediante tus herramientas (web_search, web_fetch, bash). Úsalas ahora para hacer lo que te pedí."
            elif mode != "chat" and st["fail"] and st["nf"] < 2:
                st["nf"] += 1
                nudge = ("La ÚLTIMA ejecución de pruebas FALLÓ. No digas que pasaron. Salida:\n" + st["fail"][1] +
                         "\nLee el error, corrige la causa (por ejemplo imports, estructura del paquete o instalación con pip install -e .) y vuelve a ejecutar las pruebas hasta que pasen. "
                         "Si no puedes arreglarlo, informa honestamente del fallo.")
            elif mode == "agent" and st["wrote"] and not st["ran"] and not st["nv"]:
                st["nv"] = True
                nudge = "Escribiste código pero no lo has ejecutado ni probado. Ejecútalo y/o corre sus pruebas ahora con bash y corrige lo que falle antes de dar la tarea por terminada."
            elif looks_english(content) and not st["ne"]:
                st["ne"] = True
                nudge = "Debes responder SIEMPRE en español. Reescribe tu respuesta anterior en español."
        if nudge:
            msgs.append({"role": "assistant", "content": content, "hidden": True})
            msgs.append({"role": "user", "hidden": True, "content": nudge})
            emit({"type": "clear_text"}); continue
        content = re.sub(r"</?tool_call>", "", content).strip() if not calls else content
        if calls and len(content) > 220:   # borrador de conclusión repetido mientras aún usa herramientas
            content = ""; emit({"type": "clear_text"})
        th = stats.pop("thinking", "")
        a = {"role": "assistant", "content": content, "stats": stats, **({"thinking": th} if th else {})}
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
            if name == "notify":
                emit({"type": "notify", "title": str(args.get("title") or "Panel del Pod"), "text": str(args.get("message", ""))})
                msgs.append({"role": "tool", "tool_name": name, "content": "Aviso enviado al usuario.", "tool_call_id": c["id"], "ok": True})
                emit({"type": "tool_result", "id": c["id"], "ok": True, "output": "Aviso enviado al usuario."}); continue
            key = json.dumps([name, args], sort_keys=True)
            if ok_run and key in seen and name in ("bash", "read_file", "list_dir", "web_search", "web_fetch", "describe_image"):
                ok, out = True, seen[key] + "\n[AVISO: ya ejecutaste exactamente esto y el resultado es el mismo. No lo repitas: da ahora tu respuesta final al usuario.]"
            elif ok_run:
                ok, out = exec_tool(name, args); seen[key] = out
                if name == "write_file" and str(args.get("path", "")).endswith(CODE_EXT): st["wrote"], st["ran"] = True, False
                if name == "bash":
                    st["ran"] = True
                    cmd = str(args.get("command", ""))
                    if re.search(r"pytest|unittest|npm (run )?test|go test|cargo test|mvn test|jest|vitest", cmd):
                        m = re.search(r"\[código de salida (\d+)\]", out)
                        st["fail"] = (m and m.group(1) != "0") and (cmd, out[-600:]) or None
            else:
                ok, out = False, "El usuario rechazó o no aprobó este comando. Propón una alternativa más segura."
            msgs.append({"role": "tool", "tool_name": name, "content": out, "tool_call_id": c["id"], "ok": ok})
            emit({"type": "tool_result", "id": c["id"], "ok": ok, "output": out})
    emit({"type": "notice", "text": f"Alcancé el máximo de {max_steps} pasos. Escribe «continúa» para seguir."})

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
                                   "model": MODEL, "search": bool(search_key()), "tps": LAST_SPEED["tps"]})
            if path == "/api/conversations":
                items = [jload(p, {}) for p in CONV_DIR.glob("*.json")]
                items = sorted([c for c in items if c], key=lambda c: -c.get("updated", 0))
                return self._json([{"id": c["id"], "title": c["title"], "updated": c["updated"], "n": sum(1 for m in c.get("messages", []) if m.get("role") == "user" and not m.get("hidden"))} for c in items])
            if path == "/api/file":
                from urllib.parse import parse_qs
                f = Path(parse_qs(urlparse(self.path).query).get("path", [""])[0]).resolve()
                if UPLOAD_DIR.resolve() in f.parents and f.is_file():
                    b = f.read_bytes()
                    ct = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}.get(f.suffix.lower(), "application/octet-stream")
                    self.send_response(200); self.send_header("Content-Type", ct); self.send_header("Content-Length", str(len(b))); self.end_headers()
                    return self.wfile.write(b)
                return self._json({"error": "no encontrado"}, 404)
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
            if path == "/api/upload":
                from urllib.parse import parse_qs
                n = int(self.headers.get("Content-Length") or 0)
                if n > MAX_UPLOAD:
                    self.rfile.read(n) if n < 200_000_000 else None
                    return self._json({"error": f"archivo demasiado grande (máx. {MAX_UPLOAD // 1048576} MB)"}, 413)
                name = re.sub(r"[^\w.\-]+", "_", parse_qs(urlparse(self.path).query).get("name", ["archivo"])[0])[-80:] or "archivo"
                dest = UPLOAD_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{name}"
                dest.write_bytes(self.rfile.read(n))
                return self._json({"path": str(dest), "name": name, "kind": kind_of(name), "size": n})
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
            if path == "/api/search/key":
                t = (b.get("key") or "").strip()
                if t: SEARCH_KEY_FILE.write_text(t); SEARCH_KEY_FILE.chmod(0o600)
                else: SEARCH_KEY_FILE.unlink(missing_ok=True)
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
        if not text and not b.get("attachments"):
            return self._json({"error": "mensaje vacío"}, 400)
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
            if conv["title"] == "Nueva conversación" and (text or b.get("attachments")):
                conv["title"] = title_from(text.lstrip("!/") or "Archivos adjuntos")
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
            elif text or b.get("attachments"):
                atts = b.get("attachments") or []
                if atts:
                    block = attachments_block(atts, emit)
                    conv["messages"].append({"role": "user", "display": text, "content": (text or "Analiza los archivos adjuntos.") + "\n\n[Archivos adjuntos]\n" + block, "attachments": atts})
                else:
                    conv["messages"].append({"role": "user", "content": text})
            if run_model:
                agent_turn(conv, emit, stop, mode, b.get("model") or MODEL, bool(b.get("think")))
            conv["updated"] = time.time(); jsave(conv_path(conv["id"]), conv)
            emit({"type": "title", "title": conv["title"], "id": conv["id"]})
            if mode in ("agent", "research") and not stop.is_set() and b.get("auto_push", True):
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
