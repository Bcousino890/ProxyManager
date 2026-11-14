# Tarea

# MISIÓN PRINCIPAL — TERMINAR EL COMPETIDOR DE CRAWIO

## 1. INSTRUCCIÓN INICIAL

Esta es una TAREA NUEVA.

No reutilices planes ni criterios de aceptación de conversaciones anteriores.

Debes inspeccionar el trabajo existente, recuperar el código útil y continuar el desarrollo.

Tu objetivo es entregar una aplicación funcional de Web Scraping API, comparable en experiencia de uso y funcionalidades esenciales a Crawio.com.

NO dediques tiempo a configurar una URL pública.

El usuario ya puede acceder desde su Mac mediante SSH.

## 2. ENTORNO EXISTENTE

Infraestructura:

- RunPod.
- NVIDIA RTX 3090.
- Ollama.
- Qwen3-Coder:30B.
- Linux.

Repositorio:

https://github.com/Bcousino890/ProxyManager

Rama de publicación: main.

Servicios:

- Agente Qwen: puerto 8787.
- Scraping API: puerto 8000.
- Panel de scraping: puerto 8002.

Acceso desde el Mac:

http://127.0.0.1:8002

IMPORTANTE:

No modifiques ni interrumpas el agente del puerto 8787.

No reinicies RunPod.

No elimines modelos Ollama.

No intentes utilizar ngrok.

No investigues POD_ID ni URL pública.

El acceso local mediante SSH es suficiente para aceptar esta versión.

## 3. INSPECCIÓN OBLIGATORIA

Antes de modificar el proyecto:

1. Comprueba los procesos activos.
2. Inspecciona el repositorio.
3. Revisa los cambios sin commit.
4. Revisa la carpeta tools/scraping-panel/.
5. Identifica los módulos de scraping existentes.
6. Comprueba qué API está realmente funcionando.
7. Inspecciona el frontend.
8. Revisa los tests.
9. Localiza la configuración de proxies.
10. Comprueba los errores registrados.

Conserva código y datos existentes.

No reconstruyas el proyecto desde cero sin necesidad.

Crea un nuevo plan específico de esta misión.

## 4. PRIORIDAD ABSOLUTA — HACER FUNCIONAR EL PLAYGROUND

El problema principal es que el usuario puede abrir el panel, pero el botón Extraer no devuelve resultados visibles.

DEBES corregirlo.

Comprueba:

- Eventos JavaScript.
- Formulario.
- Endpoint.
- CORS.
- Autenticación.
- Errores de red.
- Respuestas JSON.
- Timeouts.
- Logs.
- Renderizado de resultados.

Implementa preferentemente comunicación mediante rutas del mismo origen para evitar problemas entre los puertos 8000 y 8002.

El usuario debe poder:

1. Abrir el panel.
2. Escribir una URL.
3. Elegir HTTP o JavaScript.
4. Pulsar Ejecutar.
5. Ver un indicador de carga.
6. Obtener un resultado real.
7. Consultar HTML, texto y JSON.
8. Ver el código HTTP.
9. Ver tiempo y errores.
10. Copiar y descargar resultados.

No puede existir un botón que no haga nada.

## 5. PRUEBAS REALES INMEDIATAS

Prueba A:

URL: https://example.com

Motor: HTTP.

Resultado esperado:

- HTTP 200 si el acceso está disponible.
- HTML real.
- Título Example Domain.
- Contenido visible en el panel.

Prueba B:

URL: https://example.com

Motor: Playwright.

Resultado esperado:

- Chromium ejecutado realmente.
- HTML renderizado.
- Resultado mostrado en el panel.

Prueba C:

Página JavaScript de prueba controlada.

Resultado esperado:

- Contenido generado dinámicamente.
- Extracción correcta mediante Playwright.

Prueba D:

Error de conexión controlado.

Resultado esperado:

- Mensaje de error visible.
- Sin pantalla bloqueada.

Ejecuta pruebas de extremo a extremo con un navegador real, no solamente curl.

## 6. REDISEÑO PROFESIONAL

Utiliza como referencia funcional y de organización el Playground de Crawio:

https://crawio.com/app/#playground

No copies sus marcas ni elementos gráficos propietarios.

Construye una interfaz SaaS profesional con:

### Navegación

- Dashboard.
- Playground.
- Proxies.
- Trabajos.
- Historial.
- API Keys.
- Estadísticas.
- Configuración.

### Playground

- Selector de método.
- Campo URL.
- Botón Ejecutar.
- Selector HTTP/JavaScript.
- Selector de proxy.
- Timeout.
- Encabezados personalizados.
- Opciones avanzadas.

### Resultados

Pestañas:

- Body.
- Preview.
- Headers.
- Text.
- JSON.
- Metadata.

