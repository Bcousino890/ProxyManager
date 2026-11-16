"""Option B: keep your Playwright engine, wrap navigation with PageGuard.

Minimal change: `await page.goto(url)` -> `html = await guard.goto(page, url)`.
Cookies (DataDome + login) are restored at start-up and saved after every page.
Note: Playwright Chromium is more detectable than Camoufox; if challenges are frequent,
switch the browser to Camoufox (`AsyncCamoufox`, same Playwright API) or to Option A.
"""
import asyncio

from playwright.async_api import async_playwright

from ddguard.playwright_guard import PageGuard


async def main(urls):
    guard = PageGuard(store_dir="dd_sessions", notify=lambda m: print("ALERT:", m))
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # visible via Xvfb/noVNC on the VPS
        context = await browser.new_context(locale="es-ES")
        print("restored cookies:", await guard.restore(context))
        page = await context.new_page()
        for url in urls:
            html = await guard.goto(page, url)   # waits through the challenge, then continues
            print(len(html), url)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main(["https://www.idealista.com/inmueble/110467049/"]))
