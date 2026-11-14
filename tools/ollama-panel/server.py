#!/usr/bin/env python3
"""Panel del Pod: chat agéntico con Ollama + estado del pod + sincronización con GitHub.

Solo biblioteca estándar. Se ejecuta EN el pod:  python3 server.py
Variables (todas opcionales):
  PANEL_PORT=8787  PANEL_HOST=127.0.0.1  OLLAMA_URL=http://127.0.0.1:11434
  PANEL_MODEL=qwen3-coder:30b  PANEL_REPO=/ProxyManager  PANEL_WORKDIR=<repo>/pod-work
  PANEL_BRANCH=pod-sync  GITHUB_TOKEN=...  POD_HOURLY_USD=0.245  POD_LIMIT_H=3
"""
import base64, json, os, re, subprocess, sys, threading, time, uuid, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
sys.path.insert(0, str(Path(__file__).resolve().parent))
import agentkit as kit

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
NUM_CTX = int(os.environ.get("PANEL_NUM_CTX", "32768"))   # medido: 32k = 21,7 GB VRAM, misma velocidad que 16k/24k; 48k = 23,3 GB (sin margen)
MAX_STEPS = int(os.environ.get("PANEL_MAX_STEPS", "400"))
NUM_PREDICT = int(os.environ.get("PANEL_NUM_PREDICT", "8192"))
RESEARCH_STEPS = int(os.environ.get("PANEL_RESEARCH_STEPS", "45"))
WORKDIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = WORKDIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THINK_MODEL = os.environ.get("PANEL_THINK_MODEL", "qwen3:30b")
VISION_MODEL = os.environ.get("PANEL_VISION_MODEL", "qwen2.5vl:7b")
MAX_UPLOAD = 30 * 1024 * 1024
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
TEXT_EXT = (".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".toml", ".ini", ".log", ".py", ".js", ".ts", ".html", ".css", ".sh", ".sql", ".xml", ".env.example", ".cfg", ".java", ".go", ".rs", ".c", ".cpp", ".h")

def system_base():
    return f"""Eres un agente que trabaja DENTRO de un pod Linux con GPU, con herramientas reales: bash (con timeout y código de salida), read_file (paginado), write_file, edit_file, list_dir, search_files, git_status, git_diff, git_commit, git_push, run_tests, proc_start/proc_inspect/inspect_logs (procesos en segundo plano), plan, project_init, memory_update, web_search, web_fetch (internet), describe_image (ver imágenes) y notify. Los archivos que sube el usuario quedan en {UPLOAD_DIR}. Tu directorio de trabajo es {WORKDIR}.
IDIOMA: responde SIEMPRE en español, aunque el usuario escriba en inglés, las fuentes estén en inglés o el código tenga comentarios en inglés (traduce lo que cites). No traduzcas identificadores, comandos ni nombres de archivos.
Reglas generales:
- Eres el agente: cuando el usuario pide algo, lo haces tú con las herramientas. Nunca le pidas que ejecute algo por ti ni inventes salidas de comandos.
- SÍ tienes internet y SÍ puedes ejecutar comandos: nunca digas que no puedes; usa la herramienta.
- Actúa, no supongas: si necesitas saber algo del entorno, ejecútalo y lee la salida real. Tras cada herramienta lee el resultado y decide el siguiente paso.
- Ciclo de trabajo: PLANIFICAR (plan action=set con tareas pequeñas y verificables) → EJECUTAR → OBSERVAR el resultado → CORREGIR si falla → VERIFICAR con run_tests o ejecutando el programa → CONTINUAR. Marca una tarea como done SOLO con evidencia real (plan action=update, status=done, evidence=comando/prueba que lo demuestra).
- El tiempo restante y el estado real te los da el sistema en el bloque [ESTADO REAL …] al final del último mensaje: nunca inventes el tiempo. Reserva el último tramo para pruebas, revisión de secretos, commit, push y verificación; si falta tiempo, recorta funcionalidades secundarias y entrega algo funcional.
- Proyectos grandes: crea la carpeta con project_init (TASK/PLAN/PROGRESS/DECISIONS/TEST_RESULTS/BLOCKERS). Esos archivos sobreviven a la compactación del contexto: anota decisiones y bloqueos con memory_update. Si recibes [CONTEXTO RECUPERADO], continúa desde ahí sin repetir trabajo.
- Lee archivos grandes por partes (read_file offset/limit) y busca con search_files antes de leer enteros. Para cambios pequeños usa edit_file, no reescribas el archivo. Servicios y procesos que no terminan: proc_start (nunca bash a pie), y revisa con inspect_logs.
- El proyecto del usuario ya está clonado en {REPO}: para analizarlo léelo ahí, NO lo vuelvas a clonar. Lo que crees nuevo va en {WORKDIR}; el panel lo guarda en GitHub (rama {BRANCH}) al terminar. Para publicar tú: git_commit (revisa secretos) y git_push a la rama; una rama protegida distinta de la configurada (main/master) requiere aprobación del usuario; nunca force push.
- PRUEBAS REALES, no palabras: una URL «funciona» solo si http_check devolvió 2xx/3xx; «desplegado» solo si el servicio está vivo (proc_start) y responde a http_check; «URL pública» solo si http_check a un host NO local (no localhost) lo confirma — añadir una variable `public_url` no es publicar; «pruebas pasan» solo con run_tests; «publicado en GitHub» solo con git_push verificado. El estado de Git y el de la aplicación son cosas distintas: informa de ambos por separado. Un 403/captcha/DataDome se reporta tal cual, no como éxito.
- Cada instrucción nueva del usuario («pruébalo», «publícalo», «arréglalo») exige un plan nuevo y ejecutar herramientas ahora; nunca respondas repitiendo un resumen anterior. El sistema rechaza cerrar la tarea si faltan pruebas de lo pedido.
- NUNCA uses pkill/killall/kill masivo: matan procesos que no son tuyos (el panel, Ollama, servicios del usuario en 8000/8002). Para parar un servicio tuyo usa proc_inspect(action='stop', name=…); para reiniciarlo, stop + proc_start.
- Si repites una acción y el resultado no cambia, o el mismo error se repite, CAMBIA de estrategia: inspecciona la causa en vez de reintentar igual.
- Si el usuario pide que le avises (al terminar o después de algo), usa la herramienta notify con un resumen breve; además el panel avisa solo al terminar cada tarea.
- Nunca escribas secretos, tokens ni credenciales de proxies en archivos ni en commits (usa variables de entorno / .env ignorado por git). Si algo falla, lee el error, corrígelo y reintenta; no lo ocultes ni digas que funciona si la última salida real dice lo contrario.
- Texto final breve y concreto: qué hiciste, qué comprobaste (con la evidencia) y qué queda pendiente."""

SYSTEM_CODE = """
MODO PROGRAMACIÓN — trabaja como un ingeniero senior:
1. Antes de escribir, lee el código y las convenciones existentes y haz un plan de 3-5 líneas.
2. Estructura de proyecto real (Python): pod-work/NOMBRE/ con README.md (qué hace, instalar, ejecutar, probar), pyproject.toml, src/NOMBRE/__init__.py + módulos, y tests/ al mismo nivel que src/. Instala con `pip install -e .` dentro de un venv (.venv) y ejecuta run_tests. NUNCA pongas el código del paquete suelto en la raíz del proyecto.
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
    return system_base() + (SYSTEM_RESEARCH if mode == "research" else SYSTEM_CODE if mode == "agent" else "")

LEGACY_TOOLS = [
    {"type": "function", "function": {"name": "web_search", "description": "Busca en internet y devuelve título, URL y fragmento de los primeros resultados.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "web_fetch", "description": "Descarga una URL y devuelve su texto (HTML limpiado).",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "describe_image", "description": "Mira una imagen (foto, captura, diagrama) con el modelo de visión y responde una pregunta sobre ella o la describe y transcribe su texto.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "question": {"type": "string", "description": "Qué quieres saber de la imagen (opcional)"}}, "required": ["path"]}}},
]
TOOLS = kit.SCHEMAS + LEGACY_TOOLS

REFUSAL = re.compile(r"no (tengo|dispongo de) acceso|no puedo (acceder|ejecutar|buscar|navegar|conectarme)|no tengo la capacidad|sin acceso a internet|ejecuta (estos|este|los siguientes) comandos?", re.I)
DANGEROUS = re.compile(r"(\brm\s+-[a-z]*r|\bmkfs|\bdd\s+if=|:\(\)\s*\{|\bshutdown|\breboot|git\s+push\s+.*(--force|-f\b)|git\s+reset\s+--hard|>\s*/dev/sd|\bchmod\s+-R\s+777\s+/|curl[^|]*\|\s*(sudo\s+)?(ba)?sh|wget[^|]*\|\s*(sudo\s+)?(ba)?sh|\bkill\s+-9\s+1\b|\bpkill\b|\bkillall\b|\bfuser\s+-k|\bkill\s+(-\w+\s+)?\$\(|\bxargs\s+kill|\bpkill\s+ollama|\bollama\s+(rm|stop)\b|\bdocker\s+(system|volume|image)\s+prune|\bgit\s+clean\s+-[a-z]*f|git\s+push\b[^\n;&|]*\b(main|master)\b|git\s+branch\s+-D|\bsystemctl\s+(stop|disable)|--no-verify)")

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
    return kit.safe_path(p)

def token():
    return os.environ.get("GITHUB_TOKEN") or (TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else "")

def git(*args, auth=False, timeout=120):
    return kit.git(*args, auth=auth, timeout=timeout)

def cfg_load():
    return jload(STATE_FILE, {}).get("cfg", {})

def apply_config(c=None):
    """Repositorio, rama, directorio de trabajo y estrategia de publicación (persistidos en state.json)."""
    global BRANCH, WORKDIR, UPLOAD_DIR
    c = c if c is not None else cfg_load()
    BRANCH = c.get("branch") or os.environ.get("PANEL_BRANCH", "pod-sync")
    wd = c.get("workdir")
    WORKDIR = (REPO / wd).resolve() if wd else Path(os.environ.get("PANEL_WORKDIR", REPO / "pod-work"))
    WORKDIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR = WORKDIR / "uploads"; UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    kit.ENV.repo, kit.ENV.workdir, kit.ENV.branch = REPO, WORKDIR, BRANCH
    kit.ENV.token = token; kit.ENV.home = HOME
    kit.ENV.extra_secrets = lambda: [search_key()]

def strategy():
    return cfg_load().get("strategy", "push")   # local | commit | push

def set_config(b):
    c = cfg_load(); errs = []
    if "branch" in b:
        v = (b["branch"] or "").strip()
        if not re.fullmatch(r"[\w][\w./\-]{0,60}", v) or ".." in v: errs.append("rama inválida")
        elif v in kit.PROTECTED and not b.get("allow_main"): errs.append("main/master exige confirmación explícita (allow_main) desde el diálogo de GitHub")
        else: c["branch"] = v
    if "workdir" in b:
        v = (b["workdir"] or "").strip().strip("/")
        try:
            p = (REPO / v).resolve()
            if v and (REPO.resolve() == p or REPO.resolve() in p.parents) and ".git" not in p.parts: c["workdir"] = v
            else: errs.append("directorio fuera del repositorio")
        except Exception: errs.append("directorio inválido")
    if b.get("strategy") in ("local", "commit", "push"): c["strategy"] = b["strategy"]
    if b.get("repo"):
        v = b["repo"].strip()
        if re.fullmatch(r"[\w.\-]+/[\w.\-]+", v): git("remote", "set-url", "origin", f"https://github.com/{v}.git")
        else: errs.append("repositorio inválido (usa dueño/nombre)")
    if errs: return {"ok": False, "msg": "; ".join(errs)}
    st = jload(STATE_FILE, {}); st["cfg"] = c; jsave(STATE_FILE, st); apply_config(c)
    return {"ok": True}

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
    _, ahead = git("rev-list", "--count", f"origin/{BRANCH}..HEAD") if git("rev-parse", "--verify", f"origin/{BRANCH}")[0] == 0 else (1, "0")
    _, head = git("rev-parse", "--short", "HEAD")
    return {"repo": slug, "branch": branch.strip(), "target_branch": BRANCH, "head": head.strip(), "strategy": strategy(),
            "workdir": str(WORKDIR.relative_to(REPO)) if REPO in WORKDIR.parents else str(WORKDIR),
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

def git_save(message, push=None):
    """Guardar progreso según la estrategia: local (nada), commit (local) o push (rama + verificación del hash remoto).
    Siempre revisa secretos antes de commitear y nunca usa force."""
    strat = "push" if push is True else ("commit" if push is False else strategy())
    if strat == "local":
        return {"ok": True, "committed": False, "pushed": False, "msg": "Estrategia «solo local»: archivos guardados en el pod, sin commit."}
    ensure_branch()
    _, cur = git("rev-parse", "--abbrev-ref", "HEAD")
    if cur.strip() != BRANCH:   # el agente cambió de rama y no pudimos volver: no publicamos nada en la rama equivocada
        return {"ok": False, "committed": False, "pushed": False, "msg": f"No se publicó: el repositorio está en la rama «{cur.strip()}», no en «{BRANCH}». Cambia de rama o ajusta la rama en ⚙."}
    ok, msg = kit.commit_paths(message[:100], [str(WORKDIR)])
    if not ok:
        return {"ok": False, "committed": False, "pushed": False, "msg": msg}
    committed = msg.startswith("Commit creado")
    if strat == "commit":
        return {"ok": True, "committed": committed, "pushed": False, "msg": msg}
    if not token():
        return {"ok": True, "committed": committed, "pushed": False, "msg": "Commit local hecho. Falta el token de GitHub para subir."}
    r = kit.push_branch(BRANCH)
    return {"ok": r["ok"], "committed": committed, "pushed": r["ok"], "msg": r["msg"], "remote": r.get("remote"), "local": r.get("local")}

def git_pull():
    ensure_branch()
    code, out = git("pull", "--rebase", "--autostash", "origin", BRANCH, auth=True)
    if code and "couldn't find remote ref" in out:
        return {"ok": True, "msg": "La rama aún no existe en GitHub."}
    if code:
        git("rebase", "--abort")
    return {"ok": code == 0, "msg": kit.clip(out.strip(), 600)}

def git_verify():
    """Compara el commit local con el de la rama de trabajo en GitHub."""
    _, head = git("rev-parse", "HEAD"); rh, err = kit.remote_hash(BRANCH)
    return {"branch": BRANCH, "local": head.strip(), "remote": rh, "match": rh == head.strip(), "msg": err}

def git_integrate(target):
    """Lleva la rama de trabajo a otra rama (p. ej. main) SOLO si es avance rápido (sin force). La rama destino debe existir."""
    target = (target or "main").strip()
    if not re.fullmatch(r"[\w][\w./\-]{0,60}", target): return {"ok": False, "msg": "rama destino inválida"}
    th, err = kit.remote_hash(target)
    if th is None: return {"ok": False, "msg": "No pude consultar GitHub: " + err}
    if th == "": return {"ok": False, "msg": f"La rama «{target}» no existe en GitHub. Créala tú (o elige otra): el agente no crea ramas principales."}
    git("fetch", "origin", target, auth=True)
    if git("merge-base", "--is-ancestor", th, "HEAD")[0] != 0:
        return {"ok": False, "msg": f"«{target}» tiene commits que tu rama no tiene (no es avance rápido). Trae/integra primero; no se hace force push."}
    code, out = git("push", "origin", f"HEAD:refs/heads/{target}", auth=True)
    if code: return {"ok": False, "msg": kit.clip(out.strip(), 500)}
    rh, _ = kit.remote_hash(target); _, head = git("rev-parse", "HEAD")
    return {"ok": rh == head.strip(), "msg": f"{target} en GitHub = {rh[:10]} " + ("(verificado)" if rh == head.strip() else "(NO coincide)")}

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
    if name == "git_push":
        b = str(args.get("branch") or BRANCH).strip()
        return b in kit.PROTECTED and b != BRANCH     # la rama configurada por el usuario (p. ej. main) no pide aprobación; cualquier otra protegida sí
    return False

def legacy_exec(name, args):
    if name == "web_search":
        return True, web_search(args.get("query", ""))
    if name == "web_fetch":
        return True, kit.clip(web_fetch(args.get("url", "")), 9000)
    if name == "describe_image":
        return True, describe_image(args.get("path", ""), args.get("question"))
    return False, f"Herramienta desconocida: {name}. Disponibles: " + ", ".join(x["function"]["name"] for x in TOOLS)

TOOL_NAMES = {x["function"]["name"] for x in TOOLS}
FN_TAG = re.compile(r"<function=([\w\-]+)>([\s\S]*?)</function>")
PARAM_TAG = re.compile(r"<parameter=([\w\-]+)>\s*([\s\S]*?)\s*</parameter>")

def parse_text_tool_call(text):
    """Algunos modelos escriben las llamadas como JSON o como <function=…> en el texto. Devuelve (llamadas, resto) o None."""
    dec, calls, spans = json.JSONDecoder(), [], []
    for m in re.finditer(r"\{\s*\"name\"\s*:", text):
        if spans and m.start() < spans[-1][1]:
            continue
        try:
            o, j = dec.raw_decode(text, m.start())
        except ValueError:
            continue
        if isinstance(o, dict) and o.get("name") in TOOL_NAMES:
            a = o.get("arguments", o.get("parameters", {}))
            calls.append({"function": {"name": o["name"], "arguments": a if isinstance(a, dict) else {}}})
            spans.append((m.start(), j))
    for m in FN_TAG.finditer(text):
        if m.group(1) in TOOL_NAMES:
            calls.append({"function": {"name": m.group(1), "arguments": {k: v for k, v in PARAM_TAG.findall(m.group(2))}}})
            spans.append((m.start(), m.end()))
    if not calls:
        return None
    spans.sort()
    rest, last = "", 0
    for st, en in spans:
        rest += text[last:st]; last = en
    rest = re.sub(r"</?tool_call>|^```(?:json)?\s*$|^```\s*$", "", rest + text[last:], flags=re.M).strip()
    return calls, rest

LOOKS_LIKE_CALL = re.compile(r"<tool_call>|<function=|\"name\"\s*:\s*\"(?:%s)\"" % "|".join(sorted(TOOL_NAMES)))
INTENT = re.compile(r"\b(voy a|vamos a|a continuación|ahora (voy|ejecuto|creo|escribo|lanzo)|el siguiente paso es|procedo a|I will|I'll now|Let me|Next, I)\b", re.I)

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

def stream_ollama(view, emit, stop, model, tools=True, think=False, temp=None, seed=None):
    opts = {"num_ctx": NUM_CTX, "temperature": temp if temp is not None else (0.6 if think else 0.2), "top_p": 0.8, "top_k": 20, "repeat_penalty": 1.05, "num_predict": NUM_PREDICT, **({"seed": seed} if seed is not None else {})}
    body = json.dumps({"model": model, "messages": view, **({"tools": TOOLS} if tools else {}), "stream": True,
                       "options": opts, "keep_alive": "2h", **({"think": True} if think else {})}).encode()
    req = urllib.request.Request(OLLAMA + "/api/chat", body, {"Content-Type": "application/json"})
    content, calls, stats, thinking = "", [], {}, ""
    try:
        r_ = urllib.request.urlopen(req, timeout=300)
    except urllib.error.HTTPError as e:
        body_ = ""
        try: body_ = e.read().decode("utf-8", "replace")[:300]
        except Exception: pass
        raise RuntimeError(f"HTTP {e.code}: {body_ or e.reason}")
    with r_ as r:
        for line in r:
            if stop.is_set():
                break
            if not line.strip():
                continue
            d = json.loads(line)
            if d.get("error"):
                raise RuntimeError(d["error"])
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
                stats = {"tokens": ec, "tps": round(ec / (ed / 1e9), 1) if ed else None, "prompt_tokens": d.get("prompt_eval_count", 0),
                         "done_reason": d.get("done_reason")}
    stats["thinking"] = thinking
    return content, calls, stats

PARSE_FAIL = re.compile(r"tool call pars|XML syntax|unexpected EOF|invalid character|parsing failed", re.I)
SPLIT_HINT = ("[AVISO DEL SISTEMA: tu llamada a herramienta anterior NO se pudo interpretar (XML/JSON truncado o mal formado) y se perdió. "
              "Vuelve a intentarlo con contenido MÁS PEQUEÑO: escribe archivos grandes en varios write_file de máximo ~120 líneas (o crea el esqueleto y añade con edit_file), "
              "sin texto largo antes de la llamada y sin dejar etiquetas sin cerrar.]")

def call_model(ag, view_fn, emit, stop, model, tools, think):
    """Llama a Ollama con reintentos DISTINTOS (otra temperatura/semilla y, si fue un fallo de parseo, una pista de dividir).
    Devuelve (content, calls, stats); stats['parse_fail']=True si Ollama no pudo interpretar la llamada tras los reintentos; None si hay que parar."""
    last_err = None
    for attempt in range(3):
        if stop.is_set():
            return None
        pf = bool(last_err and PARSE_FAIL.search(str(last_err)))
        try:
            view = view_fn()
            if attempt and pf and view:
                v = dict(view[-1]); v["content"] = (v.get("content") or "") + "\n\n" + SPLIT_HINT; view = view[:-1] + [v]
            content, calls, stats = stream_ollama(view, emit, stop, model, tools, think, temp=(0.2 if not attempt else 0.55 + 0.15 * attempt), seed=(None if not attempt else 1000 + attempt))
        except Exception as e:
            last_err = e
            if stop.is_set():
                return None
            if PARSE_FAIL.search(str(e)):
                ag.n_invalid += 1
            if attempt < 2:
                emit({"type": "notice", "text": f"Ollama falló ({str(e)[:140]}); reintento {attempt + 1}/2 con otra temperatura" + (" y pidiendo contenido más pequeño…" if PARSE_FAIL.search(str(e)) else "…")}); emit({"type": "clear_text"})
                time.sleep(2 * (attempt + 1)); continue
            if PARSE_FAIL.search(str(e)):
                return "", [], {"parse_fail": True, "error": str(e)[:200]}
            raise
        if not content.strip() and not calls and not stats.get("thinking") and not stop.is_set():
            ag.strag.empty += 1
            if attempt < 2:
                emit({"type": "notice", "text": f"Respuesta vacía del modelo; reintento {attempt + 1}/2…"}); continue
        return content, calls, stats
    return "", [], {}

def agent_turn(conv, emit, stop, mode="agent", model=None, think=False, budget_min=None, resume=False, steer=None):
    """Controlador: PLANIFICAR → EJECUTAR → OBSERVAR → EVALUAR → CORREGIR → VERIFICAR → CONTINUAR. Devuelve el resultado:
    done | stopped | blocked | budget | error | incomplete."""
    model = THINK_MODEL if think else (model or MODEL)
    msgs = conv["messages"]
    kit.repair_history(msgs)
    pod_rem = max(0, LIMIT_H * 3600 - pod_clock()["seconds"])
    if budget_min:       # el presupuesto que escribes tú manda; el límite del pod solo avisa (antes lo anulaba y toda tarea nueva terminaba al instante)
        if pod_rem <= 0: emit({"type": "notice", "text": f"⚠ El reloj del pod ya superó el límite configurado ({LIMIT_H:g} h). Se respeta tu presupuesto de {budget_min:g} min; revisa el coste en RunPod."})
        ag = kit.Agent(conv, emit, stop, legacy_exec, budget_s=int(budget_min * 60), pod_remaining_s=None, mode=mode)
    else:
        if pod_rem <= 0 and mode != "chat":
            emit({"type": "error", "text": f"No hay presupuesto: el reloj del pod ({pod_clock()['seconds'] // 3600} h {pod_clock()['seconds'] % 3600 // 60} min) ya superó el límite de {LIMIT_H:g} h. Escribe un número de minutos en «Presupuesto» para continuar, o pulsa «Reiniciar reloj» si el pod se renovó."})
            conv["run"] = {**(conv.get("run") or {}), "status": "budget", "updated": time.time()}; jsave(conv_path(conv["id"]), conv); return "budget"
        ag = kit.Agent(conv, emit, stop, legacy_exec, budget_s=None, pod_remaining_s=pod_rem, mode=mode)
    RUNS_AGENT[conv["id"]] = ag
    first = next((m.get("display") or m["content"] for m in msgs if m["role"] == "user" and not m.get("hidden")), "")
    if mode == "agent" and not ag.project and len(first) >= 300:
        ag.init_project("sesion", first[:20000], session=True)
        emit({"type": "notice", "text": f"Memoria de la tarea guardada en {ag.project} (TASK/PLAN/PROGRESS/DECISIONS/TEST_RESULTS/BLOCKERS); pasa a la carpeta del proyecto cuando el agente llame a project_init."})
    st = {"wrote": False, "ran": False, "nv": False, "ne": False, "nf": 0, "refused": False, "intent": 0, "pend": 0, "parse": 0, "gate": 0, "gate_total": 0}
    user_msgs = [(m.get("display") or m["content"]) for m in msgs if m["role"] == "user" and not m.get("hidden") and not m.get("shell")]
    def hidden_once(text):
        """Aviso interno SIN repeticiones: si el mismo texto ya se envió hace poco, no se vuelve a enviar."""
        if any(m.get("hidden") and m["role"] == "user" and m["content"] == text for m in msgs[(conv.get("ctx") or {}).get("upto", 0):]): return False   # ya está en lo que ve el modelo
        msgs.append({"role": "user", "hidden": True, "content": text}); return True
    if mode == "agent" and user_msgs:
        if resume:
            if not ag.reqs:
                for u in user_msgs: ag.add_requirements(u)
                for r in ag.reqs: r["since"] = 0
        else:
            ag.on_user_message(user_msgs[-1])
        for n_ in ag.change_notes: emit({"type": "notice", "text": "✎ " + n_})
        ag.settle(); un = ag.unmet()
        active = [r for r in ag.reqs if kit.rstat(r) == "active"]; blocked = [r for r in ag.reqs if kit.rstat(r) == "blocked"]
        if active or blocked:
            hidden_once("CRITERIOS DE ACEPTACIÓN ACTIVOS de la tarea actual (el sistema los verifica con evidencia REAL; los retirados o ya cumplidos NO cuentan):\n" +
                        "\n".join(f"- [PENDIENTE] {r['text']}" for r in active) +
                        ("".join(f"\n- [BLOQUEADO — ya avisado, no insistas, pasa a otras tareas] {r['text'][:90]}: {r.get('reason', '')[:100]}" for r in blocked)) +
                        "\nCrea ahora un plan (plan action=set) que cubra lo pendiente y EJECÚTALO con herramientas. No repitas resúmenes anteriores: actúa sobre la última petición del usuario. Para probar una URL usa http_check; para desplegar usa proc_start + http_check; para publicar en GitHub usa git_commit + git_push.")
        ag.write_acceptance()
    max_steps = RESEARCH_STEPS if mode == "research" else MAX_STEPS
    outcome = "incomplete"
    def save(status="running"):
        conv["run"] = {**ag.state(), "status": status, "updated": time.time(), "mode": mode}
        conv["updated"] = time.time(); jsave(conv_path(conv["id"]), conv)
    def hidden_user(text):
        msgs.append({"role": "user", "hidden": True, "content": text})
    steer = steer if steer is not None else []
    def drain():
        n = 0
        while steer:
            t = steer.pop(0)
            msgs.append({"role": "user", "content": "[COMENTARIO DEL USUARIO MIENTRAS TRABAJAS — tenlo en cuenta desde ya; ajusta el plan si hace falta y sigue con herramientas]\n" + t, "display": t, "steer": True})
            emit({"type": "user", "text": t, "steer": True})
            if mode == "agent":
                ag.on_user_message(t, steer=True)
                for n_ in ag.change_notes: emit({"type": "notice", "text": "✎ " + n_})
            ag.strag.strikes = 0; st["gate"] = 0; st["pend"] = 0; n += 1
        if n: save()
        return n
    ag.push_status(); save()
    for step in range(max_steps):
        drain()
        if stop.is_set():
            emit({"type": "notice", "text": "Detenido por el usuario."}); outcome = "stopped"; break
        if mode != "chat" and ag.remaining() <= 0:
            emit({"type": "notice", "text": "Presupuesto de tiempo agotado: se guarda el resultado parcial."}); ag.log("BLOCKERS.md", "presupuesto de tiempo agotado"); outcome = "budget"; break
        if mode != "chat" and ag.in_reserve() and not ag.final_notified:
            ag.final_notified = True; ag.phase = "VERIFICAR"
            hidden_user("TIEMPO: queda poco presupuesto. FASE FINAL: no empieces funcionalidades nuevas. Ejecuta las pruebas, corrige solo lo imprescindible, revisa que no haya secretos, haz git_commit y git_push, y entrega un resultado parcial funcional.")
        view_fn = lambda: ag.build_view(system_for(mode), msgs, ag.budget_note() if mode != "chat" else None)
        if ag.estimate_tokens(view_fn()) > NUM_CTX * 0.70 or ag.ctx_tokens > NUM_CTX * 0.80:
            if ag.compact(): ag.ctx_tokens = 0; save()
        try:
            res = call_model(ag, view_fn, emit, stop, model, mode != "chat", think)
        except Exception as e:
            emit({"type": "error", "text": f"No pude hablar con Ollama tras 3 intentos: {e}"}); ag.log("BLOCKERS.md", f"Ollama no responde: {str(e)[:150]}"); outcome = "error"; break
        if res is None:
            emit({"type": "notice", "text": "Detenido por el usuario."}); outcome = "stopped"; break
        content, calls, stats = res
        if stats.get("parse_fail"):
            st["parse"] += 1; ag.log("BLOCKERS.md", f"Ollama no pudo interpretar la llamada a herramienta ({st['parse']}): {stats.get('error', '')[:100]}")
            if st["parse"] >= 4:
                emit({"type": "error", "text": "Ollama no pudo interpretar las llamadas a herramienta 4 veces seguidas: tarea BLOQUEADA (progreso guardado)."}); outcome = "blocked"; break
            hidden_user(SPLIT_HINT + " Divide el trabajo en pasos pequeños.")
            emit({"type": "notice", "text": f"El modelo escribió una llamada demasiado grande/rota ({st['parse']}/4): le pido dividirla en trozos pequeños."}); save(); continue
        if mode == "chat":
            calls = []
        elif not calls and content:
            parsed = parse_text_tool_call(content)
            calls = parsed[0] if parsed else []
            if parsed:
                emit({"type": "clear_text"}); content = parsed[1]
                if content: emit({"type": "token", "text": content})
        if not calls and not content.strip() and not stats.get("thinking"):
            emit({"type": "error", "text": "El modelo devolvió respuestas vacías 3 veces seguidas: tarea BLOQUEADA (progreso guardado; pulsa Reanudar)."})
            ag.log("BLOCKERS.md", "el modelo devolvió respuestas vacías"); outcome = "blocked"; break
        if stats.get("prompt_tokens"):
            ag.ctx_tokens = stats["prompt_tokens"] + (stats.get("tokens") or 0)
        if stats.get("tps"):
            ag.tps.append(stats["tps"]); LAST_SPEED["tps"] = stats["tps"]
        nudge = None
        probs = []
        if mode == "agent" and not calls and content.strip() and not LOOKS_LIKE_CALL.search(content):
            prev_final = next((m.get("content") for m in reversed(msgs) if m["role"] == "assistant" and not m.get("tool_calls") and not m.get("hidden") and m.get("content")), None)
            probs = ag.completion_problems(content, prev_final)
        gate_ok = False
        if probs:
            gkey = f"{ag.last_mut}:" + kit.hashlib.md5("|".join(sorted(probs)).encode()).hexdigest()[:10]
            seen_n = ag.sig_counts.get(gkey, 0)       # persistente entre turnos/reanudaciones: el mismo aviso nunca se repite más de 2 veces
            if seen_n < 2 and st["gate_total"] < 6:
                ag.sig_counts[gkey] = seen_n + 1; gate_ok = True
            else:
                for r_, _ in ag.unmet(): ag.block(r_, "sin evidencia tras 2 avisos")
                st["gate_blocked"] = True; st["claims"] = [p for p in probs if not p.startswith("Requisito")]
        if mode != "chat" and not calls and content:
            if probs and gate_ok:
                st["gate"] += 1; st["gate_total"] += 1
                nudge = ("NO puedes cerrar la tarea todavía. Faltan pruebas reales de lo que afirmas o de lo que se pidió:\n- " + "\n- ".join(probs[:6]) +
                         "\nEjecuta AHORA las herramientas necesarias (http_check, run_tests, proc_start, git_push…) y reporta el resultado REAL, aunque sea un fallo o un bloqueo (403/captcha/DataDome). "
                         "Si algo no se puede lograr, dilo con la evidencia en vez de afirmar que funciona.")
            elif LOOKS_LIKE_CALL.search(content):
                ag.n_invalid += 1; ag.strag.parsefail += 1; st["parse"] += 1
                nudge = ("Tu llamada a herramienta estaba mal formada y NO se ejecutó. Vuelve a emitirla con el formato de herramientas (nombre y argumentos como JSON válido, strings escapados). "
                         "Si el contenido es muy largo, divídelo en varias llamadas write_file/edit_file más pequeñas.")
                if st["parse"] >= 4:
                    emit({"type": "error", "text": "Cuatro llamadas a herramientas mal formadas seguidas: tarea BLOQUEADA."}); ag.log("BLOCKERS.md", "llamadas a herramientas mal formadas repetidas"); outcome = "blocked"; break
            elif not st["refused"] and REFUSAL.search(content):
                st["refused"] = True
                nudge = "Eso es incorrecto: SÍ tienes acceso a internet y a un shell mediante tus herramientas (web_search, web_fetch, bash). Úsalas ahora para hacer lo que te pedí."
            elif ag.last_test and not ag.last_test["ok"] and st["nf"] < 3:
                st["nf"] += 1
                nudge = (f"La ÚLTIMA ejecución de pruebas FALLÓ ({ag.last_test['summary']}). No digas que pasaron. Lee el error, corrige la causa y vuelve a ejecutar run_tests hasta que pasen. "
                         "Si no puedes arreglarlo, marca la tarea como blocked con evidencia e informa honestamente.")
            elif mode == "agent" and st["wrote"] and not st["ran"] and not st["nv"]:
                st["nv"] = True
                nudge = "Escribiste código pero no lo has ejecutado ni probado. Ejecútalo y/o corre run_tests ahora y corrige lo que falle antes de dar la tarea por terminada."
            elif mode == "agent" and ag.pending() and st["pend"] < 5 and not ag.in_reserve():
                st["pend"] += 1
                nudge = "Todavía hay tareas sin completar según el plan:\n" + "\n".join(f"{i}. [{kit.STATUS_ES[t['status']]}] {t['text']}" for i, t in enumerate(ag.tasks, 1) if t["status"] in ("pending", "running")) + \
                        "\nContinúa con la siguiente usando herramientas. Si alguna es imposible, márcala con plan(update, status=blocked, evidence=…)."
            elif mode == "agent" and INTENT.search(content[-400:]) and st["intent"] < 2 and len(content) < 700:
                st["intent"] += 1
                nudge = "Anuncias lo que vas a hacer pero no llamaste a ninguna herramienta. Ejecútalo ahora con la herramienta correspondiente."
            elif looks_english(content) and not st["ne"]:
                st["ne"] = True
                nudge = "Debes responder SIEMPRE en español. Reescribe tu respuesta anterior en español."
        if nudge:
            msgs.append({"role": "assistant", "content": content, "hidden": True})
            hidden_user(nudge); emit({"type": "clear_text"}); save(); continue
        content = re.sub(r"</?tool_call>", "", content).strip() if not calls else content
        if calls and len(content) > 220:   # borrador de conclusión repetido mientras aún usa herramientas
            content = ""; emit({"type": "clear_text"})
        th = stats.pop("thinking", "")
        a = {"role": "assistant", "content": content, "stats": {k: v for k, v in stats.items() if k in ("tokens", "tps")}, **({"thinking": th} if th else {})}
        if calls:
            a["tool_calls"] = [{"id": uuid.uuid4().hex[:8], **c} for c in calls]
            st["parse"] = 0; st["pend"] = 0; st["gate"] = 0
        msgs.append(a)
        emit({"type": "assistant_done", "stats": a["stats"]})
        if not calls:
            if steer:      # llegó un comentario del usuario justo al terminar: se atiende antes de cerrar
                continue
            outcome = "done"; break
        reasons = []
        for c in a["tool_calls"]:
            name = c["function"]["name"]; args = c["function"].get("arguments") or {}
            if isinstance(args, str):
                try: args = json.loads(args)
                except Exception: args = {}
            if not isinstance(args, dict): args = {}
            emit({"type": "tool_start", "id": c["id"], "name": name, "args": {k: (kit.redact(v) if isinstance(v, str) else v) for k, v in args.items()}})
            ok_run, blocked = True, False
            if name not in TOOL_NAMES:
                ag.n_calls += 1; ag.n_invalid += 1; ag.n_err += 1
                out = f"Herramienta desconocida: {name}. Disponibles: " + ", ".join(sorted(TOOL_NAMES)); ok = False
            else:
                if needs_approval(name, args):
                    ev = threading.Event(); APPROVALS[c["id"]] = {"event": ev, "ok": False}
                    emit({"type": "approval", "id": c["id"], "name": name, "args": args})
                    deadline = time.time() + 900
                    while not ev.wait(0.5):
                        if stop.is_set() or time.time() > deadline: break
                    ok_run = APPROVALS.pop(c["id"], {}).get("ok", False) and not stop.is_set()
                    blocked = not ok_run
                if ok_run:
                    ag.phase = {"run_tests": "VERIFICAR", "git_commit": "PUBLICAR", "git_push": "PUBLICAR"}.get(name, ag.phase if ag.phase != "PLANIFICAR" else "EJECUTAR")
                    ok, out = ag.exec(name, args)
                    if name == "write_file" and str(args.get("path", "")).endswith(CODE_EXT): st["wrote"], st["ran"] = True, False
                    if name == "edit_file" and str(args.get("path", "")).endswith(CODE_EXT): st["wrote"], st["ran"] = True, False
                    if name in ("bash", "run_tests"): st["ran"] = True
                else:
                    ok, out = False, "El usuario rechazó o no aprobó este comando (o no respondió a tiempo). Propón una alternativa más segura; no insistas con el mismo comando."
                    ag.n_calls += 1; ag.n_err += 1
            msgs.append({"role": "tool", "tool_name": name, "content": out, "tool_call_id": c["id"], "ok": ok})
            emit({"type": "tool_result", "id": c["id"], "ok": ok, "output": out})
            r = ag.strag.record(name, args, ok, out, blocked=blocked)
            if r: reasons.append(r)
            ag.push_status()
        if mode == "agent":
            ag.unmet()
            if ag.new_blocks:
                hidden_once("CRITERIO(S) BLOQUEADO(S), avisado UNA sola vez (queda en BLOCKERS.md): " + "; ".join(ag.new_blocks) + ". No insistas ni intentes evadir la protección. Continúa con las demás tareas pendientes independientes (frontend, backend, pruebas…) y al terminar cierra con un único informe de bloqueos.")
                ag.new_blocks.clear(); st["pend"] = 0
        if reasons:
            s = ag.strag.strikes
            ag.log("BLOCKERS.md", f"estancamiento ({s}): {reasons[0]}")
            if s >= 4:
                emit({"type": "error", "text": f"BLOQUEADO por estancamiento: {reasons[0]}. Progreso guardado; revisa BLOCKERS.md y pulsa Reanudar con nuevas indicaciones."}); outcome = "blocked"; save("blocked"); break
            hidden_user(f"ESTANCAMIENTO detectado ({s}/4): {reasons[0]}. Detén ese intento. 1) Resume en una frase qué estás intentando. 2) Inspecciona la causa real (lee el error completo, el archivo o el log relevante). "
                        "3) Cambia de estrategia: no repitas la misma acción." + (" Si no existe una alternativa válida, marca la tarea como blocked con plan(update, status=blocked, evidence=causa) y sigue con otra." if s >= 2 else ""))
            emit({"type": "notice", "text": f"⚠ Estancamiento ({s}/4): {reasons[0]}. Cambio de estrategia solicitado al modelo."})
        save()
    else:
        emit({"type": "notice", "text": f"Alcancé el máximo de {max_steps} pasos. Pulsa Reanudar para seguir."}); outcome = "incomplete"
    if outcome == "done" and mode == "agent" and ag.pending():
        outcome = "incomplete"
    if mode == "agent" and (ag.reqs or ag.ledger) and outcome in ("done", "incomplete", "budget", "blocked", "stopped"):
        try:
            report = ag.verified_report()
            has_blocked = any(kit.rstat(r_) == "blocked" for r_ in ag.reqs)
            if outcome == "done" and (ag.unmet() or has_blocked or st.get("gate_blocked")):
                outcome = "incomplete"
            if st.get("claims"): report += "\n- ⚠ Afirmaciones de la respuesta SIN evidencia (ignóralas): " + "; ".join(p[:110] for p in st["claims"][:3])
            if outcome == "incomplete":
                report += ("\n- Resultado: **INCOMPLETO** — los trabajos posibles están terminados; quedan criterios BLOQUEADOS (informe único arriba)." if has_blocked and not ag.unmet()
                           else "\n- Resultado: **INCOMPLETO** — la tarea NO se da por terminada; pulsa Reanudar para continuar con lo pendiente.")
            prev_rep = next(((m.get("content") or "").split("\n\n---\n")[-1] for m in reversed(msgs) if m["role"] == "assistant" and "Estado verificado por el controlador" in (m.get("content") or "")), None)
            if prev_rep == report:
                emit({"type": "notice", "text": "Sin cambios desde el último informe verificado (no se repite)."})
            else:
                last = msgs[-1] if msgs else None
                if last and last["role"] == "assistant" and not last.get("tool_calls"):
                    last["content"] = (last.get("content") or "") + "\n\n---\n" + report
                else:
                    msgs.append({"role": "assistant", "content": report, "verified": True})
                emit({"type": "verified", "text": report})
        except Exception as e:
            emit({"type": "notice", "text": f"No pude generar el informe verificado: {e}"})
    ag.push_status(); save(outcome)
    return outcome

RUNS_AGENT = {}   # conv_id -> Agent (último)

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

def ram_info():
    try:
        m = {l.split(":")[0]: int(l.split()[1]) for l in Path("/proc/meminfo").read_text().splitlines()}
        return {"used": (m["MemTotal"] - m["MemAvailable"]) // 1024, "total": m["MemTotal"] // 1024}
    except Exception:
        return None

def metrics():
    """Métricas reales agregadas del registro de herramientas (toollog/*.jsonl)."""
    n = ok = 0; secs = 0.0; per = {}
    for f in (HOME / "toollog").glob("*.jsonl"):
        for line in f.read_text(errors="replace").splitlines():
            try: e = json.loads(line)
            except ValueError: continue
            n += 1; ok += bool(e["ok"]); secs += e["seconds"]; p = per.setdefault(e["tool"], [0, 0, 0.0]); p[0] += 1; p[1] += bool(e["ok"]); p[2] += e["seconds"]
    return {"tool_calls": n, "ok": ok, "avg_seconds": round(secs / n, 2) if n else None,
            "per_tool": {k: {"n": v[0], "ok": v[1], "avg_s": round(v[2] / v[0], 2)} for k, v in per.items()}, "tps_last": LAST_SPEED["tps"]}

class Run:
    """Una tarea del agente: corre en su propio hilo, independiente del navegador; los eventos quedan en memoria para reenganchar."""
    def __init__(self, cid):
        self.cid, self.events, self.cond, self.status, self.stop, self.base, self.t0 = cid, [], threading.Condition(), "running", threading.Event(), 0, time.time()
        self.steer = []   # comentarios del usuario mientras la tarea corre
    def emit(self, ev):
        with self.cond:
            self.events.append(ev); self.cond.notify_all()

RUNS = {}

def run_worker(run, conv, b):
    emit, stop = run.emit, run.stop
    mode = b.get("mode", "agent"); text = (b.get("message") or "").strip()
    outcome = "error"
    try:
        if conv["title"] == "Nueva conversación" and (text or b.get("attachments")):
            conv["title"] = title_from(text.lstrip("!/") or "Archivos adjuntos")
        conv["run"] = {**(conv.get("run") or {}), "status": "running", "started": time.time()}
        run_model = True
        if b.get("resume"):
            kit.repair_history(conv["messages"])
            conv["messages"].append({"role": "user", "hidden": True, "content": "REANUDA la tarea donde la dejaste: revisa el estado real (git_status, plan action=show, PROGRESS.md/BLOCKERS.md) y continúa con la siguiente tarea pendiente sin repetir lo ya hecho." + (f"\nIndicaciones del usuario: {text}" if text else "")})
            emit({"type": "user", "text": "↻ Reanudar tarea" + (f": {text}" if text else "")})
        elif text.startswith("!"):   # comando directo en el pod
            cmd = text[1:].strip()
            emit({"type": "tool_start", "id": "sh", "name": "bash", "args": {"command": cmd}})
            r = kit.run_cmd(cmd, stop=stop); out = kit.fmt_result(r)
            emit({"type": "tool_result", "id": "sh", "ok": r["code"] == 0, "output": out})
            conv["messages"].append({"role": "user", "content": f"Ejecuté en el pod: `{kit.redact(cmd)}`\nSalida (código {r['code']}):\n```\n{clip(out, 6000)}\n```",
                                     "shell": {"cmd": kit.redact(cmd), "output": clip(out), "code": r["code"]}})
            run_model = bool(b.get("send_output", True))
        elif text.startswith("/leer "):
            emit({"type": "user", "text": text})
            url = text[6:].strip()
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pod-panel"}), timeout=20) as r:
                    raw = r.read(400000).decode("utf-8", "replace")
                page = re.sub(r"\s+", " ", re.sub(r"<(script|style)[\s\S]*?</\1>|<[^>]+>", " ", raw)).strip()
            except Exception as e:
                page = f"[error al leer: {e}]"
            conv["messages"].append({"role": "user", "content": f"Contenido de {url}:\n{clip(page, 8000)}\n\n(Resume lo relevante y espera instrucciones.)", "display": text})
        else:
            atts = b.get("attachments") or []
            emit({"type": "user", "text": text, "atts": [{"name": a.get("name"), "kind": a.get("kind"), "path": a.get("path")} for a in atts]})
            if atts:
                block = attachments_block(atts, emit)
                conv["messages"].append({"role": "user", "display": text, "content": (text or "Analiza los archivos adjuntos.") + "\n\n[Archivos adjuntos]\n" + block, "attachments": atts})
            else:
                conv["messages"].append({"role": "user", "content": text})
        jsave(conv_path(conv["id"]), conv)
        if run_model:
            bm = b.get("budget_min")
            outcome = agent_turn(conv, emit, stop, mode, b.get("model") or MODEL, bool(b.get("think")), float(bm) if bm else None, resume=bool(b.get("resume")), steer=run.steer)
        else:
            outcome = "done"
        conv["updated"] = time.time()
        conv["run"] = {**(conv.get("run") or {}), "status": outcome}
        jsave(conv_path(conv["id"]), conv)
        emit({"type": "title", "title": conv["title"], "id": conv["id"]})
        if mode in ("agent", "research") and not stop.is_set() and b.get("auto_push", True) and outcome in ("done", "budget", "blocked", "incomplete"):
            g = git_save("pod: " + conv["title"])
            if g.get("committed") or not g.get("ok"):
                emit({"type": "git", **g})
        emit({"type": "outcome", "outcome": outcome})
    except Exception as e:
        emit({"type": "error", "text": str(e)})
        conv["run"] = {**(conv.get("run") or {}), "status": "error"}
        try: jsave(conv_path(conv["id"]), conv)
        except Exception: pass
    finally:
        emit({"type": "done"})
        run.status = "done"
        with run.cond: run.cond.notify_all()
        STOPS.pop(conv["id"], None)

def mark_interrupted():
    """Al arrancar: las tareas que estaban 'running' se quedaron a medias (reinicio/corte). Se marcan para poder reanudarlas."""
    for p in CONV_DIR.glob("*.json"):
        c = jload(p, {})
        if (c.get("run") or {}).get("status") == "running":
            c["run"]["status"] = "interrupted"; jsave(p, c)

def install_hooks():
    """Hook pre-commit que bloquea secretos incluso si el modelo hace `git commit` por bash."""
    try:
        h = REPO / ".git" / "hooks" / "pre-commit"
        body = f"#!/bin/sh\n# panel-secret-scan\nexec python3 {Path(__file__).resolve().parent / 'agentkit.py'} --scan-staged\n"
        if not h.exists() or "panel-secret-scan" in h.read_text():
            h.write_text(body); h.chmod(0o755)
    except Exception:
        pass


# ---------------------------------------------------------------- despliegue (pod/VPS nuevo)
def deploy_cfg():
    return jload(STATE_FILE, {}).get("deploy", {})

def set_deploy(b):
    st = jload(STATE_FILE, {}); d = st.get("deploy", {})
    if "pod_id" in b:
        v = (b["pod_id"] or "").strip()
        if v and not re.fullmatch(r"[a-z0-9]{6,32}", v): return {"ok": False, "msg": "POD_ID inválido (letras minúsculas y números)"}
        d["pod_id"] = v
    if "app_port" in b:
        try: p = int(b["app_port"] or 0)
        except ValueError: return {"ok": False, "msg": "puerto inválido"}
        if p and not 1 <= p <= 65535: return {"ok": False, "msg": "puerto fuera de rango"}
        d["app_port"] = p
    st["deploy"] = d; jsave(STATE_FILE, st)
    return {"ok": True}

def public_url():
    d = deploy_cfg(); pid = os.environ.get("RUNPOD_POD_ID") or d.get("pod_id"); port = d.get("app_port")
    return (f"https://{pid}-{port}.proxy.runpod.net" if pid and port else None), pid, port

def deploy_check(full=False):
    """Lista de comprobaciones REALES para dejar un pod/VPS nuevo listo. Cada ítem: ok, detalle y cómo arreglarlo."""
    items = []
    def add(id_, label, ok, detail="", fix=""):
        items.append({"id": id_, "label": label, "ok": bool(ok), "detail": detail, "fix": fix})
    oi = ollama_info(); add("ollama", "Ollama responde", oi["up"], "" if oi["up"] else "no responde en " + OLLAMA, "bash tools/ollama-panel/deploy/bootstrap.sh")
    have = oi.get("models", [])
    for m, why in ((MODEL, "agente"), (THINK_MODEL, "razonar"), (VISION_MODEL, "imágenes")):
        add("model:" + m, f"Modelo {m} ({why})", m in have, "" if m in have else "no descargado", f"ollama pull {m}")
    g = gpu_info(); add("gpu", "GPU NVIDIA", bool(g), f"{g['name']} · {g['mem_total'] // 1024} GB" if g else "nvidia-smi no responde")
    try:
        mdir = Path(os.environ.get("OLLAMA_MODELS") or Path.home() / ".ollama" / "models"); dfm = subprocess.run(["df", "-P", str(mdir if mdir.exists() else mdir.parent)], capture_output=True, text=True).stdout.splitlines()[-1].split()
        persistent = dfm[5].startswith("/workspace") or "/workspace" in str(mdir)
        add("persist", "Modelos en volumen persistente", persistent, f"{mdir} en {dfm[5]} ({int(dfm[3]) // 1048576} GB libres)" + ("" if persistent else " · se pierden si recreas el pod"), "export OLLAMA_MODELS=/workspace/ollama (antes de arrancar Ollama)")
    except Exception as e:
        add("persist", "Modelos en volumen persistente", False, str(e)[:80])
    add("token", "Token de GitHub guardado", bool(token()), "" if token() else "falta", "botón 🔑 del panel")
    slug = git_info()["repo"]
    if token() and slug:
        try:
            r = _get_json(f"https://api.github.com/repos/{slug}", {"Authorization": f"Bearer {token()}"})
            add("gh_perm", f"Permiso de escritura en {slug}", (r.get("permissions") or {}).get("push", False), "", "token con permiso repo / Contents: write")
        except Exception as e:
            add("gh_perm", f"Acceso a GitHub ({slug})", False, str(e)[:80], "revisa el token o la conexión")
    rh, err = kit.remote_hash(BRANCH); add("branch", f"Rama de guardado «{BRANCH}» en GitHub", bool(rh), "" if rh else ("aún no existe (se crea en el primer guardado)" if rh == "" else err[:80]))
    _, cur = git("rev-parse", "--abbrev-ref", "HEAD"); add("on_branch", "Repositorio en la rama de guardado", cur.strip() == BRANCH, f"actual: {cur.strip()}", f"git checkout {BRANCH}")
    hook = REPO / ".git" / "hooks" / "pre-commit"; add("hook", "Hook anti-secretos instalado", hook.exists() and "panel-secret-scan" in hook.read_text(), "", "reinicia el panel")
    url, pid, port = public_url()
    add("pod_id", "POD_ID y puerto de la app configurados", bool(url), url or "indica POD_ID (consola de RunPod) y el puerto HTTP expuesto", "campos de abajo")
    if port:
        ls = subprocess.run(["ss", "-ltn"], capture_output=True, text=True).stdout
        add("port", f"Algo escucha en el puerto {port}", bool(re.search(rf":{port}\s", ls)), "", f"arranca la app con proc_start en el puerto {port}")
        if url and full:
            h = kit.http_probe(url, timeout=10)
            add("public", "URL pública responde", h["ok"], f"HTTP {h['status']}" if h["status"] else (h["error"] or ""), "comprueba que el puerto está en «HTTP Services» de RunPod")
    ok_all = all(i["ok"] for i in items if i["id"] not in ("persist", "branch", "public", "port", "pod_id", "on_branch"))
    return {"items": items, "ready": ok_all, "public_url": url, "pod_id": pid, "app_port": port, "branch": BRANCH}


def criteria_view(cid):
    ag = RUNS_AGENT.get(cid); run = RUNS.get(cid)
    if ag and run and run.status == "running": reqs = ag.reqs
    else: reqs = ((jload(conv_path(cid), {}) or {}).get("run") or {}).get("reqs", [])
    return [{"index": i, "kind": r["kind"], "status": kit.rstat(r), "text": r["text"], "reason": r.get("reason", "")} for i, r in enumerate(reqs)]

def criteria_op(cid, action, idx=None, text=None):
    """Actualizar / sustituir / retirar / reactivar criterios de aceptación (también con la tarea en curso). No borra nada: retirar es reversible."""
    conv = jload(conv_path(cid), None)
    if not conv: return {"ok": False, "msg": "conversación inexistente"}
    run = RUNS.get(cid); live = RUNS_AGENT.get(cid) if (run and run.status == "running") else None
    ag = live or kit.Agent(conv, lambda e: None, threading.Event(), legacy_exec)
    msg = ""
    if action == "retire": ok = ag.retire(int(idx), "retirado por el usuario"); msg = "criterio retirado" if ok else "índice inválido"
    elif action == "reactivate": ok = ag.reactivate(int(idx)); msg = "criterio reactivado" if ok else "índice inválido"
    elif action == "clear": n = ag.clear_blocking(); ok = True; msg = f"{n} criterios retirados: ya no bloquean (reactivables)"
    elif action in ("add", "replace"):
        if not (text or "").strip(): return {"ok": False, "msg": "texto vacío"}
        if action == "replace" and idx is not None: ag.retire(int(idx), "sustituido por el usuario")
        new = ag.on_user_message(text, steer=True); ok = True; msg = f"{len(new)} criterio(s) nuevo(s)" + ("; " + "; ".join(ag.change_notes) if ag.change_notes else "")
    else: return {"ok": False, "msg": "acción desconocida"}
    if not live:
        conv["run"] = {**(conv.get("run") or {}), "reqs": ag.reqs}; jsave(conv_path(cid), conv)
    return {"ok": ok, "msg": msg, "criteria": criteria_view(cid)}

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
                return self._json({"clock": pod_clock(), "gpu": gpu_info(), "ollama": ollama_info(), "git": git_info(), "ram": ram_info(),
                                   "model": MODEL, "search": bool(search_key()), "tps": LAST_SPEED["tps"], "num_ctx": NUM_CTX,
                                   "runs": [k for k, r in RUNS.items() if r.status == "running"]})
            if path == "/api/metrics":
                return self._json(metrics())
            m = re.fullmatch(r"/api/run/([a-f0-9]+)", path)
            if m:
                r = RUNS.get(m.group(1)); ag = RUNS_AGENT.get(m.group(1))
                return self._json({"active": bool(r and r.status == "running"), "base": r.base if r else 0, "status": ag.status() if ag else None,
                                   "run": (jload(conv_path(m.group(1)), {}) or {}).get("run")})
            m = re.fullmatch(r"/api/runs/([a-f0-9]+)", path)
            if m:
                from urllib.parse import parse_qs
                r = RUNS.get(m.group(1))
                if not r: return self._json({"status": "none"})
                return self.stream_run(r, int(parse_qs(urlparse(self.path).query).get("from", ["0"])[0]))
            if path == "/api/criteria":
                from urllib.parse import parse_qs
                return self._json({"criteria": criteria_view(parse_qs(urlparse(self.path).query).get("id", [""])[0])})
            if path == "/api/git/verify":
                return self._json(git_verify())
            if path == "/api/deploy/check":
                from urllib.parse import parse_qs
                return self._json(deploy_check(full=parse_qs(urlparse(self.path).query).get("full", ["0"])[0] == "1"))
            if path == "/api/conversations":
                items = [jload(p, {}) for p in CONV_DIR.glob("*.json")]
                items = sorted([c for c in items if c], key=lambda c: -c.get("updated", 0))
                return self._json([{"id": c["id"], "title": c["title"], "updated": c["updated"], "n": sum(1 for m in c.get("messages", []) if m.get("role") == "user" and not m.get("hidden")), "state": (c.get("run") or {}).get("status")} for c in items])
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
            if path == "/api/criteria":
                return self._json(criteria_op(b.get("id", ""), b.get("action", ""), b.get("index"), b.get("text")))
            if path == "/api/steer":
                r = RUNS.get(b.get("id")); t = (b.get("message") or "").strip()
                if not t: return self._json({"ok": False, "msg": "mensaje vacío"}, 400)
                if not (r and r.status == "running"): return self._json({"ok": False, "msg": "no hay una tarea en curso: envíalo como mensaje normal"})
                r.steer.append(t[:8000]); return self._json({"ok": True, "queued": len(r.steer)})
            if path == "/api/resume":
                return self.chat({**b, "resume": True})
            if path == "/api/config":
                return self._json(set_config(b))
            if path == "/api/deploy/config":
                return self._json(set_deploy(b))
            if path == "/api/git/integrate":
                return self._json(git_integrate(b.get("target")))
            if path == "/api/git/push":
                return self._json(git_save(b.get("message") or "pod: guardado manual desde el panel", push=True))
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
                r = kit.run_cmd(b.get("command", ""), timeout=int(b.get("timeout", 120)))
                return self._json({"code": r["code"], "output": clip(kit.fmt_result(r))})
            self._json({"error": "no encontrado"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def stream_run(self, run, start=0):
        """Emite los eventos de una tarea por SSE. Si el navegador se desconecta, la tarea CONTINÚA (se puede reenganchar)."""
        try:
            self.send_response(200)
            for k, v in {"Content-Type": "text/event-stream", "Cache-Control": "no-cache", "Connection": "close"}.items():
                self.send_header(k, v)
            self.end_headers(); self.close_connection = True
            i = start
            while True:
                with run.cond:
                    if i >= len(run.events) and run.status == "running":
                        run.cond.wait(15)
                    batch = run.events[i:]; i += len(batch)
                    finished = run.status != "running" and i >= len(run.events)
                if batch:
                    self.wfile.write(b"".join(b"data: " + json.dumps(ev, ensure_ascii=False).encode() + b"\n\n" for ev in batch))
                else:
                    self.wfile.write(b": ping\n\n")
                self.wfile.flush()
                if finished:
                    return
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    def chat(self, b):
        conv = jload(conv_path(b["id"]), None) or new_conv()
        text = (b.get("message") or "").strip()
        if not text and not b.get("attachments") and not b.get("resume"):
            return self._json({"error": "mensaje vacío"}, 400)
        run = RUNS.get(conv["id"])
        if not (run and run.status == "running"):
            run = Run(conv["id"]); RUNS[conv["id"]] = run; STOPS[conv["id"]] = run.stop
            run.base = len(conv["messages"])
            for k in [k for k, r in RUNS.items() if r.status != "running"][:-8]: RUNS.pop(k, None)
            threading.Thread(target=run_worker, args=(run, conv, b), daemon=True).start()
        self.stream_run(run, 0)

apply_config()

if __name__ == "__main__":
    if not os.environ.get("PANEL_TEST"):     # la instancia de prueba del despliegue NO debe tocar el repositorio (cambiaba de rama y reescribía el código)
        mark_interrupted(); install_hooks()
        ensure_branch()
    host, port = os.environ.get("PANEL_HOST", "127.0.0.1"), int(os.environ.get("PANEL_PORT", "8787"))
    print(f"Panel del Pod en http://{host}:{port}  ·  modelo {MODEL}  ·  workdir {WORKDIR}  ·  rama {BRANCH}")
    ThreadingHTTPServer((host, port), H).serve_forever()