Mostrar:

- HTTP status.
- Tiempo.
- Motor utilizado.
- Proxy.
- Tamaño de respuesta.
- Estado del scraping.
- Errores.

Añade:

- Copiar.
- Descargar HTML.
- Descargar JSON.
- Historial.
- Indicadores de carga.

No implementes elementos visuales sin funcionalidad.

Prioriza calidad, simplicidad y estabilidad.

## 7. MOTOR DE SCRAPING

Completa los componentes existentes utilizando:

- FastAPI.
- httpx.
- Playwright.
- Chromium.
- asyncio.
- Pydantic.

Características:

- Extracción HTML.
- Renderizado JavaScript.
- Texto visible.
- Metadatos.
- Enlaces.
- JSON.
- Sesiones autorizadas.
- Timeouts.
- Control de errores.
- Concurrencia configurable.
- Reintentos limitados.
- Límites de recursos.

Implementa protección SSRF y validación de redirecciones.

No permitas acceso a redes internas mediante URLs de usuarios.

## 8. PROXIES DECODO

Tenemos diez proxies ISP:

Host: isp.decodo.com

Puertos: 10001–10010.

Las credenciales están en un archivo privado.

Localiza el archivo configurado mediante PROXY_FILE.

No reveles contraseñas.

Para cada proxy:

- Comprueba conexión.
- Comprueba autenticación.
- Comprueba IP de salida.
- Mide latencia.
- Registra disponibilidad.
- Detecta fallos.
- Muestra resultados en el panel.

El selector de proxies debe mostrar los endpoints operativos.

Si falta el archivo privado, registra exactamente qué configuración falta.

No inventes resultados.

## 9. PRUEBA DE REFERENCIA — IDEALISTA

URL:

https://www.idealista.com/inmueble/112909923/

Resultado observado en nuestro sistema:

HTTP 403 con DataDome.

Resultado observado por el usuario en Crawio:

- HTTP 200.
- Aproximadamente 262,1 KB de HTML.
- 1,3 segundos.
- 6 créditos.
- Contenido real del inmueble.

Nuestro objetivo comercial es alcanzar capacidades comparables a Crawio en fuentes autorizadas.

Investiga y documenta las diferencias técnicas de manera reproducible.

No declares que has resuelto DataDome si solo detectaste el bloqueo.

No intentes superar CAPTCHA ni controles de acceso sin autorización.

Si una fuente bloquea la automatización, registra el resultado y estudia alternativas de acceso autorizadas.

## 10. API COMPLETA

Implementa:

GET /health
GET /ready
POST /scrape
POST /scrape/batch
GET /jobs/{id}
POST /jobs/{id}/cancel
GET /metrics
GET /proxies/status
GET /history
GET /docs

Añade autenticación mediante API key, validación y límites de recursos.

Documenta la API mediante OpenAPI.

## 11. TRABAJOS MASIVOS

Implementa:

- Colas de trabajos.
- Identificadores únicos.
- Concurrencia configurable.
- Estados.
- Persistencia.
- Reintentos limitados.
- Cancelación.
- Descarga de resultados.

No utilices bucles infinitos.

## 12. ESTADÍSTICAS

Muestra:

- Solicitudes totales.
- Extracciones útiles.
- Errores.
- Bloqueos.
- Latencia media.
- p50 y p95.
- Tráfico.
- Uso de proxies.
- Costes estimados.

No inventes métricas.

Si faltan tarifas de infraestructura, muestra costes como no configurados.

## 13. SEGURIDAD

Obligatorio:

- Credenciales privadas.
- API keys.
- Autenticación del panel.
- Protección SSRF.
- Validación DNS y redirecciones.
- Límites de respuesta.
- Timeouts.
- Aislamiento de HTML.
- Control de concurrencia.
- Secretos fuera de GitHub.

No desactives la seguridad para conseguir que una prueba pase.

## 14. TESTING

Ejecuta:

- Tests unitarios.
- Tests de integración.
- Tests HTTP.
- Tests Playwright.
- Tests de proxies.
- Tests del frontend.
- Tests de descarga.
- Tests de historial.
- Tests de trabajos.
- Tests de seguridad.

Ejecuta al menos una prueba end-to-end real con navegador:

Abrir panel → introducir URL → pulsar Ejecutar → esperar respuesta → verificar HTML y JSON.

Guarda resultados y evidencia.

No declares éxito basándote únicamente en una respuesta HTTP del healthcheck.

## 15. SERVICIOS Y DESPLIEGUE

Mantén:

API: 8000.
Panel: 8002.
Agente: 8787.

La aplicación debe permanecer funcionando después de terminar la tarea.

No necesitas una URL pública.

No reinicies el pod.

