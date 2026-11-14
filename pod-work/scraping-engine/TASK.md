# Tarea

# MISIÓN PRIORITARIA — DESARROLLAR Y VALIDAR EL MOTOR DE EXTRACCIÓN WEB

## OBJETIVO

Construir una alternativa funcional a Crawio.com, dando prioridad al motor de extracción, la gestión de proxies, el diagnóstico de DataDome y la comprobación real de resultados.

No quiero que vuelvas a configurar GitHub ni que te limites a modificar ProxyManager.

Quiero un producto de scraping que funcione, con API, panel web y pruebas ejecutadas.

## 1. INSPECCIÓN INICIAL

Inspecciona el repositorio, las ramas, el código existente, las dependencias y los procesos.

Lee TASK.md, ACCEPTANCE.md, PROGRESS.md y los registros de pruebas existentes.

Identifica qué funcionalidades del producto están implementadas de verdad y cuáles faltan.

No marques ninguna funcionalidad como completada basándote únicamente en documentación o código no ejecutado.

## 2. PRUEBA DE REFERENCIA — IDEALISTA

URL:

https://www.idealista.com/inmueble/112909923/

Resultado ya observado:

- HTTP 403.
- Cabecera `server: DataDome`.
- Cabecera `x-datadome: protected`.
- Página de desafío de aproximadamente 773 bytes.
- Ningún dato útil del anuncio.

Registra ese resultado como línea base, no como éxito.

El objetivo de la investigación es entender por qué la extracción convencional falla y qué métodos de acceso legítimos permitirían obtener los datos.

No confundas cargar una página de desafío con extraer un anuncio.

No inventes precios, superficies ni descripciones.

No intentes eludir autenticación, CAPTCHA ni restricciones de acceso no autorizadas.

Si esa página no puede extraerse legítimamente, registra el bloqueo y continúa con las demás funciones.

## 3. COMPARACIÓN CON CRAWIO

Investiga la documentación pública de Crawio.com.

Comprueba qué funcionalidades anuncia:

- Extracción de HTML.
- Renderizado JavaScript.
- Gestión de proxies.
- Sesiones.
- Geolocalización.
- Procesamiento concurrente.
- Gestión de errores.
- Resultados estructurados.
- Métricas y consumo.

Si existe una cuenta o API de Crawio que ya esté configurada legítimamente en el entorno, realiza una comparación de resultados usando las mismas URLs autorizadas.

No inventes resultados de Crawio si no puedes ejecutar su API.

Documenta las diferencias funcionales y los resultados medidos.

## 4. PROXIES DECODO

Utiliza los 10 proxies ISP del archivo privado configurado mediante PROXY_FILE.

Para cada endpoint:

1. Verifica conectividad.
2. Comprueba autenticación.
3. Registra la IP de salida observada.
4. Mide latencia.
5. Comprueba errores de red.
6. Registra estado operativo.
7. Realiza una solicitud de prueba a un endpoint autorizado.

Implementa selección y monitorización de proxies.

No publiques credenciales.

No presupongas que diez endpoints corresponden a diez IP diferentes.

## 5. MOTOR DE SCRAPING

Implementa:

- FastAPI.
- HTTP asíncrono mediante httpx.
- Renderizado JavaScript con Playwright.
- Extracción de HTML.
- Extracción de texto.
- Título, metadatos y enlaces.
- JSON estructurado.
- Trabajos por lotes.
- Concurrencia configurable.
- Reintentos limitados.
- Persistencia.
- Métricas.
- Clasificación de bloqueos.
- Límites de recursos.
- Autenticación y protección SSRF.

No construyas simplemente un wrapper que simule respuestas.

## 6. PANEL WEB

Crea un panel independiente del panel del agente Qwen.

Debe tener:

- Campo para introducir URL.
- Botón Extraer.
- Selector HTTP/JavaScript.
- Selector de proxy.
- Visualización HTML, texto y JSON.
- Código HTTP.
- Duración.
- Errores.
- Bloqueos DataDome.
- Historial de consultas.
- Descarga de resultados.

El servicio debe utilizar un puerto distinto del 8787.

## 7. DESPLIEGUE

Ejecuta los servicios mediante Docker Compose.

Comprueba que permanecen activos después de finalizar la sesión.

Configura una URL HTTPS accesible desde mi Mac cuando exista infraestructura disponible.

Si faltan POD_ID, puerto publicado o configuración del túnel, informa exactamente qué dato necesitas.

No declares que has desplegado una URL pública simplemente por añadir un campo `public_url`.

## 8. PRUEBAS Y EVIDENCIAS

Ejecuta:

