# Criterios de aceptación (verificados por el controlador con evidencia real)

Leyenda: [ ] activo · [x] cumplido · [B] bloqueado (avisado una vez) · [-] retirado (se puede reactivar)

- [ ] (target) Ejecutar una petición real contra https://example.com (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [ ] (target) Ejecutar una petición real contra https://crawio.com/app/#playground (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [ ] (target) Ejecutar una petición real contra https://www.idealista.com/inmueble/112909923/ (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [ ] (verify) Ejecutar una prueba REAL ahora (run_tests o http_check/ejecución) y mostrar su salida
- [ ] (deploy) Servicio ejecutándose y comprobado con una petición HTTP real DESPUÉS del último cambio
- [ ] (git) Commit + push verificado (hash remoto == local) DESPUÉS del último cambio
- [ ] (local) Servicio accesible localmente (localhost / túnel SSH): http_check 2xx/3xx a un puerto local DESPUÉS del último cambio
