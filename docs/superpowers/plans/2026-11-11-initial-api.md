# Initial API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a runnable, tested first slice of ProxyManager.

**Architecture:** FastAPI app with environment settings, SQLite sessions, and guarded HTTPX transport. Defaults deny outbound requests.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, HTTPX, pytest.

**Spec:** `docs/superpowers/specs/2026-11-11-proxymanager-initial-design.md`

## Global Constraints

- Product name ProxyManager.
- No third-party load tests or paid resources.
- Configurable operational values, authorization required for destinations.

## Review Focus

- Empty keys reject protected endpoints.
- A session created by one key is invisible to another.
- A 200 challenge response is not successful.
- Unknown/private destinations fail before transport.
- Redirects do not lead to another destination.

---

### Task 1: Settings and auth

**Files:** `src/proxymanager/config.py`, `src/proxymanager/app.py`, `tests/test_api.py`

**Interfaces:** `Settings.from_env()`; `create_app(settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI`.

- [ ] Write tests for health, missing key, and configured key.
- [ ] Run tests to confirm RED.
- [ ] Implement settings and auth.
- [ ] Run tests to confirm GREEN.
- [ ] Commit.

### Task 2: Session isolation

**Files:** `src/proxymanager/storage.py`, `src/proxymanager/app.py`, `tests/test_api.py`

**Interfaces:** `SessionStore.create(owner, ttl_seconds)` and `SessionStore.get(id, owner)`.

- [ ] Write tests for creation, lookup, isolation, and expiry.
- [ ] Confirm RED; implement; confirm GREEN.
- [ ] Commit.

### Task 3: Guarded fetch and classification

**Files:** `src/proxymanager/fetch.py`, `src/proxymanager/app.py`, `tests/test_api.py`

**Interfaces:** `guard_url(url, settings)`; `fetch(url, settings, transport)`.

- [ ] Write tests for allowlist, private IP, redirection, challenge content, expected content.
- [ ] Confirm RED; implement; confirm GREEN.
- [ ] Commit.

### Task 4: Packaging and documentation

**Files:** `pyproject.toml`, `.env.example`, `README.md`, `Dockerfile`, `tests/test_api.py`.

- [ ] Add install/run instructions and configuration defaults.
- [ ] Run full pytest and package install check.
- [ ] Commit.
