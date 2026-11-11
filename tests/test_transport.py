import asyncio
import ssl
from proxymanager.transport import HostnameStream


def test_proxy_tls_uses_original_hostname_and_verifies_certificate():
    observed = {}
    class Stream:
        async def start_tls(self, **kwargs):
            observed.update(kwargs)
            return self
    context = ssl.create_default_context()
    asyncio.run(HostnameStream(Stream(), 'lab.example').start_tls(context, '8.8.8.8', 5))
    assert observed['server_hostname'] == 'lab.example'
    assert observed['ssl_context'].check_hostname
    assert observed['ssl_context'].verify_mode == ssl.CERT_REQUIRED
