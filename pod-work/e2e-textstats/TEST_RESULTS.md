# Resultados de pruebas

- 2026-11-13 23:38:56 `/root/e2e/repo/pod-work/e2e-textstats/.venv/bin/python -m pytest -q -x --tb=short` → FALLÓ: 0 aprobadas, 1 falladas/errores (exit 1)
  F
  =================================== FAILURES ===================================
  _______________________________ test_word_count ________________________________
  tests/test_core.py:5: in test_word_count
      assert word_count("hola  mundo") == 2  # Dos espacios seguidos, debe ser 2 palabras
      ^^^
  …[67 caracteres omitidos]…
  2
  E    +  where 3 = word_count('hola  mundo')
  =========================== short test summary info ============================
  FAILED tests/test_core.py::test_word_count - AssertionError: assert 3 == 2
  !!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
  1 failed in 0.03s
- 2026-11-13 23:39:02 `/root/e2e/repo/pod-work/e2e-textstats/.venv/bin/python -m pytest -q -x --tb=short` → OK: 1 aprobadas, 0 falladas/errores (exit 0)