No modifiques otros servicios.

## 16. GITHUB

Repositorio:

https://github.com/Bcousino890/ProxyManager

Rama: main.

Comprueba previamente los cambios existentes sin commit.

Preserva los archivos útiles.

Realiza pruebas.

Revisa secretos.

Crea commits descriptivos.

Publica cambios validados en main respetando las protecciones configuradas.

Verifica que el hash remoto coincide.

## 17. CRITERIOS DE ACEPTACIÓN

El proyecto estará terminado únicamente si:

[ ] El botón Ejecutar funciona.

[ ] El formulario obtiene resultados reales.

[ ] HTTP funciona.

[ ] Playwright funciona.

[ ] El panel muestra HTML, texto y JSON.

[ ] Los errores son visibles.

[ ] Las pestañas funcionan.

[ ] Copiar y descargar funcionan.

[ ] Los proxies están integrados cuando se dispone de credenciales.

[ ] El historial funciona.

[ ] Los trabajos masivos funcionan.

[ ] Las métricas son reales.

[ ] Las pruebas end-to-end pasan.

[ ] Los servicios continúan activos.

[ ] Los cambios están publicados en main.

[ ] El commit remoto está verificado.

NO existe requisito de URL pública para esta versión.

Si falta algo, entrega estado INCOMPLETO y evidencia de lo pendiente.

## 18. INFORME FINAL

Entrega:

- Resumen de funcionalidades reales.
- URL local del panel.
- Endpoints API.
- Resultados de pruebas HTTP.
- Resultados de Playwright.
- Estado de proxies.
- Resultado de Idealista.
- Pruebas aprobadas y fallidas.
- Estado de procesos.
- Git commit.
- Cambios pendientes.
- Limitaciones conocidas.

No inventes resultados.

## 19. INSTRUCCIÓN FINAL

Esta es una tarea nueva con criterios nuevos.

No reutilices bloqueos de la conversación anterior.

No investigues RunPod.

No investigues ngrok.

No investigues la URL pública.

No termines simplemente por hacer commits.

No termines porque /health responde 200.

No termines porque Idealista responde 403.

Tu objetivo principal es que el usuario pueda utilizar realmente el Playground desde su Mac.

Ejecuta comandos, implementa, corrige, prueba y verifica.

COMIENZA AHORA INSPECCIONANDO EL PROYECTO EXISTENTE Y CORRIGIENDO EL BOTÓN EXTRAER.


## Instrucción del usuario (2026-11-14 01:56:04)

# MISIÓN PRINCIPAL — TERMINAR EL COMPETIDOR DE CRAWIO

## 1. INSTRUCCIÓN INICIAL

Esta es una TAREA NUEVA.

No reutilices planes ni criterios de aceptación de conversaciones anteriores.

Debes inspeccionar el trabajo existente, recuperar el código útil y continuar el desarrollo.

Tu objetivo es entregar una aplicación funcional de Web Scraping API, comparable en experiencia de uso y funcionalidades esenciales a Crawio.com.

NO dediques tiempo a configurar una URL pública.

El usuario ya puede acceder desde su Mac mediante SSH.

## 2. ENTORNO EXISTENTE

Infraestructura:

- RunPod.
- NVIDIA RTX 3090.
- Ollama.
- Qwen3-Coder:30B.
- Linux.

Repositorio:

https://github.com/Bcousino890/ProxyManager

Rama de publicación: main.

Servicios:

- Agente Qwen: puerto 8787.
- Scraping API: puerto 8000.
- Panel de scraping: puerto 8002.

Acceso desde el Mac:

http://127.0.0.1:8002

IMPORTANTE:

No modifiques ni interrumpas el agente del puerto 8787.

No reinicies RunPod.

No elimines modelos Ollama.

No intentes utilizar ngrok.

No investigues POD_ID ni URL pública.

El acceso local mediante SSH es suficiente para aceptar esta versión.

## 3. INSPECCIÓN OBLIGATORIA

Antes de modificar el proyecto:

1. Comprueba los procesos activos.
2. Inspecciona el repositorio.
3. Revisa los cambios sin commit.
4. Revisa la carpeta tools/scraping-panel/.
5. Identifica los módulos de scraping existentes.
6. Comprueba qué API está realmente funcionando.
7. Inspecciona el frontend.
8. Revisa los tests.
9. Localiza la configuración de proxies.
10. Comprueba los errores registrados.

Conserva código y datos existentes.

No reconstruyas el proyecto desde cero sin necesidad.

Crea un nuevo plan específico de esta misión.

## 4. PRIORIDAD ABSOLUTA — HACER FUNCIONAR EL PLAYGROUND

El problema principal es que el usuario puede abrir el panel, pero el botón Extraer no devuelve resultados visibles.

