"""Prueba un manejador de desafíos sin servidor: `python -m proxymanager.handlercheck modulo:fabrica --html pagina.html`."""
import argparse
import asyncio
from pathlib import Path

from .challenges import ChallengeContext, load_handler
from .config import Settings
from .fetch import classify


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("handler")
    p.add_argument("--html", type=Path, required=True, help="Página con el desafío (guardada de un destino autorizado)")
    p.add_argument("--url", default="https://destino-autorizado.example/")
    p.add_argument("--status", type=int, default=403)
    p.add_argument("--expected-text", default=None)
    args = p.parse_args()
    handler = load_handler(args.handler)
    if handler is None:
        raise SystemExit("Indica modulo:fabrica")
    html = args.html.read_text(errors="replace")
    ctx = ChallengeContext(args.url, "GET", args.status, {}, html)
    resolution = asyncio.run(handler.handle(ctx))
    print(f"manejador: {handler.name}")
    if resolution is None:
        print("resultado: None (no aplica)")
        return
    final_html = resolution.html if resolution.html is not None else html
    status = resolution.status_code or args.status
    success, validation = classify(final_html, status, Settings(db_path=":memory:"), args.expected_text)
    print(f"resolved={resolution.resolved} status={status} cookies_devueltas={len(resolution.set_cookies)} nota={resolution.note!r}")
    print(f"revalidación: success={success} {validation}")


if __name__ == "__main__":
    main()
