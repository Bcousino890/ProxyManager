# Cookies de sesión persistentes — diseño

ProxyManager debe mantener cookies HTTP por sesión para experimentos en destinos autorizados. Se usará SQLite y Fernet ya presentes. Cada valor se cifrará antes de persistir; la clave existente `PROXYMANAGER_CREDENTIAL_KEY` será obligatoria al utilizar cookies. El almacenamiento quedará aislado por propietario y sesión. Una respuesta `Set-Cookie` podrá actualizar la sesión; una solicitud posterior enviará solo las cookies compatibles con host, ruta, HTTPS y caducidad. Borrar una sesión borrará sus cookies.

Se consideró usar el jar en memoria de HTTPX, pero se perdería al reiniciar. Se consideró serializar un jar completo, pero complicaría el aislamiento y la inspección de caducidad. La tabla por cookie reutiliza el cifrado y la base existentes. Las reglas operativas pueden evolucionar; no se hará una API para leer valores de cookies.

El servidor sigue aplicando allowlist y protección SSRF antes de enviar cookies. No se usan cookies para saltar controles de sitios ajenos. La compatibilidad inicial cubre `Domain`, host-only, `Path`, `Secure`, `Max-Age`, `Expires` y eliminación. `HttpOnly` y `SameSite` se conservan como metadatos: su aplicación depende del navegador y del contexto de origen, no de un cliente HTTP servidor a servidor.
