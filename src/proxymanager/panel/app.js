"use strict";
// Todo el contenido dinámico se inserta con textContent: solo textContent y nodos DOM.
const $ = (id) => document.getElementById(id);
let key = "";
try { key = sessionStorage.getItem("pm_key") || ""; } catch (e) { /* sin almacenamiento */ }

function el(tag, text, cls) { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; }
function say(text, cls) { const m = $("msg"); m.textContent = text || ""; m.className = cls || ""; }
function num(n, d) { return n === null || n === undefined ? "–" : Number(n).toFixed(d === undefined ? 0 : d); }
function ms(n) { return n === null || n === undefined ? "–" : Math.round(n) + " ms"; }
function pct(n) { return n === null || n === undefined ? "–" : (n * 100).toFixed(n === 1 || n === 0 ? 0 : 1) + " %"; }
function bytes(n) { n = n || 0; return n < 1024 ? n + " B" : n < 1e6 ? (n / 1024).toFixed(1) + " KB" : n < 1e9 ? (n / 1e6).toFixed(2) + " MB" : (n / 1e9).toFixed(2) + " GB"; }
function when(ts) { return ts ? new Date(ts * 1000).toLocaleString() : "nunca"; }
function chip(text, kind) { return el("span", text, "chip " + (kind || "muted")); }
function cell(...kids) { const td = el("td"); td.append(...kids); return td; }
function emptyRow(body, cols, text) { const tr = el("tr"), td = el("td", text, "muted"); td.colSpan = cols; tr.append(td); body.append(tr); }
function metric(label, value, sub) {
  const box = el("div", undefined, "metric");
  box.append(el("div", label, "label"), el("div", value, "value"), el("div", sub || "", "sub"));
  return box;
}

async function api(path, options) {
  const res = await fetch(path, { ...(options || {}), headers: { "X-API-Key": key, "Content-Type": "application/json" } });
  let body = null;
  try { body = await res.json(); } catch (e) { /* vacío */ }
  if (!res.ok) {
    const detail = body && typeof body.detail === "string" ? body.detail : "Error " + res.status;
    const err = new Error(res.status === 429 ? "Demasiadas solicitudes; espera un momento." : detail); err.status = res.status; throw err;
  }
  return body;
}
function denied(e) { return e && e.status === 403 ? "Esta clave no tiene permiso para esta sección." : (e && e.message) || "Error"; }

/* ---------- navegación ---------- */
const OUTCOME_LABEL = { success: "Correctas", challenge: "Desafío / CAPTCHA", blocked: "Bloqueadas (403/429)", unexpected_response: "Respuesta inesperada", transport_error: "Error de transporte" };
const VIEWS = {
  overview: ["Resumen", () => loadOverview()], proxies: ["Proxies", () => loadProxies()], sessions: ["Sesiones", () => loadSessions()],
  bench: ["Benchmarks", () => loadRuns()], keys: ["Claves API", () => loadKeys()], playground: ["Playground", () => loadPlayground()],
  usage: ["Uso", () => loadUsage()], expenses: ["Gastos", () => loadExpenses()], audit: ["Auditoría", () => loadAudit()],
};
let current = "overview";

async function show(view) {
  if (!VIEWS[view]) view = "overview";
  current = view;
  for (const b of document.querySelectorAll(".nav-item")) { if (b.dataset.view === view) b.setAttribute("aria-current", "page"); else b.removeAttribute("aria-current"); }
  for (const v of Object.keys(VIEWS)) $("view-" + v).classList.toggle("hidden", v !== view);
  $("page-title").textContent = VIEWS[view][0];
  document.title = VIEWS[view][0] + " · ProxyManager";
  try { history.replaceState(null, "", "#" + view); } catch (e) { /* sin historial */ }
  say(""); hideNewKey();
  try { await VIEWS[view][1](); } catch (e) { say(denied(e), "bad"); }
}

function setLogged(on) { $("login-screen").classList.toggle("hidden", on); $("shell").classList.toggle("hidden", !on); }

