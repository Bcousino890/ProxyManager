"""Option A (recommended): replace page.goto() in your engine with DDSession.get().

~30-40 KB per page and no browser in normal operation: Camoufox only opens when DataDome
challenges, clears it in ~20-30 s, and closes after 5 minutes idle.
Your existing parser receives the same HTML it gets from Playwright today.
"""
import asyncio
import logging

from ddguard import Blocked, BrowserSolver, DDSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")


def notify(msg: str):
    # Hook your panel / Telegram / email here. Example with Telegram:
    #   requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    #                params={"chat_id": CHAT_ID, "text": msg})
    print("ALERT:", msg)


async def main(urls: list[str]):
    solver = BrowserSolver(
        headless=False,          # False + Xvfb/noVNC on the VPS = you can solve a slider by hand
        captcha_mode="wait",     # "wait" (human), "callback" (your solver) or "fail"
        notify=notify,
    )
    async with DDSession(store_dir="dd_sessions", solver=solver,
                         min_interval=2.5, jitter=1.5) as dd:
        for url in urls:
            try:
                page = await dd.get(url)
            except Blocked as e:  # this IP is cooling down: sleep (or switch IP with DDPool)
                print(f"paused {e.retry_after:.0f}s: {e}")
                await asyncio.sleep(e.retry_after)
                page = await dd.get(url)
            if page.verdict.value == "not_found":
                continue
            html = page.text
            # parse_listing(html)  <- your existing parser
            print(page.status, page.verdict.value, len(html), url)


if __name__ == "__main__":
    asyncio.run(main([
        "https://www.idealista.com/alquiler-viviendas/madrid/tetuan/",
        "https://www.idealista.com/inmueble/110467049/",
    ]))
