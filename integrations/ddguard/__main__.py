"""CLI:
    python -m ddguard fetch URL [URL ...]      # fetch through DDSession, print verdict/title
    python -m ddguard login [--auto]           # log in once, save cookies (visible browser)
    python -m ddguard status                   # show saved sessions
Common options: --proxy URL  --store DIR  --headful
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import time
from pathlib import Path

from .login import login
from .session import Blocked, DDSession
from .solver import BrowserSolver


def _title(html: str) -> str:
    import html as h
    t = (re.search(r"<title>(.*?)</title>", html, re.S) or [0, ""])[1]
    return h.unescape(t).replace(" — idealista", "").strip()[:75]


def _save(out: str, n: int, url: str, p, secs: float) -> None:
    """--out DIR: raw HTML per page + results.json (one summary row per URL, appended)."""
    from datetime import datetime, timezone

    from .sample import summarize
    d = Path(out)
    (d / "html").mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", url.split("idealista.com/")[-1].lower()).strip("-")
    if p.text:
        (d / "html" / f"{n:02d}_{slug}.html").write_text(p.text, encoding="utf-8")
    row = {"url": url, "status": p.status, "result": p.verdict.value,
           "challenge_cleared": p.solved, "seconds": round(secs, 1),
           "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if p.verdict.value == "ok":
        row["data"] = summarize(url, p.text)
    f = d / "results.json"
    rows = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    rows.append(row)
    f.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


async def _fetch(a):
    solver = BrowserSolver(headless=not a.headful)
    ok = 0
    async with DDSession(proxy_url=a.proxy, store_dir=a.store, solver=solver) as dd:
        for n, u in enumerate(a.urls, 1):
            t = time.time()
            if a.quiet:
                print(f"[{n}/{len(a.urls)}] {u}", flush=True)
            try:
                p = await dd.get(u)
            except Blocked as e:
                print(f"    PAUSED: protection could not be cleared on this IP "
                      f"(retry in {e.retry_after/60:.0f} min)" if a.quiet else
                      f"BLOCKED {u}: {e} (retry in {e.retry_after:.0f}s)")
                break
            ok += p.verdict.value == "ok"
            if a.out:
                _save(a.out, n, u, p, time.time() - t)
            if a.quiet:
                note = "  (DataDome challenge detected -> cleared, resumed)" if p.solved else ""
                if p.verdict.value == "not_found":
                    note = "  (listing no longer published)"
                print(f"    {p.status} {p.verdict.value.upper()}  {time.time()-t:4.1f}s  "
                      f"{len(p.text)//1024} KB  | {_title(p.text)}{note}", flush=True)
            else:
                print(f"{p.verdict.value:10} {p.status} browser={p.solved!s:5} "
                      f"{time.time()-t:5.1f}s {u} | {_title(p.text)}")
        if a.quiet:
            print(f"\nDone: {ok}/{len(a.urls)} pages OK. Session saved -> reused on next run.")


def main():
    ap = argparse.ArgumentParser(prog="ddguard")
    ap.add_argument("cmd", choices=["fetch", "login", "status"])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--proxy")
    ap.add_argument("--store", default="dd_sessions")
    ap.add_argument("--headful", action="store_true")
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="clean output, no internal logs")
    ap.add_argument("--out", help="save raw HTML + results.json to this folder")
    a = ap.parse_intermixed_args()
    if not a.proxy:  # keep proxy credentials out of the command line / screen recordings
        import os
        a.proxy = os.environ.get("DDGUARD_PROXY") or None
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.quiet:
        import warnings
        warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.CRITICAL if a.quiet else logging.WARNING,
                        format="%(asctime)s %(name)s %(message)s")
    if a.cmd == "fetch":
        asyncio.run(_fetch(a))
    elif a.cmd == "login":
        ok = asyncio.run(login(a.proxy, a.store, "auto" if a.auto else "manual"))
        raise SystemExit(0 if ok else 1)
    else:
        for p in sorted(Path(a.store).glob("*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            cd = max(0, d["cooldown_until"] - time.time())
            print(f"{d['identity']:20} ok={d['ok_requests']} challenges={d['challenges']} "
                  f"logged_in={d['logged_in']} profile={d['tls_profile']} cooldown={cd:.0f}s "
                  f"cookies={len(d['cookies'])}")


if __name__ == "__main__":
    main()