/* ---------- Resumen ---------- */
async function loadOverview() {
  const [ov, us, ex] = await Promise.allSettled([api("/v1/overview"), api("/v1/usage?days=14"), api("/v1/expenses")]);
  if ([ov, us, ex].every((r) => r.status === "rejected")) throw ov.reason;
  const grid = $("metrics"); grid.replaceChildren();
  const o = ov.status === "fulfilled" ? ov.value : null, u = us.status === "fulfilled" ? us.value : null, x = ex.status === "fulfilled" ? ex.value : null;
  grid.append(
    metric("Solicitudes hoy", u ? String(u.today.requests) : "–", u ? u.totals.requests + " en " + u.days + " días" : "Sin permiso de uso"),
    metric("Éxito", u ? pct(u.totals.success_rate) : "–", "contenido esperado recibido"),
    metric("Latencia p95", u ? ms(u.totals.p95_ms) : "–", u ? "media " + ms(u.totals.avg_ms) : ""),
    metric("Concurrencia", o ? String(o.concurrency.current) : "–", o ? "límite " + o.concurrency.per_proxy_limit + " por proxy" : "Sin permiso"),
    metric("Proxies", o ? o.healthy + " / " + o.total : "–", "responden (transporte)"),
    metric("Bloqueos (24 h)", o ? String(o.proxies.reduce((a, p) => a + p.delivery_24h.blocked, 0)) : "–", o ? "de " + o.proxies.reduce((a, p) => a + p.delivery_24h.requests, 0) + " solicitudes con proxy" : ""),
    metric("Tráfico del mes", o ? bytes(o.traffic_month_bytes) : "–", o ? (o.estimated_proxy_cost_usd === null ? "coste: define PROXYMANAGER_PROXY_COST_PER_GB_USD" : "≈ " + o.estimated_proxy_cost_usd.toFixed(2) + " USD (estimación)") : ""),
    metric("Gasto del mes", x ? x.spent_usd.toFixed(2) + " USD" : "–", x ? "de " + x.budget_usd.toFixed(2) + " USD" : "Sin permiso de gastos"),
  );
  drawRequests($("ov-requests"), u); drawLatency($("ov-latency"), u);
  const split = $("ov-split"); split.replaceChildren();
  if (o) {
    const t = el("div"); t.append(el("span", "Transporte", "muted"), el("strong", o.healthy + " de " + o.total + " proxies responden"), el("span", "El proxy devolvió una respuesta HTTP.", "muted small"));
    const d = el("div"), tot = u ? u.totals.requests : 0;
    d.append(el("span", "Entrega", "muted"), el("strong", u && tot ? pct(u.totals.success_rate) + " correctas" : "Sin datos"), el("span", u && tot ? "Bloqueo/desafío: " + (u.outcomes.challenge + u.outcomes.blocked) + " · error de red: " + u.outcomes.transport_error + " · otras: " + u.outcomes.unexpected_response : "Aún no hay solicitudes registradas.", "muted small"));
    split.append(t, d);
  } else split.append(el("p", "Sin permiso para ver proxies.", "empty"));
}

const EMPTY_USAGE = "Aún no hay solicitudes. Lanza una en el Playground o ejecuta comprobaciones en Proxies.";
function drawRequests(box, u) {
  if (!u) { box.replaceChildren(el("p", "Sin permiso de uso.", "empty")); return; }
  const d = u.daily;
  PM.stackedBars(box, d.map((x) => x.date), [
    { name: "Correctas", cls: "bar-ok", values: d.map((x) => x.outcomes.success) },
    { name: "Bloqueo / desafío", cls: "bar-block", values: d.map((x) => x.outcomes.challenge + x.outcomes.blocked) },
    { name: "Error de transporte", cls: "bar-err", values: d.map((x) => x.outcomes.transport_error) },
    { name: "Otras", cls: "bar-other", values: d.map((x) => x.outcomes.unexpected_response) },
  ], { label: "Solicitudes por día", empty: EMPTY_USAGE });
}
function drawLatency(box, u) {
  if (!u) { box.replaceChildren(el("p", "Sin permiso de uso.", "empty")); return; }
  const d = u.daily;
  PM.lines(box, d.map((x) => x.date), [{ name: "p95", cls: "l1", values: d.map((x) => x.p95_ms) }, { name: "Media", cls: "l2", values: d.map((x) => x.avg_ms) }], { label: "Latencia por día", unit: " ms", empty: EMPTY_USAGE });
}

