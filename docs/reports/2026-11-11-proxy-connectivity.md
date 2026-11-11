# Comprobación inicial de proxies — 11 noviembre 2026

Fuente: archivo local `data.txt` aportado por el propietario. No se copia al repositorio ni se reproducen direcciones, usuarios o contraseñas en este informe.

## Método

Se interpretaron diez entradas `host:port:usuario:contraseña`: un host, diez puertos, un usuario y una contraseña. Se hizo una petición GET por entrada a `https://zinto.app/robots.txt`, sitio propio del usuario, con HTTPS a través de un proxy HTTP autenticado. Se comparó el código HTTP y el SHA-256 del cuerpo con una petición directa. Sin paralelismo superior a dos y sin prueba de carga.

## Resultado

| Entrada | Conexión autenticada | HTTP | Coincide con petición directa | Tiempo observado |
|---|---|---:|---|---:|
| 1 | Sí | 200 | Sí | 851 ms |
| 2 | Sí | 200 | Sí | 842 ms |
| 3 | Sí | 200 | Sí | 497 ms |
| 4 | Sí | 200 | Sí | 460 ms |
| 5 | Sí | 200 | Sí | 521 ms |
| 6 | Sí | 200 | Sí | 406 ms |
| 7 | Sí | 200 | Sí | 413 ms |
| 8 | Sí | 200 | Sí | 444 ms |
| 9 | Sí | 200 | Sí | 348 ms |
| 10 | Sí | 200 | Sí | 416 ms |

La petición directa obtuvo HTTP 200 y 63 bytes. Las diez respuestas por proxy tuvieron el mismo código y contenido. Es **una única muestra por puerto**: no demuestra disponibilidad sostenida, diez IP de salida distintas, geolocalización, ASN ni clasificación ISP/residencial/datacenter. Esos campos permanecen como desconocidos. No se probó DataDome ni ningún sitio de terceros.
