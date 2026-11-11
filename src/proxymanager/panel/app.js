"use strict";
// Todo el contenido dinámico se inserta con textContent: nunca innerHTML.
const $ = (id) => document.getElementById(id);
let key = "";
try { key = sessionStorage.getItem("pm_key") || ""; } catch (e) { /* sin almacenamiento */ }

function el(tag, text, cls) { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; }
function say(text, cls) { const m = $("msg"); m.textContent = text || ""; m.className = cls || ""; }
function fmt(n, d) { return n === null || n === undefined ? "–" : Number(n).toFixed(d === undefined ? 0 : d); }

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

function setLogged(on) {
  $("login").classList.toggle("hidden", on); $("app").classList.toggle("hidden", !on); $("logout").classList.toggle("hidden", !on);
}

async function loadOverview() {
  const data = await api("/v1/overview");
  $("summary").textContent = "· sanos: " + data.healthy + " de " + data.total;
  const gb = data.traffic_month_bytes / 1e9;
  $("traffic").textContent = "Tráfico del mes (cuerpos de respuesta): " + (gb < 0.01 ? (data.traffic_month_bytes / 1e6).toFixed(2) + " MB" : gb.toFixed(2) + " GB") + (data.estimated_proxy_cost_usd === null ? " · coste estimado: define PROXYMANAGER_PROXY_COST_PER_GB_USD" : " · coste estimado ≈ " + data.estimated_proxy_cost_usd.toFixed(2) + " USD (no incluye cabeceras ni sobrecarga TLS)");
  if (!$("checkurl").value && data.allowed_hosts.length) $("checkurl").placeholder = "https://" + data.allowed_hosts[0] + "/";
  const body = $("proxies"); body.replaceChildren();
  for (const p of data.proxies) {
    const s = p.stats, tr = el("tr");
    tr.append(el("td", p.provider + " :" + p.port), el("td", p.country));
    tr.append(el("td", s.healthy ? "sano" : (s.events ? "degradado" : "sin datos"), s.healthy ? "ok" : (s.events ? "bad" : "muted")));
    tr.append(el("td", s.success_rate === null ? "–" : Math.round(s.success_rate * 100) + " % (" + s.events + ")"));
    tr.append(el("td", fmt(s.avg_duration_ms) + " ms"));
    const td = el("td"), b = el("button", "Comprobar");
    b.addEventListener("click", () => runCheck(p.id, b));
    const h = el("button", "Historial"); h.addEventListener("click", () => toggleHistory(p.id, tr, h));
    td.append(b, " ", h); tr.append(td); body.append(tr);
  }
}

async function toggleHistory(id, row, button) {
  const next = row.nextElementSibling;
  if (next && next.classList.contains("detail")) { next.remove(); return; }
  button.disabled = true;
  try {
    const items = (await api("/v1/proxies/" + id + "/checks")).slice(0, 8);
    const tr = el("tr", undefined, "detail"), td = el("td"); td.colSpan = 6;
    if (!items.length) td.textContent = "Sin comprobaciones todavía.";
    for (const c of items) {
      const line = new Date(c.created_at * 1000).toLocaleTimeString() + " · " + c.state + " · " + (c.success ? "OK" : "fallo") + " · " + (c.status_code || "–") + " · " + fmt(c.duration_ms) + " ms" + (c.error ? " · " + c.error.type : "");
      td.append(el("div", line, c.success ? "ok" : "bad"));
    }
    tr.append(td); row.after(tr);
  } catch (e) { say(e.message, "bad"); } finally { button.disabled = false; }
}

async function addProxy() {
  const payload = { provider: $("p-provider").value.trim(), host: $("p-host").value.trim(), port: parseInt($("p-port").value, 10), country: $("p-country").value.trim().toUpperCase(), kind: $("p-kind").value };
  if ($("p-user").value) payload.username = $("p-user").value;
  if ($("p-pass").value) payload.password = $("p-pass").value;
  try { await api("/v1/proxies", { method: "POST", body: JSON.stringify(payload) }); say("Proxy guardado (credenciales cifradas).", "ok"); await loadOverview(); }
  catch (e) { say(e.status === 403 ? "Esta clave no puede añadir proxies." : e.message, "bad"); }
  finally { $("p-pass").value = ""; $("p-user").value = ""; }
}

async function importBatch() {
  const text = $("i-text").value;
  try {
    const r = await api("/v1/proxies/import", { method: "POST", body: JSON.stringify({ provider: $("i-provider").value.trim(), text }) });
    say("Importadas: " + r.added + " · duplicadas omitidas: " + r.duplicates_skipped + " · total: " + r.total, "ok"); await loadOverview();
  } catch (e) { say(e.status === 403 ? "Esta clave no puede importar proxies." : e.message, "bad"); }
  finally { $("i-text").value = ""; }
}