- Tests unitarios.
- Tests de integración.
- Tests de Playwright.
- Pruebas de proxies.
- Pruebas de API.
- Pruebas del panel.
- Pruebas de Docker.
- Pruebas sobre páginas autorizadas.

Incluye una página HTML estática y otra que requiera JavaScript.

Para Idealista, entrega el resultado real observado y el diagnóstico del bloqueo.

Cada prueba debe aportar evidencia:

- Comando ejecutado.
- Código de salida.
- Resultado HTTP.
- Datos obtenidos.
- Duración.
- Estado final.

No marques como éxito una prueba que devuelve CAPTCHA o un desafío.

## 9. GITHUB

Trabaja en el repositorio correcto.

No sobrescribas los componentes del panel del agente.

Realiza commits incrementales.

Ejecuta las pruebas antes de publicar.

Publica el código validado en main, respetando las protecciones de la rama.

Verifica el hash remoto.

## 10. PROHIBIDO TERMINAR PREMATURAMENTE

No puedes declarar COMPLETADO únicamente porque:

- Las pruebas unitarias pasan.
- Existe un commit.
- GitHub está configurado.
- Se ha añadido una variable de entorno.
- Se ha creado una estructura de carpetas.
- Se ha implementado `/health`.
- Se ha detectado DataDome.

El producto solo estará completado cuando:

1. La API ejecute una extracción real autorizada.
2. Playwright renderice una página de prueba.
3. El panel permita introducir una URL y ver resultados reales.
4. Los proxies estén comprobados.
5. Los resultados sean verificables.
6. El despliegue funcione.
7. El código esté publicado.
8. Los bloqueos y limitaciones estén documentados.

Si falta cualquiera de los requisitos obligatorios, informa INCOMPLETO.

## 11. INFORME FINAL

Entrega:

- URL del panel.
- URL de la API.
- Repositorio y commit.
- Número de proxies operativos.
- Pruebas aprobadas y fallidas.
- Resultados reales de extracción.
- Resultado específico de Idealista.
- Comparación verificable con Crawio.
- Latencia.
- Coste estimado.
- Funcionalidades pendientes.

Ejecuta todas las operaciones que permitan tus herramientas. No me entregues únicamente código ni recomendaciones.

COMIENZA AHORA Y NO RECONFIGURES GITHUB SI YA FUNCIONA.


## Instrucción del usuario (2026-11-14 00:50:03)

# MISIÓN PRIORITARIA — DESARROLLAR Y VALIDAR EL MOTOR DE EXTRACCIÓN WEB

## OBJETIVO

Construir una alternativa funcional a Crawio.com, dando prioridad al motor de extracción, la gestión de proxies, el diagnóstico de DataDome y la comprobación real de resultados.

No quiero que vuelvas a configurar GitHub ni que te limites a modificar ProxyManager.

Quiero un producto de scraping que funcione, con API, panel web y pruebas ejecutadas.

## 1. INSPECCIÓN INICIAL

Inspecciona el repositorio, las ramas, el código existente, las dependencias y los procesos.

Lee TASK.md, ACCEPTANCE.md, PROGRESS.md y los registros de pruebas existentes.

Identifica qué funcionalidades del producto están implementadas de verdad y cuáles faltan.

No marques ninguna funcionalidad como completada basándote únicamente en documentación o código no ejecutado.

## 2. PRUEBA DE REFERENCIA — IDEALISTA

URL:

https://www.idealista.com/inmueble/112909923/

Resultado ya observado:

- HTTP 403.
- Cabecera `server: DataDome`.
- Cabecera `x-datadome: protected`.
- Página de desafío de aproximadamente 773 bytes.
- Ningún dato útil del anuncio.

Registra ese resultado como línea base, no como éxito.

El objetivo de la investigación es entender por qué la extracción convencional falla y qué métodos de acceso legítimos permitirían obtener los datos.

No confundas cargar una página de desafío con extraer un anuncio.

No inventes precios, superficies ni descripciones.

No intentes eludir autenticación, CAPTCHA ni restricciones de acceso no autorizadas.

Si esa página no puede extraerse legítimamente, registra el bloqueo y continúa con las demás funciones.

## 3. COMPARACIÓN CON CRAWIO

Investiga la documentación pública de Crawio.com.

Comprueba qué funcionalidades anuncia:

- Extracción de HTML.
- Renderizado JavaScript.
- Gestión de proxies.
- Sesiones.
- Geolocalización.
- Procesamiento concurrente.
- Gestión de errores.
- Resultados estructurados.
- Métricas y consumo.

