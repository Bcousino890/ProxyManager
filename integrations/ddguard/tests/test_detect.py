"""Offline tests: run with `python -m pytest tests -q` (no network)."""
import asyncio
import time

from ddguard.detect import Verdict, classify, parse_dd
from ddguard.session import DDSession, profile_for_ua
from ddguard.solver import SolveFailed
from ddguard.store import SessionStore, identity_key

# Real 403 body captured from idealista.com on 14 Nov 2026 (cid/hash shortened).
INTERSTITIAL = ("<html lang=\"es\"><head><title>idealista.com</title></head><body><p id=\"cmsg\">"
                "Please enable JS and disable any ad blocker</p><script data-cfasync=\"false\">"
                "var dd={'rt':'i','cid':'AHrlqAAAA==','hsh':'AC81AADC','b':1709036,'s':17156,"
                "'e':'d45e','qp':'','host':'geo.captcha-delivery.com','cookie':'f0Wz'}</script>"
                "<script data-cfasync=\"false\" src=\"https://ct.captcha-delivery.com/i.js\"></script>"
                "</body></html>")
CAPTCHA = INTERSTITIAL.replace("'rt':'i'", "'rt':'c'")
BANNED = INTERSTITIAL.replace("'rt':'i'", "'rt':'c','t':'bv'")


def test_parse_dd():
    dd = parse_dd(INTERSTITIAL)
    assert dd["rt"] == "i" and dd["host"] == "geo.captcha-delivery.com"


def test_classify():
    assert classify(403, INTERSTITIAL).verdict == Verdict.INTERSTITIAL
    assert classify(403, CAPTCHA).verdict == Verdict.CAPTCHA
    assert classify(403, BANNED).verdict == Verdict.BANNED
    assert classify(200, "<html>" + "x" * 50000).verdict == Verdict.OK
    assert classify(200, "<html>ok</html>", data_marker="main-info").verdict == Verdict.ERROR
    assert classify(404, "gone").verdict == Verdict.NOT_FOUND
    assert classify(429, "slow down").verdict == Verdict.RATE_LIMITED


def test_profile_matches_browser():
    assert profile_for_ua("Mozilla/5.0 (X11; Linux x86_64; rv:158.0) Gecko/20100101 Firefox/158.0") \
        .startswith("firefox")
    assert profile_for_ua(None) == "safari2601"


def test_store_roundtrip(tmp_path):
    st = SessionStore(tmp_path)
    s = st.load(identity_key(None))
    s.cookies["datadome"] = "abc"
    st.save(s)
    assert st.load("direct").cookies["datadome"] == "abc"
    assert identity_key("http://u:p@h:1") != identity_key("http://u:p@h:2")


class _FakeSolver:
    engine = "fake"

    def __init__(self, fail=None):
        self.calls, self.fail = 0, fail

    async def solve(self, url, cookies, proxy):
        self.calls += 1
        if self.fail:
            raise SolveFailed(self.fail)
        from ddguard.solver import SolveResult
        return SolveResult({"datadome": "fresh"}, "Mozilla/5.0 rv:158.0 Firefox/158.0",
                           "<html>main-info__title" + "d" * 30000, "fake", 0.1)

    async def close(self):
        pass


def _session(tmp_path, solver, responses):
    s = DDSession(store_dir=str(tmp_path), solver=solver, min_interval=0, jitter=0)

    async def raw(url, referer):
        st, body = responses.pop(0)
        return classify(st, body), body, st
    s._raw_get = raw  # noqa: SLF001
    return s


def test_challenge_is_served_by_browser_and_cookie_adopted(tmp_path):
    solver = _FakeSolver()
    s = _session(tmp_path, solver, [(403, INTERSTITIAL)])
    page = asyncio.run(s.get("https://www.idealista.com/inmueble/1/"))
    assert page.verdict == Verdict.OK and page.solved and solver.calls == 1
    assert s.state.cookies["datadome"] == "fresh" and s.state.tls_profile.startswith("firefox")


def test_failed_solve_cools_down_without_http_retries(tmp_path):
    from ddguard.session import Blocked
    s = _session(tmp_path, _FakeSolver(fail="slider CAPTCHA in headless mode"), [(403, CAPTCHA)])
    try:
        asyncio.run(s.get("https://www.idealista.com/inmueble/1/"))
        raise AssertionError("should have raised Blocked")
    except Blocked:
        pass
    assert s.state.cooldown_until > time.time()
    try:  # while cooling down, no request is sent at all
        asyncio.run(s.get("https://www.idealista.com/inmueble/2/"))
        raise AssertionError("should have raised Blocked")
    except Blocked:
        pass
