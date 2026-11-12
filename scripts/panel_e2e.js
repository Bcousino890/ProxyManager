// Prueba de navegador del panel. Uso: BASE=http://127.0.0.1:PUERTO ADMIN=clave EVAL=clave node scripts/panel_e2e.js
// Espera una API con host permitido lab.example que responde 200 "Producto de prueba" y 403 con desafío en /blocked.
// Sale con código 0 si todo pasa; imprime un fallo por línea si no. AXE=1 añade axe-core si está disponible.
const { chromium } = require("playwright");
const BASE = process.env.BASE, ADMIN = process.env.ADMIN, EVAL = process.env.EVAL;
const VIEWS = ["overview", "proxies", "sessions", "bench", "keys", "playground", "usage", "expenses", "audit"];
const failures = [];
let lastStep = "inicio";
const check = (ok, what) => { if (!ok) failures.push(what); };

async function login(page, secret) {
  await page.goto(BASE + "/panel"); await page.fill("#key", secret); await page.click("#enter"); await page.waitForSelector("#metrics .metric");
}
async function go(page, view) { await page.click(`[data-view=${view}]`); await page.waitForSelector(`#view-${view}:not(.hidden)`); await page.waitForTimeout(250); }

(async () => {
  const browser = await chromium.launch();
  for (const [name, viewport] of [["escritorio", { width: 1200, height: 850 }], ["móvil", { width: 390, height: 844 }]]) {
    const page = await browser.newPage({ viewport });
    const errors = [];
    // 401 (clave mala) y 422 (host no permitido) se provocan a propósito en la prueba
    page.on("console", (m) => { if (m.type() === "error" && !m.text().includes("401") && !m.text().includes("422")) errors.push(m.text()); });
    page.on("pageerror", (e) => errors.push(String(e)));

    await page.goto(BASE + "/panel");
    await page.fill("#key", "clave-incorrecta"); await page.click("#enter"); await page.waitForTimeout(300);
    check((await page.textContent("#login-msg")).includes("inválida"), `${name}: clave incorrecta sin mensaje`);
    await login(page, ADMIN);
    check((await page.locator("#metrics .metric").count()) === 8, `${name}: faltan métricas en Resumen`);
    // primera pasada: base vacía => estado vacío claro; segunda: ya hay uso de la primera => gráfica dibujada
    const hasChart = (await page.locator("#ov-requests svg").count()) === 1, hasEmpty = (await page.textContent("#ov-requests")).includes("Aún no hay solicitudes");
    check(name === "escritorio" ? hasEmpty : hasChart, `${name}: estado vacío o gráfica ausente en Resumen`);

    // navegación: las nueve secciones cargan y no desbordan
    for (const v of VIEWS) {
      await go(page, v);
      check((await page.getAttribute(`[data-view=${v}]`, "aria-current")) === "page", `${name}: ${v} sin aria-current`);
      check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${name}: desbordamiento horizontal en ${v}`);
    }

    lastStep = "proxies: alta";
    // proxies: alta, lote, historial; las credenciales no quedan en pantalla
    await go(page, "proxies"); await page.click("summary");
    await page.fill("#p-provider", "e2e"); await page.fill("#p-host", `h${name.length}.example`); await page.fill("#p-port", "8080");
    await page.fill("#p-user", "u"); await page.fill("#p-pass", "no-debe-quedarse");
    const added = page.waitForResponse((r) => r.url().includes("/v1/overview")); await page.click("#p-add"); await added; await page.waitForTimeout(150);
    check((await page.inputValue("#p-pass")) === "" && (await page.inputValue("#p-user")) === "", `${name}: credenciales no se limpian tras guardar`);
    await page.fill("#i-provider", "lote"); await page.fill("#i-text", `lote${name.length}a.example:8080:usuario:clave-secreta-lote\nlote${name.length}b.example:8081:usuario:clave-secreta-lote`);
    const imported = page.waitForResponse((r) => r.url().includes("/v1/proxies/import")); await page.click("#i-add"); await imported; await page.waitForTimeout(200);
    check((await page.inputValue("#i-text")) === "", `${name}: el lote sigue en pantalla`);
    const html = await page.content();
    check(!html.includes("no-debe-quedarse") && !html.includes("clave-secreta-lote"), `${name}: credenciales en el DOM`);
    check((await page.locator("#proxies tr").count()) >= 3, `${name}: proxies no listados`);
    await page.click("#proxies tr button:has-text('Historial')"); await page.waitForSelector(".detail");

    lastStep = "sesiones";
    // sesiones
    await go(page, "sessions");
    const known = await page.$$eval("#sessions tr td:first-child", (n) => n.map((x) => x.textContent));
    await page.click("#s-create");
    const isNew = (seen) => [...document.querySelectorAll("#sessions tr td:first-child")].map((x) => x.textContent).find((t) => t.startsWith("ses_") && !seen.includes(t));
    await page.waitForFunction(isNew, known);
    const sid = await page.evaluate(isNew, known); check(!!sid, `${name}: sesión nueva no listada`);
    page.once("dialog", (d) => d.accept()); await page.click(`button[aria-label="Borrar sesión ${sid}"]`);
    await page.waitForFunction((id) => !document.querySelector("#sessions").textContent.includes(id), sid);
    check(!(await page.textContent("#sessions")).includes(sid), `${name}: la sesión no se borró del panel`);

    lastStep = "playground:";
    // playground: éxito, bloqueo con desafío, ejemplos de código sin la clave real
    await go(page, "playground");
    await page.click("#pg-example"); check((await page.inputValue("#pg-url")).includes("lab.example"), `${name}: URL de ejemplo no se rellena`);
    await page.fill("#pg-url", "https://lab.example/ok"); await page.uncheck("#pg-proxy", { force: true });
    await page.click("#pg-run"); await page.waitForSelector("#pg-resp:not(.hidden)");
    check((await page.textContent("#pg-status")).includes("200"), `${name}: playground sin HTTP 200`);
    check((await page.textContent("#pg-callout")).includes("Contenido esperado"), `${name}: callout de éxito ausente`);
    check((await page.textContent("#pg-body")).includes("Producto de prueba"), `${name}: cuerpo no visible`);
    await page.fill("#pg-url", "https://lab.example/blocked"); await page.click("#pg-run"); await page.waitForFunction(() => document.querySelector("#pg-status").textContent.includes("403"));
    check((await page.textContent("#pg-callout")).includes("no lo resuelve"), `${name}: callout de desafío ausente`);
    await page.click("[data-pane=details]"); check((await page.textContent("#pg-details")).includes("challenge_detected"), `${name}: detalles sin validación`);
    for (const [lang, needle] of [["python", "requests.post"], ["node", "fetch("], ["curl", "curl -X POST"]]) {
      await page.click(`[data-lang=${lang}]`);
      const code = await page.textContent("#pg-code");
      check(code.includes(needle) && code.includes("PROXYMANAGER_API_KEY") && !code.includes(ADMIN), `${name}: ejemplo ${lang} incorrecto o con clave real`);
    }
    await page.check("#pg-sticky", { force: true }); await page.waitForSelector("#pg-session:not(.hidden)");
    check((await page.textContent("#pg-code")).includes("session_id"), `${name}: la sesión persistente no entra en el ejemplo`);
    await page.fill("#pg-url", "https://otro-host.example/"); await page.click("#pg-run"); await page.waitForFunction(() => document.querySelector("#pg-callout").textContent.includes("no autorizado") || document.querySelector("#pg-callout").textContent.includes("Destino"));

    lastStep = "uso y resumen";
    // uso y resumen reflejan las solicitudes reales
    await go(page, "usage");
    check((await page.textContent("#u-totals")).match(/Solicitudes\s*[2-9]/) !== null, `${name}: Uso no refleja las solicitudes`);
    check((await page.textContent("#u-domains")).includes("lab.example"), `${name}: dominio ausente en Uso`);
    check(!(await page.textContent("#u-domains")).includes("/ok") && !(await page.textContent("#u-domains")).includes("blocked"), `${name}: ruta visible en Uso`);
    await page.selectOption("#u-days", "7"); await page.waitForTimeout(300);
    await go(page, "overview");
    check((await page.locator("#ov-requests svg").count()) === 1, `${name}: gráfica de solicitudes sin dibujar`);

    lastStep = "claves:";
    // claves: crear, ocultar/mostrar, no persistir, revocar
    await go(page, "keys");
    await page.fill("#k-name", `clave-${name.length}`); await page.check("#k-scopes input[value=sessions]"); await page.click("#k-create"); await page.waitForSelector("#k-new:not(.hidden)");
    check((await page.getAttribute("#k-value", "type")) === "password", `${name}: la clave nueva no empieza oculta`);
    const made = await page.inputValue("#k-value"); check(made.startsWith("pm_"), `${name}: clave no mostrada`);
    await page.click("#k-toggle"); check((await page.getAttribute("#k-value", "type")) === "text", `${name}: no se puede mostrar`);
    await page.click("#k-toggle"); check((await page.getAttribute("#k-value", "type")) === "password", `${name}: no se puede ocultar`);
    await page.waitForSelector("#keys tr"); check(!(await page.locator("#keys").textContent()).includes(made), `${name}: la clave completa aparece en la lista`);
    check((await page.locator("#keys").textContent()).includes("pm_…"), `${name}: falta la huella de la clave`);
    await go(page, "overview"); await go(page, "keys");
    check((await page.inputValue("#k-value")) === "" && !(await page.content()).includes(made), `${name}: la clave sigue en el DOM tras salir`);
    page.once("dialog", (d) => d.accept()); await page.click("#keys tr button:has-text('Revocar')"); await page.waitForSelector("#keys tr td:has-text('revocada')");

    await go(page, "expenses"); await page.fill("#e-concept", `concepto-${name.length}`); await page.fill("#e-amount", "1.5"); await page.click("#e-add"); await page.waitForSelector("#expenses tr td:nth-child(2)");
    check(await page.isVisible("#expenses tr td:nth-child(2)"), `${name}: concepto oculto`);
    await go(page, "audit"); await page.waitForSelector("#events tr");
    check(errors.length === 0, `${name}: errores de consola: ${errors.join(" | ")}`);
    await page.close();
  }

  const limited = await browser.newPage(); await login(limited, EVAL);
  await go(limited, "audit"); await limited.waitForTimeout(300);
  check((await limited.textContent("#msg")).includes("permiso"), "la clave de evaluación debería ver aviso de permiso en Auditoría");
  await go(limited, "keys"); await limited.waitForTimeout(300);
  check((await limited.textContent("#msg")).includes("permiso"), "la clave de evaluación debería ver aviso de permiso en Claves");

  if (process.env.AXE === "1") {
    let axeSource = null;
    try { axeSource = require("axe-core").source; } catch (e) { try { axeSource = require("fs").readFileSync(process.env.AXE_CORE_PATH, "utf8"); } catch (e2) { /* no disponible */ } }
    if (!axeSource) failures.push("AXE=1 pero axe-core no está disponible (npm i -g axe-core o AXE_CORE_PATH)");
    else for (const scheme of ["light", "dark"]) for (const width of [1200, 390]) {
      const context = await browser.newContext({ colorScheme: scheme, bypassCSP: true, viewport: { width, height: 850 } }); // solo para inyectar axe en el test
      const page = await context.newPage(); await login(page, ADMIN);
      for (const v of VIEWS) {
        await go(page, v); await page.addScriptTag({ content: axeSource });
        const bad = await page.evaluate(() => axe.run({ runOnly: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] }).then((r) => r.violations.map((x) => x.id + " x" + x.nodes.length)));
        check(bad.length === 0, `axe ${scheme}/${width}px/${v}: ${bad.join(", ")}`);
      }
      await context.close();
    }
  }
  await browser.close();
  if (failures.length) { console.log(failures.join("\n")); process.exit(1); }
  console.log("panel e2e OK");
})().catch((e) => { console.log("excepción en «" + lastStep + "»: " + e.message.split("\n")[0]); process.exit(1); });
