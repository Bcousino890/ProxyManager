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
- 2026-11-14 03:31:40 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ____ ERROR collecting pod-work/scraping_engine/tests/unit/test_sessions.py _____
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_sessions.py'.
  Hint: make sure your test mo
  …[355 caracteres omitidos]…
  sions'
  =========================== short test summary info ============================
  ERROR tests/unit/test_sessions.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.08s
- 2026-11-14 03:31:48 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ____ ERROR collecting pod-work/scraping_engine/tests/unit/test_sessions.py _____
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_sessions.py'.
  Hint: make sure your test mo
  …[363 caracteres omitidos]…
  nager'
  =========================== short test summary info ============================
  ERROR tests/unit/test_sessions.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.09s
- 2026-11-14 03:32:03 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ____ ERROR collecting pod-work/scraping_engine/tests/unit/test_sessions.py _____
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_sessions.py'.
  Hint: make sure your test mo
  …[363 caracteres omitidos]…
  nager'
  =========================== short test summary info ============================
  ERROR tests/unit/test_sessions.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.08s
- 2026-11-14 03:32:13 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 2)
  ==================================== ERRORS ====================================
  ____ ERROR collecting pod-work/scraping_engine/tests/unit/test_sessions.py _____
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_sessions.py'.
  Hint: make sure your test mo
  …[441 caracteres omitidos]…
  okies'
  =========================== short test summary info ============================
  ERROR tests/unit/test_sessions.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  1 error in 0.09s
