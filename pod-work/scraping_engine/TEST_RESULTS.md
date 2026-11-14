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