/* ---------- Proxies ---------- */
async function loadProxies() {
  const data = await api("/v1/overview");
  if (!$("checkurl").value && data.allowed_hosts.length) $("checkurl").placeholder = "https://" + data.allowed_hosts[0] + "/";
  const body = $("proxies"); body.replaceChildren();
  $("proxies-empty").classList.toggle("hidden", data.proxies.length > 0);
  for (const p of data.proxies) {
    const s = p.stats, d = p.delivery_24h, tr = el("tr");
    tr.append(cell(el("span", p.provider + " :" + p.port, "mono")), el("td", p.country, "col-hide"));
    tr.append(cell(chip(s.healthy ? "sano" : (s.events ? "degradado" : "sin datos"), s.healthy ? "ok" : (s.events ? "bad" : "muted")), document.createTextNode(s.success_rate === null ? "" : " " + Math.round(s.success_rate * 100) + " % (" + s.events + ")")));
    let delivery;
    if (!d.requests) delivery = chip("sin datos", "muted");
    else if (d.success === 0 && d.blocked > 0) delivery = chip("bloqueado " + d.blocked + "/" + d.requests, "bad");
    else if (d.blocked > 0) delivery = chip("parcial " + d.success + "/" + d.requests, "warn");
    else if (d.success > 0) delivery = chip("correcta " + d.success + "/" + d.requests, "ok");
    else delivery = chip("solo errores de red", "muted");
    tr.append(cell(delivery), el("td", ms(s.avg_duration_ms), "col-hide"), el("td", bytes(p.traffic_month_bytes), "col-hide"));
    const td = el("td"), b = el("button", "Comprobar", "btn");
    b.addEventListener("click", () => runCheck(p.id, b));
    const h = el("button", "Historial", "btn"); h.addEventListener("click", () => toggleHistory(p.id, tr, h));
    td.append(b, " ", h); tr.append(td); body.append(tr);
  }
}
async function toggleHistory(id, row, button) {
  const next = row.nextElementSibling;
  if (next && next.classList.contains("detail")) { next.remove(); return; }
  button.disabled = true;
  try {
    const items = (await api("/v1/proxies/" + id + "/checks")).slice(0, 8);
    const tr = el("tr", undefined, "detail"), td = el("td"); td.colSpan = 7;
    if (!items.length) td.textContent = "Sin comprobaciones todavía.";
    for (const c of items) td.append(el("div", new Date(c.created_at * 1000).toLocaleTimeString() + " · " + c.state + " · " + (c.success ? "OK" : "fallo") + " · " + (c.status_code || "–") + " · " + ms(c.duration_ms) + (c.error ? " · " + c.error.type : ""), c.success ? "ok" : "bad"));
    tr.append(td); row.after(tr);
  } catch (e) { say(e.message, "bad"); } finally { button.disabled = false; }
}
async function runCheck(id, button) {
  const url = $("checkurl").value.trim();
  if (!url) { say("Indica una URL de comprobación.", "warn"); return; }
  button.disabled = true;
  try { await api("/v1/proxies/" + id + "/checks", { method: "POST", body: JSON.stringify({ url }) }); say("Comprobación en cola; actualiza en unos segundos.", "ok"); }
  catch (e) { say(e.message, "bad"); } finally { button.disabled = false; }
}
async function addProxy() {
  const payload = { provider: $("p-provider").value.trim(), host: $("p-host").value.trim(), port: parseInt($("p-port").value, 10), country: $("p-country").value.trim().toUpperCase(), kind: $("p-kind").value };
  if ($("p-user").value) payload.username = $("p-user").value;
  if ($("p-pass").value) payload.password = $("p-pass").value;
  try { await api("/v1/proxies", { method: "POST", body: JSON.stringify(payload) }); say("Proxy guardado (credenciales cifradas).", "ok"); await loadProxies(); }
  catch (e) { say(e.status === 403 ? "Esta clave no puede añadir proxies." : e.message, "bad"); }
  finally { $("p-pass").value = ""; $("p-user").value = ""; }
}
async function importBatch() {
  const text = $("i-text").value;
  try {
    const r = await api("/v1/proxies/import", { method: "POST", body: JSON.stringify({ provider: $("i-provider").value.trim(), text }) });
    say("Importadas: " + r.added + " · duplicadas omitidas: " + r.duplicates_skipped + " · total: " + r.total, "ok"); await loadProxies();
  } catch (e) { say(e.status === 403 ? "Esta clave no puede importar proxies." : e.message, "bad"); }
  finally { $("i-text").value = ""; }
}

