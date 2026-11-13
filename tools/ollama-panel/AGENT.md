# Agente del panel — arquitectura y operación

## Flujo real
Usuario → `POST /api/chat` → **Run** (hilo propio, independiente del navegador) → `agent_turn` (controlador)
→ Ollama `/api/chat` (stream, tools) → herramienta (`agentkit.Agent.exec`) → resultado (censurado, limitado) → Ollama → …
Los eventos se guardan en memoria (SSE reenganchable: `GET /api/runs/<id>`); la conversación se guarda en disco **tras cada paso**.

Puntos donde puede romperse y qué hace el controlador:
| Fallo | Respuesta |
|---|---|
| Ollama caído / 5xx / timeout (300 s sin datos) | 2 reintentos con espera; luego `error` (progreso guardado) |
| Respuesta vacía | 2 reintentos; a la 3ª → BLOQUEADO |
| Llamada a herramienta mal formada (`<tool_call>`/`<function=…>` en texto) | se parsea si es posible; si no, aviso con formato correcto; a la 4ª → BLOQUEADO |
| Comando ≠ 0, timeout, salida enorme | `[stdout]`/`[stderr]`/código/duración; proceso matado por grupo; salida completa en `~/.pod-panel/toollog/out/` |
| Mismo comando sin cambios / mismo error 3× / mismo archivo reescrito 5× / comando rechazado 2× | estancamiento: se pide cambiar de estrategia (1-3) y a la 4ª → BLOQUEADO + `BLOCKERS.md` |
| Contexto > 70 % de `num_ctx` | compactación determinista (conserva todos los mensajes del usuario, archivos, errores, pruebas + memoria del proyecto) |
| Reinicio del panel con tarea en curso | al arrancar se marca `interrupted`; botón **Reanudar** (repara llamadas sin resultado) |
| Tiempo agotado | `budget`: se guarda y publica el resultado parcial; el último 15 % (3–15 min) es «fase final» |

## Herramientas
`bash` (cwd, timeout, stdout/stderr/código), `read_file` (paginado), `write_file`, `edit_file`, `list_dir`, `search_files`,
`git_status`, `git_diff`, `git_commit` (escáner de secretos), `git_push` (solo rama, sin force, verifica hash remoto; main/master piden aprobación),
`run_tests`, `proc_start` / `proc_inspect` / `inspect_logs` (procesos desacoplados con log), `plan` (estados PENDIENTE/EJECUTANDO/COMPLETADO/FALLIDO/BLOQUEADO; COMPLETADO exige evidencia),
`project_init` / `memory_update`, `notify`, `web_search`, `web_fetch`, `describe_image`.

## Memoria persistente
`TASK/PLAN/PROGRESS/DECISIONS/TEST_RESULTS/BLOCKERS.md` por proyecto (en `pod-work/.sessions/<conv>/` hasta que el agente llama a `project_init`). PROGRESS/TEST_RESULTS/PLAN se actualizan automáticamente con evidencia.

## Seguridad
Escáner de secretos (tokens, claves privadas, credenciales en URLs/proxies, `.env`, cookies, sqlite…) en escritura, `git_commit` y un **hook pre-commit** (`.git/hooks/pre-commit`) que también frena `git commit` hecho por bash. Registros y comandos mostrados se censuran. Comandos destructivos (`rm -r`, `git push` a main, `--no-verify`, `ollama rm`, …) piden aprobación (caduca a los 15 min → rechazado).

## Ollama
`num_ctx` 32768 por defecto (`PANEL_NUM_CTX`), `temperature` 0.2, `top_p` 0.8, `top_k` 20, `repeat_penalty` 1.05, `num_predict` 8192, `keep_alive` 2h. «Razonar» cambia al modelo `qwen3:30b` con `think=true` (no es un modo del coder).

## Operación
- Pruebas: `cd tools/ollama-panel && python3 -m pytest tests -q` (Ollama falso, sin GPU).
- Despliegue seguro: `bash /root/restart-panel-safe.sh` (prueba en otro puerto, sustituye, revierte si falla). Reversión manual: `bash /root/rollback-panel.sh`.
- Métricas: `GET /api/metrics`; registro por conversación: `~/.pod-panel/toollog/<id>.jsonl`.
