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