/* ---------- Sesiones ---------- */
async function loadSessions() {
  const items = await api("/v1/sessions"), body = $("sessions"); body.replaceChildren();
  if (!items.length) emptyRow(body, 4, "No tienes sesiones activas.");
  for (const item of items) {
    const tr = el("tr"), actions = el("td"), remove = el("button", "Borrar sesión", "btn");
    remove.setAttribute("aria-label", "Borrar sesión " + item.session_id);
    remove.addEventListener("click", async () => {
      if (!window.confirm("¿Borrar esta sesión y sus cookies?")) return;
      remove.disabled = true;
      try { await api("/v1/sessions/" + encodeURIComponent(item.session_id), { method: "DELETE" }); await loadSessions(); say("Sesión borrada.", "ok"); }
      catch (e) { remove.disabled = false; say(e.message, "bad"); }
    });
    actions.append(remove);
    tr.append(el("td", item.session_id, "mono"), el("td", new Date(item.created_at * 1000).toLocaleString()), el("td", new Date(item.expires_at * 1000).toLocaleString()), actions);
    body.append(tr);
  }
}
async function createSession() {
  try { await api("/v1/sessions", { method: "POST" }); await loadSessions(); say("Sesión creada.", "ok"); } catch (e) { say(e.message, "bad"); }
}

/* ---------- Benchmarks ---------- */
let benchActive = false;
async function loadRuns() {
  const runs = await api("/v1/benchmarks"), body = $("runs"); body.replaceChildren();
  benchActive = runs.some((r) => r.state === "queued" || r.state === "running");
  if (!runs.length) emptyRow(body, 6, "Aún no hay benchmarks.");
  for (const r of runs) {
    const s = r.summary || {}, tr = el("tr");
    tr.append(el("td", r.id.slice(0, 12), "mono"));
    tr.append(cell(chip(r.state + (s.stopped_because ? " (" + s.stopped_because + ")" : ""), r.state === "completed" ? "ok" : (r.state === "failed" ? "bad" : "muted"))));
    tr.append(el("td", (s.completed || 0) + " / " + r.params.requests));
    tr.append(el("td", Object.entries(s.outcomes || {}).map(([k, v]) => (OUTCOME_LABEL[k] || k) + ": " + v).join(" · ") || "–"));
    tr.append(el("td", s.latency_ms ? num(s.latency_ms.p50) + " / " + num(s.latency_ms.p95) : "–"));
    const td = el("td");
    if (r.state === "queued" || r.state === "running") {
      const b = el("button", "Cancelar", "btn"); b.addEventListener("click", async () => { try { await api("/v1/benchmarks/" + r.id + "/cancel", { method: "POST" }); await loadRuns(); } catch (e) { say(e.message, "bad"); } });
      td.append(b);
    }
    tr.append(td); body.append(tr);
  }
}
async function startBench() {
  const rps = parseFloat($("b-rps").value);
  const payload = { url: $("b-url").value.trim(), requests: parseInt($("b-req").value, 10), concurrency: parseInt($("b-con").value, 10), use_proxy: true };
  if (rps > 0) payload.rps = rps;
  if (!window.confirm("¿Lanzar " + payload.requests + " solicitudes contra " + payload.url + "? Confirma que el destino es tuyo o está autorizado.")) return;
  try { await api("/v1/benchmarks", { method: "POST", body: JSON.stringify(payload) }); say("Benchmark en cola.", "ok"); await loadRuns(); } catch (e) { say(e.message, "bad"); }
}

