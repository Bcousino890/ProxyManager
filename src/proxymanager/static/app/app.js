"use strict";
const root = document.getElementById("root");
let me = null, revealed = null;

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
  const res = await fetch(path, {
    method: opts.method || "GET", credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-PM-CSRF": "1" },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (res.status === 204) return null;
  let data = null;
  try { data = await res.json(); } catch (_) {}
  if (!res.ok) {
    const d = data && data.detail;
    const err = new Error(typeof d === "string" ? d : "Error " + res.status);
    err.status = res.status;
    throw err;
  }
  return data;
}

const fmt = n => new Intl.NumberFormat("es-ES").format(n);
const date = ts => ts ? new Date(ts * 1000).toLocaleString("es-ES", { dateStyle: "medium", timeStyle: "short" }) : "—";
const origin = location.origin;
const copy = async (text, btn) => { try { await navigator.clipboard.writeText(text); const t = btn.textContent; btn.textContent = "Copiado"; setTimeout(() => btn.textContent = t, 1200); } catch (_) { prompt("Copia manualmente:", text); } };

function snippets(key, body) {
  const json = JSON.stringify(body);
  return {
    curl: `curl -X POST '${origin}/scrape' \\\n  -H 'x-api-key: ${key}' \\\n  -H 'content-type: application/json' \\\n  -d '${json.replace(/'/g, "'\\''")}'`,
    python: `import requests\n\nr = requests.post(\n    "${origin}/scrape",\n    headers={"x-api-key": "${key}"},\n    json=${json},\n    timeout=60,\n)\nprint(r.json()["status_code"], r.json()["success"])`,
    node: `const r = await fetch("${origin}/scrape", {\n  method: "POST",\n  headers: { "x-api-key": "${key}", "content-type": "application/json" },\n  body: JSON.stringify(${json}),\n});\nconsole.log(await r.json());`,
  };
}

function codeTabs(key, body) {
  const s = snippets(key, body); let cur = "curl";
  const pre = h("pre", { class: "code" }, s.curl);
  const tabs = h("div", { class: "tabs" });
  for (const name of Object.keys(s)) {
    const b = h("button", { class: "small" + (name === cur ? " on" : ""), onclick: () => { cur = name; pre.textContent = s[name]; tabs.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); } }, { curl: "cURL", python: "Python", node: "Node.js" }[name]);
    tabs.append(b);
  }
  const cp = h("button", { class: "small", onclick: e => copy(pre.textContent, e.target) }, "Copiar");
  tabs.append(cp);
  return h("div", {}, tabs, pre);
}

// ---------- autenticación ----------
function authScreen(mode = "login") {
  const err = h("div", { class: "err", role: "alert" });
  const email = h("input", { type: "email", autocomplete: "email", required: true });
  const pass = h("input", { type: "password", autocomplete: mode === "login" ? "current-password" : "new-password", required: true, minlength: 1 });
  const form = h("form", { class: "card", onsubmit: async e => {
    e.preventDefault(); err.textContent = "";
    try {
      const out = await api(mode === "login" ? "/v1/account/login" : "/v1/account/signup", { method: "POST", body: { email: email.value, password: pass.value } });
      if (out && out.api_key) { revealed = { name: "Por defecto", key: out.api_key }; location.hash = "#apikey"; }
      await boot();
    } catch (x) { err.textContent = x.message; }
  } },
    h("div", { class: "brand" }, h("span", { class: "logo" }, "P"), "ProxyManager"),
    h("h1", {}, mode === "login" ? "Inicia sesión" : "Crea tu cuenta"),
    mode === "signup" && h("p", { class: "lead" }, "Incluye créditos gratuitos para probar la API."),
    h("label", {}, "Correo electrónico", email),
    h("label", {}, mode === "login" ? "Contraseña" : "Contraseña", pass),
    err,
    h("button", { class: "primary", type: "submit" }, mode === "login" ? "Entrar" : "Crear cuenta"),
    h("p", { class: "muted" }, mode === "login" ? "¿No tienes cuenta? " : "¿Ya tienes cuenta? ",
      h("a", { href: "#", onclick: e => { e.preventDefault(); root.replaceChildren(authScreen(mode === "login" ? "signup" : "login")); } }, mode === "login" ? "Regístrate" : "Inicia sesión")),
    h("p", { class: "muted" }, h("a", { href: "/docs/" }, "Documentación de la API")));
  return h("div", { class: "auth" }, form);
}

