"""Classify HTTP responses for authorized, offline research.

Classification is evidence-based and deliberately does not attempt to defeat a
challenge. A response body is untrusted input; parsing here is intentionally
limited to extracting a few visible fields from a DataDome challenge marker.
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field

_DD_OBJ = re.compile(r"var\s+dd\s*=\s*(\{.*?\})\s*</script>", re.IGNORECASE | re.DOTALL)
_DD_KV = re.compile(r"['\"]([\w-]+)['\"]\s*:\s*['\"]([^'\"]*)['\"]")
_CHALLENGE_MARKERS = (
    "captcha-delivery.com",
    "datadome",
    "device check",
    "captcha",
)


class Verdict(str, enum.Enum):
    OK = "ok"
    CHALLENGE = "challenge"
    INTERSTITIAL = "interstitial"
    CAPTCHA = "captcha"
    BANNED = "banned"
    AUTH_REQUIRED = "auth_required"
    ACCESS_DENIED = "access_denied"
    RATE_LIMITED = "rate_limited"
    NOT_FOUND = "not_found"
    SERVER_ERROR = "server_error"
    ERROR = "error"
    UNCLASSIFIABLE = "unclassifiable"


@dataclass(frozen=True)
class Classified:
    verdict: Verdict
    status: int | None
    dd: dict[str, str] = field(default_factory=dict)

    @property
    def is_challenge(self) -> bool:
        return self.verdict in {
            Verdict.CHALLENGE,
            Verdict.INTERSTITIAL,
            Verdict.CAPTCHA,
            Verdict.BANNED,
        }


def parse_dd(body: str) -> dict[str, str]:
    """Extract visible string key/value pairs from a ``var dd = {...}`` marker."""
    match = _DD_OBJ.search(body or "")
    return dict(_DD_KV.findall(match.group(1))) if match else {}


def looks_like_challenge(body: str, headers: dict[str, str] | None = None) -> bool:
    """Return whether the response contains a recognizable challenge indicator."""
    head = (body or "")[:6000].lower()
    normalized_headers = {key.lower(): value.lower() for key, value in (headers or {}).items()}
    return (
        any(marker in head for marker in _CHALLENGE_MARKERS)
        or "var dd=" in head
        or normalized_headers.get("x-datadome") == "protected"
    )


def classify(
    status: int | None,
    body: str = "",
    headers: dict[str, str] | None = None,
    data_marker: str | None = None,
) -> Classified:
    """Classify an HTTP response without making any network request.

    ``data_marker`` is an optional application-level marker used to validate a
    successful response; absence of it does not imply a DataDome challenge.
    """
    headers = headers or {}
    dd = parse_dd(body)
    if looks_like_challenge(body, headers):
        if dd.get("t") == "bv":
            verdict = Verdict.BANNED
        elif dd.get("rt") == "c":
            verdict = Verdict.CAPTCHA
        elif dd.get("rt") == "i":
            verdict = Verdict.INTERSTITIAL
        else:
            verdict = Verdict.CHALLENGE
        return Classified(verdict, status, dd)

    if status is None or status <= 0:
        return Classified(Verdict.ERROR, status)
    if status in (401,):
        return Classified(Verdict.AUTH_REQUIRED, status)
    if status == 403:
        return Classified(Verdict.ACCESS_DENIED, status)
    if status == 429:
        return Classified(Verdict.RATE_LIMITED, status)
    if status in (404, 410):
        return Classified(Verdict.NOT_FOUND, status)
    if status >= 500:
        return Classified(Verdict.SERVER_ERROR, status)
    if status == 200:
        if data_marker and data_marker not in (body or ""):
            return Classified(Verdict.UNCLASSIFIABLE, status)
        return Classified(Verdict.OK, status)
    return Classified(Verdict.UNCLASSIFIABLE, status)
