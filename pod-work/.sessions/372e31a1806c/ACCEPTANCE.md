# Criterios de aceptación (verificados por el controlador con evidencia real)

Leyenda: [ ] activo · [x] cumplido · [B] bloqueado (avisado una vez) · [-] retirado (se puede reactivar)

- [B] (target) Ejecutar una petición real contra https://www.idealista.com/inmueble/112909923/ (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos) — HTTP 403 con protección antibot (p. ej. DataDome): bloqueo real del sitio, NO extracción exitosa
- [B] (verify) Ejecutar una prueba REAL ahora (run_tests o http_check/ejecución) y mostrar su salida — la prueba contra la URL objetivo está bloqueada (antibot); no es una prueba superada
- [-] (target) Ejecutar una petición/extracción real contra una URL de Idealista y reportar el resultado REAL — criterio de una tarea anterior (reactivable)
- [ ] (public) URL pública (no localhost) comprobada con http_check y estado 2xx/3xx
- [x] (target) Ejecutar una petición real contra https://example.com (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [x] (target) Ejecutar una petición real contra https://crawio.com/app/#playground (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [x] (deploy) Servicio ejecutándose y comprobado con una petición HTTP real DESPUÉS del último cambio
- [x] (git) Commit + push verificado (hash remoto == local) DESPUÉS del último cambio
- [x] (local) Servicio accesible localmente (localhost / túnel SSH): http_check 2xx/3xx a un puerto local DESPUÉS del último cambio
- [x] (target) Ejecutar una petición real contra https://www.bcousinoprop.com/ (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