async function loadExpenses() {
  const d = await api("/v1/expenses");
  $("exp-month").textContent = "· " + d.month;
  $("exp-summary").textContent = "Gastado " + d.spent_usd.toFixed(2) + " de " + d.budget_usd.toFixed(2) + " USD · " + (d.over_budget ? "presupuesto superado en " + Math.abs(d.remaining_usd).toFixed(2) : "quedan " + d.remaining_usd.toFixed(2)) + " USD";
  $("exp-summary").className = d.over_budget ? "bad" : "";
  $("exp-bar").max = d.budget_usd || 1; $("exp-bar").value = Math.min(d.spent_usd, d.budget_usd || 1);
  const body = $("expenses"); body.replaceChildren();
  for (const e of d.entries) { const tr = el("tr"); tr.append(el("td", new Date(e.at * 1000).toLocaleDateString()), el("td", e.concept), el("td", e.amount_usd.toFixed(2))); body.append(tr); }
}

async function loadSessions() {
  const items = await api("/v1/sessions"), body = $("sessions"); body.replaceChildren();
  if (!items.length) {
    const tr = el("tr"), td = el("td", "No tienes sesiones activas."); td.colSpan = 4; tr.append(td); body.append(tr);
  }
  for (const item of items) {
    const tr = el("tr"), actions = el("td"), remove = el("button", "Borrar sesión");
    remove.setAttribute("aria-label", "Borrar sesión " + item.session_id);
    remove.addEventListener("click", async () => {
      if (!window.confirm("¿Borrar esta sesión y sus cookies?")) return;
      remove.disabled = true;
      try { await api("/v1/sessions/" + encodeURIComponent(item.session_id), { method: "DELETE" }); await loadSessions(); say("Sesión borrada.", "ok"); }
      catch (e) { remove.disabled = false; say(e.message, "bad"); }
    });
    actions.append(remove);
    tr.append(el("td", item.session_id), el("td", new Date(item.created_at * 1000).toLocaleString()), el("td", new Date(item.expires_at * 1000).toLocaleString()), actions);
    body.append(tr);
  }
}

async function createSession() {
  try { await api("/v1/sessions", { method: "POST" }); await loadSessions(); say("Sesión creada.", "ok"); }
  catch (e) { say(e.message, "bad"); }
}

async function addExpense() {
  try {
    await api("/v1/expenses", { method: "POST", body: JSON.stringify({ concept: $("e-concept").value, amount_usd: parseFloat($("e-amount").value) }) });
    $("e-concept").value = ""; $("e-amount").value = ""; await loadExpenses(); say("Gasto anotado.", "ok");
  } catch (e) { say(e.message, "bad"); }
}

async function runCheck(id, button) {
  const url = $("checkurl").value.trim();
  if (!url) { say("Indica una URL de comprobación.", "warn"); return; }
  button.disabled = true;
  try { await api("/v1/proxies/" + id + "/checks", { method: "POST", body: JSON.stringify({ url }) }); say("Comprobación en cola; actualiza en unos segundos.", "ok"); }
  catch (e) { say(e.message, "bad"); } finally { button.disabled = false; }
}

