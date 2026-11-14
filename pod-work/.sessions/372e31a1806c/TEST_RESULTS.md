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
- 2026-11-14 02:23:06 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → OK: 23 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 02:25:39 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5292 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.71s
- 2026-11-14 02:25:55 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.87s
- 2026-11-14 02:26:27 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.69s
- 2026-11-14 02:26:40 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.70s
- 2026-11-14 02:27:16 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.69s
- 2026-11-14 02:27:41 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.68s
- 2026-11-14 02:27:59 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.86s
- 2026-11-14 02:28:13 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.66s
- 2026-11-14 02:28:44 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.68s
- 2026-11-14 02:29:08 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.84s
- 2026-11-14 02:29:44 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.68s
- 2026-11-14 02:29:58 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ______________________ ERROR collecting tests/test_api.py ______________________
  ImportError while importing test module '/ProxyManager/tests/test_api.py'.
  Hint: make sure your test modules/packages have valid Python na
  …[876 caracteres omitidos]…
  lient  # noqa
  
  -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
  =========================== short test summary info ============================
  ERROR tests/test_api.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 warning, 1 error in 0.35s
- 2026-11-14 02:30:12 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.69s
- 2026-11-14 02:30:35 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.83s
- 2026-11-14 02:30:53 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.75s
- 2026-11-14 02:31:11 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.89s
- 2026-11-14 02:31:40 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.72s
- 2026-11-14 02:32:20 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 1.00s
- 2026-11-14 02:32:43 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.67s
- 2026-11-14 02:33:09 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.65s
- 2026-11-14 02:33:42 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.87s
- 2026-11-14 02:34:04 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.69s
- 2026-11-14 02:34:35 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.70s
- 2026-11-14 02:35:00 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.88s
- 2026-11-14 02:35:27 `/ProxyManager/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  _______________ test_scrape_classification_and_destination_guard _______________
  tests/test_api.py:54: in test_scrape_classification_and_destination_guard
      assert client.post("/scrape", headers=headers, json={"u
  …[5302 caracteres omitidos]…
  ture-warnings.html
  =========================== short test summary info ============================
  FAILED tests/test_api.py::test_scrape_classification_and_destination_guard - ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed, 1 warning in 0.69s
