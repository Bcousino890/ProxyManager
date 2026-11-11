# PROYECTO TFG — PLATAFORMA PROFESIONAL DE INVESTIGACIÓN DE DATADOME, CAPTCHA, SESIONES HTTP Y BENCHMARKING

## MISIÓN PRINCIPAL

Actúa como un equipo de ingeniería de software y ciberseguridad de nivel senior, compuesto por:

- Arquitecto principal de software.
- Ingeniero especializado en protocolos HTTP y sistemas antibot.
- Especialista en DataDome y mecanismos CAPTCHA.
- Ingeniero de redes, proxies ISP y residenciales.
- Desarrollador backend Python.
- Ingeniero DevOps e infraestructura Linux.
- Especialista en seguridad de aplicaciones.
- Ingeniero de automatización y QA.
- Ingeniero de rendimiento y pruebas de carga.
- Analista de costes de infraestructura.
- Responsable de documentación e investigación académica.

Tu misión es diseñar, desarrollar, desplegar, probar, optimizar y documentar una plataforma tecnológica real para mi Trabajo de Fin de Grado universitario.

**No quiero únicamente una propuesta, una prueba de concepto visual o un repositorio con código sin ejecutar. Quiero un producto funcional, verificable, desplegado y preparado para ser evaluado mediante API.**

Dispones de autorización general para tomar decisiones técnicas y trabajar autónomamente en los sistemas propios del proyecto.

Solo deberás solicitar aprobación para pagos, contratos, operaciones destructivas irreversibles o actuaciones que necesiten autorización externa.

---

# 1. CONTEXTO ACADÉMICO

Estoy desarrollando mi TFG sobre:

**Arquitectura, análisis y evaluación experimental de sistemas avanzados de protección antibot: DataDome, CAPTCHA, persistencia de sesiones, cookies HTTP y redes residenciales e ISP.**

La universidad realizará una evaluación práctica del software.

El objetivo es construir una infraestructura capaz de procesar y medir hasta 100.000 solicitudes HTTP, con una API accesible para los profesores.

Se ha indicado que podrían utilizarse como referencias tecnológicas sitios como:

- Idealista.
- Vinted.
- Realtor.com.
- Airbnb.

Estos dominios son referencias del trabajo académico, no una autorización automática para ejecutar pruebas sobre ellos.

Antes de realizar solicitudes automatizadas o pruebas de carga contra servicios de terceros, se deberá verificar la autorización correspondiente. No se desarrollarán procedimientos de evasión de controles de acceso en sitios ajenos.

Para demostrar DataDome real, utiliza una instalación de evaluación legítima proporcionada por la universidad, por el propietario de la web o mediante acceso autorizado del fabricante.

**No sustituyas DataDome real por una imitación sin identificar claramente la diferencia.**

Si falta acceso a DataDome, completa el resto del sistema y deja la integración preparada, indicando las validaciones pendientes.

---

# 2. OBJETIVOS Y CRITERIOS DE ÉXITO

Construir un servicio profesional que incluya:

1. API REST pública y segura.
2. Gestor propio de conexiones proxy.
3. Soporte para proxies ISP, residenciales y datacenter.
4. Gestión de sesiones HTTP autorizadas.
5. Gestión persistente y segura de cookies.
6. Análisis de desafíos CAPTCHA.
7. Evaluación de respuestas de DataDome en un entorno autorizado.
8. Sistema de autenticación.
9. Trabajadores de procesamiento asíncrono.
10. Benchmark de 100.000 solicitudes.
11. Monitorización en tiempo real.
12. Control automático de gastos.
13. Panel web administrativo.
14. Despliegue en VPS mensual.
15. Recuperación automática ante fallos.
16. Métricas históricas durante al menos 30 días.
17. Documentación completa para los profesores.
18. Pruebas automatizadas y evidencias reproducibles.

No confundas una solicitud enviada con una solicitud correctamente procesada.

El éxito deberá medirse verificando que se devuelve el contenido esperado y que se cumplen los criterios establecidos para cada experimento.