DEBES corregirlo.

Comprueba:

- Eventos JavaScript.
- Formulario.
- Endpoint.
- CORS.
- Autenticación.
- Errores de red.
- Respuestas JSON.
- Timeouts.
- Logs.
- Renderizado de resultados.

Implementa preferentemente comunicación mediante rutas del mismo origen para evitar problemas entre los puertos 8000 y 8002.

El usuario debe poder:

1. Abrir el panel.
2. Escribir una URL.
3. Elegir HTTP o JavaScript.
4. Pulsar Ejecutar.
5. Ver un indicador de carga.
6. Obtener un resultado real.
7. Consultar HTML, texto y JSON.
8. Ver el código HTTP.
9. Ver tiempo y errores.
10. Copiar y descargar resultados.

No puede existir un botón que no haga nada.

## 5. PRUEBAS REALES INMEDIATAS

Prueba A:

URL: https://example.com

Motor: HTTP.

Resultado esperado:

- HTTP 200 si el acceso está disponible.
- HTML real.
- Título Example Domain.
- Contenido visible en el panel.

Prueba B:

URL: https://example.com

Motor: Playwright.

Resultado esperado:

- Chromium ejecutado realmente.
- HTML renderizado.
- Resultado mostrado en el panel.

Prueba C:

Página JavaScript de prueba controlada.

Resultado esperado:

- Contenido generado dinámicamente.
- Extracción correcta mediante Playwright.

Prueba D:

Error de conexión controlado.

Resultado esperado:

- Mensaje de error visible.
- Sin pantalla bloqueada.

Ejecuta pruebas de extremo a extremo con un navegador real, no solamente curl.

## 6. REDISEÑO PROFESIONAL

Utiliza como referencia funcional y de organización el Playground de Crawio:

https://crawio.com/app/#playground

No copies sus marcas ni elementos gráficos propietarios.

Construye una interfaz SaaS profesional con:

### Navegación

- Dashboard.
- Playground.
- Proxies.
- Trabajos.
- Historial.
- API Keys.
- Estadísticas.
- Configuración.

### Playground

- Selector de método.
- Campo URL.
- Botón Ejecutar.
- Selector HTTP/JavaScript.
- Selector de proxy.
- Timeout.
- Encabezados personalizados.
- Opciones avanzadas.

### Resultados

Pestañas:

- Body.
- Preview.
- Headers.
- Text.
- JSON.
- Metadata.

Mostrar:

- HTTP status.
- Tiempo.
- Motor utilizado.
- Proxy.
- Tamaño de respuesta.
- Estado del scraping.
- Errores.

Añade:

- Copiar.
- Descargar HTML.
- Descargar JSON.
- Historial.
- Indicadores de carga.

No implementes elementos visuales sin funcionalidad.

Prioriza calidad, simplicidad y estabilidad.

## 7. MOTOR DE SCRAPING

Completa los componentes existentes utilizando:

- FastAPI.
- httpx.
- Playwright.
- Chromium.
- asyncio.
- Pydantic.

Características:

- Extracción HTML.
- Renderizado JavaScript.
- Texto visible.
- Metadatos.
- Enlaces.
- JSON.
- Sesiones autorizadas.
- Timeouts.
- Control de errores.
- Concurrencia configurable.
- Reintentos limitados.
- Límites de recursos.

Implementa protección SSRF y validación de redirecciones.

No permitas acceso a redes internas mediante URLs de usuarios.

## 8. PROXIES DECODO

Tenemos diez proxies ISP:

Host: isp.decodo.com

Puertos: 10001–10010.

Las credenciales están en un archivo privado.

Localiza el archivo configurado mediante PROXY_FILE.

No reveles contraseñas.

Para cada proxy:

- Comprueba conexión.
- Comprueba autenticación.
- Comprueba IP de salida.
- Mide latencia.
- Registra disponibilidad.
- Detecta fallos.
- Muestra resultados en el panel.

El selector de proxies debe mostrar los endpoints operativos.

Si falta el archivo privado, registra exactamente qué configuración falta.

No inventes resultados.

## 9. PRUEBA DE REFERENCIA — IDEALISTA

URL:

https://www.idealista.com/inmueble/112909923/

Resultado observado en nuestro sistema:

HTTP 403 con DataDome.

Resultado observado por el usuario en Crawio:

- HTTP 200.
- Aproximadamente 262,1 KB de HTML.
- 1,3 segundos.
- 6 créditos.
- Contenido real del inmueble.

Nuestro objetivo comercial es alcanzar capacidades comparables a Crawio en fuentes autorizadas.

Investiga y documenta las diferencias técnicas de manera reproducible.

No declares que has resuelto DataDome si solo detectaste el bloqueo.

