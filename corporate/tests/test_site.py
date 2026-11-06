"""Regression tests for isolated MUSITU corporate Package A source and static build."""
from pathlib import Path
import hashlib, json, re, urllib.parse
from bs4 import BeautifulSoup
import pytest

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
SITE=json.loads((ROOT/'content/pages.json').read_text())
MANIFEST=json.loads((DIST/'manifest.json').read_text())
ROUTES=MANIFEST['routes']

def path_for(route): return DIST/route.lstrip('/')/'index.html'
def soup_for(route):return BeautifulSoup(path_for(route).read_text(), 'html.parser')


def test_route_count_and_exact_master():
 assert len(ROUTES)==34
 assert set(ROUTES)==set(SITE)
 assert len(set(ROUTES))==34
 assert len(list(DIST.rglob('index.html')))==34

@pytest.mark.parametrize('route',ROUTES)
def test_static_page(route):
 p=path_for(route);assert p.exists(),route
 b=soup_for(route)
 assert b.title and 'MUSITU' in b.title.get_text()
 assert b.select_one('meta[name="robots"]')['content']=='noindex,nofollow'
 assert b.select_one('meta[name="description"]')['content'].strip()
 assert b.select_one('meta[http-equiv="Content-Security-Policy"]')
 assert b.select_one('main#main') and b.select_one('header') and b.select_one('footer')
 assert len(b.select('h1'))==1
 assert b.html['lang']=='en'
 assert b.select_one('a.skip-link[href="#main"]')
 assert b.select_one('dialog#search-dialog')
 assert b.select_one('dialog#evidence-dialog')
 assert b.select_one('dialog#ask-dialog')
 assert len(b.select('script'))==2 and all(e.get('src','').startswith('/assets/') and not e.get_text(strip=True) for e in b.select('script'))
 assert len(b.select('link[rel="stylesheet"]'))==1
 assert not b.select('iframe,embed,object,form[action],script:not([src])')
 assert '__VIDEO_PLACEHOLDER__' not in p.read_text()
 assert 'data:image/png;base64,' not in p.read_text()
 # All internal links resolve against the canonical 34-route baseline.
 for a in b.select('a[href]'):
  raw=a.get('href','');u=urllib.parse.urlsplit(raw)
  if not u.scheme and not u.netloc and u.path.startswith('/'):
   assert u.path in ROUTES or (u.path=='/' and u.fragment),f'{route} -> {raw}'
  assert not raw.startswith('//') and not raw.lower().startswith(('javascript:','data:','file:'))
  if a.get('target')=='_blank':
   assert {'noopener','noreferrer'}.issubset(set(a.get('rel',[])))

@pytest.mark.parametrize('route',ROUTES)
def test_no_customer_transaction_backend(route):
 data=path_for(route).read_text().lower()
 assert 'fetch(' not in data and '<script src="http' not in data
 assert not re.search(r'<form[^>]+action=',data)
 assert not re.search(r'<input[^>]+type=["\']password',data)


def test_families_and_public_info():
 script=(DIST/'assets/site-data.js').read_text()
 prefix='window.MUSITU_PUBLIC = '
 assert script.strip().startswith(prefix)
 payload=json.loads(script.strip()[len(prefix):].rstrip(';'))
 families=payload['families'];assert len(families)==6
 assert set(f['id'] for f in families)=={'axiom','education','foundry','markets','fmi','worldfabric'}
 assert len(payload['routes'])==34
 assert all(e['limits'] and e['kind'] and e['date'] and e['claim'] for e in payload['evidence'])
 assert not any('private' in e['link'].lower() for e in payload['evidence'])
 assert 'customer billing' not in soup_for('/products/axiom/').title.get_text().lower()


def test_owner_cleared_studio_media_gate():
 p=soup_for('/products/foundry/studio/')
 video=p.select_one('video.studio-demo-player')
 assert video and video.get('poster')=='/assets/studio-poster.png'
 assert p.select_one('video.studio-demo-player source[src="/assets/studio-demo-82s.mp4"][type="video/mp4"]')
 mp4=DIST/'assets/studio-demo-82s.mp4'; poster=DIST/'assets/studio-poster.png'
 assert hashlib.sha256(mp4.read_bytes()).hexdigest()=='afd6dfd3c73668e544f3f8a857697fed0abaadccd4927202bb3a185612c2dea0'
 assert hashlib.sha256(poster.read_bytes()).hexdigest()=='0ea5e961d916375029010dbae01bf8a1783e5fd6b90f74c006dc852df1c285d0'
 assert not p.select('img[src^="data:"]')


def test_master_hash_and_no_external_runtime():
 expect='c30e0ae55938ea9324aec8ac0998041a7c0a804ef28110c70b38408fa6cf8909'
 provenance=json.loads((ROOT/'content/source-provenance.json').read_text())
 assert provenance['sha256']==expect
 assert (DIST/'robots.txt').read_text()=='User-agent: *\nDisallow: /\n'
 assert not (DIST/'sitemap.xml').exists() # Canonical owner domain remains unapproved
 assert "fetch(" not in (DIST/'assets/site.js').read_text()
 assert not any(t in (DIST/'assets/site.js').read_text() for t in ['XMLHttpRequest(', 'sendBeacon(', 'WebSocket('])


def test_deterministic_manifest():
 for filename,expected in MANIFEST['files'].items():
  assert hashlib.sha256((DIST/filename).read_bytes()).hexdigest()==expected,filename
 assert MANIFEST['production_approved'] is False
 assert MANIFEST['media_publication_approved'] is True
 assert MANIFEST['brand_master_approved'] is True
 assert MANIFEST['brand_master_sha256']=='f0e73478176b335bf3cfb5afd8bd7249d5aa39f2627798af7c71d9f13972c2fd'
 assert all(x.startswith('/') for x in MANIFEST['routes'])


def test_staging_conditional_flags():
 assert {'/status/','/legal/privacy/','/legal/terms/','/developers/','/news/'}.issubset(set(MANIFEST['gated_routes']))
 for x in MANIFEST['gated_routes']:
  assert 'noindex' in path_for(x).read_text()


def test_mobile_theme_access():
 for route in ROUTES:
  b=soup_for(route)
  assert b.select_one('.mobile-menu-panel .mobile-theme-control')
  assert b.select_one('.mobile-menu-panel .mobile-theme-control')['type']=='button'


def test_generated_asset_size_policy():
 allowed_large={'assets/studio-demo-82s.mp4'}
 for p in DIST.rglob('*'):
  if p.is_file() and p.name!='manifest.json' and p.relative_to(DIST).as_posix() not in allowed_large:
   assert p.stat().st_size < 250000, p
 assert (DIST/'assets/studio-demo-82s.mp4').stat().st_size==1540312
