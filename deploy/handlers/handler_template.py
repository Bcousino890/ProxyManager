"""Plantilla de manejador de desafíos. Cópiala, renómbrala y conecta con:

    PROXYMANAGER_CHALLENGE_HANDLER=handler_template:TemplateHandler  (archivo en deploy/handlers/)

Prueba sin servidor:  python -m proxymanager.handlercheck handler_template:TemplateHandler --html pagina.html
Esta plantilla NO resuelve nada: devuelve None (no aplica). Sustituye `handle` por tu integración
autorizada (p. ej. una instalación propia o de evaluación de DataDome). Ver docs/extending-challenge-handlers.md.
"""
from proxymanager.challenges import ChallengeContext, ChallengeResolution


class TemplateHandler:
    name = "template"

    async def handle(self, context: ChallengeContext) -> ChallengeResolution | None:
        # context.html / status_code / headers = respuesta con el desafío
        # context.cookies = cookies de la sesión del cliente; context.proxy_id = proxy usado
        # Si lo resuelves: return ChallengeResolution(resolved=True, html=..., status_code=200, set_cookies=[...])
        return None
