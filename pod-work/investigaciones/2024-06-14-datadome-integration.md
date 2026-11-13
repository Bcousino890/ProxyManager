# Investigación: Integración de Datadome

## Resumen Ejecutivo
Datadome es una plataforma de protección contra bots y fraude en línea. Para su integración, se requieren: 1) Cuenta y claves API, 2) Integración del lado del servidor (ej. Nginx, Cloudflare), 3) Tag JavaScript del lado del cliente, y 4) Monitoreo en el dashboard. No es un paquete de software para instalar via apt.

## Hallazgos

### 1. ¿Qué es Datadome y sus productos?
- Plataforma de gestión de bots y fraude en línea [1].
- Productos clave: Bot Protect (protección básica), Agentic Trust (tráfico de agentes de IA), DDoS Protect, Account Protect, Ad Protect [2].

### 2. ¿Cómo obtener claves API y configurar la cuenta?
- Crear cuenta en [dashboard.datadome.co](https://dashboard.datadome.co) [3].
- Claves: *server-side* (para integración en servidores) y *client-side* (para el tag JavaScript) [3].

### 3. Integración del lado del servidor
- **Recomendación principal**: Integrar en el *Edge* (CDN/Nginx) para mejor rendimiento [3].
- Opciones soportadas: Nginx, Cloudflare, AWS CloudFront, Apache, etc. [3].
- Ejemplo para Nginx: Incluir el módulo `datadome` en la configuración [3].

### 4. Integración del lado del cliente
- Añadir el *JavaScript Tag* en las páginas web: `<script src="https://js.datadome.co/script.js"></script>` [3].
- Para apps móviles: Usar SDKs para Android/iOS [3].

### 5. Verificación de integración
- Monitorear tráfico en el *dashboard* tras la integración [3].
- Verificar en tiempo real en *Test your site* [3].

## Límites
- La documentación oficial es la fuente primaria; no se encontraron fuentes alternativas en la búsqueda (limitado a GitHub/Wikipedia/Stack Overflow).
- No hay paquete de instalación para sistemas Linux (error `apt-get install datadome`).

## Fuentes
1. [Datadome Products](https://docs.datadome.co/platform/products)
2. [Getting Started Guide](https://docs.datadome.co/docs/getting-started)
3. [Documentation Index](https://docs.datadome.co/)
