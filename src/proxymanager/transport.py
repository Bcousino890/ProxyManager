"""HTTP CONNECT to a validated IP, with TLS verified for the original hostname."""
import httpcore
import httpx
from httpcore._backends.auto import AutoBackend


class HostnameStream(httpcore.AsyncNetworkStream):
    def __init__(self, stream, hostname):
        self.stream, self.hostname = stream, hostname

    async def read(self, max_bytes, timeout=None):
        return await self.stream.read(max_bytes, timeout)

    async def write(self, buffer, timeout=None):
        await self.stream.write(buffer, timeout)

    async def aclose(self):
        await self.stream.aclose()

    def get_extra_info(self, info):
        return self.stream.get_extra_info(info)

    async def start_tls(self, ssl_context, server_hostname=None, timeout=None):
        stream = await self.stream.start_tls(ssl_context=ssl_context, server_hostname=self.hostname, timeout=timeout)
        return HostnameStream(stream, self.hostname)


class HostnameBackend(httpcore.AsyncNetworkBackend):
    def __init__(self, hostname):
        self.hostname = hostname
        self.backend = AutoBackend()

    async def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        stream = await self.backend.connect_tcp(host, port, timeout, local_address, socket_options)
        return HostnameStream(stream, self.hostname)

    async def sleep(self, seconds):
        await self.backend.sleep(seconds)


class ResponseStream(httpx.AsyncByteStream):
    def __init__(self, stream):
        self.stream = stream

    async def __aiter__(self):
        try:
            async for part in self.stream:
                yield part
        except Exception as exc:
            raise httpx.TransportError('Proxy response stream failed') from exc

    async def aclose(self):
        await self.stream.aclose()


class PinnedProxyTransport(httpx.AsyncBaseTransport):
    def __init__(self, proxy_url, hostname):
        proxy = httpx.Proxy(proxy_url)
        self.pool = httpcore.AsyncHTTPProxy(proxy_url=str(proxy.url), proxy_auth=proxy.raw_auth, network_backend=HostnameBackend(hostname))

    async def handle_async_request(self, request):
        core_request = httpcore.Request(method=request.method, url=httpcore.URL(scheme=request.url.raw_scheme, host=request.url.raw_host, port=request.url.port, target=request.url.raw_path), headers=request.headers.raw, content=request.stream, extensions=request.extensions)
        try:
            response = await self.pool.handle_async_request(core_request)
        except Exception as exc:
            raise httpx.TransportError('Proxy connection failed') from exc
        return httpx.Response(response.status, headers=response.headers, stream=ResponseStream(response.stream), extensions=response.extensions)

    async def aclose(self):
        await self.pool.aclose()
