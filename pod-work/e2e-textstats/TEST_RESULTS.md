# Resultados de pruebas

- 2026-11-13 23:41:49 `/root/e2e/repo/pod-work/e2e-textstats/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  F
  =================================== FAILURES ===================================
  _________________________ test_word_count_double_space _________________________
  tests/test_core.py:4: in test_word_count_double_space
      assert textstats.core.word_count("hola  mundo") == 2
  E   AssertionError: asser
  …[332 caracteres omitidos]…
  rc/textstats/core.py'> = textstats.core
  =========================== short test summary info ============================
  FAILED tests/test_core.py::test_word_count_double_space - AssertionError: ass...
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed in 0.03s
- 2026-11-13 23:42:06 `/root/e2e/repo/pod-work/e2e-textstats/.venv/bin/python -m pytest -q -x --tb=short` → OK: 3 aprobadas, 0 falladas/errores (exit 0)