No intentes superar CAPTCHA ni controles de acceso sin autorización.

Si una fuente bloquea la automatización, registra el resultado y estudia alternativas de acceso autorizadas.

## 10. API COMPLETA

Implementa:

GET /health
GET /ready
POST /scrape
POST /scrape/batch
GET /jobs/{id}
POST /jobs/{id}/cancel
GET /metrics
GET /proxies/status
GET /history
GET /docs

Añade autenticación mediante API key, validación y límites de recursos.

Documenta la API mediante OpenAPI.

## 11. TRABAJOS MASIVOS

Implementa:

- Colas de trabajos.
- Identificadores únicos.
- Concurrencia configurable.
- Estados.
- Persistencia.
- Reintentos limitados.
- Cancelación.
- Descarga de resultados.

No utilices bucles infinitos.

## 12. ESTADÍSTICAS

Muestra:

- Solicitudes totales.
- Extracciones útiles.
- Errores.
- Bloqueos.
- Latencia media.
- p50 y p95.
- Tráfico.
- Uso de proxies.
- Costes estimados.

No inventes métricas.

Si faltan tarifas de infraestructura, muestra costes como no configurados.

## 13. SEGURIDAD

Obligatorio:

- Credenciales privadas.
- API keys.
- Autenticación del panel.
- Protección SSRF.
- Validación DNS y redirecciones.
- Límites de respuesta.
- Timeouts.
- Aislamiento de HTML.
- Control de concurrencia.
- Secretos fuera de GitHub.

No desactives la seguridad para conseguir que una prueba pase.

## 14. TESTING

Ejecuta:

- Tests unitarios.
- Tests de integración.
- Tests HTTP.
- Tests Playwright.
- Tests de proxies.
- Tests del frontend.
- Tests de descarga.
- Tests de historial.
- Tests de trabajos.
- Tests de seguridad.

Ejecuta al menos una prueba end-to-end real con navegador:

Abrir panel → introducir URL → pulsar Ejecutar → esperar respuesta → verificar HTML y JSON.

Guarda resultados y evidencia.

No declares éxito basándote únicamente en una respuesta HTTP del healthcheck.

## 15. SERVICIOS Y DESPLIEGUE

Mantén:

API: 8000.
Panel: 8002.
Agente: 8787.

La aplicación debe permanecer funcionando después de terminar la tarea.

No necesitas una URL pública.

No reinicies el pod.

No modifiques otros servicios.

## 16. GITHUB

Repositorio:

https://github.com/Bcousino890/ProxyManager

Ra


## Comentario del usuario (2026-11-14 01:57:31)

# REGLA CRÍTICA — DESARROLLO CONTINUO CON GITHUB Y RECUPERACIÓN AUTOMÁTICA

ESTE PROYECTO YA EXISTE. NO EMPIECES DESDE CERO.

Debes continuar sobre el código previamente desarrollado, conservar los componentes funcionales y mejorar progresivamente el producto.

Repositorio:
https://github.com/Bcousino890/ProxyManager

Rama principal de entrega: main.

Directorio del proyecto: localízalo inspeccionando el repositorio. No supongas que todos los componentes están en una sola carpeta.

## 1. RECUPERACIÓN DEL ESTADO

Antes de trabajar:

1. Ejecuta git status.
2. Identifica la rama actual.
3. Comprueba el último commit local y remoto.
4. Inspecciona todos los cambios sin commit.
5. Lee TASK.md, ACCEPTANCE.md, PLAN.md, PROGRESS.md, TEST_RESULTS.md y BLOCKERS.md cuando existan.
6. Identifica lo que ya está implementado.
7. Identifica lo que funciona realmente.
8. Identifica lo pendiente.
9. Continúa desde el último estado válido.

Nunca sobrescribas archivos modificados sin inspeccionarlos.

No utilices git reset --hard, git clean -fd ni force push.

## 2. GUARDADO CONTINUO EN GITHUB

No esperes al final de las dos horas para guardar.

Trabaja por hitos pequeños y verificables.

Después de cada hito funcional:

1. Guarda los archivos.
2. Ejecuta las pruebas relevantes.
3. Corrige cualquier fallo causado por ese hito.
4. Actualiza PROGRESS.md.
5. Actualiza TEST_RESULTS.md.
6. Comprueba que no hay credenciales ni secretos.
7. Ejecuta git diff --check.
8. Crea un commit descriptivo.
9. Haz push a la rama de trabajo autorizada.
10. Verifica que el hash remoto coincide.

No publiques código deliberadamente roto en main.

Si utilizas una rama de desarrollo, guarda allí los avances y lleva a main solamente los cambios validados.

No necesitas que cada commit represente el proyecto completo: debe representar una mejora funcional, probada y recuperable.