- 2026-11-14 03:32:24 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 6 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 03:34:25 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_diagnostics.py'.
  Hint: make sure your test
  …[279 caracteres omitidos]…
  fier import (
  E   ModuleNotFoundError: No module named 'scraping_engine.diagnostics'
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.06s
- 2026-11-14 03:34:45 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_diagnostics.py'.
  Hint: make sure your test
  …[299 caracteres omitidos]…
  duleNotFoundError: No module named 'scraping_engine.diagnostics.response_classifier'
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.06s
- 2026-11-14 03:34:58 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_diagnostics.py'.
  Hint: make sure your test
  …[299 caracteres omitidos]…
  duleNotFoundError: No module named 'scraping_engine.diagnostics.response_classifier'
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.06s
- 2026-11-14 03:35:12 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_diagnostics.py'.
  Hint: make sure your test
  …[300 caracteres omitidos]…
  duleNotFoundError: No module named 'scraping_engine.diagnostics.response_classifier'
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.06s
- 2026-11-14 03:36:01 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:27: in test_response_classifier_success
      classification = classifier.classify(
  E   AttributeError: '
  …[25 caracteres omitidos]…
  t has no attribute 'classify'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.08s
- 2026-11-14 03:36:11 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:27: in test_response_classifier_success
      classification = classifier.classify(
  E   AttributeError: '
  …[25 caracteres omitidos]…
  t has no attribute 'classify'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.08s
- 2026-11-14 03:36:53 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.08s
- 2026-11-14 03:37:04 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.08s
- 2026-11-14 03:37:19 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.09s
- 2026-11-14 03:37:38 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.08s
- 2026-11-14 03:37:46 `cd /ProxyManager/pod-work/scraping_engine && python -c "
import sys
sys.path.insert(0, 'src')
from s` → OK: 0 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 03:38:01 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.08s
- 2026-11-14 03:39:04 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_extractors.py ____
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_extractors.py'.
  Hint: make sure your test 
  …[277 caracteres omitidos]…
  enericExtractor
  E   ModuleNotFoundError: No module named 'scraping_engine.extractors'
  =========================== short test summary info ============================
  ERROR tests/unit/test_extractors.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.07s
- 2026-11-14 03:39:18 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_extractors.py ____
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_extractors.py'.
  Hint: make sure your test 
  …[285 caracteres omitidos]…
  tractor
  E   ModuleNotFoundError: No module named 'scraping_engine.extractors.generic'
  =========================== short test summary info ============================
  ERROR tests/unit/test_extractors.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.07s
- 2026-11-14 03:39:30 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_extractors.py ____
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_extractors.py'.
  Hint: make sure your test 
  …[293 caracteres omitidos]…
  tor
  E   ModuleNotFoundError: No module named 'src.scraping_engine.extractors.generic'
  =========================== short test summary info ============================
  ERROR tests/unit/test_extractors.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.07s
- 2026-11-14 03:39:42 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_extractors.py ____
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_extractors.py'.
  Hint: make sure your test 
  …[309 caracteres omitidos]…
  ule>
      from bs4 import BeautifulSoup
  E   ModuleNotFoundError: No module named 'bs4'
  =========================== short test summary info ============================
  ERROR tests/unit/test_extractors.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.07s
- 2026-11-14 03:39:57 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 03:40:14 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.20s
- 2026-11-14 03:40:27 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:40:40 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:41:10 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_success
      assert classification.http_code == 200
  E   AttributeError: 
  …[31 caracteres omitidos]…
   has no attribute 'http_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:41:27 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:40: in test_response_classifier_success
      assert classification.is_accessible is True
  E   AttributeEr
  …[40 caracteres omitidos]…
   no attribute 'is_accessible'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 03:41:44 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_success _______________________
  tests/unit/test_diagnostics.py:41: in test_response_classifier_success
      assert classification.is_content_valid is True
  E   Attribut
  …[46 caracteres omitidos]…
   attribute 'is_content_valid'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_success - Att...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:42:04 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:62: in test_response_classifier_datadome
      assert classification.status == ResponseStatus.CLIENT_ERR
  …[54 caracteres omitidos]…
  s no attribute 'CLIENT_ERROR'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - At...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.17s
- 2026-11-14 03:42:26 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:62: in test_response_classifier_datadome
      assert classification.status == ResponseStatus.CLIENT_ERR
  …[54 caracteres omitidos]…
  s no attribute 'CLIENT_ERROR'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - At...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.17s
- 2026-11-14 03:43:49 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:62: in test_response_classifier_datadome
      assert classification.status == ResponseStatus.CLIENT_ERR
  …[54 caracteres omitidos]…
  s no attribute 'CLIENT_ERROR'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - At...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.17s
- 2026-11-14 03:44:11 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:56: in test_response_classifier_datadome
      classification = classifier.classify_response(
  src/scrapi
  …[164 caracteres omitidos]…
  tus' has no attribute 'ERROR'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - At...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 03:44:25 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:56: in test_response_classifier_datadome
      classification = classifier.classify_response(
  src/scrapi
  …[164 caracteres omitidos]…
  tus' has no attribute 'ERROR'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - At...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.17s
- 2026-11-14 03:44:44 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:62: in test_response_classifier_datadome
      assert classification.status == ResponseStatus.CLIENT_ERR
  …[378 caracteres omitidos]…
  = ResponseStatus.CLIENT_ERROR
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - As...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 03:45:06 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[125 caracteres omitidos]…
  0x791b004991f0>.is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.17s
- 2026-11-14 03:45:20 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[125 caracteres omitidos]…
  0x745879b6cc50>.is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.18s
- 2026-11-14 03:45:29 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[125 caracteres omitidos]…
  0x74e430ff89e0>.is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.20s
- 2026-11-14 03:46:12 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[125 caracteres omitidos]…
  0x742bdcef8fb0>.is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.17s
- 2026-11-14 03:46:30 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 03:46:45 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.17s
- 2026-11-14 03:47:00 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 03:47:31 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.17s
- 2026-11-14 03:47:57 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.19s
- 2026-11-14 03:48:24 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 03:50:07 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 03:50:32 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[103 caracteres omitidos]…
  tatus_code=200).is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.18s
- 2026-11-14 03:50:45 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[103 caracteres omitidos]…
  tatus_code=200).is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.18s
- 2026-11-14 03:50:55 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[103 caracteres omitidos]…
  tatus_code=200).is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.18s
- 2026-11-14 03:51:32 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[103 caracteres omitidos]…
  tatus_code=200).is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.19s
- 2026-11-14 03:52:32 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[103 caracteres omitidos]…
  tatus_code=200).is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.18s
- 2026-11-14 03:52:52 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[103 caracteres omitidos]…
  tatus_code=200).is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.18s
- 2026-11-14 03:53:19 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:79: in test_response_classifier_empty_content
      assert classification.is_content_valid is False
  E  
  …[103 caracteres omitidos]…
  tatus_code=200).is_content_valid
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.19s
- 2026-11-14 03:53:37 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 03:53:48 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.19s
- 2026-11-14 03:54:08 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.19s
- 2026-11-14 03:54:47 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_datadome _______________________
  tests/unit/test_diagnostics.py:65: in test_response_classifier_datadome
      assert classification.is_accessible is False
  E   assert T
  …[106 caracteres omitidos]…
  tatus_code=403).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_datadome - as...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 03:55:00 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:80: in test_response_classifier_empty_content
      assert len(classification.evidence) > 0
  E   Attribu
  …[36 caracteres omitidos]…
  ject has no attribute 'evidence'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.19s
