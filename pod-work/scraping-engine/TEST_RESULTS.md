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