## 3. FRECUENCIA DE GUARDADO

Haz un commit después de cada módulo o corrección importante.

No acumules decenas de archivos sin guardar.

Si un módulo requiere muchas iteraciones, realiza commits intermedios en la rama de desarrollo cuando alcances un estado consistente.

Reserva tiempo para publicar antes de agotar el presupuesto de ejecución.

Si el agente se interrumpe, el código y el progreso deben poder recuperarse.

## 4. CORRECCIÓN AUTOMÁTICA

Cuando una prueba falle:

1. Lee el error completo.
2. Identifica la causa.
3. Inspecciona los archivos relacionados.
4. Aplica una corrección concreta.
5. Ejecuta nuevamente la prueba.
6. Ejecuta una regresión relevante.
7. Guarda el resultado.
8. Continúa.

No reescribas todo el módulo sin necesidad.

No repitas el mismo comando indefinidamente.

No marques pruebas como aprobadas si fallan.

## 5. CONTINUIDAD ENTRE CONVERSACIONES

Guarda el estado del proyecto en archivos versionados:

- TASK.md
- ACCEPTANCE.md
- PLAN.md
- PROGRESS.md
- DECISIONS.md
- TEST_RESULTS.md
- BLOCKERS.md

PROGRESS.md debe contener:

- Última tarea completada.
- Funcionalidades implementadas.
- Funcionalidades pendientes.
- Errores conocidos.
- Servicios activos.
- Rutas relevantes.
- Último commit.
- Próxima acción concreta.

Cuando comience una conversación nueva, lee estos archivos y continúa.

No repitas trabajos ya validados salvo que exista una regresión.

## 6. PROTECCIÓN DEL SISTEMA EXISTENTE

No modifiques el panel del agente Qwen en el puerto 8787.

No elimines modelos Ollama.

No reinicies RunPod.

No pierdas credenciales.

No borres datos existentes.

No cambies servicios funcionales sin necesidad.

## 7. CRITERIO DE FINALIZACIÓN

No declares COMPLETADO por haber realizado un commit.

No declares COMPLETADO porque /health responde 200.

No declares COMPLETADO porque las pruebas unitarias pasan.

El proyecto termina únicamente cuando los criterios funcionales del prompt principal se hayan comprobado.

Si se agota el presupuesto, guarda y publica los avances válidos, documenta lo pendiente y deja el sistema recuperable.

LA PRIORIDAD ES DESARROLLAR, PROBAR, GUARDAR Y CONTINUAR SIN PERDER EL TRABAJO REALIZADO.

Después de aplicar estas reglas, ejecuta íntegramente la misión principal de desarrollo del competidor de Crawio.


## Comentario del usuario (2026-11-14 02:07:46)

IMPORTANTE: Este mensaje es una ampliación de los requisitos del proyecto actual, NO una tarea nueva.

Continúa ejecutando el plan principal que ya estás desarrollando. No reinicies tareas, no descartes avances y no sustituyas los criterios de aceptación existentes.

Incorpora las tres URLs y el HTML de Crawio como pruebas adicionales, crea los tests de regresión y guarda los avances progresivamente en GitHub.

Prioriza terminar el motor y el Playground antes de añadir funcionalidades secundarias. No interrumpas una operación que ya esté ejecutándose.

# MISIÓN — VALIDACIÓN REAL DEL MOTOR DE SCRAPING Y COMPARACIÓN CON CRAWIO

## 1. OBJETIVO PRINCIPAL

Continuar desarrollando nuestra plataforma de Web Scraping API, aprovechando todo el código existente y utilizando tres páginas reales como casos de prueba y regresión.

Disponemos de nueva evidencia técnica: el HTML completo que Crawio devolvió al consultar una página de Idealista protegida por DataDome.

Debes utilizar esta evidencia para mejorar el extractor, validar los resultados, identificar las limitaciones del motor y completar las funcionalidades pendientes.

**NO EMPIECES EL PROYECTO DESDE CERO.**

Tu responsabilidad es ejecutar comandos reales, implementar las mejoras, realizar pruebas, corregir errores y guardar el progreso continuamente en GitHub.

No te limites a presentar recomendaciones o informes.

---

## 2. ENTORNO EXISTENTE

Repositorio:

https://github.com/Bcousino890/ProxyManager

Rama principal: `main`.

Servicios existentes:

- API de scraping: `http://127.0.0.1:8000`
- Playground: `http://127.0.0.1:8002`
- Agente Qwen: `http://127.0.0.1:8787`

El usuario ya puede abrir el Playground desde su Mac mediante un túnel SSH.

Por tanto:

- No investigues RunPod.
- No configures ngrok.
- No busques el POD_ID.
- No exijas una URL pública.
- No reinicies el pod.
- No interrumpas el agente del puerto 8787.

