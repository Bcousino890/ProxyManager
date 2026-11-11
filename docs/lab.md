# Laboratorio local de la fase 3

`tests/lab_server.py` inicia un servidor HTTP solo en `127.0.0.1`, en un puerto temporal. Ofrece `/content` (texto esperado), `/captcha` (desafío CAPTCHA genérico), `/redirect` (302), `/slow` (respuesta lenta) y `/cut` (cuerpo truncado). `tests/test_local_lab.py` dirige `fetch` a ese servidor mediante un transporte de prueba. La resolución DNS simulada usa una IP pública ficticia para mantener intacta la validación de `guard_url`; el transporte redirige la conexión a loopback y no sale a Internet.

Ejecutar: `.venv/bin/pytest -q tests/test_local_lab.py`.

Este laboratorio comprueba que el clasificador actual distingue contenido esperado y un marcador CAPTCHA genérico, que no sigue redirecciones, y que reporta tiempo de espera y corte como errores de transporte. No reproduce DataDome ni ninguna protección real de terceros, y no demuestra capacidad de superarla. La evaluación con DataDome real sigue pendiente de acceso y autorización.
