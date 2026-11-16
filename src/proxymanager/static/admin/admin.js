"use strict";
const root = document.getElementById("root");
let KEY = "";
try { KEY = sessionStorage.getItem("pm_admin") || ""; } catch (_) {}

function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v === true) el.setAttribute(k, "");
    else if (v !== false && v != null) el.setAttribute(k, v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  return el;
}
async function api(path, opts = {}) {
  const headers = { "Content-Type": "application/json", "X-PM-CSRF": "1" };
  if (KEY) headers["X-API-Key"] = KEY;   // acceso de emergencia con la clave maestra; si no, va la cookie de sesión
  const res = await fetch(path, { method: opts.method || "GET", credentials: "same-origin", headers, body: opts.body ? JSON.stringify(opts.body) : undefined });
  if (res.status === 204) return null;
  let data = null; try { data = await res.json(); } catch (_) {}
  if (!res.ok) { const e = new Error(typeof (data && data.detail) === "string" ? data.detail : "Error " + res.status); e.status = res.status; throw e; }
  return data;
}
const fmt = n => new Intl.NumberFormat("es-ES").format(n);
const date = ts => ts ? new Date(ts * 1000).toLocaleString("es-ES", { dateStyle: "medium", timeStyle: "short" }) : "—";
const KINDS = { unknown: "Sin verificar", isp: "ISP", residential: "Residencial", datacenter: "Datacenter" };
const stat = (label, value, sub) => h("div", { class: "card stat" }, h("span", {}, label), h("b", {}, value), h("span", {}, sub || ""));

function masterKeyScreen(err) {
  const key = h("input", { type: "password", autocomplete: "off", required: true });
  const msg = h("div", { class: "err" }, err || "");
  return h("form", { class: "card", onsubmit: async e => {
    e.preventDefault(); KEY = key.value;
    try { await api("/v1/admin/stats"); try { sessionStorage.setItem("pm_admin", KEY); } catch (_) {} start(); }
    catch (x) { KEY = ""; msg.textContent = x.status === 403 || x.status === 401 ? "Clave de administración incorrecta" : x.message; }
  } }, h("h1", {}, "Acceso con clave maestra"),
    h("p", { class: "muted" }, "Para situaciones de emergencia, o para crear el primer administrador con nombre."),
    h("label", {}, "Clave de administración (PROXYMANAGER_ADMIN_KEY)", key), msg,
    h("button", { class: "primary", type: "submit" }, "Entrar"),
    h("p", {}, h("a", { href: "#", onclick: e => { e.preventDefault(); loginScreen(); } }, "← Volver al inicio de sesión normal")));
}

function bootstrapScreen() {
  const masterKey = h("input", { type: "password", autocomplete: "off", required: true });
  const name = h("input", { autocomplete: "name", required: true, maxlength: 120 });
  const email = h("input", { type: "email", autocomplete: "email", required: true });
  const pass = h("input", { type: "password", autocomplete: "new-password", required: true, minlength: 10 });
  const err = h("div", { class: "err" });
  return h("form", { class: "card", onsubmit: async e => {
    e.preventDefault(); err.textContent = "";
    try {
      await api("/v1/admin/register", { method: "POST", body: { master_key: masterKey.value, name: name.value, email: email.value, password: pass.value } });
      start();
    } catch (x) { err.textContent = x.message; }
  } }, h("h1", {}, "Crear el primer administrador"),
    h("p", { class: "muted" }, "Todavía no hay ningún administrador con nombre en este despliegue. Usa la clave maestra (",
      h("code", {}, "PROXYMANAGER_ADMIN_KEY"), ", definida en el servidor) una sola vez para crear el tuyo."),
    h("label", {}, "Clave de administración (PROXYMANAGER_ADMIN_KEY)", masterKey),
    h("label", {}, "Tu nombre", name), h("label", {}, "Correo electrónico", email),
    h("label", {}, "Contraseña (mínimo 10 caracteres)", pass), err,
    h("button", { class: "primary", type: "submit" }, "Crear administrador y entrar"));
}

