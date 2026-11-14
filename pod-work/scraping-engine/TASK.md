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


## Instrucción del usuario (2026-11-14 01:10:51)

# ACTUALIZACIÓN CRÍTICA DEL ESTADO REAL

Antes de comenzar, debes saber:

1. El panel ya es accesible desde mi Mac en http://127.0.0.1:8002 mediante SSH. NO pierdas tiempo intentando exponerlo públicamente con ngrok o RunPod.

2. Existen 12 archivos sin commit. Inspecciónalos, preserva los cambios útiles y verifica que no contienen credenciales. No los elimines ni sobrescribas.

3. El controlador únicamente ha acreditado 2 pruebas aprobadas. No afirmes que toda la aplicación está probada.

4. El panel responde HTTP 200, pero eso NO demuestra que el botón Extraer funcione. Debes probar el flujo real desde el navegador.

5. La URL de Idealista devuelve HTTP 403 por DataDome. Registra este resultado como bloqueo real.

6. El usuario ha demostrado que Crawio obtiene HTTP 200 y aproximadamente 262,1 KB de HTML útil para esa misma URL. Utiliza esa información como referencia comparativa, no como prueba de que nuestro sistema tenga la misma capacidad.

7. El agente debe mantener abiertos los servicios:
   - API: 8000
   - Panel: 8002
   - Agente Qwen: 8787

8. El estado actual no es COMPLETADO. Debes crear un nuevo plan que incluya todas las funcionalidades pendientes, con pruebas verificables.

PRIORIDAD ABSOLUTA: reparar el botón Extraer, completar el motor y rediseñar el Playground profesional.

NO CIERRES EL TRABAJO PORQUE LOS PROCESOS RESPONDAN HTTP 200.

NO CIERRES EL TRABAJO PORQUE GITHUB ESTÉ SINCRONIZADO.

DEBES DEMOSTRAR QUE EL USUARIO PUEDE INTRODUCIR UNA URL Y RECIBIR DATOS REALES EN LA INTERFAZ.

# MISIÓN MAESTRA — CONSTRUIR UNA ALTERNATIVA FUNCIONAL Y PROFESIONAL A CRAWIO.COM

## 0. TU ROL Y RESPONSABILIDAD

Eres un Principal Software Engineer, Web Scraping Infrastructure Architect, Backend Engineer, Frontend Engineer, QA Engineer y DevOps Engineer.

Especialidades:

- Python 3.12+
- FastAPI y Pydantic
- httpx y asyncio
- Playwright y Chromium
- Extracción de HTML y datos estructurados
- Gestión de proxies ISP
- Redes HTTP, TLS y diagnóstico de errores
- Arquitecturas de scraping escalables
- Docker y Docker Compose
- PostgreSQL, SQLite y Redis
- APIs REST
- Sistemas de trabajos asíncronos
- Observabilidad, métricas y costes
- Frontend SaaS profesional
- Git y GitHub
- Testing end-to-end

Tu trabajo NO consiste en explicar cómo se construye una plataforma de scraping.

Tu trabajo consiste en ejecutar comandos reales, modificar el código existente, implementar funcionalidades, instalar dependencias, probar, corregir, desplegar y entregar una aplicación funcional.

Dispones de un agente con herramientas reales de terminal, edición de archivos, pruebas, Git y control de procesos.

Utiliza estas herramientas.

No termines simplemente por haber escrito código.

---

# 1. CONTEXTO DEL PROYECTO

Estamos desarrollando nuestra propia plataforma de Web Scraping API, inspirada funcionalmente en:

https://crawio.com/

Referencia visual:

https://crawio.com/app/#playground

El usuario ya ha conseguido abrir el panel existente desde su Mac.

Entorno actual:

Panel del agente Qwen:
http://127.0.0.1:8787

API del scraper:
http://127.0.0.1:8000

Panel del scraper:
http://127.0.0.1:8002

Acceso desde el Mac mediante túnel SSH.

Infraestructura:

- RunPod.
- NVIDIA RTX 3090 con 24 GB VRAM.
- Ollama.
- Qwen3-Coder:30B.
- Linux.
- GitHub.

Repositorio:

https://github.com/Bcousino890/ProxyManager

Rama de publicación:

main

Último commit comunicado anteriormente:

2539a4fafd

Verifica el estado actual del repositorio, ya que podrían existir cambios posteriores.

POD_ID observado:

jqef2hnlvre179

No presupongas que sigue activo o que los puertos están expuestos públicamente.

IMPORTANTE:

El panel del agente que funciona en 8787 NO debe modificarse ni interrumpirse.

El desarrollo debe continuar sobre el producto de scraping existente.

No reconstruyas el proyecto desde cero salvo que exista una justificación técnica demostrable.

