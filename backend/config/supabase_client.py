import httpx
from supabase import create_client, ClientOptions
from config.settings import settings

# Use HTTP/1.1 to avoid httpx HTTP/2 stream errors (LocalProtocolError, StreamClosedError)
# when multiple concurrent requests hit Supabase from async workers.
http_client = httpx.Client(http2=False)
options = ClientOptions(httpx_client=http_client)
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY, options)
