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

    await page.click("[data-tab=expenses]"); await page.waitForSelector("#exp-summary:not(:empty)");
    await page.fill("#e-concept", `concepto-${name.length}`); await page.fill("#e-amount", "1.5"); await page.click("#e-add");
    await page.waitForSelector("#expenses tr");
    check(await page.isVisible("#expenses tr td:nth-child(2)"), `${name}: columna Concepto oculta`);
    check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${name}: desbordamiento horizontal`);
    await page.click("[data-tab=audit]"); await page.waitForSelector("#events tr");
    check(errors.length === 0, `${name}: errores de consola: ${errors.join(" | ")}`);
    await page.close();
  }

  const limited = await browser.newPage();
  await limited.goto(BASE + "/panel"); await limited.fill("#key", EVAL); await limited.click("#enter"); await limited.waitForSelector("#tab-add");
  await limited.click("[data-tab=audit]"); await limited.waitForTimeout(400);
  check((await limited.textContent("#msg")).includes("permiso"), "clave de evaluación debería ver aviso de permiso en Auditoría");
  await browser.close();

  if (failures.length) { console.log(failures.join("\n")); process.exit(1); }
  console.log("panel e2e OK");
})().catch((e) => { console.log("excepción: " + e.message); process.exit(1); });