---

# 2. PROBLEMAS REALES DETECTADOS

Actualmente:

1. El panel básico abre correctamente en el navegador del Mac.
2. Se muestra un formulario con URL, tipo HTTP/JavaScript, proxy y botón Extraer.
3. Al pulsar Extraer no aparece ningún resultado visible.
4. No hay un indicador de carga.
5. No hay mensajes de error visibles.
6. No hay un visor de respuestas HTML o JSON.
7. El selector de proxies muestra únicamente "Ninguno".
8. La API expone al menos GET /health y POST /scrape.
9. No existe evidencia suficiente de que los trabajos masivos y otros módulos estén completos.
10. La URL de Idealista devuelve HTTP 403 por DataDome desde nuestro motor.
11. El panel actual tiene una interfaz HTML extremadamente básica.

NO declares el producto completado.

La prioridad es arreglar lo existente y demostrar resultados reales.

---

# 3. EVIDENCIA REAL DE CRAWIO

El usuario ha probado Crawio con:

https://www.idealista.com/inmueble/112909923/

Resultado observado en las capturas:

- HTTP 200 OK.
- HTML recibido: aproximadamente 262,1 KB.
- Tiempo: aproximadamente 1,3 segundos.
- Coste comunicado por Crawio: 6 créditos.
- Vista previa del inmueble disponible.
- Metadatos reales del anuncio.
- Cabecera x-datadome: protected.
- Título del anuncio relacionado con alquiler de piso en Goya, Barrio de Salamanca, Madrid.

Nuestro motor devolvió:

- HTTP 403.
- DataDome.
- Página de desafío.
- Ningún contenido útil del inmueble.

Esta comparación es una REFERENCIA DE CALIDAD, no una garantía de que podamos reproducir inmediatamente el mismo resultado.

No inventes datos del anuncio.

No confundas un HTTP 200 con una extracción válida.

No afirmes paridad con Crawio sin pruebas equivalentes y verificables.

No intentes eludir mecanismos de autenticación o protección de terceros sin autorización.

Si una página rechaza el acceso automatizado, clasifica correctamente la respuesta y estudia las vías de acceso autorizadas disponibles.

---

# 4. INSPECCIÓN INICIAL OBLIGATORIA

Antes de programar, utiliza las herramientas para ejecutar:

pwd
whoami
git status --short --branch
git remote -v
python3 --version
docker --version
docker compose version
free -h
df -h
ss -ltnp

Localiza los procesos que escuchan en:

- 8000
- 8002
- 8787

Inspecciona la estructura del producto de scraping y sus archivos de configuración.

Lee cuando existan:

TASK.md
ACCEPTANCE.md
PLAN.md
PROGRESS.md
DECISIONS.md
TEST_RESULTS.md
BLOCKERS.md

Comprueba qué funcionalidades están implementadas realmente.

Conserva las modificaciones preexistentes.

No ejecutes comandos destructivos.

No borres modelos de Ollama.

No reinicies el pod.

No interrumpas el agente.

Genera un plan nuevo que cubra TODOS los requisitos de esta misión.

No reutilices un plan antiguo que ya esté marcado como completado.

---

# 5. PRIORIDAD P0 — REPARAR EL BOTÓN EXTRAER

Actualmente, el usuario pulsa Extraer y no ocurre nada visible.

Debes investigar y corregir la causa real.

Comprueba:

1. Estructura HTML del formulario.
2. Eventos JavaScript.
3. Método HTTP empleado.
4. Endpoint al que llama el frontend.
5. URL absoluta o relativa.
6. Autenticación.
7. CORS.
8. Redirecciones.
9. Formato JSON enviado.
10. Esquema Pydantic requerido.
11. Respuesta del backend.
12. Excepciones del navegador.
13. Errores de red.
14. Timeouts.
15. Renderizado del resultado.
16. Logs de servidor.

IMPORTANTE:

El usuario accede desde su Mac mediante túnel SSH.

El frontend debe funcionar correctamente en:

http://127.0.0.1:8002

Aunque el backend se encuentre en el puerto 8000.

Preferiblemente utiliza rutas relativas y un proxy de backend del mismo origen, evitando dependencias innecesarias de CORS.

No muestres al usuario un botón que aparentemente funciona pero no hace nada.

Implementa:

- Indicador de carga.
- Tiempo transcurrido.
- Mensajes visibles de error.
- Botón desactivado durante una solicitud.
- Resultados visibles.
- Manejo correcto de excepciones.
- Cancelación, si existe soporte real.

## Prueba P0-A

URL:
https://example.com

Motor:
HTTP

Resultado esperado:

- Solicitud real.
- Código HTTP real.
- HTML.
- Título 
