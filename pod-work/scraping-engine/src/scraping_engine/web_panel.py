from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Panel de Scraping")

# Montar archivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Panel de Scraping</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <h1>Motor de Extracción Web</h1>
        <form id="scrapeForm">
            <label for="url">URL:</label>
            <input type="text" id="url" name="url" required><br><br>
            
            <label for="use_js">Tipo de Scraping:</label>
            <select id="use_js" name="use_js">
                <option value="false">HTTP</option>
                <option value="true">JavaScript</option>
            </select><br><br>

            <label for="proxy">Proxy:</label>
            <select id="proxy" name="proxy">
                <option value="">Ninguno</option>
                <!-- Opciones de proxy se llenarán dinámicamente -->
            </select><br><br>

            <button type="submit">Extraer</button>
        </form>

        <div id="result"></div>

        <script>
            document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const url = formData.get('url');
                const use_js = formData.get('use_js') === 'true';
                const proxy = formData.get('proxy');

                const response = await fetch('/scrape', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, use_javascript: use_js, proxy_url: proxy })
                });

                const result = await response.json();
                document.getElementById('result').innerHTML = `
                    <h2>Resultado:</h2>
                    <p><strong>Estado:</strong> ${result.status_code}</p>
                    <p><strong>Tipo de contenido:</strong> ${result.content_type}</p>
                    <p><strong>Duración:</strong> ${result.duration_ms.toFixed(2)} ms</p>
                    <p><strong>Bloqueo DataDome:</strong> ${result.is_datadome_blocked ? 'Sí' : 'No'}</p>
                    <h3>Contenido:</h3>
                    <pre>${result.content.substring(0, 1000)}...</pre>
                `;
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)