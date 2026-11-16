"""Classify an Idealista response: real page, DataDome challenge, ban or rate limit.

DataDome answers a blocked request with HTTP 403 (sometimes 405/429) and a tiny HTML page
holding `var dd={'rt':'i'|'c', 'cid':..., 'host':'geo.captcha-delivery.com', ...}`.

  rt = 'i'  -> "interstitial" device check. A real browser passes it on its own in ~5-30 s.
  rt = 'c'  -> slider CAPTCHA. Needs a human (or a paid solver) unless the browser is trusted.
  t  = 'bv' -> the IP is banned. Solving is impossible; wait or change IP.
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field

_DD_OBJ = re.compile(r"var\s+dd\s*=\s*(\{.*?\})\s*</script>", re.S)
_DD_KV = re.compile(r"'(\w+)'\s*:\s*'([^']*)'")


class Verdict(str, enum.Enum):
    OK = "ok"                      # real page with data
    INTERSTITIAL = "interstitial"  # rt:'i' - a browser clears it automatically
    CAPTCHA = "captcha"            # rt:'c' - slider, needs a human/solver
    BANNED = "banned"              # t:'bv' - IP blocked, do not insist
    RATE_LIMITED = "rate_limited"  # 429 without a DataDome page
    NOT_FOUND = "not_found"        # 404/410 - listing removed, not a block
    ERROR = "error"                # network error / 5xx / unknown


@dataclass
class Classified:
    verdict: Verdict
    status: int
    dd: dict = field(default_factory=dict)  # parsed `var dd={...}` when present

    @property
    def is_challenge(self) -> bool:
        return self.verdict in (Verdict.INTERSTITIAL, Verdict.CAPTCHA)


def parse_dd(body: str) -> dict:
    m = _DD_OBJ.search(body or "")
    return dict(_DD_KV.findall(m.group(1))) if m else {}


def looks_like_challenge(body: str) -> bool:
    head = (body or "")[:6000]
    return "captcha-delivery.com" in head or "var dd=" in head


def classify(status: int, body: str, headers: dict | None = None,
             data_marker: str | None = None) -> Classified:
    """`data_marker`: a string that only appears on a real page (validate on data, not on 200)."""
    headers = {k.lower(): v for k, v in (headers or {}).items()}
    if looks_like_challenge(body) or headers.get("x-datadome") == "protected" and status in (403, 405):
        dd = parse_dd(body)
        if dd.get("t") == "bv":
            return Classified(Verdict.BANNED, status, dd)
        if dd.get("rt") == "c":
            return Classified(Verdict.CAPTCHA, status, dd)
        return Classified(Verdict.INTERSTITIAL, status, dd)
    if status == 429:
        return Classified(Verdict.RATE_LIMITED, status)
    if status in (404, 410):
        return Classified(Verdict.NOT_FOUND, status)
    if status == 200:
        if data_marker and data_marker not in body:
            return Classified(Verdict.ERROR, status)  # 200 without data = soft block, fail loud
        return Classified(Verdict.OK, status)
    return Classified(Verdict.ERROR, status)
