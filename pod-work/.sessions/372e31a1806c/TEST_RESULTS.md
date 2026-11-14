# Resultados de pruebas

- 2026-11-14 02:07:31 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 02:09:12 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 02:10:05 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 1)
  /usr/local/bin/python3: No module named pytest
- 2026-11-14 02:10:15 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 5)
  no tests ran in 0.01s
- 2026-11-14 02:10:18 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ______________________ ERROR collecting tests/test_api.py ______________________
  ImportError while importing test module '/ProxyManager/tests/test_api.py'.
  Hint: make sure your test modules/packages have valid Python na
  …[227 caracteres omitidos]…
  odule>
      from fastapi.testclient import TestClient
  E   ModuleNotFoundError: No module named 'fastapi'
  =========================== short test summary info ============================
  ERROR test_api.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.09s
- 2026-11-14 02:10:29 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 5)
  no tests ran in 0.01s
- 2026-11-14 02:11:45 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 5)
  no tests ran in 0.01s
- 2026-11-14 02:11:48 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ______________________ ERROR collecting tests/test_api.py ______________________
  ImportError while importing test module '/ProxyManager/tests/test_api.py'.
  Hint: make sure your test modules/packages have valid Python na
  …[713 caracteres omitidos]…
   TestClient  # noqa
  
  -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
  =========================== short test summary info ============================
  ERROR test_api.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 warning, 1 error in 0.35s
- 2026-11-14 02:11:57 `python3 -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ______________________ ERROR collecting tests/test_api.py ______________________
  ImportError while importing test module '/ProxyManager/tests/test_api.py'.
  Hint: make sure your test modules/packages have valid Python na
  …[713 caracteres omitidos]…
   TestClient  # noqa
  
  -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
  =========================== short test summary info ============================
  ERROR test_api.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 warning, 1 error in 0.33s
- 2026-11-14 02:12:52 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 02:14:52 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 02:15:24 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 02:17:00 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 02:18:26 `cd /ProxyManager && python -m pytest tests/test_fetch.py::test_fetch_example_com -v` → FALLÓ: 0 aprobadas, 0 falladas/errores (exit 4)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- /usr/local/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, platformdirs-4.14.5
  collecting ... collected 0 items
  
  ============================ no tests ran in 0.00s =============================
  
  ERROR: file or directory not found: tests/test_fetch.py::test_fetch_example_com
- 2026-11-14 02:19:00 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 02:19:58 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