/* ---------- Claves API ---------- */
const KEY_SCOPES = ["system:read", "sessions", "scrape", "proxies:read", "proxies:write", "checks:write", "bench:read", "bench:write", "usage:read", "expenses:read", "expenses:write", "audit:read"];
function buildScopeBoxes() {
  const box = $("k-scopes");
  for (const sc of KEY_SCOPES) { const label = el("label"), input = el("input"); input.type = "checkbox"; input.value = sc; label.append(input, document.createTextNode(sc)); box.append(label); }
}
function hideNewKey() { $("k-value").value = ""; $("k-value").type = "password"; $("k-toggle").textContent = "Mostrar"; $("k-toggle").setAttribute("aria-pressed", "false"); $("k-new").classList.add("hidden"); }
async function loadKeys() {
  const keys = await api("/v1/keys"), body = $("keys"); body.replaceChildren();
  if (!keys.length) emptyRow(body, 6, "Aún no has creado claves adicionales.");
  for (const k of keys) {
    const tr = el("tr"), state = { active: "activa", revoked: "revocada", expired: "caducada" }[k.state] || k.state;
    tr.append(el("td", k.name), el("td", k.hint, "mono"), cell(chip(state, k.state === "active" ? "ok" : "muted")), el("td", k.scopes.join(", ")), el("td", when(k.last_used_at)));
    const td = el("td");
    if (k.state === "active") {
      const b = el("button", "Revocar", "btn");
      b.addEventListener("click", async () => { if (!window.confirm("¿Revocar «" + k.name + "»? Dejará de funcionar de inmediato.")) return; try { await api("/v1/keys/" + k.id, { method: "DELETE" }); await loadKeys(); } catch (e) { say(e.message, "bad"); } });
      td.append(b);
    }
    tr.append(td); body.append(tr);
  }
}
async function createKey() {
  const scopes = [...document.querySelectorAll("#k-scopes input:checked")].map((i) => i.value);
  const payload = { name: $("k-name").value, scopes };
  if ($("k-days").value) payload.expires_days = parseFloat($("k-days").value);
  try {
    const made = await api("/v1/keys", { method: "POST", body: JSON.stringify(payload) });
    $("k-value").value = made.key; $("k-value").type = "password"; $("k-new").classList.remove("hidden"); $("k-name").value = ""; $("k-days").value = "";
    for (const i of document.querySelectorAll("#k-scopes input")) i.checked = false;
    say("Clave creada. Cópiala ahora.", "ok"); await loadKeys();
  } catch (e) { say(e.status === 403 ? "Solo la clave de administración puede gestionar claves." : e.message, "bad"); }
}
function toggleKey() { const show = $("k-value").type === "password"; $("k-value").type = show ? "text" : "password"; $("k-toggle").textContent = show ? "Ocultar" : "Mostrar"; $("k-toggle").setAttribute("aria-pressed", String(show)); }
async function copyText(text, okMsg) { try { await navigator.clipboard.writeText(text); say(okMsg || "Copiado.", "ok"); } catch (e) { say("No se pudo copiar automáticamente.", "warn"); } }