- 2026-11-14 03:55:14 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:80: in test_response_classifier_empty_content
      assert len(classification.evidence) > 0
  E   assert 
  …[105 caracteres omitidos]…
  , http_status_code=200).evidence
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.20s
- 2026-11-14 03:55:27 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 5 aprobadas, 1 falladas/errores (exit 1)
  .....F
  =================================== FAILURES ===================================
  ______________________ test_protection_detector_detection ______________________
  tests/unit/test_diagnostics.py:89: in test_protection_detector_detection
      classification = ResponseClassification(
  E   TypeError
  …[51 caracteres omitidos]…
  ed keyword argument 'content'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_detection - T...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 5 passed in 0.18s
- 2026-11-14 03:55:40 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 5 aprobadas, 1 falladas/errores (exit 1)
  .....F
  =================================== FAILURES ===================================
  ______________________ test_protection_detector_detection ______________________
  tests/unit/test_diagnostics.py:97: in test_protection_detector_detection
      result = detector.detect(classification, classificatio
  …[75 caracteres omitidos]…
  ect has no attribute 'detect'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_detection - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 5 passed in 0.19s
- 2026-11-14 03:55:52 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 5 aprobadas, 1 falladas/errores (exit 1)
  .....F
  =================================== FAILURES ===================================
  ______________________ test_protection_detector_detection ______________________
  tests/unit/test_diagnostics.py:104: in test_protection_detector_detection
      assert result.is_protected is True
  E   AttributeError
  …[114 caracteres omitidos]…
  ===================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_detection - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 5 passed in 0.19s
  
  sys:1: RuntimeWarning: coroutine 'ProtectionDetector.detect_protection' was never awaited
- 2026-11-14 03:56:04 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  .venv/lib/python3.12/site-packages/_pytest/python.py:617: in _importtestmodule
      mod = import_path(self.path, mode=importmode, root=self
  …[917 caracteres omitidos]…
  detect_protection(
  E                
  E   SyntaxError: 'await' outside async function
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.12s
- 2026-11-14 03:56:30 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  .venv/lib/python3.12/site-packages/_pytest/python.py:617: in _importtestmodule
      mod = import_path(self.path, mode=importmode, root=self
  …[917 caracteres omitidos]…
  detect_protection(
  E                
  E   SyntaxError: 'await' outside async function
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.12s
- 2026-11-14 03:56:51 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  .venv/lib/python3.12/site-packages/_pytest/python.py:617: in _importtestmodule
      mod = import_path(self.path, mode=importmode, root=self
  …[917 caracteres omitidos]…
  detect_protection(
  E                
  E   SyntaxError: 'await' outside async function
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.13s
- 2026-11-14 03:57:12 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      classification = classifier.classify_response(**response)
  E  
  …[70 caracteres omitidos]…
  eyword argument 'status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - TypeE...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 03:57:25 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      classification = classifier.classify_response(**response)
  E  
  …[70 caracteres omitidos]…
  eyword argument 'status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - TypeE...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:57:43 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:38: in test_response_classifier_basic
      assert classification.content_length == 34
  E   assert None ==
  …[86 caracteres omitidos]…
  atus_code=200).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:57:54 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:38: in test_response_classifier_basic
      assert classification.content_length == 34
  E   assert None ==
  …[86 caracteres omitidos]…
  atus_code=200).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:58:23 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:38: in test_response_classifier_basic
      assert classification.content_length == 34
  E   assert None ==
  …[86 caracteres omitidos]…
  atus_code=200).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:58:42 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:38: in test_response_classifier_basic
      assert classification.content_length == 34
  E   assert None ==
  …[86 caracteres omitidos]…
  atus_code=200).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 03:59:06 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:38: in test_response_classifier_basic
      assert classification.content_length == 34
  E   assert None ==
  …[86 caracteres omitidos]…
  atus_code=200).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 04:00:20 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:38: in test_response_classifier_basic
      assert classification.content_length == 34
  E   assert None ==
  …[86 caracteres omitidos]…
  atus_code=200).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 04:02:50 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:38: in test_response_classifier_basic
      assert classification.content_length == 34
  E   assert None ==
  …[86 caracteres omitidos]…
  atus_code=200).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 04:03:06 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:38: in test_response_classifier_basic
      assert classification.content_length == 34
  E   assert 30 == 3
  …[82 caracteres omitidos]…
  atus_code=200).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 04:03:18 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:54: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[75 caracteres omitidos]…
  eyword argument 'status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - T...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.17s