No consideres exitoso un HTTP 200 si contiene una página de bloqueo, un CAPTCHA sin completar o contenido distinto al esperado.

---

# 3. PRESUPUESTO Y RESTRICCIONES

## Presupuesto

Presupuesto máximo inicial: **25 USD equivalentes para el primer mes**.

Debe incluir, cuando corresponda:

- VPS.
- IPv4.
- Impuestos.
- Transferencia.
- Servicios de proxy.
- Software con licencia.
- Costes mínimos.
- Renovaciones.
- Cargos adicionales.

No supongas que el presupuesto permite pagar una licencia comercial de DataDome o transferencias ilimitadas mediante proxies residenciales.

Si el acceso a DataDome real supera el presupuesto, informa del impedimento y prepara una solicitud de acceso académico o un entorno autorizado ya existente.

## Servidor

El proyecto debe permanecer funcionando de manera continua durante al menos 30 días.

Investiga y compara:

- OVHcloud VPS-1.
- OVHcloud VPS-2.
- Hetzner CX23.
- Hetzner CX33.
- Otras alternativas fiables si son más económicas.

Comprueba precios actuales, disponibilidad, CPU, RAM, almacenamiento, ancho de banda y condiciones de renovación.

Prioriza:

- Facturación mensual económica.
- Linux Ubuntu LTS.
- 4 GB de RAM como mínimo deseable.
- 8 GB si el presupuesto lo permite.
- Almacenamiento SSD o NVMe.
- Dirección IPv4 pública.
- Docker.
- Reinicios automáticos.

No sobredimensiones el servidor.

Si una arquitectura con clientes HTTP permite realizar las pruebas legítimas sin utilizar navegadores completos, prioriza esa solución para reducir CPU y RAM.

---

# 4. INVESTIGACIÓN DE PROXIES

Realiza una investigación actualizada directamente en las páginas oficiales de:

- IPRoyal.
- Proxy-Cheap.
- Webshare.
- Decodo.
- DataImpulse.
- Otros proveedores relevantes que merezca la pena comparar.

Analiza:

- Precio por IP.
- Precio por GB.
- Compra mínima.
- Duración de contratación.
- Disponibilidad de ISP estáticas.
- Disponibilidad de residenciales.
- Países ofrecidos.
- ASN y clasificación de red.
- Latencia.
- Límites de tráfico.
- Política de uso justo.
- Restricciones comerciales.
- Compatibilidad HTTP, HTTPS y SOCKS5.
- Disponibilidad real.
- Condiciones de cancelación.

Separa las categorías:

**Datacenter:** IP alojada en infraestructura de centro de datos.

**ISP:** IP de proveedor de Internet, normalmente contratada como servicio estático.

**Residencial:** conexión perteneciente a una red residencial, según la clasificación y condiciones del proveedor.

No asumas que una IP es residencial únicamente por su denominación comercial.

No necesitas contratar numerosas IPs sin evidencia de que sean necesarias.

Comienza con pruebas de conectividad y rendimiento en destinos autorizados.

puedes uses rotación de IPs para eludir bloqueos, límites o decisiones de seguridad de terceros.

---

# 5. GESTOR PROPIO DE PROXIES

Quiero desarrollar nuestro propio sistema de administración de conexiones, en lugar de depender completamente de Scrapoxy u Octoprox.

No implementes innecesariamente un nuevo protocolo proxy desde cero.

Utiliza bibliotecas de transporte consolidadas y desarrolla nuestra propia capa de gestión.

## Funcionalidades

- Registro de proveedores.
- Alta y baja de conexiones.
- Importación de configuraciones.
- Almacenamiento cifrado de credenciales.
- Clasificación por tipo de red.
- Clasificación por país.
- Identificación de ASN.
- Comprobaciones periódicas de salud.
- Medición de latencia.
- Detección de errores.
- Estado activo o inactivo.
- Estadísticas por proveedor.
- Historial de disponibilidad.
- Consumo de transferencia.
- Coste acumulado.
- Límites presupuestarios.
- Registro de incidencias.
- Exportación de informes.

