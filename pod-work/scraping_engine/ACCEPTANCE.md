# Criterios de aceptación (verificados por el controlador con evidencia real)

Leyenda: [ ] activo · [x] cumplido · [B] bloqueado (avisado una vez) · [-] retirado (se puede reactivar)

- [ ] (verify) Ejecutar una prueba REAL ahora (run_tests o http_check/ejecución) y mostrar su salida
- [ ] (deploy) Servicio ejecutándose y comprobado con una petición HTTP real DESPUÉS del último cambio
- [ ] (git) Commit + push verificado (hash remoto == local) DESPUÉS del último cambio
- [ ] (public) URL pública (no localhost) comprobada con http_check y estado 2xx/3xx
- [x] (target) Ejecutar una petición real contra https://example.com (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [x] (target) Ejecutar una petición real contra https://www.bcousinoprop.com/ (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [x] (verify) Ejecutar una prueba REAL ahora (run_tests o http_check/ejecución) y mostrar su salida
- [x] (deploy) Servicio ejecutándose y comprobado con una petición HTTP real DESPUÉS del último cambio
- [x] (git) Commit + push verificado (hash remoto == local) DESPUÉS del último cambio
