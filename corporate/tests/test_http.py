"""Real loopback HTTP response verification (Python client; not hosted-browser testing)."""
import sys, threading, urllib.request, urllib.error, json
from pathlib import Path
from http.server import ThreadingHTTPServer
from functools import partial
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from preview_server import Handler, ROOT as STATIC_ROOT
ROUTES=json.loads((ROOT/'dist/manifest.json').read_text())['routes']

@pytest.fixture(scope='module')
def server():
    http=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(STATIC_ROOT)))
    thread=threading.Thread(target=http.serve_forever,daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{http.server_port}'
    http.shutdown();http.server_close()

@pytest.mark.parametrize('route',ROUTES)
def test_routes_http_and_security_headers(server,route):
    request=urllib.request.Request(server+route,headers={'User-Agent':'MUSITU-local-review/1.0'})
    try:
        response=urllib.request.urlopen(request,timeout=5)
    except urllib.error.HTTPError as e:
        response=e
    with response as r:
        assert r.status==(404 if route=='/404/' else 200),route
        h=r.headers
        assert h['X-Robots-Tag']=='noindex, nofollow'
        assert h['X-Content-Type-Options']=='nosniff'
        assert "frame-ancestors 'none'" in h['Content-Security-Policy']
        assert b'<main id="main"' in r.read()

def test_unknown_route_is_actual_404(server):
    with pytest.raises(urllib.error.HTTPError) as caught:
        urllib.request.urlopen(server+'/definitely-not-a-route/',timeout=5)
    assert caught.value.code==404

def test_local_asset_loading(server):
    with urllib.request.urlopen(server+'/assets/site.js',timeout=5) as r:
        assert r.status==200
        assert b'MUSITU corporate site' in r.read()
