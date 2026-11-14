# Resultados de pruebas

- 2026-11-14 00:51:18 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 1)
  /usr/local/bin/python3: No module named pytest
- 2026-11-14 00:51:45 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 5)
  no tests ran in 0.01s
  
  /ProxyManager/pod-work/scraping-engine/.venv/lib/python3.12/site-packages/pytest_asyncio/plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
  The event loop scope for asynchronous fixtures will default to the fixture 
  …[132 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 00:52:02 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 00:55:11 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 01:00:35 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 01:02:51 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 01:16:49 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 01:18:44 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 01:20:58 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 01:23:19 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 01:23:54 `cd /ProxyManager/pod-work/scraping-engine && source .venv/bin/activate && python -m pytest tests/tes` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- /ProxyManager/pod-work/scraping-engine/.venv/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, asy
  …[1640 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:24:34 `cd /ProxyManager/pod-work/scraping-engine && source .venv/bin/activate && python -m pytest tests/tes` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- /ProxyManager/pod-work/scraping-engine/.venv/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, asy
  …[1640 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:24:39 `cd /ProxyManager/pod-work/scraping-engine && source .venv/bin/activate && python -c "from scraping_e` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 1)
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
  ImportError: cannot import name 'WebScraper' from 'scraping_engine.engine' (/ProxyManager/pod-work/scraping-engine/src/scraping_engine/engine.py)
- 2026-11-14 01:25:08 `cd /ProxyManager/pod-work/scraping-engine && source .venv/bin/activate && python -c "from scraping_e` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 1)
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "/ProxyManager/pod-work/scraping-engine/src/scraping_engine/__init__.py", line 1, in <module>
      from .engine import ScrapingEngine, WebScraper
  ImportError: cannot import name 'WebScraper' from 'scraping_engine.engine' (/ProxyManager/pod-work/scraping-engine/src/scraping_engine/engine.py)
- 2026-11-14 01:25:16 `cd /ProxyManager/pod-work/scraping-engine && source .venv/bin/activate && python -c "from scraping_e` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 1)
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "/ProxyManager/pod-work/scraping-engine/src/scraping_engine/__init__.py", line 1, in <module>
      from .engine import ScrapingEngine, WebScraper
  ImportError: cannot import name 'WebScraper' from 'scraping_engine.engine' (/ProxyManager/pod-work/scraping-engine/src/scraping_engine/engine.py)

- 2026-11-14 01:32:19 ## Resultados de pruebas

- **Prueba de extracción de Idealista**: Fallida (403 DataDome) - como esperado.
- **Prueba de comparación con Crawio**: No ejecutable sin credenciales API.
- 2026-11-14 01:37:17 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping-engine/tests/test_playwright.py ______
  ImportError while importing test module '/ProxyManager/pod-work/scraping-engine/tests/test_playwright.py'.
  Hint: make sure your test modul
  …[1180 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:37:31 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping-engine/tests/test_playwright.py ______
  ImportError while importing test module '/ProxyManager/pod-work/scraping-engine/tests/test_playwright.py'.
  Hint: make sure your test modul
  …[1180 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:37:42 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _________________________ test_scrape_with_javascript __________________________
  tests/test_playwright.py:7: in test_scrape_with_javascript
      scraper = WebScraper()
                ^^^^^^^^^^
  E   NameError: name 'We
  …[1222 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:38:03 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _________________________ test_scrape_with_javascript __________________________
  tests/test_playwright.py:10: in test_scrape_with_javascript
      result = await engine.scrape("https://httpbin.org/html", method="http"
  …[1302 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:38:21 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _________________________ test_scrape_with_javascript __________________________
  tests/test_playwright.py:10: in test_scrape_with_javascript
      result = await engine.scrape_url("https://httpbin.org/html", method="h
  …[1314 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:38:41 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _________________________ test_scrape_with_javascript __________________________
  tests/test_playwright.py:10: in test_scrape_with_javascript
      result = await engine._scrape_with_httpx("https://httpbin.org/html", N
  …[1535 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:39:00 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _________________________ test_scrape_with_javascript __________________________
  tests/test_playwright.py:16: in test_scrape_with_javascript
      assert result.status_code == 200
  E   AssertionError: assert 500 == 200
  …[1471 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:39:46 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _________________________ test_scrape_with_javascript __________________________
  tests/test_playwright.py:16: in test_scrape_with_javascript
      assert result.status_code == 200
  E   AssertionError: assert 500 == 200
  …[6173 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:40:06 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _________________________ test_scrape_with_javascript __________________________
  tests/test_playwright.py:16: in test_scrape_with_javascript
      assert result.status_code == 200
  E   AssertionError: assert 500 == 200
  …[6173 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:40:30 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _________________________ test_scrape_with_javascript __________________________
  tests/test_playwright.py:16: in test_scrape_with_javascript
      assert result.status_code == 200
  E   AssertionError: assert 500 == 200
  …[6171 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 01:40:50 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 3 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 01:41:50 `/ProxyManager/pod-work/scraping-engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 3 aprobadas, 0 falladas/errores (exit 0)