function loginScreen() {
  root.replaceChildren(h("div", { class: "auth" }, h("p", {}, "Cargando…")));
  api("/v1/admin/bootstrap-status").then(s => {
    if (s.needs_bootstrap) { root.replaceChildren(h("div", { class: "auth" }, h("div", { class: "brand" }, h("span", { class: "logo" }, "P"), "ProxyManager · Admin"), bootstrapScreen())); return; }
    const email = h("input", { type: "email", autocomplete: "email", required: true });
    const pass = h("input", { type: "password", autocomplete: "current-password", required: true });
    const err = h("div", { class: "err" });
    const form = h("form", { class: "card", onsubmit: async e => {
      e.preventDefault(); err.textContent = "";
      try { await api("/v1/admin/login", { method: "POST", body: { email: email.value, password: pass.value } }); start(); }
      catch (x) { err.textContent = x.status === 401 ? "Correo o contraseña incorrectos" : x.message; }
    } }, h("h1", {}, "Acceso de administrador"),
      h("label", {}, "Correo electrónico", email), h("label", {}, "Contraseña", pass), err,
      h("button", { class: "primary", type: "submit" }, "Entrar"),
      h("p", {}, h("a", { href: "#", onclick: e => { e.preventDefault(); root.replaceChildren(h("div", { class: "auth" }, h("div", { class: "brand" }, h("span", { class: "logo" }, "P"), "ProxyManager · Admin"), masterKeyScreen())); } }, "Entrar con la clave maestra")));
    root.replaceChildren(h("div", { class: "auth" }, h("div", { class: "brand" }, h("span", { class: "logo" }, "P"), "ProxyManager · Admin"), form));
  }).catch(x => root.replaceChildren(h("div", { class: "auth" }, h("div", { class: "notice bad" }, x.message))));
}