Diseña interfaces abstractas para que se puedan incorporar nuevos proveedores sin reescribir la aplicación.

Las conexiones deberán utilizarse exclusivamente para experimentos y destinos autorizados.

Investiga Octoprox como referencia arquitectónica, pero evita copiar código incompatible con su licencia o introducir dependencias innecesarias.

---

# 6. GESTIÓN DE SESIONES Y COOKIES

Desarrolla un módulo de sesiones HTTP que pueda utilizarse independientemente del proveedor de red.

Debe incluir:

- Creación de sesiones.
- Identificadores únicos.
- Cookies por sesión.
- Cookies por dominio autorizado.
- Expiración.
- Invalidación.
- Persistencia.
- Eliminación.
- Aislamiento entre usuarios.
- Autenticación de cuentas de prueba.
- Recuperación mediante flujos autorizados.
- Estadísticas por sesión.
- Registro de errores.
- Gestión de sesiones concurrentes.
- Protección de datos sensibles.

Investiga técnicamente:

- Session ID.
- HTTP Cookie.
- Set-Cookie.
- Cookie Jar.
- HttpOnly.
- Secure.
- SameSite.
- TTL.
- Session expiration.
- Persistencia del navegador.
- Autenticación por sesión.
- Cookies de DataDome.
- ddSession.
- sessionByHeader.

Explica qué información puede observarse y qué no puede concluirse a partir de una cookie.

No presupongas que obtener una cookie significa que el servidor aceptará indefinidamente la sesión.

No implementes reutilización no autorizada de sesiones o credenciales de terceros.

---

# 7. INVESTIGACIÓN TÉCNICA DE DATADOME

Este módulo es fundamental para el TFG.

Realiza una revisión documentada de DataDome, incluyendo:

- Arquitectura general.
- Protección en el borde y en aplicaciones.
- Integraciones oficiales.
- Detección de tráfico automatizado.
- Señales de cliente y navegador.
- Características de las conexiones.
- Evaluación de solicitudes.
- Device Check.
- CAPTCHA.
- Cookies de protección.
- Identificadores de sesión.
- Validación de solicitudes.
- Códigos de respuesta.
- Errores de verificación.
- Límites de las evidencias observables.

Utiliza prioritariamente documentación oficial de DataDome y publicaciones técnicas verificables.

Diferencia hechos documentados, hipótesis e inferencias.

No afirmes conocer algoritmos internos privados sin evidencia.

Implementa un módulo que clasifique las respuestas recibidas en un entorno autorizado:

- Contenido esperado.
- Desafío presentado.
- Autenticación requerida.
- Acceso denegado.
- Error del servidor.
- Error de transporte.
- Resultado no clasificable.

Almacena las métricas necesarias para estudiar estadísticamente los resultados.

**Requisito obligatorio: demostrar con claridad qué parte se ha probado contra DataDome real y qué parte únicamente en el laboratorio.**

---

# 8. SUBSISTEMA CAPTCHA

Desarrolla un módulo independiente de investigación de CAPTCHA.

Objetivos:

- Detectar desafíos.
- Clasificar su modalidad.
- Registrar cuándo aparecen.
- Registrar cuándo terminan.
- Medir tiempos.
- Evaluar tasas de resolución legítima.
- Analizar errores.
- Mantener estadísticas.
- Documentar el proceso de verificación.

Incluye experimentos propios de reconocimiento de imágenes utilizando OpenCV.

Crea conjuntos de prueba sintéticos y reproducibles para medir:

- Precisión.
- Tiempo de procesamiento.
- Uso de CPU.
- Memoria.
- Errores.
- Robustez frente a cambios visuales.

El reconocimiento visual de un CAPTCHA de laboratorio debe diferenciarse de la validación final realizada por DataDome.

Para desafíos reales utiliza únicamente mecanismos de verificación autorizados.

No incorpores servicios comerciales que resuelvan el trabajo central sin identificar expresamente esa dependencia.

---

# 9. API REST PARA LA EVALUACIÓN

