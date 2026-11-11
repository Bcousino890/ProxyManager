# Session Cookies Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Persist encrypted cookies per HTTP session and send only those valid for the next authorized request.

**Architecture:** Add a CookieStore using the existing SQLite database and Fernet key. Route Set-Cookie and Cookie through the existing guarded fetch path.

**Tech Stack:** Python 3.12, FastAPI, HTTPX, SQLite, cryptography, pytest.

**Spec:** `docs/superpowers/specs/2026-11-11-session-cookies-design.md`

## Global Constraints

- Never store cookie values in plaintext or API responses.
- Keep the existing HTTPS allowlist and pinned destination behavior.
- Do not require DataDome or external network for tests.

## Review Focus

- Host-only cookies leaking to subdomains.
- Domain attributes broadening beyond explicitly authorized hosts.
- Path prefix matching without a slash boundary.
- Expired and deleted cookies being resent.
- Cookies surviving session deletion or crossing owners.

### Task 1: Persistence and matching

**Files:** `src/proxymanager/cookies.py`, `tests/test_cookies.py`.

- [x] Write failing tests for encrypted persistence, matching, expiry and deletion.
- [x] Run tests and confirm expected failures.
- [x] Implement CookieStore and rerun tests.

### Task 2: Fetch integration

**Files:** `src/proxymanager/fetch.py`, `src/proxymanager/app.py`, `tests/test_api.py`.

- [x] Write failing API tests for roundtrip, isolation and configuration failure.
- [x] Run tests and confirm expected failures.
- [x] Wire CookieStore to guarded fetch, then run full suite.
- [x] Update handoff, verify diff and commit.
