from fastapi import FastAPI
from scraping_engine.api.routes.health import router as health_router

app = FastAPI(
    title="Scraping Engine API",
    version="0.1.0",
    description="Motor de scraping modular con soporte para HTTP y Playwright"
)

# Incluir rutas
app.include_router(health_router)

@app.get("/")
async def root():
    return {"message": "Bienvenido al motor de scraping"}