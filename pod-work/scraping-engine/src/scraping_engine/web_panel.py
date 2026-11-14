from pydantic import BaseModel
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="Panel de Scraping")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Obtener la lista de proxies desde el entorno o archivo
    proxy_list = []
    proxy_file = os.getenv("PROXY_FILE", "/ProxyManager/pod-work/scraping-engine/proxies.txt")
    if os.path.exists(proxy_file):
        with open(proxy_file, 'r') as f:
            proxy_list = [line.strip() for line in f.readlines() if line.strip()]

    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel de Scraping</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .tab { display: none; }
        .tab.active { display: block; }
        button.tablink { background-color: #f1f1f1; border: none; outline: none; cursor: pointer; padding: 14px 16px; margin-right: 5px; }
        button.tablink.active { background-color: #ccc; }
        .result-container { margin-top: 20px; }
        pre { background-color: #f4f4f4; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Motor de Extracción Web</h1>
    
    <form id="scrapeForm">
        <label for="url">URL:</label><br>
        <input type="text" id="url" name="url" required style="width: 500px;"><br><br>

        <label for="use_js">Tipo de Scraping:</label><br>
        <select id="use_js" name="use_js">
            <option value="false">HTTP</option>
            <option value="true">JavaScript</option>
        </select><br><br>

        <label for="proxy">Proxy:</label><br>
        <select id="proxy" name="proxy">
            <option value="">Ninguno</option>
"""
    for p in proxy_list:
        html_content += f'<option value="{p}">{p}</option>'
    html_content += """
        </select><br><br>

        <button type="submit">Extraer</button>
    </form>

    <div id="loading" style="display:none;">Cargando...</div>

    <div class="result-container">
        <div id="tabs">
            <button class="tablink active" onclick="openTab(event, 'html')">HTML</button>
            <button class="tablink" onclick="openTab(event, 'text')">Texto</button>
            <button class="tablink" onclick="openTab(event, 'json')">JSON</button>
        </div>

        <div id="html" class="tab active">
            <h2>HTML:</h2>
            <pre id="html-result"></pre>
        </div>

        <div id="text" class="tab">
            <h2>Texto:</h2>
            <pre id="text-result"></pre>
        </div>

        <div id="json" class="tab">
            <h2>JSON:</h2>
            <pre id="json-result"></pre>
        </div>
    </div>

    <script>
        document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const url = formData.get('url');
            const use_js = formData.get('use_js') === 'true';
            const proxy = formData.get('proxy');

            const loadingElement = document.getElementById('loading');
            loadingElement.style.display = 'block';

            try {
                const response = await fetch('/scrape', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url, use_js, proxy})
                });

                const result = await response.json();
                
                document.getElementById('html-result').textContent = result.content;
                document.getElementById('text-result').textContent = result.content.replace(/<[^>]*>/g, '');
                document.getElementById('json-result').textContent = JSON.stringify(result, null, 2);
                
                // Mostrar las pestañas
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                document.getElementById('html').classList.add('active');
                document.querySelector('.tablink.active').classList.remove('active');
                document.querySelector('.tablink').classList.add('active');
            } catch (error) {
                console.error('Error:', error);
                alert('Error al extraer datos.');
            } finally {
                loadingElement.style.display = 'none';
            }
        });

        function openTab(evt, tabName) {
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            const tablinks = document.querySelectorAll('.tablink');
            tablinks.forEach(link => link.classList.remove('active'));
            
            document.getElementById(tabName).classList.add('active');
            evt.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""
    return html_content

class PanelScrapeRequest(BaseModel):
    url: str
    use_js: bool = False
    proxy: str = ""


@app.post("/scrape")
async def scrape(request: PanelScrapeRequest):
    """Mismo contrato que envía el formulario del panel (JSON). Usa el motor real: HTTP o Playwright."""
    from scraping_engine.engine import ScrapingEngine
    engine = ScrapingEngine()
    fn = engine._scrape_with_playwright if request.use_js else engine._scrape_with_httpx
    result = await fn(request.url, request.proxy or None)
    return {
        "content": result.content or "",
        "status_code": result.status_code,
        "duration": result.duration_ms,
        "error": result.error,
        "datadome_blocked": result.is_datadome_blocked,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)