// ---------- páginas ----------
const PAGES = {
  overview: ["Descripción general", async () => {
    const u = await api("/v1/account/usage");
    const rate = u.requests ? Math.round(100 * u.successful / u.requests) : null;
    const max = Math.max(1, ...u.daily.map(d => d.n));
    return [
      h("div", { class: "stats" },
        stat("Créditos disponibles", fmt(me.credits_remaining), `de ${fmt(me.credits_total)} · plan ${me.plan}`),
        stat("Solicitudes (30 días)", fmt(u.requests), `${fmt(u.credits)} créditos usados`),
        stat("Tasa de éxito", rate == null ? "—" : rate + " %", "contenido validado"),
        stat("Latencia media", u.avg_duration_ms == null ? "—" : Math.round(u.avg_duration_ms) + " ms", "")),
      h("div", { class: "card" }, h("h2", {}, "Solicitudes por día"),
        u.daily.length ? h("div", { class: "chart", role: "img", "aria-label": "Solicitudes por día" }, u.daily.map(d => h("div", { style: `height:${Math.max(2, 100 * d.n / max)}%`, title: `${d.day}: ${d.n} solicitudes` }))) : h("p", { class: "lead" }, "Aún no hay solicitudes. Prueba el Playground o usa tu clave API.")),
      h("div", { class: "card" }, h("h2", {}, "Inicio rápido"),
        h("p", { class: "lead" }, "Sustituye TU_CLAVE_API por una clave creada en la sección Clave API."),
        codeTabs("TU_CLAVE_API", { url: "https://example.com/", method: "GET" })),
    ];
  }],
  apikey: ["Clave API", async () => {
    const keys = await api("/v1/account/keys");
    const name = h("input", { placeholder: 'Nombre de la clave, por ejemplo "dev" o "prod"', maxlength: 60 });
    const limit = h("input", { type: "number", min: 1, placeholder: "Límite de créditos (opcional)" });
    const err = h("div", { class: "err" });
    const out = [];
    if (revealed) {
      out.push(h("div", { class: "notice" }, h("b", {}, `Clave «${revealed.name}» creada.`), " Cópiala ahora: no volverá a mostrarse completa.",
        h("div", { class: "keybox" }, h("code", {}, revealed.key), h("button", { class: "small", onclick: e => copy(revealed.key, e.target) }, "Copiar"))));
    }
    out.push(
      h("p", { class: "lead" }, "Envía cualquiera de estas claves en la cabecera ", h("code", {}, "x-api-key"), " al llamar a ", h("code", {}, "/scrape"), ". Las claves comparten tus créditos; asigna una por entorno, ponle un límite propio y revócala si se filtra."),
      h("div", { class: "card" }, h("h2", {}, `Claves API · ${keys.length}/10`),
        h("div", { class: "tablewrap" }, h("table", {},
          h("thead", {}, h("tr", {}, ["Nombre", "Clave", "Créditos usados", "Último uso", "Creada", ""].map(t => h("th", {}, t)))),
          h("tbody", {}, keys.map(k => h("tr", {},
            h("td", {}, k.name), h("td", { class: "mono" }, k.masked),
            h("td", {}, fmt(k.credits_used), k.credit_limit ? " / " + fmt(k.credit_limit) : "", k.credit_limit ? h("div", { class: "bar" }, h("i", { style: `width:${Math.min(100, 100 * k.credits_used / k.credit_limit)}%` })) : null),
            h("td", {}, date(k.last_used_at)), h("td", {}, date(k.created_at)),
            h("td", {}, h("button", { class: "small danger", onclick: async () => { if (confirm(`¿Revocar la clave «${k.name}»? Las aplicaciones que la usen dejarán de funcionar.`)) { await api("/v1/account/keys/" + k.id, { method: "DELETE" }); revealed = null; render(); } } }, "Revocar"))))))),
        h("div", { class: "row", style: "margin-top:16px" }, name, limit,
          h("button", { class: "primary", onclick: async () => { err.textContent = ""; try { const k = await api("/v1/account/keys", { method: "POST", body: { name: name.value, credit_limit: limit.value ? Number(limit.value) : null } }); revealed = k; render(); } catch (x) { err.textContent = x.message; } } }, "Crear clave")),
        err,
        h("p", { class: "muted" }, "Guarda las claves solo en el servidor. Se almacenan como hash: si pierdes una, revócala y crea otra.")),
      h("div", { class: "card" }, h("h2", {}, "Inicio rápido"), codeTabs(revealed ? revealed.key : "TU_CLAVE_API", { url: "https://example.com/", method: "GET" })));
    return out;
  }],
  playground: ["Playground", async () => {
    const url = h("input", { type: "url", placeholder: "https://example.com/page", required: true });
    const method = h("select", {}, ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"].map(m => h("option", {}, m)));
    const proxy = h("input", { type: "checkbox" });
    const country = h("input", { placeholder: "País (ES, US…)", maxlength: 2 });
    const expected = h("input", { placeholder: "Texto esperado en la respuesta (opcional)" });
    const headers = h("textarea", { placeholder: '{"Accept-Language": "es"}', "aria-label": "Cabeceras JSON" });
    const body = h("textarea", { placeholder: "Cuerpo de la solicitud (opcional)", "aria-label": "Cuerpo" });
    const bodyType = h("select", { "aria-label": "Tipo de contenido del cuerpo" },
      h("option", { value: "json" }, "JSON"), h("option", { value: "form" }, "Formulario (x-www-form-urlencoded)"),
      h("option", { value: "text" }, "Texto"), h("option", { value: "custom" }, "Personalizado"));
    const bodyTypeCustom = h("input", { placeholder: "tipo/subtipo, p. ej. application/xml", style: "display:none" });
    bodyType.addEventListener("change", () => { bodyTypeCustom.style.display = bodyType.value === "custom" ? "" : "none"; });
    const BODY_CONTENT_TYPES = { json: "application/json", form: "application/x-www-form-urlencoded", text: "text/plain" };
    const result = h("div", { class: "card" }, h("p", { class: "lead" }, "Tu respuesta aparecerá aquí."));
    const example = h("div");
    const contentTypeFor = () => bodyType.value === "custom" ? bodyTypeCustom.value.trim() : BODY_CONTENT_TYPES[bodyType.value];
    const build = () => {
      const b = { url: url.value || "https://example.com/page", method: method.value };
      if (proxy.checked || country.value) { b.use_proxy = true; if (country.value) b.country = country.value.toUpperCase(); }
      if (expected.value) b.expected_text = expected.value;
      if (body.value) {
        b.body = body.value;
        const ct = contentTypeFor();
        if (ct) b.headers = { ...(b.headers || {}), "content-type": ct };
      }
      return b;
    };
    const refresh = () => example.replaceChildren(codeTabs("TU_CLAVE_API", build()));
    [url, method, proxy, country, expected, body, bodyType, bodyTypeCustom].forEach(e => e.addEventListener("input", refresh));
    refresh();
    const run = h("button", { class: "primary", type: "submit" }, "Ejecutar");
    const step = (icon, text) => h("div", { class: "row", style: "align-items:center;gap:8px" }, h("span", {}, icon), h("span", {}, text));
    const form = h("form", { class: "card", onsubmit: async e => {
      e.preventDefault(); run.disabled = true; run.textContent = "Ejecutando…";
      let extraHeaders = {};
      try {
        if (headers.value.trim()) extraHeaders = JSON.parse(headers.value);
      } catch (_) { result.replaceChildren(h("div", { class: "notice bad" }, "Las cabeceras no son un JSON válido.")); run.disabled = false; run.textContent = "Ejecutar"; return; }
      const payload = build();
      if (Object.keys(extraHeaders).length) payload.headers = { ...(payload.headers || {}), ...extraHeaders };
      const started = performance.now();
      result.replaceChildren(h("div", { class: "card", style: "display:grid;gap:6px" }, step("●", "Enviando solicitud")));
      try {
        const r = await api("/v1/account/playground", { method: "POST", body: payload });
        me = await api("/v1/account/me"); updateFoot();
        const text = r.html || "";
        const destHost = (() => { try { return new URL(payload.url).hostname; } catch (_) { return payload.url; } })();
        result.replaceChildren(
          h("div", { class: "card", style: "display:grid;gap:6px;margin-bottom:12px" },
            step("✓", "Enviando solicitud"),
            step(r.success ? "✓" : "✗", `Descargando ${destHost}${r.duration_ms != null ? ` · ${Math.round(r.duration_ms)} ms` : ""}`),
            step("✓", `Hecho · ${Math.round(performance.now() - started)} ms total · ${r.credits_charged ? r.credits_charged + " créditos" : "no facturado"}`)),
          h("div", { class: "row res", style: "align-items:center" },
            h("span", { class: "badge" + (r.success ? "" : " bad") }, r.success ? "Éxito" : "No validado"),
            r.status_code != null ? h("span", {}, "HTTP " + r.status_code) : h("span", { class: "err" }, (r.error && r.error.message) || "Error de transporte"),
            h("span", {}, r.duration_ms != null ? Math.round(r.duration_ms) + " ms" : ""),
            h("span", {}, fmt(r.bytes_transferred || 0) + " bytes"),
            h("span", {}, `${r.credits_charged} créditos`)),
          r.validation && h("p", { class: "muted" }, `Contenido esperado: ${r.validation.content_expected ? "sí" : "no"} · desafío detectado: ${r.validation.challenge_detected ? "sí" : "no"}`),
          h("pre", { class: "code" }, JSON.stringify(r.headers || {}, null, 2)),
          h("pre", { class: "code", style: "margin-top:10px;max-height:420px" }, text.length > 20000 ? text.slice(0, 20000) + "\n… (recortado en el Playground)" : text || "(cuerpo vacío)"));
      } catch (x) {
        const hint = x.message === "Destino no autorizado"
          ? h("p", { class: "muted", style: "margin-top:8px" }, "Si este destino debería estar permitido, revisa ", h("code", {}, "PROXYMANAGER_ALLOW_ANY_PUBLIC_HOST"), " o ", h("code", {}, "PROXYMANAGER_ALLOWED_HOSTS"), " en el ", h("code", {}, ".env"), " del servidor, vuelve a cargarlo con ", h("code", {}, "source .env"), " y reinicia el servidor antes de reintentar. Detalle en la ", h("a", { href: "/docs/" }, "documentación"), ".")
          : null;
        result.replaceChildren(h("div", { class: "notice bad" }, x.message), hint);
      }
      run.disabled = false; run.textContent = "Ejecutar";
    } },
      h("div", { class: "row" }, method, h("div", { style: "flex:4 1 280px" }, url), run),
      h("div", { class: "grid2", style: "margin-top:14px" },
        h("div", { style: "display:grid;gap:10px" }, h("label", {}, "Cabeceras (JSON)", headers),
          h("label", {}, "Cuerpo", body, h("div", { class: "row", style: "margin-top:6px" }, bodyType, bodyTypeCustom))),
        h("div", { style: "display:grid;gap:10px;align-content:start" },
          h("label", { class: "toggle" }, proxy, "Usar proxy del catálogo"), country, expected)));
    return [h("p", { class: "lead" }, "Solo las solicitudes validadas consumen créditos. Las pruebas del Playground usan tus créditos."), form, result,
      h("div", { class: "card" }, h("h2", {}, "Ejemplos de código"), example)];
  }],
  usage: ["Uso", async () => {
    const u = await api("/v1/account/usage");
    let tab = "resumen";
    const PERIODS = [["hour", "Última hora"], ["today", "Hoy"], ["7d", "7 días"], ["30d", "30 días"]];
    const OUTCOMES = [["all", "Todas"], ["delivered", "Entregadas"], ["blocked", "Bloqueadas"], ["site_error", "Error del sitio"], ["not_reachable", "No se pudo conectar"]];
    let period = "7d", outcome = "all";
    const body = h("div");
    const tabs = h("div", { class: "tabs" });
    const renderTabs = () => tabs.replaceChildren(
      h("button", { class: tab === "resumen" ? "on" : "", onclick: () => { tab = "resumen"; renderTabs(); renderBody(); } }, "Resumen"),
      h("button", { class: tab === "log" ? "on" : "", onclick: () => { tab = "log"; renderTabs(); renderBody(); } }, "Registro de solicitudes"));
    const summaryView = () => [h("div", { class: "stats" },
      stat("Solicitudes", fmt(u.requests), "últimos 30 días"), stat("Validadas", fmt(u.successful), ""), stat("Créditos", fmt(u.credits), ""), stat("Transferido", (u.bytes / 1048576).toFixed(2) + " MB", "contenido recibido")),
      h("div", { class: "card" }, h("h2", {}, "Solicitudes por día"),
        u.daily.length ? h("div", { class: "chart", role: "img" }, u.daily.map(d => h("div", { style: `height:${Math.max(2, 100 * d.n / Math.max(1, ...u.daily.map(x => x.n)))}%`, title: `${d.day}: ${d.n}` }))) : h("p", { class: "lead" }, "Sin actividad todavía."))];
    const logView = async () => {
      const log = await api(`/v1/account/usage/log?period=${period}&outcome=${outcome}`);
      const chip = (val, label, count) => h("button", { class: "small" + (outcome === val ? " on" : ""), onclick: () => { outcome = val; renderBody(); } }, label, count != null ? ` (${fmt(count)})` : "");
      return [
        h("div", { class: "row", style: "align-items:center;gap:8px" },
          h("span", { class: "muted" }, "Periodo:"),
          ...PERIODS.map(([val, label]) => h("button", { class: "small" + (period === val ? " on" : ""), onclick: () => { period = val; renderBody(); } }, label))),
        h("div", { class: "row", style: "align-items:center;gap:8px;margin-top:6px" },
          h("span", { class: "muted" }, "Resultado:"),
          chip("all", "Todas", log.total), ...OUTCOMES.slice(1).map(([val, label]) => chip(val, label, log.counts[val]))),
        h("div", { class: "card", style: "margin-top:14px" }, h("h2", {}, `Solicitudes · ${fmt(log.rows.length)} de ${fmt(log.total)}`),
          log.rows.length ? h("div", { class: "tablewrap" }, h("table", {},
            h("thead", {}, h("tr", {}, ["Fecha (UTC)", "Método", "Solicitud", "Resultado", "Tiempo", "Créditos", "Clave"].map(t => h("th", {}, t)))),
            h("tbody", {}, log.rows.map(r => h("tr", {},
              h("td", {}, date(r.ts)), h("td", {}, r.method),
              h("td", {}, r.host + r.path, r.proxied ? " " : "", r.proxied ? h("span", { class: "badge" }, "proxy") : null),
              h("td", {}, h("span", { class: "badge" + (r.outcome === "delivered" ? "" : " bad") }, { delivered: "Entregada", blocked: "Bloqueada", site_error: "Error del sitio", not_reachable: "No se pudo conectar" }[r.outcome] || r.outcome), r.status_code != null ? ` · HTTP ${r.status_code}` : ""),
              h("td", {}, r.duration_ms != null ? (r.duration_ms / 1000).toFixed(2) + " s" : "—"),
              h("td", {}, r.credits), h("td", {}, r.key_name || "Playground")))))) : h("p", { class: "lead" }, "Sin solicitudes en ese periodo y filtro."))];
    };
    const renderBody = async () => {
      body.replaceChildren(h("p", { class: "lead" }, "Cargando…"));
      body.replaceChildren(...(tab === "resumen" ? summaryView() : await logView()));
    };
    renderTabs(); await renderBody();
    return [tabs, body];
  }],
  account: ["Cuenta", async () => {
    const cur = h("input", { type: "password", autocomplete: "current-password" });
    const nw = h("input", { type: "password", autocomplete: "new-password", minlength: 1 });
    const msg = h("div", { class: "err" });
    return [h("div", { class: "card" }, h("h2", {}, "Perfil"), h("p", {}, h("b", {}, me.email)), h("p", { class: "muted" }, "Cuenta creada el " + date(me.created_at)),
      h("button", { onclick: async () => { await api("/v1/account/logout", { method: "POST" }); me = null; await boot(); } }, "Cerrar sesión")),
      h("div", { class: "card", style: "display:grid;gap:12px;max-width:420px" }, h("h2", {}, "Cambiar contraseña"),
        h("label", {}, "Contraseña actual", cur), h("label", {}, "Nueva contraseña", nw), msg,
        h("button", { class: "primary", onclick: async () => { msg.className = "err"; try { await api("/v1/account/password", { method: "POST", body: { current_password: cur.value, new_password: nw.value } }); msg.className = "muted"; msg.textContent = "Contraseña actualizada; se cerraron las demás sesiones."; cur.value = nw.value = ""; } catch (x) { msg.textContent = x.message; } } }, "Actualizar"))];
  }],
  subscription: ["Suscripción", async () => {
    const pct = me.credits_total ? 100 * me.credits_used / me.credits_total : 100;
    return [h("div", { class: "card" }, h("h2", {}, "Plan actual"), h("p", {}, h("b", {}, me.plan), " · ", fmt(me.credits_remaining), " créditos disponibles de ", fmt(me.credits_total)),
      h("div", { class: "bar" }, h("i", { style: `width:${Math.min(100, pct)}%` })),
      h("p", { class: "muted" }, `Coste: ${me.credits_per_request} crédito por solicitud validada; ${me.credits_per_proxied_request} si se enruta por proxy. Las solicitudes no validadas no consumen créditos. Límite: ${me.rate_limit_per_minute} solicitudes por minuto y clave.`)),
      h("div", { class: "card" }, h("h2", {}, "Ampliar créditos"),
        h("p", { class: "lead" }, "Los pagos en línea aún no están activados. Para recargar créditos o cambiar de plan, escribe al administrador indicando tu correo de cuenta."),
        me.support_email ? h("p", {}, h("a", { href: "mailto:" + me.support_email }, me.support_email)) : h("p", { class: "muted" }, "El administrador aún no ha configurado un correo de contacto."))];
  }],
  support: ["Apoyo", async () => [h("div", { class: "card" }, h("h2", {}, "Ayuda"),
    h("p", {}, "Consulta la ", h("a", { href: "/docs/" }, "documentación de la API"), " y la ", h("a", { href: "/api-reference" }, "referencia OpenAPI interactiva"), "."),
    h("p", { class: "muted" }, me.support_email ? "Contacto: " + me.support_email : "Sin correo de contacto configurado."))]],
};
const ORDER = [["overview", "Descripción general"], ["apikey", "Clave API"], ["playground", "Playground"], ["usage", "Uso"], ["account", "Cuenta"], ["subscription", "Suscripción"], ["support", "Apoyo"]];

function stat(label, value, sub) { return h("div", { class: "card stat" }, h("span", {}, label), h("b", {}, value), h("span", {}, sub)); }
function updateFoot() { const f = document.getElementById("foot"); if (f && me) f.textContent = `${me.email} · ${fmt(me.credits_remaining)} créditos`; }

async function render() {
  if (!me) return;
  const id = (location.hash || "#overview").slice(1);
  const page = PAGES[id] || PAGES.overview;
  const key = PAGES[id] ? id : "overview";
  const content = h("div", { class: "content" }, h("p", { class: "lead" }, "Cargando…"));
  const nav = h("nav", {}, ORDER.map(([k, label]) => h("a", { href: "#" + k, class: k === key ? "on" : "" }, label)), h("a", { href: "/docs/" }, "Documentación de la API"));
  root.replaceChildren(h("div", { class: "layout" },
    h("aside", {}, h("div", { class: "brand" }, h("span", { class: "logo" }, "P"), "ProxyManager"), nav, h("div", { class: "side-foot", id: "foot" })),
    h("main", {}, h("header", { class: "top" }, h("div", { class: "crumb" }, "Espacio de trabajo › ", h("b", {}, page[0])), h("button", { onclick: render }, "Refrescar")), content)));
  updateFoot();
  try { me = await api("/v1/account/me"); updateFoot(); content.replaceChildren(...await page[1]()); }
  catch (x) { if (x.status === 401) { me = null; return boot(); } content.replaceChildren(h("div", { class: "notice bad" }, x.message)); }
  if (key !== "apikey") revealed = null;
}

async function boot() {
  try { me = await api("/v1/account/me"); } catch (_) { me = null; }
  if (!me) { root.replaceChildren(authScreen("login")); return; }
  render();
}
window.addEventListener("hashchange", render);
boot();