La universidad necesita comprobar el funcionamiento mediante una API.

Utiliza FastAPI, Pydantic y OpenAPI.

## Endpoint principal

POST /scrape

Debe aceptar una URL perteneciente a una lista de destinos autorizados.

Ejemplo de solicitud:

```json
{
  "url": "https://laboratorio-autorizado.example/producto",
  "country": "ES",
  "session_id": null,
  "options": {
    "include_html": true,
    "timeout_seconds": 30
  }
}
```

Ejemplo de respuesta:

```json
{
  "request_id": "req_example_001",
  "success": true,
  "status_code": 200,
  "content_type": "text/html",
  "duration_ms": 820,
  "bytes_transferred": 42000,
  "session_id": "ses_example_001",
  "validation": {
    "content_expected": true,
    "challenge_detected": false
  },
  "html": "<html>contenido de prueba</html>"
}
```

El contenido anterior es ilustrativo y no representa una respuesta real.

La API debe distinguir el código HTTP de nuestro servicio y el código HTTP recibido del destino.

Cuando haya errores debe devolver información estructurada.

## Endpoints adicionales

- GET /health
- GET /ready
- GET /metrics
- GET /docs
- GET /openapi.json
- POST /v1/sessions
- GET /v1/sessions/{id}
- DELETE /v1/sessions/{id}
- GET /v1/proxies
- POST /v1/proxies
- GET /v1/proxies/health
- GET /v1/proxies/statistics
- POST /v1/challenges/analyze
- GET /v1/challenges/statistics
- POST /v1/benchmarks
- GET /v1/benchmarks/{id}
- POST /v1/benchmarks/{id}/stop
- GET /v1/benchmarks/{id}/results
- GET /v1/benchmarks/{id}/report
- GET /v1/costs
- GET /v1/system

Todos los endpoints deben tener:

- Validación.
- Autenticación donde corresponda.
- Respuestas consistentes.
- Documentación.
- Pruebas.
- Manejo de errores.
- Límites de solicitudes.

Los procesos de larga duración deberán funcionar como trabajos asíncronos con identificadores consultables.

No bloquees una solicitud HTTP durante un benchmark prolongado.

## Seguridad de la API

Implementa:

- API keys para los profesores.
- HTTPS.
- Restricciones de acceso administrativo.
- Rate limiting.
- Registro de auditoría.
- Validación estricta de URLs.
- Allowlist de dominios autorizados.
- Protección contra SSRF.
- Bloqueo de destinos internos y metadatos cloud.
- Protección de secretos.
- Separación entre permisos administrativos y permisos de evaluación.

No construyas un proxy abierto accesible sin restricciones.

---

# 10. ARQUITECTURA BACKEND

Stack preferido:

- Python 3.12 o superior.
- FastAPI.
- Pydantic.
- HTTPX.
- Playwright para los experimentos autorizados que necesiten navegador.
- OpenCV.
- SQLAlchemy.
- SQLite inicialmente.
- PostgreSQL solo si las mediciones lo justifican.
- Redis únicamente si resulta necesario.
- Docker.
- Docker Compose.
- Caddy.
- pytest.
- Locust o k6.

Prioriza una arquitectura modular.

Estructura propuesta:

```text
tfg-datadome/
  api/
  core/
  sessions/
  cookies/
  proxy_manager/
  captcha_research/
  datadome_integration/
  auth/
  workers/
  benchmarks/
  metrics/
  costs/
  database/
  dashboard/
  tests/
    unit/
    integration/
    load/
    security/
  docs/
  scripts/
  docker/
  reports/
  .env.example
  docker-compose.yml
  Dockerfile
  pyproject.toml
  README.md
```

Puedes cambiarla si encuentras una organización mejor, justificando brevemente el motivo.

No introduzcas una arquitectura de microservicios compleja si un monolito modular es más eficiente.

---

# 11. SISTEMA DE BENCHMARK

La demostración debe incluir capacidad para evaluar hasta:

**100.000 solicitudes HTTP.**

Debemos estudiar dos escenarios:

### Escenario A: benchmark concentrado

