"""Light summary of a fetched page, used by `python -m ddguard fetch --out DIR` to prove the HTML
is real data. It is NOT a full parser (the client's own engine does the parsing)."""
from __future__ import annotations

import html as _html
import re


def _txt(s: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _grab(pat: str, text: str) -> str | None:
    m = re.search(pat, text, re.S)
    return _txt(m.group(1)) if m else None


def summarize(url: str, page_html: str) -> dict:
    if "/inmueble/" in url:
        feats = re.search(r'class="info-features"[^>]*>(.*?)</div>', page_html, re.S)
        return {
            "type": "listing",
            "id": (re.search(r"/inmueble/(\d+)", url) or [None, None])[1],
            "title": _grab(r'class="main-info__title-main"[^>]*>(.*?)</span>', page_html),
            "location": _grab(r'class="main-info__title-minor"[^>]*>(.*?)</span>', page_html),
            # <span class="info-data-price"><span class="txt-bold">990</span> €/mes</span>
            "price": _grab(r'class="info-data-price"[^>]*>(<span[^>]*>.*?</span>[^<]*)</span>',
                           page_html),
            "features": [_txt(x) for x in re.findall(r"<span>(.*?)</span>", feats.group(1), re.S)
                         if _txt(x)] if feats else [],
        }
    cards = []
    for m in re.finditer(r'<article[^>]*data-element-id="(\d+)"(.*?)</article>', page_html, re.S):
        body = m.group(2)
        cards.append({
            "id": m.group(1),
            "title": _grab(r'class="item-link[^"]*"[^>]*>(.*?)</a>', body),
            "price": _grab(r'class="item-price[^"]*"[^>]*>(.*?)</span>', body),
            "details": [_txt(x) for x in re.findall(r'class="item-detail"[^>]*>(.*?)</span>', body)],
        })
    return {"type": "search", "results": len(cards), "listings": cards}