async function loadRuns() {
  const runs = await api("/v1/benchmarks"), body = $("runs"); body.replaceChildren();
  for (const r of runs) {
    const s = r.summary || {}, tr = el("tr");
    tr.append(el("td", r.id.slice(0, 12)));
    tr.append(el("td", r.state + (s.stopped_because ? " (" + s.stopped_because + ")" : ""), r.state === "completed" ? "ok" : (r.state === "failed" ? "bad" : "muted")));
    tr.append(el("td", (s.completed || 0) + " / " + r.params.requests));
    tr.append(el("td", Object.entries(s.outcomes || {}).map(([k, v]) => k + ": " + v).join(", ") || "–"));
    tr.append(el("td", s.latency_ms ? fmt(s.latency_ms.p50) + " / " + fmt(s.latency_ms.p95) : "–"));
    const td = el("td");
    if (r.state === "queued" || r.state === "running") {
      const b = el("button", "Cancelar"); b.addEventListener("click", async () => { try { await api("/v1/benchmarks/" + r.id + "/cancel", { method: "POST" }); await loadRuns(); } catch (e) { say(e.message, "bad"); } });
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
  try { await api("/v1/benchmarks", { method: "POST", body: JSON.stringify(payload) }); say("Benchmark en cola.", "ok"); await loadRuns(); }
  catch (e) { say(e.message, "bad"); }
}

async function loadAudit() {
  const events = await api("/v1/audit?limit=50"), body = $("events"); body.replaceChildren();
  for (const e of events) {
    const tr = el("tr");
    tr.append(el("td", new Date(e.at * 1000).toLocaleString()), el("td", e.method), el("td", e.route), el("td", String(e.status), e.status >= 400 ? "bad" : "ok"));
    body.append(tr);
  }
}

const KEY_SCOPES = ["system:read", "sessions", "scrape", "proxies:read", "proxies:write", "checks:write", "bench:read", "bench:write", "expenses:read", "expenses:write", "audit:read"];
function buildScopeBoxes() {
  const box = $("k-scopes");
  for (const sc of KEY_SCOPES) {
    const label = el("label"), input = el("input"); input.type = "checkbox"; input.value = sc;
    label.append(input, document.createTextNode(sc)); box.append(label);
  }
}
function hideNewKey() { $("k-value").value = ""; $("k-new").classList.add("hidden"); }

async function loadKeys() {
  const keys = await api("/v1/keys"), body = $("keys"); body.replaceChildren();
  for (const k of keys) {
    const tr = el("tr");
    tr.append(el("td", k.name), el("td", { active: "activa", revoked: "revocada", expired: "caducada" }[k.state] || k.state, k.state === "active" ? "ok" : "muted"), el("td", k.scopes.join(", ")), el("td", k.last_used_at ? new Date(k.last_used_at * 1000).toLocaleString() : "nunca"));
    const td = el("td");
    if (k.state === "active") {
      const b = el("button", "Revocar");
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
    $("k-value").value = made.key; $("k-new").classList.remove("hidden"); $("k-name").value = ""; $("k-days").value = "";
    for (const i of document.querySelectorAll("#k-scopes input")) i.checked = false;
    say("Clave creada. Cópiala ahora.", "ok"); await loadKeys();
  } catch (e) { say(e.status === 403 ? "Solo la clave de administración puede gestionar claves." : e.message, "bad"); }
}

async function copyKey() {
  try { await navigator.clipboard.writeText($("k-value").value); say("Copiada.", "ok"); } catch (e) { $("k-value").select(); say("Selecciona y copia manualmente.", "warn"); }
}

const loaders = { overview: loadOverview, sessions: loadSessions, bench: loadRuns, expenses: loadExpenses, keys: loadKeys, audit: loadAudit };
async function show(tab) {
  for (const b of document.querySelectorAll("#tabs button")) b.setAttribute("aria-pressed", String(b.dataset.tab === tab));
  for (const t of Object.keys(loaders)) $("tab-" + t).classList.toggle("hidden", t !== tab);
  $("tab-add").classList.toggle("hidden", tab !== "overview");
  say(""); hideNewKey();
  try { await loaders[tab](); } catch (e) { say(e.status === 403 ? "Esta clave no tiene permiso para esta sección." : e.message, "bad"); }
}

async function enter() {
  key = $("key").value.trim(); $("key").value = "";
  try { await api("/v1/system"); } catch (e) { say(e.status === 401 ? "Clave inválida." : e.message, "bad"); key = ""; return; }
  try { sessionStorage.setItem("pm_key", key); } catch (e) { /* sin almacenamiento */ }
  setLogged(true); say(""); await show("overview");
}

$("enter").addEventListener("click", enter);
$("key").addEventListener("keydown", (e) => { if (e.key === "Enter") enter(); });
$("logout").addEventListener("click", () => { key = ""; try { sessionStorage.removeItem("pm_key"); } catch (e) { /* nada */ } setLogged(false); hideNewKey(); say(""); });
$("refresh").addEventListener("click", () => show("overview"));
$("b-start").addEventListener("click", startBench);
$("p-add").addEventListener("click", addProxy);
$("i-add").addEventListener("click", importBatch);
$("e-add").addEventListener("click", addExpense);
$("k-create").addEventListener("click", createKey);
$("k-copy").addEventListener("click", copyKey);
buildScopeBoxes();
$("s-create").addEventListener("click", createSession);
for (const b of document.querySelectorAll("#tabs button")) b.addEventListener("click", () => show(b.dataset.tab));
if (key) { api("/v1/system").then(() => { setLogged(true); return show("overview"); }).catch(() => { key = ""; }); }
setInterval(() => { if (key && !document.hidden && !$("tab-bench").classList.contains("hidden")) loadRuns().catch(() => {}); }, 5000);