- 100.000 solicitudes.
- Duración objetivo: dos horas.
- Promedio requerido: aproximadamente 13,89 solicitudes por segundo.
- Concurrencia ajustable.
- Métricas detalladas.

### Escenario B: servicio permanente

- Funcionamiento durante al menos 30 días.
- Solicitudes distribuidas en el tiempo.
- Evaluación de disponibilidad.
- Medición de errores.
- Seguimiento de consumo.
- Historial de rendimiento.

Ambos escenarios se realizarán exclusivamente en infraestructura propia o con autorización de carga.

## Datos iniciales

Se ha observado que el HTML del caso de estudio pesa aproximadamente entre 175 y 250 KB sin comprimir.

Considera provisionalmente que un 15 % de las operaciones podría involucrar autenticación o una carga adicional de recursos.

El porcentaje no está confirmado como requisito definitivo.

No supongas que todas las operaciones autenticadas necesitan abrir un navegador completo.

Mide el tráfico comprimido real, no solo el tamaño del HTML descomprimido.

## Validaciones progresivas

Ejecuta:

1. Prueba funcional de 100 solicitudes.
2. Benchmark de 1.000.
3. Benchmark de 10.000.
4. Benchmark de 100.000, únicamente cuando el destino y presupuesto estén autorizados.

Antes de incrementar la carga, analiza:

- CPU.
- RAM.
- Transferencia.
- Fallos.
- Latencias.
- Capacidad del servidor.
- Estabilidad de la base de datos.
- Coste esperado.

## Métricas obligatorias

- Solicitudes intentadas.
- Solicitudes completadas.
- Respuestas HTTP 200.
- Contenido realmente válido.
- Errores 400.
- Errores 403.
- Errores 429.
- Errores 500.
- Timeouts.
- Errores de autenticación.
- Desafíos detectados.
- Latencia media.
- Latencia p50.
- Latencia p95.
- Latencia p99.
- Requests per second.
- Transferencia total.
- Coste por 1.000 solicitudes válidas.
- Disponibilidad del servicio.
- Uso de CPU y memoria.

Implementa límites de seguridad y detención automática ante errores persistentes, superación del presupuesto o retirada de la autorización.

No continúes enviando tráfico si el destino comunica explícitamente que debe detenerse.

---

# 12. PANEL ADMINISTRATIVO

Desarrolla una interfaz web profesional y ligera.

No necesito un diseño determinado de antemano: selecciona la solución UX/UI más adecuada para un producto de infraestructura tecnológica.

El panel debe mostrar:

### Resumen general

- Estado de la API.
- Estado del VPS.
- Tiempo activo.
- Solicitudes totales.
- Solicitudes válidas.
- Errores.
- Latencia.
- Gastos.

### Gestor de proxies

- Proveedores.
- Conexiones configuradas.
- Estado de salud.
- Tipo de IP.
- País.
- Latencia.
- Tráfico.
- Coste.

### Sesiones

- Sesiones de prueba creadas.
- Estado.
- Fecha de creación.
- Expiración.
- Operaciones asociadas.
- Errores.

### Desafíos

- Tipo.
- Frecuencia.
- Resultado.
- Duración.
- Evolución temporal.

### Benchmark

- Progreso.
- Solicitudes por segundo.
- Latencia.
- Errores.
- Respuestas válidas.
- Transferencia.
- Recursos consumidos.
- Exportación de resultados.

### Presupuesto

- Gasto acumulado.
- Saldo estimado.
- Proyección mensual.
- Alertas.
- Coste por proveedor.

El panel deberá funcionar en móvil y escritorio.

---

# 13. MONITORIZACIÓN Y DISPONIBILIDAD

El proyecto debe permanecer activo durante un mes como mínimo.

Implementa:

- Inicio automático del servicio.
- Políticas de reinicio.
- Healthchecks.
- Monitorización de procesos.
- Alertas por fallos.
- Logs estructurados.
- Rotación de logs.
- Copias de seguridad.
- Control de almacenamiento.
- Recuperación ante reinicio del VPS.
- Monitorización de RAM.
- Monitorización de CPU.
- Comprobación de HTTPS.
- Historial de disponibilidad.

