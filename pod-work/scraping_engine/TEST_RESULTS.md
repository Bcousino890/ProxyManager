# Resultados de pruebas

- 2026-11-14 03:25:45 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 5)
  no tests ran in 0.01s
- 2026-11-14 03:26:01 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping_engine/tests/unit/test_base.py _______
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_base.py'.
  Hint: make sure your test module
  …[394 caracteres omitidos]…
  ng_engine'
  =========================== short test summary info ============================
  ERROR tests/unit/test_base.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.12s
- 2026-11-14 03:27:13 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 1)
  /ProxyManager/pod-work/scraping_engine/.venv/bin/python: No module named pytest
- 2026-11-14 03:27:33 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping_engine/tests/unit/test_base.py _______
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_base.py'.
  Hint: make sure your test module
  …[1110 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 03:27:53 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping_engine/tests/unit/test_base.py _______
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_base.py'.
  Hint: make sure your test module
  …[1118 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 03:28:15 `cd /ProxyManager/pod-work/scraping_engine && source .venv/bin/activate && python -m pytest tests/uni` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- /ProxyManager/pod-work/scraping_engine/.venv/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, asy
  …[1570 caracteres omitidos]…
  fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.
  
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
- 2026-11-14 03:29:19 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping_engine/tests/unit/test_base.py _______
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_base.py'.
  Hint: make sure your test module
  …[335 caracteres omitidos]…
  gine.core'
  =========================== short test summary info ============================
  ERROR tests/unit/test_base.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.07s
- 2026-11-14 03:29:32 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping_engine/tests/unit/test_base.py _______
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_base.py'.
  Hint: make sure your test module
  …[335 caracteres omitidos]…
  gine.core'
  =========================== short test summary info ============================
  ERROR tests/unit/test_base.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.08s
- 2026-11-14 03:29:53 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping_engine/tests/unit/test_base.py _______
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_base.py'.
  Hint: make sure your test module
  …[340 caracteres omitidos]…
  core.base'
  =========================== short test summary info ============================
  ERROR tests/unit/test_base.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.07s
- 2026-11-14 03:30:12 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 2 aprobadas, 0 falladas/errores (exit 0)