Si existe una cuenta o API de Crawio que ya esté configurada legítimamente en el entorno, realiza una comparación de resultados usando las mismas URLs autorizadas.

No inventes resultados de Crawio si no puedes ejecutar su API.

Documenta las diferencias funcionales y los resultados medidos.

## 4. PROXIES DECODO

Utiliza los 10 proxies ISP del archivo privado configurado mediante PROXY_FILE.

Para cada endpoint:

1. Verifica conectividad.
2. Comprueba autenticación.
3. Registra la IP de salida observada.
4. Mide latencia.
5. Comprueba errores de red.
6. Registra estado operativo.
7. Realiza una solicitud de prueba a un endpoint autorizado.

Implementa selección y monitorización de proxies.

No publiques credenciales.

No presupongas que diez endpoints corresponden a diez IP diferentes.

## 5. MOTOR DE SCRAPING

Implementa:

- FastAPI.
- HTTP asíncrono mediante httpx.
- Renderizado JavaScript con Playwright.
- Extracción de HTML.
- Extracción de texto.
- Título, metadatos y enlaces.
- JSON estructurado.
- Trabajos por lotes.
- Concurrencia configurable.
- Reintentos limitados.
- Persistencia.
- Métricas.
- Clasificación de bloqueos.
- Límites de recursos.
- Autenticación y protección SSRF.

No construyas simplemente un wrapper que simule respuestas.

## 6. PANEL WEB

Crea un panel independiente del panel del agente Qwen.

Debe tener:

- Campo para introducir URL.
- Botón Extraer.
- Selector HTTP/JavaScript.
- Selector de proxy.
- Visualización HTML, texto y JSON.
- Código HTTP.
- Duración.
- Errores.
- Bloqueos DataDome.
- Historial de consultas.
- Descarga de resultados.

El servicio debe utilizar un puerto distinto del 8787.

## 7. DESPLIEGUE

Ejecuta los servicios mediante Docker Compose.

Comprueba que permanecen activos después de finalizar la sesión.

Configura una URL HTTPS accesible desde mi Mac cuando exista infraestructura disponible.

Si faltan POD_ID, puerto publicado o configuración del túnel, informa exactamente qué dato necesitas.

No declares que has desplegado una URL pública simplemente por añadir un campo `public_url`.

## 8. PRUEBAS Y EVIDENCIAS

Ejecuta:

- Tests unitarios.
- Tests de integración.
- Tests de Playwright.
- Pruebas de proxies.
- Pruebas de API.
- Pruebas del panel.
- Pruebas de Docker.
- Pruebas sobre páginas autorizadas.

Incluye una página HTML estática y otra que requiera JavaScript.

Para Idealista, entrega el resultado real observado y el diagnóstico del bloqueo.

Cada prueba debe aportar evidencia:

- Comando ejecutado.
- Código de salida.
- Resultado HTTP.
- Datos obtenidos.
- Duración.
- Estado final.

No marques como éxito una prueba que devuelve CAPTCHA o un desafío.

## 9. GITHUB

Trabaja en el repositorio correcto.

No sobrescribas los componentes del panel del agente.

Realiza commits incrementales.

Ejecuta las pruebas antes de publicar.

Publica el código validado en main, respetando las protecciones de la rama.

Verifica el hash remoto.

## 10. PROHIBIDO TERMINAR PREMATURAMENTE

No puedes declarar COMPLETADO únicamente porque:

- Las pruebas unitarias pasan.
- Existe un commit.
- GitHub está configurado.
- Se ha añadido una variable de entorno.
- Se ha creado una estructura de carpetas.
- Se ha implementado `/health`.
- Se ha detectado DataDome.

El producto solo estará completado cuando:

1. La API ejecute una extracción real autorizada.
2. Playwright renderice una página de prueba.
3. El panel permita introducir una URL y ver resultados reales.
4. Los proxies estén comprobados.
5. Los resultados sean verificables.
6. El despliegue funcione.
7. El código esté publicado.
8. Los bloqueos y limitaciones estén documentados.

Si falta cualquiera de los requisitos obligatorios, informa INCOMPLETO.

## 11. INFORME FINAL

Entrega:

- URL del panel.
- URL de la API.
- Repositorio y commit.
- Número de proxies operativos.
- Pruebas aprobadas y fallidas.
- Resultados reales de extracción.
- Resultado específico de Idealista.
- Comparación verificable con Crawio.
- Latencia.
- Coste estimado.
- Funcionalidades pendientes.

Ejecuta todas las operaciones que permitan tus herramientas. No me entregues únicamente código ni recomendaciones.

COMIENZA AHORA Y NO RECONFIGURES GITHUB SI YA FUNCIONA.