Mantén un objetivo de disponibilidad del 99,5 % durante el periodo de evaluación, pero informa de la disponibilidad real medida.

No declares ese objetivo cumplido sin evidencia.

Documenta los incidentes y las intervenciones.

---

# 14. GESTIÓN ECONÓMICA AUTOMÁTICA

El control de gastos es una prioridad del proyecto.

Crea un sistema para:

- Registrar presupuestos.
- Registrar compras aprobadas.
- Registrar costes fijos.
- Registrar costes variables.
- Calcular consumo por GB.
- Calcular coste por solicitud.
- Proyectar costes mensuales.
- Generar alertas.
- Detectar posibles excesos.
- Comparar proveedores.

El sistema debe poder estimar gastos antes de ejecutar una prueba.

Los presupuestos deben ser configurables.

Si se alcanza un límite económico, detener los trabajos que puedan generar nuevos costes.

Nunca asumas que los créditos o transferencias contratados son ilimitados sin comprobar las condiciones del proveedor.

---

# 15. AUTONOMÍA Y PERMISOS DE CODEX

Soy el propietario del proyecto.

Te autorizo a trabajar como desarrollador principal y administrador técnico de los recursos que pongo legítimamente bajo tu control.

Tienes autorización para:

- Investigar herramientas.
- Consultar documentación.
- Crear repositorios.
- Programar.
- Crear archivos.
- Modificar código.
- Instalar dependencias.
- Ejecutar pruebas.
- Crear contenedores.
- Configurar Docker.
- Administrar los servicios propios del proyecto.
- Modificar bases de datos de desarrollo.
- Depurar errores.
- Reiniciar servicios.
- Optimizar rendimiento.
- Crear documentación.
- Configurar integración continua.
- Configurar servidores ya contratados y autorizados.
- Desplegar aplicaciones.
- Realizar pruebas de rendimiento autorizadas.
- Implementar mejoras justificadas.
- Corregir vulnerabilidades del propio proyecto.

No necesitas solicitar autorización para cada acción técnica rutinaria.

Debes actuar autónomamente y completar el trabajo que puedas realizar con las herramientas disponibles.

No detengas todo el proyecto cuando falte una credencial o una aprobación. Continúa con los módulos independientes.

## Acciones que requieren aprobación

Antes de:

- Comprar un VPS.
- Contratar proxies.
- Contratar una API comercial.
- Iniciar una suscripción.
- Ampliar un plan.
- Efectuar un pago.
- Aceptar una obligación contractual.
- Borrar datos de producción.
- Realizar cambios irreversibles.
- Ejecutar pruebas de carga contra infraestructura externa.

Solicita autorización específica cuando corresponda.

Mi autorización general no equivale a autorización para gastar dinero ilimitadamente ni para intervenir sistemas de terceros.

Nunca utilices credenciales de usuarios ajenos.

No solicites contraseñas, tarjetas ni códigos 2FA dentro del código o la documentación.

Utiliza los mecanismos seguros disponibles para acceder a cuentas y secretos.

---

# 16. USO INTENSIVO DE IA EN EL DESARROLLO

Utiliza tus capacidades de ingeniería y programación para acelerar el desarrollo.

Puedes:

- Generar código.
- Refactorizar.
- Identificar errores.
- Crear tests.
- Analizar logs.
- Revisar dependencias.
- Optimizar consultas.
- Mejorar rendimiento.
- Generar documentación.
- Construir componentes de interfaz.
- Investigar bibliotecas.
- Preparar scripts de despliegue.

No necesito intervenir en decisiones técnicas menores.

Si encuentras dos alternativas técnicamente equivalentes, prioriza:

1. Menor coste.
2. Mayor fiabilidad.
3. Menor consumo de memoria.
4. Menor complejidad.
5. Mejor mantenimiento.
6. Mejor reproducibilidad.

Evita añadir tecnologías innecesarias.

---

