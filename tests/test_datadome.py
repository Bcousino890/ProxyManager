import pytest

from proxymanager.datadome import Verdict, classify, parse_dd


INTERSTITIAL = (
    "<html><script>var dd={'rt':'i','cid':'sample','host':'geo.captcha-delivery.com'}"
    "</script></html>"
)
CAPTCHA = INTERSTITIAL.replace("'rt':'i'", "'rt':'c'")
BANNED = INTERSTITIAL.replace("'rt':'i'", "'rt':'c','t':'bv'")


def test_parse_visible_challenge_fields():
    assert parse_dd(INTERSTITIAL) == {
        "rt": "i",
        "cid": "sample",
        "host": "geo.captcha-delivery.com",
    }


@pytest.mark.parametrize(
    ("status", "body", "verdict"),
    [
        (403, INTERSTITIAL, Verdict.INTERSTITIAL),
        (403, CAPTCHA, Verdict.CAPTCHA),
        (403, BANNED, Verdict.BANNED),
        (200, "<html>captcha challenge</html>", Verdict.CHALLENGE),
        (200, "<html>expected data</html>", Verdict.OK),
        (200, "<html>other content</html>", Verdict.UNCLASSIFIABLE),
        (401, "login", Verdict.AUTH_REQUIRED),
        (403, "denied", Verdict.ACCESS_DENIED),
        (429, "slow down", Verdict.RATE_LIMITED),
        (404, "missing", Verdict.NOT_FOUND),
        (503, "unavailable", Verdict.SERVER_ERROR),
        (0, "", Verdict.ERROR),
    ],
)
def test_classify_http_and_challenge_responses(status, body, verdict):
    result = classify(status, body, data_marker="expected data" if status == 200 else None)
    assert result.verdict == verdict


def test_challenge_header_is_case_insensitive():
    result = classify(403, "blocked", {"X-DataDome": "protected"})
    assert result.verdict == Verdict.CHALLENGE
    assert result.is_challenge


def test_non_challenge_403_is_access_denied():
    assert not classify(403, "forbidden").is_challenge
