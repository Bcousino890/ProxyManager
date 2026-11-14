# Criterios de aceptación (verificados por el controlador con evidencia real)

- [x] (target) Ejecutar una petición real contra https://www.idealista.com/inmueble/112909923/ (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [x] (verify) Ejecutar una prueba REAL ahora (run_tests o http_check/ejecución) y mostrar su salida
- [x] (deploy) Servicio ejecutándose y comprobado con una petición HTTP real DESPUÉS del último cambio
- [x] (git) Commit + push verificado (hash remoto == local) DESPUÉS del último cambio
- [x] (public) URL pública (no localhost) comprobada con http_check y estado 2xx/3xx
- [ ] (target) Ejecutar una petición real contra https://crawio.com/ (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [ ] (target) Ejecutar una petición real contra https://www.idealista.com/inmueble/112909923/ (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [ ] (target) Ejecutar una petición real contra https://example.com (http_check o el propio servicio) y reportar el resultado REAL (estado, bloqueo, datos)
- [ ] (target) Ejecutar una petición/extracción real contra una URL de Idealista y reportar el resultado REAL
- [ ] (verify) Ejecutar una prueba REAL ahora (run_tests o http_check/ejecución) y mostrar su salida
- [ ] (deploy) Servicio ejecutándose y comprobado con una petición HTTP real DESPUÉS del último cambio
- [ ] (git) Commit + push verificado (hash remoto == local) DESPUÉS del último cambio
- [ ] (public) URL pública (no localhost) comprobada con http_check y estado 2xx/3xx