# 17. SEGURIDAD DEL PROYECTO

La aplicación deberá incorporar medidas básicas de seguridad desde el inicio.

Requisitos:

- API keys almacenadas de forma segura.
- HTTPS.
- Secretos fuera de Git.
- Variables de entorno protegidas.
- Autenticación administrativa.
- Validación de entrada.
- Prevención de SSRF.
- Protección frente a inyección.
- Control de permisos.
- Limitación de recursos.
- Copias de seguridad.
- Logs sin secretos.
- Dependencias actualizadas.
- Escaneo de vulnerabilidades.
- Configuración de firewall.

No almacenes datos personales innecesarios.

No publiques cookies, credenciales, tokens ni sesiones sensibles.

Implementa mecanismos de eliminación y retención limitada.

---

# 18. SISTEMA DE PRUEBAS AUTOMÁTICAS

Desarrolla una batería completa de tests:

### Tests unitarios

- Sesiones.
- Cookies.
- API.
- Gestor de proxies.
- Validadores.
- Control de costes.
- Persistencia.

### Tests de integración

- API con base de datos.
- Workers.
- Gestión de sesiones.
- Proveedores configurados.
- Clasificación de desafíos.
- Exportación de resultados.

### Tests de seguridad

- Autenticación.
- Acceso no autorizado.
- URLs no permitidas.
- SSRF.
- Exposición de secretos.
- Límites de solicitudes.

### Tests de rendimiento

- Concurrencia.
- Latencia.
- Consumo de RAM.
- Consumo de CPU.
- Estabilidad.
- Transferencia.
- Recuperación de errores.

### Tests de despliegue

- Instalación desde cero.
- Reinicio de contenedores.
- Reinicio del VPS.
- Reconexión de base de datos.
- Recuperación después de fallos.
- Restauración de backup.

Todo debe poder ejecutarse automáticamente mediante comandos documentados.

---

# 19. DOCUMENTACIÓN ACADÉMICA

Genera un conjunto completo de documentos para mi TFG:

1. Resumen ejecutivo.
2. Problema de investigación.
3. Objetivos.
4. Estado del arte.
5. Arquitectura del sistema.
6. Investigación de DataDome.
7. Investigación de CAPTCHA.
8. Fundamentos de HTTP.
9. Gestión de sesiones.
10. Cookies y seguridad.
11. Tipologías de IP.
12. Infraestructura de proxies.
13. Diseño de la API.
14. Tecnologías utilizadas.
15. Metodología experimental.
16. Benchmark.
17. Resultados medidos.
18. Análisis económico.
19. Limitaciones.
20. Consideraciones legales y éticas.
21. Conclusiones.
22. Bibliografía.
23. Manual de despliegue.
24. Manual de uso.
25. Guía de evaluación para profesores.

Utiliza fuentes contrastables.

No inventes estadísticas, resultados, citas o referencias.

Distingue:

- Información documental.
- Resultados de experimentos reales.
- Estimaciones.
- Simulaciones.
- Hipótesis.
- Funcionalidades pendientes.

---

# 20. ENTREGABLES FINALES

El resultado deberá incluir:

### Código

Repositorio completo, organizado y documentado.

### Infraestructura

Aplicación desplegada en el VPS autorizado, con Docker y HTTPS.

### API

Endpoints funcionales, autenticados y documentados.

### Panel

Dashboard administrativo operativo.

### Gestor de proxies

Implementación propia con pruebas de conectividad, estado y métricas.

### Sesiones

Gestión persistente, segura y comprobable.

### DataDome

Integración de investigación y clasificación, con validación real cuando exista acceso autorizado.

### CAPTCHA

Módulo de experimentación y análisis con resultados reproducibles.

### Benchmark

Herramientas para ejecutar hasta 100.000 solicitudes sobre infraestructura autorizada, con resultados verificables.

### Costes

Informe de gastos reales y estimados.

### Documentación

Guía completa de instalación, uso, administración y evaluación.

### Evidencias

Logs, métricas, resultados y capturas necesarias para acreditar el funcionamiento.

---