const dateFull = ts => ts ? new Date(ts * 1000).toLocaleString("es-ES", { dateStyle: "full", timeStyle: "short" }) : "—";
const PAGES = {
  desafios: ["Desafíos", async () => {
    const s = await api("/v1/admin/challenge-handler");
    const by = h("input", { placeholder: "Quién autorizó (nombre y cargo o empresa)", maxlength: 200 });
    const ref = h("textarea", { placeholder: "Referencia verificable: correo, contrato, ticket, fecha… copia el texto o un enlace", maxlength: 4000 });
    const msg = h("div", { class: "err" });
    const out = [h("p", { class: "lead" }, "Un manejador conectado por código (", h("code", {}, "PROXYMANAGER_CHALLENGE_HANDLER"), ") no actúa en ", h("code", {}, "/scrape"), " hasta que aquí se declare quién autorizó su uso contra el destino. La declaración queda registrada con fecha; activar sin una autorización real es responsabilidad de quien lo hace.")];
    if (!s.configured) {
      out.push(h("div", { class: "notice" }, "No hay ningún manejador configurado en este despliegue (", h("code", {}, "PROXYMANAGER_CHALLENGE_HANDLER"), " vacío). No hay nada que activar aquí."));
      return out;
    }
    out.push(h("div", { class: "card" }, h("h2", {}, "Estado"),
      h("p", {}, "Manejador configurado: ", h("code", {}, s.handler_name)),
      h("p", {}, "Estado: ", h("span", { class: "badge" + (s.enabled ? "" : " bad") }, s.enabled ? "ACTIVADO" : "Desactivado")),
      s.enabled && h("p", { class: "muted" }, `Autorizado por «${s.authorized_by}» el ${dateFull(s.declared_at)}.`),
      s.enabled && h("p", { class: "muted" }, "Referencia declarada: ", h("code", {}, s.authorization_reference)),
      s.enabled
        ? h("button", { class: "danger", onclick: async () => { if (confirm("¿Desactivar el manejador de desafíos ahora mismo?")) { await api("/v1/admin/challenge-handler/disable", { method: "POST" }); render(); } } }, "Desactivar ahora")
        : h("div", { style: "display:grid;gap:10px;max-width:520px;margin-top:10px" },
            h("label", {}, "Quién autorizó", by), h("label", {}, "Referencia de la autorización", ref), msg,
            h("button", { class: "primary", onclick: async () => {
              msg.textContent = "";
              if (!confirm("Vas a declarar quién autorizó esto y activar el manejador de desafíos. Confirma que tienes autorización real y verificable antes de continuar.")) return;
              try { await api("/v1/admin/challenge-handler/enable", { method: "POST", body: { authorized_by: by.value, authorization_reference: ref.value } }); render(); }
              catch (x) { msg.textContent = x.message; }
            } }, "Declarar autorización y activar"))));
    out.push(h("div", { class: "card" }, h("h2", {}, "Registro de activaciones"),
      s.log.length ? h("div", { class: "tablewrap" }, h("table", {}, h("thead", {}, h("tr", {}, ["Fecha", "Acción", "Autorizado por", "Referencia"].map(t => h("th", {}, t)))),
        h("tbody", {}, s.log.map(l => h("tr", {}, h("td", {}, dateFull(l.at)), h("td", {}, l.action === "enable" ? "Activación" : "Desactivación"), h("td", {}, l.authorized_by || "—"), h("td", {}, l.authorization_reference || "—")))))) : h("p", { class: "lead" }, "Sin movimientos todavía.")));
    return out;
  }],
  overview: ["Resumen", async () => {
    const [s, proxies] = await Promise.all([api("/v1/admin/stats"), api("/v1/proxies")]);
    const active = proxies.filter(p => p.enabled).length, healthy = proxies.filter(p => p.last_check && p.last_check.success).length;
    return [h("div", { class: "stats" }, stat("Clientes", fmt(s.users)), stat("Solicitudes 24 h", fmt(s.requests_24h), `${fmt(s.successful_24h)} validadas`), stat("Solicitudes totales", fmt(s.requests_total)),
      stat("Créditos usados", fmt(s.credits_used), `de ${fmt(s.credits_granted)} concedidos`), stat("Proxies activos", `${active}/${proxies.length}`, `${healthy} con última comprobación OK`)),
      h("div", { class: "card" }, h("h2", {}, "Atajos"), h("p", {}, h("a", { href: "#proxies" }, "Añadir o configurar proxies"), " · ", h("a", { href: "#clientes" }, "Clientes y créditos"), " · ", h("a", { href: "/app/" }, "Ver el panel de cliente"), " · ", h("a", { href: "/docs/" }, "Documentación pública")))];
  }],
  proxies: ["Proxies", async () => {
    const list = await api("/v1/proxies");
    const msg = h("div", { class: "err", role: "status" });
    const say = (t, bad = true) => { msg.className = bad ? "err" : "muted"; msg.textContent = t; };
    const f = { provider: h("input", { placeholder: "Proveedor (p. ej. webshare)" }), host: h("input", { placeholder: "host o IP" }), port: h("input", { type: "number", placeholder: "Puerto", min: 1, max: 65535 }),
      user: h("input", { placeholder: "Usuario", autocomplete: "off" }), pass: h("input", { type: "password", placeholder: "Contraseña", autocomplete: "new-password" }),
      kind: h("select", {}, Object.entries(KINDS).map(([v, l]) => h("option", { value: v }, l))), country: h("input", { placeholder: "País (ES)", maxlength: 2 }) };
    const bulk = { provider: h("input", { placeholder: "Proveedor del lote" }), text: h("textarea", { placeholder: "host:puerto:usuario:contraseña\nuna línea por proxy", autocomplete: "off", spellcheck: false }),
      kind: h("select", {}, Object.entries(KINDS).map(([v, l]) => h("option", { value: v }, l))), country: h("input", { placeholder: "País (ZZ = desconocido)", maxlength: 2 }) };
    const checkUrl = h("input", { type: "url", placeholder: "URL autorizada para comprobar (https://…)" });
    const reload = () => render();
    const wrap = fn => async () => { say(""); try { await fn(); } catch (x) { say(x.message); } };
    const kindSel = p => { const s = h("select", { "aria-label": "Tipo" }, Object.entries(KINDS).map(([v, l]) => h("option", { value: v, selected: v === p.kind }, l))); s.addEventListener("change", wrap(async () => { await api("/v1/proxies/" + p.id, { method: "PATCH", body: { kind: s.value } }); say("Tipo actualizado", false); })); return s; };
    const countryIn = p => { const i = h("input", { value: p.country, maxlength: 2, style: "width:64px", "aria-label": "País" }); i.addEventListener("change", wrap(async () => { await api("/v1/proxies/" + p.id, { method: "PATCH", body: { country: i.value } }); say("País actualizado", false); })); return i; };
    return [
      h("p", { class: "lead" }, "Estos proxies enrutan las solicitudes de los clientes que usan ", h("code", {}, "use_proxy"), " o ", h("code", {}, "country"), ". Las credenciales se guardan cifradas y nunca se muestran. Ajusta el tipo y país solo cuando los hayas verificado."),
      h("div", { class: "card" }, h("h2", {}, `Catálogo · ${list.length}`), h("div", { class: "row", style: "margin:10px 0" }, checkUrl),
        list.length ? h("div", { class: "tablewrap" }, h("table", {}, h("thead", {}, h("tr", {}, ["Proveedor", "Host", "Tipo", "País", "Última comprobación", "Activo", ""].map(t => h("th", {}, t)))),
          h("tbody", {}, list.map(p => h("tr", {}, h("td", {}, p.provider), h("td", { class: "mono" }, `${p.host}:${p.port}`), h("td", {}, kindSel(p)), h("td", {}, countryIn(p)),
            h("td", {}, p.last_check ? h("span", { class: "badge" + (p.last_check.success ? "" : " bad") }, p.last_check.success ? "OK" : "Fallo") : "—", p.last_check ? " " + date(p.last_check.at) : ""),
            h("td", {}, h("input", { type: "checkbox", checked: p.enabled, style: "width:auto", "aria-label": "Activo", onchange: wrap(async e => { await api("/v1/proxies/" + p.id, { method: "PATCH", body: { enabled: e.target.checked } }); }) })),
            h("td", { style: "white-space:nowrap" },
              h("button", { class: "small", onclick: wrap(async () => { if (!checkUrl.value) throw new Error("Escribe arriba una URL autorizada"); await api(`/v1/proxies/${p.id}/checks`, { method: "POST", body: { url: checkUrl.value } }); say("Comprobación en cola; pulsa Refrescar en unos segundos", false); }) }, "Comprobar"), " ",
              h("button", { class: "small danger", onclick: wrap(async () => { if (confirm(`¿Eliminar ${p.host}:${p.port}?`)) { await api("/v1/proxies/" + p.id, { method: "DELETE" }); reload(); } }) }, "Eliminar"))))))) : h("p", { class: "lead" }, "Aún no hay proxies. Añade uno abajo o pega un lote."), msg),
      h("div", { class: "card", style: "display:grid;gap:10px" }, h("h2", {}, "Añadir un proxy"),
        h("div", { class: "row" }, f.provider, f.host, f.port), h("div", { class: "row" }, f.user, f.pass, f.kind, f.country),
        h("div", {}, h("button", { class: "primary", onclick: wrap(async () => { await api("/v1/proxies", { method: "POST", body: { provider: f.provider.value, host: f.host.value, port: Number(f.port.value), kind: f.kind.value, country: (f.country.value || "ZZ").toUpperCase(), username: f.user.value || null, password: f.pass.value || null } }); reload(); }) }, "Añadir proxy"))),
      h("div", { class: "card", style: "display:grid;gap:10px" }, h("h2", {}, "Importar lote"), bulk.text, h("div", { class: "row" }, bulk.provider, bulk.kind, bulk.country),
        h("div", {}, h("button", { class: "primary", onclick: wrap(async () => { const r = await api("/v1/proxies/import", { method: "POST", body: { provider: bulk.provider.value, text: bulk.text.value, kind: bulk.kind.value, country: (bulk.country.value || "ZZ").toUpperCase() } }); bulk.text.value = ""; say(`Importados ${r.added}; total ${r.total}`, false); setTimeout(reload, 900); }) }, "Importar"),
          h("span", { class: "muted", style: "margin-left:12px" }, "Se valida el lote entero antes de insertar; los duplicados host:puerto se omiten.")))];
  }],
  clientes: ["Clientes", async () => {
    const users = await api("/v1/admin/users");
    const email = h("input", { type: "email", placeholder: "Correo del cliente" }), credits = h("input", { type: "number", placeholder: "Créditos a sumar" }), plan = h("input", { placeholder: "Plan (opcional)" });
    const msg = h("div", { class: "err" });
    const grant = async (mail, n, pl) => { msg.textContent = ""; try { await api("/v1/admin/credits", { method: "POST", body: { email: mail, credits: Number(n), plan: pl || null } }); render(); } catch (x) { msg.textContent = x.message; } };
    return [h("div", { class: "card" }, h("h2", {}, `Clientes · ${users.length}`), users.length ? h("div", { class: "tablewrap" }, h("table", {}, h("thead", {}, h("tr", {}, ["Correo", "Plan", "Alta", "Usados", "Concedidos", ""].map(t => h("th", {}, t)))),
      h("tbody", {}, users.map(u => h("tr", {}, h("td", {}, u.email), h("td", {}, u.plan), h("td", {}, date(u.created_at)), h("td", {}, fmt(u.credits_used)), h("td", {}, fmt(u.credits_total)),
        h("td", {}, h("button", { class: "small", onclick: () => { email.value = u.email; credits.focus(); } }, "Recargar"))))))) : h("p", { class: "lead" }, "Todavía no hay clientes registrados.")),
      h("div", { class: "card" }, h("h2", {}, "Conceder créditos"), h("div", { class: "row" }, email, credits, plan, h("button", { class: "primary", onclick: () => grant(email.value, credits.value, plan.value) }, "Aplicar")), msg,
        h("p", { class: "muted" }, "Usa un número negativo para restar. Los pagos en línea aún no están conectados: las recargas son manuales."))];
  }],
  equipo: ["Equipo", async () => {
    const me = await api("/v1/admin/me");
    const team = await api("/v1/admin/team");
    const byId = Object.fromEntries(team.map(a => [a.id, a]));
    const name = h("input", { placeholder: "Nombre", maxlength: 120 });
    const email = h("input", { type: "email", placeholder: "Correo electrónico" });
    const pass = h("input", { type: "password", placeholder: "Contraseña (mínimo 10 caracteres)", minlength: 10 });
    const msg = h("div", { class: "err" });
    return [
      h("p", { class: "lead" }, me.id ? `Sesión iniciada como ${me.name} (${me.email}).` : "Sesión iniciada con la clave maestra."),
      h("div", { class: "card" }, h("h2", {}, `Administradores · ${team.length}`),
        h("div", { class: "tablewrap" }, h("table", {}, h("thead", {}, h("tr", {}, ["Nombre", "Correo", "Invitado por", "Alta", ""].map(t => h("th", {}, t)))),
          h("tbody", {}, team.map(a => h("tr", {},
            h("td", {}, a.name, a.id === me.id ? " (tú)" : ""), h("td", {}, a.email),
            h("td", {}, a.created_by === "clave-maestra" ? "Clave maestra" : (a.created_by && byId[a.created_by] ? byId[a.created_by].name : "—")),
            h("td", {}, date(a.created_at)),
            h("td", {}, a.id === me.id ? null : h("button", { class: "small danger", onclick: async () => { if (confirm(`¿Eliminar a ${a.name} como administrador?`)) { await api("/v1/admin/team/" + a.id, { method: "DELETE" }); render(); } } }, "Eliminar"))))))),
        h("div", { class: "row", style: "margin-top:16px" }, name, email, pass,
          h("button", { class: "primary", onclick: async () => { msg.textContent = ""; try { await api("/v1/admin/team", { method: "POST", body: { name: name.value, email: email.value, password: pass.value } }); render(); } catch (x) { msg.textContent = x.message; } } }, "Invitar")),
        msg)];
  }],
};
const ORDER = [["overview", "Resumen"], ["proxies", "Proxies"], ["clientes", "Clientes"], ["desafios", "Desafíos"], ["equipo", "Equipo"]];
async function render() {
  const id = (location.hash || "#overview").slice(1), key = PAGES[id] ? id : "overview", page = PAGES[key];
  const content = h("div", { class: "content" }, h("p", { class: "lead" }, "Cargando…"));
  root.replaceChildren(h("div", { class: "layout" }, h("aside", {}, h("div", { class: "brand" }, h("span", { class: "logo" }, "P"), "Admin"),
    h("nav", {}, ORDER.map(([k, l]) => h("a", { href: "#" + k, class: k === key ? "on" : "" }, l)), h("a", { href: "/app/" }, "Panel de cliente ↗"), h("a", { href: "/docs/" }, "Documentación ↗")),
    h("div", { class: "side-foot", id: "admin-foot" }, h("a", { href: "#", onclick: async e => { e.preventDefault(); try { await api("/v1/admin/logout", { method: "POST" }); } catch (_) {} try { sessionStorage.removeItem("pm_admin"); } catch (_) {} KEY = ""; loginScreen(); } }, "Cerrar sesión"))),
    h("main", {}, h("header", { class: "top" }, h("div", { class: "crumb" }, "Administración › ", h("b", {}, page[0])), h("button", { onclick: render }, "Refrescar")), content)));
  api("/v1/admin/me").then(me => { const foot = document.getElementById("admin-foot"); if (foot) foot.prepend(h("div", { style: "margin-bottom:8px" }, me.name)); }).catch(() => {});
  try { content.replaceChildren(...await page[1]()); }
  catch (x) { if (x.status === 401 || x.status === 403) return loginScreen(); content.replaceChildren(h("div", { class: "notice bad" }, x.message)); }
}
async function start() { window.removeEventListener("hashchange", render); window.addEventListener("hashchange", render); render(); }
(async () => {
  if (KEY) { start(); return; }
  try { await api("/v1/admin/me"); start(); } catch (_) { loginScreen(); }
})();