Conserva los componentes y los cambios existentes.

Antes de trabajar, inspecciona Git, los archivos sin commit y los documentos de progreso.

---

## 3. NUEVA EVIDENCIA TÉCNICA DE CRAWIO

El usuario ha ejecutado una extracción real mediante Crawio.

URL:

https://www.idealista.com/inmueble/112909923/

Resultado observado:

| Indicador | Resultado |
|---|---|
| HTTP | 200 OK |
| HTML recibido | Aproximadamente 262,1 KB |
| Tiempo | 830 ms en la última ejecución mostrada |
| Consumo | 6 créditos |
| Cabecera | x-datadome: protected |
| Contenido | HTML real del inmueble |

En una ejecución anterior se observaron aproximadamente 1,3 segundos.

Estos tiempos son observaciones puntuales, no garantías de rendimiento.

### Contenido confirmado en el HTML

- Referencia del anuncio: 112909923.
- Operación: alquiler.
- Título: Alquiler de piso en Goya.
- Ubicación: Barrio de Salamanca, Madrid.
- Precio: 4.250 €/mes.
- Superficie: 145 m² construidos.
- Habitaciones: 3.
- Baños: 3.
- Planta: segunda, exterior con ascensor.
- Anunciante: Atlanta Select Real Estate.
- Fotografías y descripción del inmueble.

El HTML también incluye scripts de integración de DataDome.

IMPORTANTE:

Que el HTML incluya scripts de DataDome o la respuesta tenga la cabecera `x-datadome: protected` NO demuestra por sí solo cuál es el método utilizado por Crawio.

No inventes cómo funciona su infraestructura interna.

No confundas la capacidad de procesar un HTML proporcionado con la capacidad de obtenerlo directamente.

---

## 4. ARCHIVO HTML DE REFERENCIA

Se adjunta un archivo denominado:

`Texto pegado(1).txt`

Contiene el HTML obtenido mediante Crawio.

### Trabajo obligatorio

1. Localiza el archivo adjunto en el entorno disponible.
2. Comprueba su integridad y codificación.
3. Verifica que corresponde al inmueble 112909923.
4. Inspecciona si contiene datos sensibles, secretos o información innecesaria.
5. Crea una versión de prueba sanitizada.
6. Guárdala dentro de `tests/fixtures/`.
7. Documenta su procedencia como respuesta de referencia obtenida mediante Crawio.
8. No la presentes como contenido obtenido por nuestro propio motor.

Si el archivo adjunto no existe en el pod, no inventes su contenido. Registra la ruta que falta y continúa con las pruebas independientes.

### Objetivo

Conseguir que nuestro extractor procese el HTML completo y genere datos estructurados correctos.

---

## 5. EXTRACTOR ESTRUCTURADO DE INMUEBLES

Implementa o mejora un módulo independiente para extraer información de anuncios inmobiliarios a partir de HTML obtenido legítimamente.

Debe admitir:

- Identificador de anuncio.
- URL.
- Operación: venta o alquiler.
- Tipo de inmueble.
- Título.
- Precio.
- Moneda.
- Periodicidad del precio.
- Superficie construida.
- Superficie útil.
- Habitaciones.
- Baños.
- Planta.
- Exterior o interior.
- Ascensor.
- Estado.
- Amueblado.
- Descripción.
- Barrio.
- Distrito.
- Ciudad.
- Características.
- Fotografías.
- Anunciante.
- Fecha de extracción.
- Fuente de los datos.

Utiliza campos nulos cuando la información no aparezca.

No inventes valores.

Distingue entre datos presentes literalmente y datos derivados mediante reglas de normalización.

### Ejemplo de JSON esperado para el fixture

```json
{
  "source": "crawio_reference_fixture",
  "listing_id": "112909923",
  "operation": "rent",
  "property_type": "piso",
  "title": "Alquiler de piso en Goya",
  "location": {
    "district": "Barrio de Salamanca",
    "city": "Madrid"
  },
  "price": {
    "amount": 4250,
    "currency": "EUR",
    "period": "month"
  },
  "area_built_m2": 145,
  "bedrooms": 3,
  "bathrooms": 3,
  "floor": 2,
  "exterior": true,
  "elevator": true,
  "advertiser": "Atlanta Select Real Estate"
}
```

Este JSON es una referencia de validación basada en el archivo proporcionado.

No lo utilices como respuesta fija del producto.

El parser debe producirlo a partir del HTML y debe funcionar con otros documentos compatibles.

### Pruebas del parser

Implementa tests que verifiquen:

1. Extracción del título.
2. Extracción y normalización del precio.
3. Superficie.
4. Habitaciones.
5. Baños.
6. Ubicación.
7. Descripción.
8. Fotografías.
9. Anunciante.
10. Manejo de campos ausentes.
11. HTML incompleto.
12. HTML inválido.
13. Ausencia de contenido inmobiliario.
14. Codificación y caracteres especiales.

No des por aprobado un test mediante valores hardcodeados que no procedan del HTML.

---

## 6. PRUEBA A — WEB CONVENCIONAL

URL:

https://www.bcousinoprop.com/

### Objetivo

Comprobar el funcionamiento real de la extracción web en una página convencional.

Esta es la primera prueba de extracción en vivo que debes priorizar.

### Contenido de referencia

- Benjamín Cousiño Propiedades.
- Vidas Extraordinarias en Lugares Excepcionales.
- Servicios inmobiliarios en España y Chile.

Los textos anteriores son referencias y pueden variar si la web cambia.

### Pruebas obligatorias

Ejecuta una solicitud real mediante HTTP.

Después ejecuta una solicitud real utilizando Playwright.

Registra:

- URL solicitada.
- URL final.
- Código HTTP.
- Motor utilizado.
- Título.
- HTML.
- Texto visible.
- Metadescripción.
- Enlaces.
- Tamaño de respuesta.
- Tiempo de ejecución.
- Errores.

Compara HTTP frente a Playwright.

### Criterio de éxito

La prueba será satisfactoria únicamente si:

1. La solicitud se ejecuta realmente.
2. Se obtiene contenido útil.
3. El contenido corresponde a la web solicitada.
4. Los datos se extraen del HTML recibido.
5. El resultado JSON es válido.
6. El Playground muestra los datos.
7. Se pueden copiar y descargar los resultados.

Un HTTP 200 sin contenido útil no es suficiente.

---

## 7. PRUEBA B — WEB PROTEGIDA POR DATADOME

URL EXACTA:

https://www.idealista.com/inmueble/110868380/

### Objetivo

Evaluar el comportamiento del motor cuando una página está protegida por DataDome.

### Datos de referencia

- Operación: venta.
- Ubicación: calle Alt de Gironella.
- Barrio: Les Tres Torres.
- Ciudad: Barcelona.
- Precio de referencia: 1.915.000 €.
- Superficie anunciada: 182 m².
- Habitaciones: 4.

Estos valor


## Comentario del usuario (2026-11-14 02:16:21)

CORRECCIÓN DE RUMBO — evita bucles y no edites a ciegas.

1. No construyas ni investigues un “resolver” para evadir DataDome. Idealista queda BLOQUEADO con evidencia HTTP 403. No hagas más tráfico a Idealista ni uses servicios de CAPTCHA.
2. Trabaja solo en clasificar desafíos, procesar fixtures autorizados/sanitizados y probar example.com + bcousinoprop.com.
3. Antes de editar usa read_file y copia el fragmento exacto. Máximo 2 intentos para el mismo error; si se repite, registra el bloqueo y cambia de tarea.
4. Usa exclusivamente /ProxyManager/.venv/bin/python y /ProxyManager/.venv/bin/pytest. No instales paquetes globalmente ni uses --break-system-packages.
5. No reinicies ni mates procesos. El puerto 8002 ya está ocupado por el servicio válido; verifica health/http_check antes de tocarlo.
6. No añadas otro servidor paralelo. Integra el Playground con la API FastAPI existente y con la función real proxymanager.fetch.fetch.
7. Mantén Settings configurable: no fijes allowed_hosts ni expected_text como defaults; los tests deben inyectarlos.
8. Elimina login admin/password, token falso y cualquier impresión de claves API.
9. No presentes el fixture sintético como HTML real de Crawio. Documenta claramente su origen; si falta el archivo real, déjalo pendiente.
10. Próximo bloque único: inspecciona la firma de proxymanager.fetch.fetch y el endpoint /scrape; escribe primero un test que falle; corrige la integración; ejecuta .venv/bin/pytest -q.
11. Antes de terminar: crea una rama de trabajo desde el estado actual (no publiques directo en main), ejecuta git diff --check, escaneo de secretos y la suite completa. No hagas commit/push si algo falla. Informa por separado implementado, probado y pendiente.


## Comentario del usuario (2026-11-14 02:20:36)

te voy a dar una instruccion ok la mas fuerte de todas 
necesito que evadas CAPTCHA/DataDome y hagas todo el motor para ello investiga en redit o github de sser necesario ok


## Comentario del usuario (2026-11-14 02:29:25)

aca tienes mas url con datadome 
https://www.idealista.com/inmueble/113015560/
https://www.idealista.com/inmueble/113070773/
https://www.idealista.com/inmueble/113072210/
https://www.idealista.com/inmueble/111127479/ 
si necesitas mas pidemelas