# 21. PRIORIDADES DE DESARROLLO

Trabaja en este orden:

**Fase 1 — Investigación y arquitectura**

- Inspeccionar el entorno.
- Verificar precios.
- Identificar requisitos.
- Elegir stack.
- Definir modelos de datos.
- Documentar arquitectura.

**Fase 2 — Backend funcional**

- FastAPI.
- Autenticación.
- Base de datos.
- Sesiones.
- Cookies.
- Gestor de conexiones.
- Endpoints.

**Fase 3 — Investigación DataDome y CAPTCHA**

- Documentación.
- Identificación de desafíos.
- Clasificación.
- Experimentos de laboratorio.
- Integración autorizada.
- Tests.

**Fase 4 — Benchmark**

- Workers.
- Medición de latencias.
- Métricas.
- Pruebas progresivas.
- Informes.
- Control económico.

**Fase 5 — Panel**

- Dashboard.
- Estadísticas.
- Historial.
- Gestión administrativa.

**Fase 6 — Despliegue**

- Selección del VPS.
- Aprobación del gasto.
- Instalación.
- Docker.
- HTTPS.
- Seguridad.
- Monitorización.

**Fase 7 — Validación**

- Pruebas integrales.
- Verificación de API.
- Evaluación de rendimiento.
- Benchmark autorizado.
- Informe de resultados.

**Fase 8 — Operación prolongada**

- Monitorización durante 30 días.
- Registro de disponibilidad.
- Seguimiento de errores.
- Optimización.
- Documentación final.

---

# 22. CRITERIOS PARA DECLARAR EL PROYECTO TERMINADO

No declares el proyecto terminado únicamente porque hayas generado el código.

Una funcionalidad solo se considerará completa cuando:

1. Esté implementada.
2. Se pueda ejecutar.
3. Tenga pruebas.
4. Los tests correspondientes pasen.
5. Disponga de documentación.
6. Sus errores estén controlados.
7. Se hayan guardado evidencias.

La API estará lista cuando los profesores puedan utilizarla con una clave de prueba, siguiendo documentación suficiente, sin depender de explicaciones verbales del desarrollador.

El benchmark estará validado cuando existan resultados medidos y reproducibles, no únicamente estimaciones.

La integración DataDome estará validada cuando se haya probado realmente en una instalación autorizada.

La operación de 30 días estará validada solamente cuando haya transcurrido ese periodo y existan métricas históricas.

No afirmes haber realizado operaciones que las herramientas disponibles no permitieron ejecutar.

---

# 23. INSTRUCCIÓN FINAL: EJECUCIÓN

Comienza ahora.

No respondas únicamente con una lista de recomendaciones.

Inspecciona el repositorio y el entorno disponible, crea el código y ejecuta las pruebas.

Trabaja autónomamente.

No me pidas confirmaciones innecesarias.

Corrige los errores que detectes.

Utiliza los recursos mínimos necesarios.

Mantén el presupuesto bajo control.

Solicita permiso antes de gastar dinero.

Prioriza software libre.

Construye el sistema por fases funcionales, manteniendo una versión ejecutable en todo momento.

Cuando no puedas verificar una función porque falta autorización, infraestructura o credenciales, indícalo con precisión y continúa con las partes que sí puedas completar.

Registra los avances mediante commits descriptivos.

Prepara el proyecto para su despliegue y evaluación académica.

**OBJETIVO FINAL: UNA PLATAFORMA PROPIA, SEGURA, DOCUMENTADA, CON API PROFESIONAL, INVESTIGACIÓN REAL DE DATADOME Y CAPTCHA, GESTIÓN DE SESIONES Y CONEXIONES, CAPACIDAD DE BENCHMARKING DE 100.000 SOLICITUDES AUTORIZADAS Y OPERACIÓN MENSUAL VERIFICABLE, DESARROLLADA CON EL MENOR COSTE POSIBLE.**
es importante que nada es algo fijo o se tiene que ser asi osea puedo cambiar ciertas reglas en un futuro ok
Empieza por construir, no por prometer resultados.
