# Criterios de aceptación (verificados por el controlador con evidencia real)

Leyenda: [ ] activo · [x] cumplido · [B] bloqueado (avisado una vez) · [-] retirado (se puede reactivar)

- [ ] (target) Ejecutar una petición real contra https://example.com (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [ ] (target) Ejecutar una petición real contra https://www.bcousinoprop.com/ (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [ ] (verify) Ejecutar una prueba REAL ahora (run_tests o http_check/ejecución) y mostrar su salida
- [ ] (deploy) Servicio ejecutándose y comprobado con una petición HTTP real DESPUÉS del último cambio
- [ ] (git) Commit + push verificado (hash remoto == local) DESPUÉS del último cambio