- 2026-11-14 04:03:30 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:56: in test_response_classifier_data_dome
      assert classification.status == ResponseStatus.CLIENT_ER
  …[369 caracteres omitidos]…
  = ResponseStatus.CLIENT_ERROR
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:03:40 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_protection_detector_no_protection ____________________
  tests/unit/test_diagnostics.py:74: in test_protection_detector_no_protection
      assert result.is_protected is False
  E   AttributeEr
  …[114 caracteres omitidos]…
  ======================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_no_protection
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.17s
  
  sys:1: RuntimeWarning: coroutine 'ProtectionDetector.detect_protection' was never awaited
- 2026-11-14 04:04:03 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_protection_detector_no_protection ____________________
  tests/unit/test_diagnostics.py:67: in test_protection_detector_no_protection
      result = detector.detect_protection(
  src/scraping_e
  …[499 caracteres omitidos]…
  g pattern on a bytes-like object
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_no_protection
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.18s
- 2026-11-14 04:04:37 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_protection_detector_no_protection ____________________
  tests/unit/test_diagnostics.py:67: in test_protection_detector_no_protection
      result = detector.detect_protection(
  src/scraping_e
  …[499 caracteres omitidos]…
  g pattern on a bytes-like object
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_no_protection
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.18s
- 2026-11-14 04:05:20 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 5 aprobadas, 1 falladas/errores (exit 1)
  .....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:91: in test_response_classifier_empty_content
      classification = classifier.classify_response(**re
  …[78 caracteres omitidos]…
  d keyword argument 'status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 5 passed in 0.17s
- 2026-11-14 04:05:37 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 6 aprobadas, 1 falladas/errores (exit 1)
  ......F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_timeout _______________________
  tests/unit/test_diagnostics.py:109: in test_response_classifier_timeout
      classification = classifier.classify_response(**respon
  …[77 caracteres omitidos]…
  eyword argument 'status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_timeout - Typ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 6 passed in 0.17s
- 2026-11-14 04:06:49 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 6 aprobadas, 1 falladas/errores (exit 1)
  ......F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_timeout _______________________
  tests/unit/test_diagnostics.py:109: in test_response_classifier_timeout
      classification = classifier.classify_response(**respon
  …[77 caracteres omitidos]…
  eyword argument 'status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_timeout - Typ...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 6 passed in 0.17s
- 2026-11-14 04:07:32 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      classification = classifier.classify_response(**response)
  E  
  …[75 caracteres omitidos]…
  d argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - TypeE...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 04:07:46 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      classification = classifier.classify_response(**response)
  src
  …[136 caracteres omitidos]…
  p_status_code' is not defined
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - NameE...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 04:09:09 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      classification = classifier.classify_response(**response)
  src
  …[136 caracteres omitidos]…
  p_status_code' is not defined
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - NameE...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.19s
- 2026-11-14 04:09:55 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:54: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[80 caracteres omitidos]…
  d argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - T...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:11:05 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:54: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[80 caracteres omitidos]…
  d argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - T...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.19s
- 2026-11-14 04:11:27 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:54: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[80 caracteres omitidos]…
  d argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - T...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:11:53 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_protection_detector_no_protection ____________________
  tests/unit/test_diagnostics.py:67: in test_protection_detector_no_protection
      result = detector.detect_protection(
  src/scraping_e
  …[197 caracteres omitidos]…
  word argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_no_protection
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.19s
- 2026-11-14 04:12:16 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_protection_detector_no_protection ____________________
  tests/unit/test_diagnostics.py:67: in test_protection_detector_no_protection
      result = detector.detect_protection(
  src/scraping_e
  …[197 caracteres omitidos]…
  word argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_no_protection
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.20s
- 2026-11-14 04:13:31 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_protection_detector_no_protection ____________________
  tests/unit/test_diagnostics.py:67: in test_protection_detector_no_protection
      result = detector.detect_protection(
  src/scraping_e
  …[197 caracteres omitidos]…
  word argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_no_protection
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.17s
- 2026-11-14 04:14:09 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      classification = classifier.classify_response(**response)
  src
  …[191 caracteres omitidos]…
  eyword argument 'status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - TypeE...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 04:14:32 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:37: in test_response_classifier_basic
      assert classification.http_status_code == 200
  E   AttributeEr
  …[73 caracteres omitidos]…
   Did you mean: 'status_code'?
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Attri...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.19s
- 2026-11-14 04:14:42 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:58: in test_response_classifier_data_dome
      assert classification.http_status_code == 403
  E   Attrib
  …[78 caracteres omitidos]…
   Did you mean: 'status_code'?
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.20s
- 2026-11-14 04:14:52 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 4 aprobadas, 1 falladas/errores (exit 1)
  ....F
  =================================== FAILURES ===================================
  ____________________ test_protection_detector_no_protection ____________________
  tests/unit/test_diagnostics.py:67: in test_protection_detector_no_protection
      result = detector.detect_protection(
  src/scraping_e
  …[197 caracteres omitidos]…
  word argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_protection_detector_no_protection
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 4 passed in 0.19s
- 2026-11-14 04:15:09 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 5 aprobadas, 1 falladas/errores (exit 1)
  .....F
  =================================== FAILURES ===================================
  ____________________ test_response_classifier_empty_content ____________________
  tests/unit/test_diagnostics.py:91: in test_response_classifier_empty_content
      classification = classifier.classify_response(**re
  …[83 caracteres omitidos]…
  word argument 'http_status_code'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_empty_content
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 5 passed in 0.18s
- 2026-11-14 04:15:27 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 6 aprobadas, 1 falladas/errores (exit 1)
  ......F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_timeout _______________________
  tests/unit/test_diagnostics.py:111: in test_response_classifier_timeout
      assert classification.status == ResponseStatus.TIMEOUT
  …[346 caracteres omitidos]…
  ut'> = ResponseStatus.TIMEOUT
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_timeout - ass...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 6 passed in 0.20s
- 2026-11-14 04:16:36 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 6 aprobadas, 1 falladas/errores (exit 1)
  ......F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_timeout _______________________
  tests/unit/test_diagnostics.py:111: in test_response_classifier_timeout
      assert classification.status == ResponseStatus.TIMEOUT
  …[346 caracteres omitidos]…
  ut'> = ResponseStatus.TIMEOUT
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_timeout - ass...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 6 passed in 0.20s
- 2026-11-14 04:16:43 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 6 aprobadas, 1 falladas/errores (exit 1)
  ......F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_timeout _______________________
  tests/unit/test_diagnostics.py:111: in test_response_classifier_timeout
      assert classification.status == ResponseStatus.TIMEOUT
  …[346 caracteres omitidos]…
  ut'> = ResponseStatus.TIMEOUT
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_timeout - ass...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 6 passed in 0.18s
- 2026-11-14 04:17:26 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 6 aprobadas, 1 falladas/errores (exit 1)
  ......F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_timeout _______________________
  tests/unit/test_diagnostics.py:111: in test_response_classifier_timeout
      assert classification.status == ResponseStatus.TIMEOUT
  …[276 caracteres omitidos]…
  ut'> = ResponseStatus.TIMEOUT
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_timeout - Ass...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 6 passed in 0.18s
- 2026-11-14 04:18:46 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 6 aprobadas, 1 falladas/errores (exit 1)
  ......F
  =================================== FAILURES ===================================
  _______________________ test_response_classifier_timeout _______________________
  tests/unit/test_diagnostics.py:111: in test_response_classifier_timeout
      assert classification.status == ResponseStatus.TIMEOUT
  …[276 caracteres omitidos]…
  ut'> = ResponseStatus.TIMEOUT
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_timeout - Ass...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 6 passed in 0.20s
- 2026-11-14 04:19:17 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 7 aprobadas, 1 falladas/errores (exit 1)
  .......F
  =================================== FAILURES ===================================
  __________________________ test_detection_result_repr __________________________
  tests/unit/test_diagnostics.py:126: in test_detection_result_repr
      assert 'DATADOME' in repr_str
  E   AssertionError: assert 'D
  …[75 caracteres omitidos]…
  lt object at 0x79ef933720c0>'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_detection_result_repr - Assertion...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 7 passed in 0.17s
- 2026-11-14 04:19:37 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 15 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 04:20:45 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → OK: 15 aprobadas, 0 falladas/errores (exit 0)
- 2026-11-14 04:21:36 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping_engine/tests/unit/test_base.py _______
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_base.py'.
  Hint: make sure your test module
  …[646 caracteres omitidos]…
  oxyManager/pod-work/scraping_engine/src/scraping_engine/diagnostics/response_classifier.py)
  =========================== short test summary info ============================
  ERROR tests/unit/test_base.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.21s
- 2026-11-14 04:21:58 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ______ ERROR collecting pod-work/scraping_engine/tests/unit/test_base.py _______
  tests/unit/test_base.py:2: in <module>
      from scraping_engine.core.base import BaseEngine, ScrapingResult
  src/scraping_engine/__init__.p
  …[309 caracteres omitidos]…
  ror: name 'ProtectionType' is not defined
  =========================== short test summary info ============================
  ERROR tests/unit/test_base.py - NameError: name 'ProtectionType' is not defined
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.21s
- 2026-11-14 04:22:09 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_diagnostics.py'.
  Hint: make sure your test
  …[412 caracteres omitidos]…
  ger/pod-work/scraping_engine/src/scraping_engine/diagnostics/response_classifier.py)
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.22s
- 2026-11-14 04:22:25 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:32: in test_response_classifier_basic
      classification = classifier.classify_response(**response)
  E  
  …[52 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Attri...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.35s
- 2026-11-14 04:22:41 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:32: in test_response_classifier_basic
      classification = ResponseClassifier.classify(**response)
  E   
  …[62 caracteres omitidos]…
  word argument 'response_time'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - TypeE...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.30s
- 2026-11-14 04:22:58 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.30s
- 2026-11-14 04:23:11 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.32s
- 2026-11-14 04:23:44 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.32s
- 2026-11-14 04:24:17 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.31s
- 2026-11-14 04:24:54 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.31s
- 2026-11-14 04:25:12 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.30s
- 2026-11-14 04:25:52 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.30s
- 2026-11-14 04:26:09 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:35: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.33s
- 2026-11-14 04:26:30 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.31s
- 2026-11-14 04:27:05 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.30s
- 2026-11-14 04:27:30 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.30s
- 2026-11-14 04:28:37 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.33s
- 2026-11-14 04:29:02 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.32s
- 2026-11-14 04:29:22 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.32s
- 2026-11-14 04:31:03 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 04:32:05 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:33: in test_response_classifier_basic
      assert classification.is_accessible is True
  E   AssertionErro
  …[258 caracteres omitidos]…
  r_message=None).is_accessible
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 04:32:28 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:37: in test_response_classifier_basic
      assert classification.content_length == 30
  E   AssertionError
  …[225 caracteres omitidos]…
  _message=None).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 04:32:44 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_basic
      assert classification.content_length == 30
  E   AssertionError
  …[225 caracteres omitidos]…
  _message=None).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.19s
- 2026-11-14 04:33:01 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_basic
      assert classification.content_length == 30
  E   AssertionError
  …[225 caracteres omitidos]…
  _message=None).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 04:33:42 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_basic
      assert classification.content_length == 30
  E   AssertionError
  …[225 caracteres omitidos]…
  _message=None).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.18s
- 2026-11-14 04:33:59 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_basic
      assert classification.content_length == 30
  E   AssertionError
  …[225 caracteres omitidos]…
  _message=None).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.21s
- 2026-11-14 04:34:47 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 2 aprobadas, 1 falladas/errores (exit 1)
  ..F
  =================================== FAILURES ===================================
  ________________________ test_response_classifier_basic ________________________
  tests/unit/test_diagnostics.py:39: in test_response_classifier_basic
      assert classification.content_length == 30
  E   AssertionError
  …[225 caracteres omitidos]…
  _message=None).content_length
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_basic - Asser...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 2 passed in 0.17s
- 2026-11-14 04:35:09 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.19s
- 2026-11-14 04:35:30 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:35:55 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:36:11 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.17s
- 2026-11-14 04:36:25 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ==================================== ERRORS ====================================
  ___ ERROR collecting pod-work/scraping_engine/tests/unit/test_diagnostics.py ___
  ImportError while importing test module '/ProxyManager/pod-work/scraping_engine/tests/unit/test_diagnostics.py'.
  Hint: make sure your test
  …[496 caracteres omitidos]…
  (/ProxyManager/pod-work/scraping_engine/src/scraping_engine/diagnostics/evidence.py)
  =========================== short test summary info ============================
  ERROR tests/unit/test_diagnostics.py
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 error in 0.07s
- 2026-11-14 04:36:40 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:37:29 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:37:43 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:38:18 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.20s
- 2026-11-14 04:38:52 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[57 caracteres omitidos]…
  attribute 'classify_response'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.19s
- 2026-11-14 04:39:38 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:55: in test_response_classifier_data_dome
      classification = classifier.classify_response(**response
  …[77 caracteres omitidos]…
  word argument 'response_time'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - T...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:39:50 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:57: in test_response_classifier_data_dome
      assert classification.status == ResponseStatus.DATA_DOME
  …[59 caracteres omitidos]…
  ect has no attribute 'status'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.18s
- 2026-11-14 04:40:15 `/ProxyManager/pod-work/scraping_engine/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 3 aprobadas, 1 falladas/errores (exit 1)
  ...F
  =================================== FAILURES ===================================
  ______________________ test_response_classifier_data_dome ______________________
  tests/unit/test_diagnostics.py:57: in test_response_classifier_data_dome
      assert classification.status == ResponseStatus.DATA_DOME
  …[59 caracteres omitidos]…
  ect has no attribute 'status'
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed, 3 passed in 0.19s
- 2026-11-14 04:40:31 `cd /ProxyManager/pod-work/scraping_engine && python -m pytest tests/unit/test_diagnostics.py::test_r` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 4)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- /usr/local/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, platformdirs-4.14.5
  collecting ... co
  …[779 caracteres omitidos]…
  st summary info ============================
  ERROR tests/unit/test_diagnostics.py
  =============================== 1 error in 0.06s ===============================
  
  ERROR: found no collectors for /ProxyManager/pod-work/scraping_engine/tests/unit/test_diagnostics.py::test_response_classifier_data_dome
- 2026-11-14 04:40:48 `cd /ProxyManager/pod-work/scraping_engine && source .venv/bin/activate && python -m pytest tests/uni` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.7.0 -- /ProxyManager/pod-work/scraping_engine/.venv/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, asy
  …[1002 caracteres omitidos]…
  tatus'
  
  tests/unit/test_diagnostics.py:57: AttributeError
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  ============================== 1 failed in 0.05s ===============================
- 2026-11-14 04:41:22 `cd /ProxyManager/pod-work/scraping_engine && source .venv/bin/activate && python -m pytest tests/uni` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.7.0 -- /ProxyManager/pod-work/scraping_engine/.venv/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, asy
  …[1002 caracteres omitidos]…
  tatus'
  
  tests/unit/test_diagnostics.py:57: AttributeError
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - A...
  ============================== 1 failed in 0.04s ===============================
- 2026-11-14 04:41:41 `cd /ProxyManager/pod-work/scraping_engine && source .venv/bin/activate && python -m pytest tests/uni` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.7.0 -- /ProxyManager/pod-work/scraping_engine/.venv/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, asy
  …[1044 caracteres omitidos]…
  not defined
  
  tests/unit/test_diagnostics.py:58: NameError
  =========================== short test summary info ============================
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_data_dome - N...
  ============================== 1 failed in 0.06s ===============================
- 2026-11-14 04:42:29 `cd /ProxyManager/pod-work/scraping_engine && source .venv/bin/activate && python -m pytest tests/uni` → FALLÓ: 2 aprobadas, 4 falladas/errores (exit 1)
  ============================= test session starts ==============================
  platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.7.0 -- /ProxyManager/pod-work/scraping_engine/.venv/bin/python
  cachedir: .pytest_cache
  rootdir: /ProxyManager
  configfile: pyproject.toml
  plugins: anyio-4.16.0, asy
  …[5199 caracteres omitidos]…
  st_diagnostics.py::test_protection_detector_no_protection
  FAILED tests/unit/test_diagnostics.py::test_response_classifier_timeout - Ass...
  FAILED tests/unit/test_diagnostics.py::test_detection_result_repr - NameError...
  ========================= 4 failed, 2 passed in 0.07s ==========================
