# Modelos recomendados por fase — revisado el 11 de noviembre de 2026

Estas son **recomendaciones de trabajo**, no requisitos del software ni garantía de disponibilidad en una cuenta. Elegir el modelo que figure en el selector de tu sesión; volver a consultar documentación si cambian las opciones. `medium` suele bastar para una tarea bien delimitada; subir el esfuerzo cuando haya arquitectura, seguridad, datos contradictorios o una revisión final. `xhigh` consume más tiempo y recursos, así que reservarlo para trabajo crítico.

| Fase | Claude Code | Esfuerzo Claude | Codex | Esfuerzo Codex | Motivo |
|---|---|---|---|---|---|
| 1. Investigación y arquitectura | Claude Opus 5.5 | high | GPT-6 Astra | high | Decisiones con requisitos y costes cruzados |
| 2. Backend funcional | Claude Sonnet 5.5 | high | GPT-6.1 Sol | high | Código modular y pruebas con criterio de seguridad |
| 3. DataDome y CAPTCHA | Claude Opus 5.5 | xhigh | GPT-6 Astra | xhigh | Evidencia técnica, límites de inferencia e integración autorizada |
| 4. Benchmark | Claude Opus 5.5 | high | GPT-6 Astra | high | Concurrencia, métricas, límites de coste y parada |
| 5. Panel | Claude Sonnet 5.5 | medium | GPT-6.1 Terra | high | Implementación visual y comprobación de UX |
| 6. Despliegue | Claude Opus 5.5 | high | GPT-6 Astra | high | Seguridad, configuración y recuperación |
| 7. Validación | Claude Opus 5.5 | xhigh | GPT-6 Astra | xhigh | Revisión integral y evaluación de evidencia |
| 8. Operación de 30 días | Claude Sonnet 5.5 | medium | GPT-6.1 Sol | medium | Seguimiento e incidencias; escalar a high en fallos complejos |

Para tareas mecánicas pequeñas dentro de cualquier fase, Claude Haiku 5.5 o GPT-6 Luna con esfuerzo `low` pueden ahorrar recursos, siempre con revisión de cambios. Para una decisión excepcional que desborde Opus con esfuerzo alto, considerar Claude Fable 5.2, si está disponible y el coste se justifica. No sustituir pruebas por la elección de un modelo más fuerte.

## Cómo seleccionarlos

En Claude Code, `/model` permite elegir el modelo y `/effort` el nivel; también existen `--model` y `--effort` al iniciar una sesión. Los alias `opus`, `sonnet` y `haiku` cambian de versión con el tiempo, por lo que la tabla usa nombres explícitos. En Codex, seleccionar el modelo y el esfuerzo disponibles en el cliente antes de empezar cada fase. No se fijan modelos en archivos compartidos del repositorio para permitir elecciones por sesión.

## Base documental

- [OpenAI Docs: modelos](https://developers.openai.com/api/docs/models): Astra para las tareas más exigentes, Sol para equilibrio y Terra para razonamiento visual/interfaz.
- [OpenAI Docs: esfuerzo de razonamiento](https://developers.openai.com/api/docs/guides/reasoning): `medium`/`high` para trabajo complejo; `xhigh` para investigación y revisión profunda cuando compense el coste.
- [Claude Code: configuración de modelos y esfuerzo](https://code.claude.com/docs/en/model-config): Opus para razonamiento complejo, Sonnet para desarrollo diario, Haiku para tareas simples; niveles disponibles y selección por sesión.
- [Claude Platform: modelos](https://platform.claude.com/docs/en/models/overview): capacidades de Opus 5.5, Sonnet 5.5, Haiku 5.5 y Fable 5.2.

La asignación de fases es una **inferencia de ingeniería** a partir de esas capacidades y del trabajo pendiente, no una tabla oficial de los fabricantes. La disponibilidad depende del plan y proveedor de cada cuenta.
