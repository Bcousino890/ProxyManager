// Prueba de navegador del panel. Uso: BASE=http://127.0.0.1:PUERTO ADMIN=clave EVAL=clave node scripts/panel_e2e.js
// Sale con código 0 si todo pasa; imprime un fallo por línea si no.
const { chromium } = require("playwright");
const BASE = process.env.BASE, ADMIN = process.env.ADMIN, EVAL = process.env.EVAL;
const failures = [];
const check = (ok, what) => { if (!ok) failures.push(what); };

(async () => {
  const browser = await chromium.launch();
  for (const [name, viewport] of [["escritorio", { width: 1100, height: 800 }], ["móvil", { width: 390, height: 800 }]]) {
    const page = await browser.newPage({ viewport });
    const errors = [];
    page.on("console", (m) => { if (m.type() === "error" && !m.text().includes("401")) errors.push(m.text()); });
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.goto(BASE + "/panel");

    await page.fill("#key", "clave-incorrecta"); await page.click("#enter"); await page.waitForTimeout(300);
    check((await page.textContent("#msg")).includes("inválida"), `${name}: clave incorrecta sin mensaje`);

    await page.fill("#key", ADMIN); await page.click("#enter"); await page.waitForSelector("#tab-add");
    await page.click("summary");
    await page.fill("#p-provider", "e2e"); await page.fill("#p-host", `h${name.length}.example`); await page.fill("#p-port", "8080");
    await page.fill("#p-user", "u"); await page.fill("#p-pass", "no-debe-quedarse");
    const refreshed = page.waitForResponse((r) => r.url().includes("/v1/overview")); await page.click("#p-add"); await refreshed;
    await page.waitForTimeout(150);
    check((await page.inputValue("#p-pass")) === "" && (await page.inputValue("#p-user")) === "", `${name}: credenciales no se limpian tras guardar`);
    check(!(await page.content()).includes("no-debe-quedarse"), `${name}: la contraseña aparece en el DOM`);
    await page.click("#proxies tr button:has-text('Historial')"); await page.waitForSelector(".detail");

    await page.click("[data-tab=sessions]"); await page.waitForSelector("#sessions tr");
    await page.click("#s-create"); await page.waitForSelector("#sessions tr button");
    const sessionId = await page.textContent("#sessions tr td:first-child");
    check(sessionId.startsWith("ses_"), `${name}: sesión no listada`);
    page.once("dialog", (dialog) => dialog.accept());
    await page.click("#sessions tr button");
    await page.waitForFunction(() => document.querySelector("#sessions").textContent.includes("No tienes sesiones activas."));
    check(!(await page.textContent("#sessions")).includes(sessionId), `${name}: sesión no se borró del panel`);

    await page.click("[data-tab=expenses]"); await page.waitForSelector("#exp-summary:not(:empty)");
    await page.fill("#e-concept", `concepto-${name.length}`); await page.fill("#e-amount", "1.5"); await page.click("#e-add");
    await page.waitForSelector("#expenses tr");
    check(await page.isVisible("#expenses tr td:nth-child(2)"), `${name}: columna Concepto oculta`);
    check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${name}: desbordamiento horizontal`);
    await page.click("[data-tab=keys]"); await page.waitForSelector("#k-scopes input");
    await page.fill("#k-name", `clave-${name.length}`); await page.check("#k-scopes input[value=sessions]"); await page.click("#k-create");
    await page.waitForSelector("#k-new:not(.hidden)");
    const made = await page.inputValue("#k-value");
    check(made.startsWith("pm_"), `${name}: la clave nueva no se muestra`);
    await page.waitForSelector("#keys tr");
    check(!(await page.locator("#keys").textContent()).includes(made), `${name}: la clave aparece en la lista`);
    await page.click("[data-tab=overview]"); await page.click("[data-tab=keys]");
    check((await page.inputValue("#k-value")) === "", `${name}: la clave sigue visible tras cambiar de pestaña`);
    page.once("dialog", (d) => d.accept()); await page.click("#keys tr button:has-text('Revocar')"); await page.waitForSelector("#keys tr td:has-text('revocada')");
    await page.click("[data-tab=audit]"); await page.waitForSelector("#events tr");
    check(errors.length === 0, `${name}: errores de consola: ${errors.join(" | ")}`);
    await page.close();
  }

  const limited = await browser.newPage();
  await limited.goto(BASE + "/panel"); await limited.fill("#key", EVAL); await limited.click("#enter"); await limited.waitForSelector("#tab-add");
  await limited.click("[data-tab=audit]"); await limited.waitForTimeout(400);
  check((await limited.textContent("#msg")).includes("permiso"), "clave de evaluación debería ver aviso de permiso en Auditoría");

  if (process.env.AXE === "1") {
    const AxeBuilder = require("@axe-core/playwright").default;
    for (const scheme of ["light", "dark"]) {
      const context = await browser.newContext({ colorScheme: scheme, bypassCSP: true }); // solo para inyectar axe en el test
      const page = await context.newPage(); await page.goto(BASE + "/panel");
      await page.fill("#key", ADMIN); await page.click("#enter"); await page.waitForSelector("#tab-add");
      await page.click("[data-tab=sessions]"); await page.waitForSelector("#sessions tr");
      const report = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
      check(report.violations.length === 0, `${scheme}: axe: ${report.violations.map((v) => v.id).join(", ")}`);
      await context.close();
    }
  }
  await browser.close();

  if (failures.length) { console.log(failures.join("\n")); process.exit(1); }
  console.log("panel e2e OK");
})().catch((e) => { console.log("excepción: " + e.message); process.exit(1); });
