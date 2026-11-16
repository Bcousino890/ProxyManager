# DataDome response research module

`proxymanager.datadome` adds offline response classification to ProxyManager. It extracts visible challenge metadata (`rt`, `t`, and similar string fields) and classifies ordinary HTTP outcomes. The classifier makes no network requests and does not attempt to solve or bypass a challenge.

## Use

```python
from proxymanager.datadome import Verdict, classify

result = classify(403, response_body, response_headers)
if result.is_challenge:
    print(result.verdict.value)
```

The `data_marker` argument optionally checks whether a successful response contains expected application content. A DataDome-style challenge marker is treated as a challenge even when the status is 200; an HTTP 200 alone is not considered proof of valid content.

## Boundaries and evidence

- Unit tests use synthetic fixtures and make no external requests.
- The module is not a DataDome integration test and does not establish how a real deployment behaves.
- Browser challenge-solving, CAPTCHA automation, fingerprint emulation, retrying blocked requests, and IP/proxy rotation to circumvent access decisions are intentionally not migrated.
- The project's destination allowlist, SSRF protections, authentication, and encrypted session-cookie handling remain in effect. Use only a lab or target for which testing is explicitly authorized.
