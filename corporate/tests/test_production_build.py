"""Production-mode build contract for MUSITU corporate Package A."""
from pathlib import Path
from bs4 import BeautifulSoup
from xml.etree import ElementTree
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
ORIGIN='https://mftintelligence.com'
MANIFEST=json.loads((DIST/'manifest.json').read_text())
ROUTES=MANIFEST['routes']

def soup(route):
 return BeautifulSoup((DIST/route.lstrip('/')/'index.html').read_text(),'html.parser')

def test_production_manifest_contract():
 assert MANIFEST['build_mode']=='production'
 assert MANIFEST['canonical_origin']==ORIGIN
 assert MANIFEST['indexing_enabled'] is True
 assert MANIFEST['production_approved'] is False
 assert MANIFEST['studio_media_included'] is True
 assert MANIFEST['route_count']==34

def test_production_indexing_and_canonical_contract():
 for route in ROUTES:
  b=soup(route)
  if route=='/404/':
   assert b.select_one('meta[name="robots"]')['content']=='noindex,nofollow'
   assert not b.select_one('link[rel="canonical"]')
  else:
   assert b.select_one('meta[name="robots"]')['content']=='index,follow'
   assert b.select_one('link[rel="canonical"]')['href']==ORIGIN+route
   assert b.select_one('meta[property="og:url"]')['content']==ORIGIN+route
  assert not b.select_one('.review-ribbon')
  assert 'Independent staging preview' not in b.get_text()
  assert 'Editorial staging specification' not in b.get_text()

def test_production_robots_sitemap_and_headers():
 robots=(DIST/'robots.txt').read_text()
 assert robots==f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n'
 root=ElementTree.parse(DIST/'sitemap.xml').getroot()
 locs=[x.text for x in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
 assert len(locs)==33 and ORIGIN+'/' in locs and ORIGIN+'/404/' not in locs
 headers=(DIST/'_headers').read_text()
 assert "Content-Security-Policy:" in headers and "frame-ancestors 'none'" in headers
 assert 'X-Content-Type-Options: nosniff' in headers
 assert 'X-Robots-Tag' not in headers

def test_production_legal_identity_and_media():
 expected='Mhundwa Village, Seke, Mashonaland East, Zimbabwe'
 assert expected in soup('/legal/privacy/').get_text(' ',strip=True)
 assert 'MUSITU is the website operator and data controller' in soup('/legal/privacy/').get_text(' ',strip=True)
 assert expected in soup('/legal/terms/').get_text(' ',strip=True)
 footer=soup('/').select_one('footer')
 assert expected not in footer.get_text(' ',strip=True)
 assert 'Zimbabwe-founded' not in footer.get_text(' ',strip=True)
 assert footer.select_one('a[href="mailto:support@mftintelligence.com"]')
 assert 'MUSITU is a technology organization' in soup('/company/').get_text(' ',strip=True)
 assert 'Zimbabwe-founded' not in soup('/company/').get_text(' ',strip=True)
 video=DIST/'assets/studio-demo-82s.mp4'
 poster=DIST/'assets/studio-poster.png'
 assert hashlib.sha256(video.read_bytes()).hexdigest()=='afd6dfd3c73668e544f3f8a857697fed0abaadccd4927202bb3a185612c2dea0'
 assert hashlib.sha256(poster.read_bytes()).hexdigest()=='0ea5e961d916375029010dbae01bf8a1783e5fd6b90f74c006dc852df1c285d0'
 assert soup('/products/foundry/studio/').select_one('video.studio-demo-player source[src="/assets/studio-demo-82s.mp4"]')
def test_production_copy_does_not_reference_private_review():
 stale={
  '/products/foundry/studio/':('STAGING-ONLY MEDIA','can be enabled in an authorized protected preview'),
  '/experiences/lab/':('available in the owner-approved offline reviewer',),
  '/sitemap/':('nonproduction preview','private review build'),
  '/status/':('The status of this preview','No corporate production monitoring','This route remains noindex'),
  '/experiences/intelligence/':('corporate staging website',),
  '/contact/':('Publication gate',),
 }
 for route,phrases in stale.items():
  text=soup(route).get_text(' ',strip=True)
  for phrase in phrases:
   assert phrase not in text,(route,phrase)
