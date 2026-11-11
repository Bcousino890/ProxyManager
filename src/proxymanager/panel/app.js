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
    td.append(b); tr.append(td); body.append(tr);
  }
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

const loaders = { overview: loadOverview, bench: loadRuns, audit: loadAudit };
async function show(tab) {
  for (const b of document.querySelectorAll("#tabs button")) b.setAttribute("aria-pressed", String(b.dataset.tab === tab));
  for (const t of Object.keys(loaders)) $("tab-" + t).classList.toggle("hidden", t !== tab);
  say("");
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
$("logout").addEventListener("click", () => { key = ""; try { sessionStorage.removeItem("pm_key"); } catch (e) { /* nada */ } setLogged(false); say(""); });
$("refresh").addEventListener("click", () => show("overview"));
$("b-start").addEventListener("click", startBench);
for (const b of document.querySelectorAll("#tabs button")) b.addEventListener("click", () => show(b.dataset.tab));
if (key) { api("/v1/system").then(() => { setLogged(true); return show("overview"); }).catch(() => { key = ""; }); }
setInterval(() => { if (key && !document.hidden && !$("tab-bench").classList.contains("hidden")) loadRuns().catch(() => {}); }, 5000);