/* ---------- Playground ---------- */
let pg = { lang: "curl", sessionId: null, body: "", system: null };
function pgPayload() {
  const p = { url: $("pg-url").value.trim() || "https://host-permitido/ruta", use_proxy: $("pg-proxy").checked };
  if ($("pg-geo").checked && $("pg-country").value.trim()) p.country = $("pg-country").value.trim().toUpperCase();
  if (pg.sessionId) p.session_id = pg.sessionId;
  return p;
}
function pyLiteral(v) { return v === true ? "True" : v === false ? "False" : JSON.stringify(v); }
function renderCode() {
  const p = pgPayload(), base = window.location.origin;
  let text;
  if (pg.lang === "python") {
    text = "import os\nimport requests\n\nresponse = requests.post(\n    \"" + base + "/scrape\",\n    headers={\"X-API-Key\": os.environ[\"PROXYMANAGER_API_KEY\"]},\n    json={" + Object.entries(p).map(([k, v]) => JSON.stringify(k) + ": " + pyLiteral(v)).join(", ") + "},\n    timeout=90,\n)\nresult = response.json()\nprint(response.status_code, result.get(\"status_code\"), result.get(\"proxy_id\"))";
  } else if (pg.lang === "node") {
    text = "const response = await fetch(\"" + base + "/scrape\", {\n  method: \"POST\",\n  headers: {\n    \"X-API-Key\": process.env.PROXYMANAGER_API_KEY,\n    \"Content-Type\": \"application/json\",\n  },\n  body: JSON.stringify(" + JSON.stringify(p, null, 2).split("\n").join("\n  ") + "),\n});\nconst result = await response.json();\nconsole.log(response.status, result.status_code, result.proxy_id);";
  } else {
    text = "curl -X POST '" + base + "/scrape' \\\n  -H \"X-API-Key: $PROXYMANAGER_API_KEY\" \\\n  -H 'Content-Type: application/json' \\\n  --max-time 90 \\\n  -d '" + JSON.stringify(p).replace(/'/g, "'\\''") + "'";
  }
  $("pg-code").textContent = text;
}
function classifyResult(r) {
  if (r.success) return "success";
  if (r.status_code === null || r.status_code === undefined) return "transport_error";
  if (r.validation && r.validation.challenge_detected) return "challenge";
  if ([401, 403, 429].includes(r.status_code)) return "blocked";
  return "unexpected_response";
}
const CALLOUT = {
  success: ["good", "Contenido esperado recibido."],
  challenge: ["", "El proxy respondió (transporte correcto), pero el sitio devolvió un desafío o protección anti-bots. ProxyManager lo detecta; no lo resuelve ni lo esquiva."],
  blocked: ["", "El proxy respondió (transporte correcto), pero el sitio rechazó la solicitud."],
  transport_error: ["err", "No hubo respuesta HTTP: fallo de transporte (proxy, red o TLS). Se puede reintentar con otro proxy."],
  unexpected_response: ["", "El sitio respondió, pero no con el contenido esperado."],
};
function showResponse(payload, r, errorText) {
  $("pg-empty").classList.add("hidden"); $("pg-resp").classList.remove("hidden");
  const kind = errorText ? "error" : classifyResult(r);
  const status = $("pg-status");
  status.textContent = errorText ? "Error" : (r.status_code ? "HTTP " + r.status_code : "Sin respuesta");
  status.className = "chip " + (kind === "success" ? "ok" : kind === "error" || kind === "transport_error" ? "bad" : "warn");
  $("pg-url-shown").textContent = "GET " + payload.url;
  const meta = $("pg-meta"); meta.replaceChildren();
  const callout = $("pg-callout");
  if (errorText) {
    callout.className = "callout err"; callout.textContent = errorText;
    $("pg-body").textContent = ""; $("pg-body-info").textContent = "Sin cuerpo"; $("pg-details").textContent = ""; pg.body = "";
    return;
  }
  meta.append(el("span", "Duración " + ms(r.duration_ms)), el("span", "Tamaño " + bytes(r.bytes_transferred)), el("span", r.content_type || "tipo desconocido"),
    el("span", r.proxy_id ? "Proxy " + r.proxy_id.slice(0, 12) : "Sin proxy (directo)"), el("span", "Intentos " + r.attempts));
  const rid = el("button", "Id " + r.request_id.slice(0, 12)); rid.type = "button"; rid.title = "Copiar el id de solicitud"; rid.addEventListener("click", () => copyText(r.request_id, "Id copiado."));
  meta.append(rid);
  const [tone, text] = CALLOUT[kind]; callout.className = "callout " + tone; callout.textContent = text;
  pg.body = r.html || "";
  const LIMIT = 20000;
  $("pg-body").textContent = pg.body.slice(0, LIMIT);
  $("pg-body-info").textContent = pg.body ? (pg.body.length > LIMIT ? "Mostrando " + LIMIT.toLocaleString() + " de " + pg.body.length.toLocaleString() + " caracteres" : pg.body.length.toLocaleString() + " caracteres") : "Sin cuerpo";
  const { html, ...rest } = r;
  $("pg-details").textContent = JSON.stringify(rest, null, 2) + "\n\n(Las cookies de sesión se guardan cifradas y no se devuelven; el cuerpo completo no se muestra aquí.)";
}
async function runPlayground(ev) {
  if (ev) ev.preventDefault();
  const payload = pgPayload();
  if (!$("pg-url").value.trim()) { say("Indica una URL de destino.", "warn"); return; }
  $("pg-run").disabled = true; $("pg-run").textContent = "Ejecutando…"; say("");
  const abort = new AbortController(), timer = setTimeout(() => abort.abort(), 90000);
  try {
    const res = await fetch("/scrape", { method: "POST", headers: { "X-API-Key": key, "Content-Type": "application/json" }, body: JSON.stringify(payload), signal: abort.signal });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) showResponse(payload, null, res.status === 429 ? "Demasiadas solicitudes; espera un momento." : (typeof data.detail === "string" ? data.detail : "Error " + res.status) + (res.status === 403 ? " (esta clave necesita el permiso scrape)" : ""));
    else showResponse(payload, data);
  } catch (e) { showResponse(payload, null, e.name === "AbortError" ? "Tiempo de espera agotado (90 s)." : "No se pudo conectar con la API."); }
  finally { clearTimeout(timer); $("pg-run").disabled = false; $("pg-run").textContent = "Ejecutar"; }
}
async function loadPlayground() {
  renderCode();
  try {
    pg.system = await api("/v1/system");
    $("pg-timeout").textContent = pg.system.timeout_seconds + " s"; $("pg-maxbytes").textContent = bytes(pg.system.max_response_bytes); $("pg-attempts").textContent = String(pg.system.scrape_proxy_attempts);
  } catch (e) { /* sin system:read: se deja "–" */ }
}
function pgExample() {
  const hosts = pg.system ? pg.system.allowed_hosts : [];
  if (!hosts.length) { say("No hay hosts permitidos configurados en el servidor.", "warn"); return; }
  $("pg-url").value = "https://" + hosts[0] + "/"; renderCode();
}
async function pgSticky() {
  if (!$("pg-sticky").checked) { pg.sessionId = null; $("pg-session").classList.add("hidden"); renderCode(); return; }
  try { const s = await api("/v1/sessions", { method: "POST" }); pg.sessionId = s.session_id; $("pg-session").textContent = "Sesión " + s.session_id.slice(0, 16) + "… (reutiliza proxy y cookies)"; $("pg-session").classList.remove("hidden"); }
  catch (e) { $("pg-sticky").checked = false; say(e.status === 403 ? "Esta clave no puede crear sesiones." : e.message, "bad"); }
  renderCode();
}
function selectTab(group, attr, value, onSelect) {
  for (const t of group) t.setAttribute("aria-selected", String(t.dataset[attr] === value));
  onSelect(value);
}

