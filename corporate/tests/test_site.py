from pathlib import Path
import html, json, re
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
EXPECTED=['','products','products/axiom','products/education','products/fmi','products/foundry','products/markets','products/worldfabric','experiences/intelligence','research','evidence','company','trust','resources','contact','support','legal/privacy','legal/terms','accessibility','404','developers','status']

def test_routes():
    for path in EXPECTED:
        assert (DIST/path/'index.html').is_file() if path else (DIST/'index.html').is_file()

def test_semantic_a11y_and_metadata():
    for p in sorted(DIST.rglob('index.html')):
        soup=BeautifulSoup(p.read_text(),'html.parser')
        assert soup.html.get('lang')=='en',p
        assert soup.select_one('main#main'),p
        assert soup.select_one('nav[aria-label="Main navigation"]'),p
        assert soup.select_one('.skip[href="#main"]'),p
        assert len(soup.select('h1'))==1,p
        assert soup.title and soup.title.text.strip(),p
        assert soup.select_one('meta[name="description"]'),p
        assert soup.select_one('meta[name="robots"][content="noindex,nofollow"]'),p
        assert not soup.select('form'),p
        assert not soup.select('script[src^="http"]'),p
        assert not soup.select('img[src^="http"]'),p

def test_local_links():
    for p in sorted(DIST.rglob('*.html')):
        soup=BeautifulSoup(p.read_text(),'html.parser')
        for a in soup.select('a[href]'):
            href=a['href']
            if href.startswith('/'):
                target=href.split('#')[0].split('?')[0]
                path=DIST/target.lstrip('/')
                if target.endswith('/'):path=path/'index.html'
                assert path.exists(),(p,href)
            elif href.startswith('#') and href!='#':
                assert soup.select_one('[id="'+href[1:]+'"]'),(p,href)

def test_claim_safety_and_stage_labels():
    catalog=(DIST/'products/index.html').read_text()
    assert catalog.count('data-product-card')==6
    assert catalog.count('aria-haspopup="dialog"')==6
    soup=BeautifulSoup(catalog,'html.parser')
    assert len(soup.select('#catalog-grid h2'))==6
    for p in EXPECTED:
        if p.startswith('products/'):
            s=(DIST/p/'index.html').read_text()
            assert 'Important limits' in s and 'PUBLIC MATURITY STATE' in s and 'EVIDENCE' in s
    assert 'noindex' in (DIST/'index.html').read_text()
    assert 'Disallow: /' in (DIST/'robots.txt').read_text()

def test_no_sensitive_or_remote_services():
    js=(DIST/'assets/site.js').read_text()
    for token in ['fetch(', 'localStorage','sessionStorage','document.cookie','XMLHttpRequest','sendBeacon','analytics']:
        assert token not in js.replace('no analytics',''),token
    assert 'prefers-reduced-motion' in (DIST/'assets/site.css').read_text()

def test_manifest_integrity():
    import hashlib
    m=json.loads((DIST/'build-manifest.json').read_text())
    for item in m:
        p=DIST/item['path']
        assert p.stat().st_size==item['bytes']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']