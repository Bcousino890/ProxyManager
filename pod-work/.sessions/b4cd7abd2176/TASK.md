# Tarea

IMPORTANTE — CONFIGURACIÓN GITHUB

El repositorio actual todavía no tiene una rama main.

Debes comprobar primero el repositorio y las ramas disponibles.

Trabaja en una rama de desarrollo y realiza commits incrementales.

Al finalizar, después de ejecutar y aprobar las pruebas, crea la rama main si todavía no existe, integra el código validado y publícalo en GitHub.

No utilices force push ni sobrescribas cambios existentes.

Verifica que el hash remoto coincide con el commit final.

No declares el proyecto terminado hasta comprobar la publicación y entregar la URL funcional del panel de scraping.



# REGLAS DE EJECUCIÓN PARA EL AGENTE LOCAL QWEN

Estás ejecutándote mediante un panel de agente conectado a Ollama y GitHub.

Debes aprovechar las herramientas reales del panel: terminal, lectura y edición de archivos, ejecución de pruebas y operaciones Git.

## Persistencia y progreso

Al comenzar, crea y mantén:

- TASK.md: requisitos y criterios de aceptación.
- PROGRESS.md: estado actual, tareas completadas y pendientes.
- TEST_RESULTS.md: pruebas ejecutadas y resultados.
- ARCHITECTURE.md: decisiones técnicas importantes.

Actualiza PROGRESS.md después de cada fase completada.

No repitas investigaciones ya realizadas salvo que haya cambiado su resultado.

Si pierdes contexto, lee primero estos archivos y continúa desde el último estado verificado.

## Ejecución

Trabaja en ciclos:

1. Inspecciona.
2. Decide una implementación pequeña.
3. Escribe el código.
4. Ejecuta el código.
5. Comprueba el resultado.
6. Corrige errores.
7. Ejecuta pruebas de regresión.
8. Guarda el progreso.
9. Continúa con la siguiente funcionalidad.

No escribas cientos de líneas sin ejecutar pruebas intermedias.

## Terminal

Usa comandos no interactivos cuando sea posible.

Aplica timeouts a procesos que puedan bloquearse.

No dejes comandos de ejecución indefinida ocupando la sesión del agente.

Utiliza Docker Compose con ejecución desacoplada para los servicios persistentes.

No imprimas credenciales.

## GitHub

Comprueba el repositorio y la rama antes de modificar archivos.

Realiza commits incrementales.

No dependas exclusivamente del botón de subida automática del panel.

No publiques cambios que contengan secretos o pruebas críticas fallidas.

El resultado final debe estar en main únicamente después de la validación.

Comprueba el commit remoto después del push.

## Recursos del servidor

Antes de ejecutar pruebas pesadas, comprueba CPU, RAM, VRAM y espacio en disco.

Limita la concurrencia para evitar que Chromium, Docker u otros procesos agoten los recursos del sistema.

Si Qwen y Chromium comparten el mismo pod, reserva memoria suficiente para ambos.

## Prioridades

P0: API funcional, tests, seguridad y Git.
P1: Playwright, proxies y resultados reales.
P2: trabajos masivos y métricas.
P3: panel y URL pública.
P4: optimización avanzada.

No declares éxito sin ejecutar pruebas reales.

Si una funcionalidad no está terminada, documéntala sin inventar resultados.

Continúa trabajando hasta agotar el presupuesto de ejecución o completar todos los criterios de aceptación.