/* ---------- Uso ---------- */
async function loadUsage() {
  const u = await api("/v1/usage?days=" + $("u-days").value);
  const t = $("u-totals"); t.replaceChildren();
  t.append(metric("Solicitudes", String(u.totals.requests), "en " + u.days + " días"), metric("Éxito", pct(u.totals.success_rate), "contenido esperado"), metric("Latencia p95", ms(u.totals.p95_ms), "media " + ms(u.totals.avg_ms)), metric("Cuerpos recibidos", bytes(u.totals.bytes), "sin cabeceras ni TLS"));
  drawRequests($("u-requests"), u); drawLatency($("u-latency"), u);
  PM.hbars($("u-domains"), u.domains.map((d) => ({ label: d.host, value: d.requests, text: d.requests + " · " + pct(d.success_rate) + " ok" })), { empty: EMPTY_USAGE });
  PM.hbars($("u-outcomes"), Object.entries(u.outcomes).filter(([, n]) => n > 0).map(([k, n]) => ({ label: OUTCOME_LABEL[k] || k, value: n, text: String(n) })), { empty: EMPTY_USAGE });
}

/* ---------- Gastos y auditoría ---------- */
async function loadExpenses() {
  const d = await api("/v1/expenses");
  $("exp-month").textContent = "· " + d.month;
  $("exp-summary").textContent = "Gastado " + d.spent_usd.toFixed(2) + " de " + d.budget_usd.toFixed(2) + " USD · " + (d.over_budget ? "presupuesto superado en " + Math.abs(d.remaining_usd).toFixed(2) : "quedan " + d.remaining_usd.toFixed(2)) + " USD";
  $("exp-summary").className = d.over_budget ? "bad" : "";
  $("exp-bar").max = d.budget_usd || 1; $("exp-bar").value = Math.min(d.spent_usd, d.budget_usd || 1);
  const body = $("expenses"); body.replaceChildren();
  if (!d.entries.length) emptyRow(body, 3, "Sin gastos anotados este mes.");
  for (const e of d.entries) { const tr = el("tr"); tr.append(el("td", new Date(e.at * 1000).toLocaleDateString()), el("td", e.concept), el("td", e.amount_usd.toFixed(2))); body.append(tr); }
}
async function addExpense() {
  try { await api("/v1/expenses", { method: "POST", body: JSON.stringify({ concept: $("e-concept").value, amount_usd: parseFloat($("e-amount").value) }) }); $("e-concept").value = ""; $("e-amount").value = ""; await loadExpenses(); say("Gasto anotado.", "ok"); }
  catch (e) { say(e.message, "bad"); }
}
async function loadAudit() {
  const events = await api("/v1/audit?limit=50"), body = $("events"); body.replaceChildren();
  if (!events.length) emptyRow(body, 4, "Sin eventos todavía.");
  for (const e of events) { const tr = el("tr"); tr.append(el("td", new Date(e.at * 1000).toLocaleString()), el("td", e.method), el("td", e.route, "mono"), cell(chip(String(e.status), e.status >= 400 ? "bad" : "ok"))); body.append(tr); }
}

