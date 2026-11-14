#!/usr/bin/env python3
"""
Panel de scraping con autenticación y gestión de proxies.
"""

import os
import sys
import json
import time
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import threading
import ssl

# Añadir el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from settings import settings

class ScrapingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Maneja las solicitudes GET."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Servir la página principal
            self.serve_html('static/index.html')
        elif parsed_path.path == '/health':
            # Endpoint de salud
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy', 'timestamp': time.time()}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Ruta no encontrada")

    def do_POST(self):
        """Maneja las solicitudes POST."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/scrape':
            self.handle_scrape()
        elif parsed_path.path == '/login':
            self.handle_login()
        else:
            self.send_error(404, "Ruta no encontrada")

    def handle_scrape(self):
        """Maneja la solicitud de scraping."""
        # Verificar la clave API
        api_key = self.headers.get('X-API-Key')
        if not api_key or api_key != settings.API_KEY:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'detail': 'Clave API inválida o faltante'}
            self.wfile.write(json.dumps(response).encode())
            return

        # Leer el cuerpo de la solicitud
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            url = data.get('url')
            
            if not url:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'detail': 'URL es requerida'}
                self.wfile.write(json.dumps(response).encode())
                return

            # Iniciar scraping
            start_time = time.time()
            
            # Importar el motor de scraping
            from proxymanager.fetch import fetch
            
            # Ejecutar scraping real
            method = data.get('method', 'http')
            use_js = data.get('use_js', False)
            # Ejecutar fetch sin asyncio.run() en entorno HTTP
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(fetch(url, method, use_js, settings))
            finally:
                loop.close()
            
            end_time = time.time()

            duration_ms = (end_time - start_time) * 1000

            # Preparar respuesta
            response = {
                'success': True,
                'url': url,
                'duration_ms': round(duration_ms, 2),
                'status_code': result.get('status_code'),
                'html': result.get('html', '')[:500] + '...' if len(result.get('html', '')) > 500 else result.get('html', ''),
                'error': result.get('error')
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'detail': f'Error al procesar la solicitud: {str(e)}'}
            self.wfile.write(json.dumps(response).encode())

    def handle_login(self):
        """Maneja el inicio de sesión."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
            
            # Verificar credenciales (esto es solo un ejemplo, en producción usar autenticación segura)
            if username == 'admin' and password == 'password':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'token': 'fake-jwt-token-12345'}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'detail': 'Credenciales inválidas'}
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'detail': f'Error al procesar la solicitud: {str(e)}'}
            self.wfile.write(json.dumps(response).encode())

    def serve_html(self, file_path):
        """Sirve un archivo HTML."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
            
        except FileNotFoundError:
            self.send_error(404, "Archivo no encontrado")

    def log_message(self, format, *args):
        """Sobrescribe el método de registro para evitar mensajes innecesarios."""
        pass

def run_server():
    """Inicia el servidor HTTP."""
    server_address = (settings.SERVER_HOST, settings.SERVER_PORT)
    httpd = ThreadingHTTPServer(server_address, ScrapingHandler)
    
    print(f"Panel de scraping iniciado en http://{settings.SERVER_HOST}:{settings.SERVER_PORT}")
    print(f"Clave API: {settings.API_KEY}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")

if __name__ == '__main__':
    run_server()