/* ---------- arranque ---------- */
async function enter(ev) {
  if (ev) ev.preventDefault();
  key = $("key").value.trim(); $("key").value = "";
  try { await api("/v1/system"); } catch (e) { $("login-msg").textContent = e.status === 401 ? "Clave inválida." : e.message; key = ""; return; }
  $("login-msg").textContent = "";
  try { sessionStorage.setItem("pm_key", key); } catch (e) { /* sin almacenamiento */ }
  setLogged(true); await show((location.hash || "").slice(1) || "overview");
}
for (const n of document.querySelectorAll("[data-icon]")) n.prepend(PM.icon(n.dataset.icon));
$("pg-empty-icon").append(PM.icon("globe"));
buildScopeBoxes();
$("login-form").addEventListener("submit", enter);
$("logout").addEventListener("click", () => { key = ""; try { sessionStorage.removeItem("pm_key"); } catch (e) { /* nada */ } hideNewKey(); pg = { lang: pg.lang, sessionId: null, body: "", system: null }; setLogged(false); say(""); });
$("refresh").addEventListener("click", () => show(current));
for (const b of document.querySelectorAll(".nav-item")) b.addEventListener("click", () => show(b.dataset.view));
$("p-add").addEventListener("click", addProxy); $("i-add").addEventListener("click", importBatch);
$("s-create").addEventListener("click", createSession); $("b-start").addEventListener("click", startBench);
$("k-create").addEventListener("click", createKey); $("k-toggle").addEventListener("click", toggleKey); $("k-copy").addEventListener("click", () => copyText($("k-value").value, "Clave copiada."));
$("e-add").addEventListener("click", addExpense); $("u-days").addEventListener("change", () => loadUsage().catch((e) => say(denied(e), "bad")));
$("pg-form").addEventListener("submit", runPlayground); $("pg-example").addEventListener("click", pgExample);
$("pg-url").addEventListener("input", renderCode); $("pg-proxy").addEventListener("change", renderCode); $("pg-country").addEventListener("input", renderCode);
$("pg-geo").addEventListener("change", () => { $("pg-geo-box").classList.toggle("hidden", !$("pg-geo").checked); renderCode(); });
$("pg-sticky").addEventListener("change", pgSticky);
$("pg-copy-code").addEventListener("click", () => copyText($("pg-code").textContent, "Código copiado."));
$("pg-copy-body").addEventListener("click", () => copyText(pg.body, "Cuerpo copiado."));
const langTabs = [...document.querySelectorAll("[data-lang]")], paneTabs = [...document.querySelectorAll("[data-pane]")];
for (const t of langTabs) t.addEventListener("click", () => selectTab(langTabs, "lang", t.dataset.lang, (v) => { pg.lang = v; renderCode(); }));
for (const t of paneTabs) t.addEventListener("click", () => selectTab(paneTabs, "pane", t.dataset.pane, (v) => { $("pg-pane-body").classList.toggle("hidden", v !== "body"); $("pg-pane-details").classList.toggle("hidden", v !== "details"); }));
window.addEventListener("hashchange", () => { if (key && VIEWS[(location.hash || "").slice(1)] && (location.hash || "").slice(1) !== current) show((location.hash || "").slice(1)); });
if (key) { api("/v1/system").then(() => { setLogged(true); return show((location.hash || "").slice(1) || "overview"); }).catch(() => { key = ""; }); }
setInterval(() => { if (key && !document.hidden && current === "bench" && benchActive) loadRuns().catch(() => {}); }, 5000);
