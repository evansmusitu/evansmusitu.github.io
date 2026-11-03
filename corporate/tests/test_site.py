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

# Contract tests added in review round three: make every staging gate machine-checkable.
def test_strict_static_security_policy_and_safe_links():
    import sys
    sys.path.insert(0,str(ROOT/'scripts'))
    from build import checked_link_url, H, PRODUCTS
    for value in ('javascript:alert(1)','data:text/html,hi','//example.com/','http://example.com/','file:///etc/passwd','#',''):
        import pytest
        with pytest.raises(ValueError):checked_link_url(value)
    for value in ('/products/','#main','https://github.com/evansmusitu','mailto:support@example.com'):
        assert checked_link_url(value)==value
    assert H('<script>alert(1)</script>')=='&lt;script&gt;alert(1)&lt;/script&gt;'
    assert len(set(z['slug'] for z in PRODUCTS))==6
    for p in sorted(DIST.rglob('index.html')):
        soup=BeautifulSoup(p.read_text(),'html.parser')
        csp=soup.select_one('meta[http-equiv="Content-Security-Policy"]')
        assert csp,p
        directive=csp.get('content','')
        for must in ("default-src 'none'", "script-src 'self'", "style-src 'self'", "connect-src 'none'", "form-action 'none'", "object-src 'none'", "base-uri 'none'"):
            assert must in directive,(p,must)
        assert soup.select_one('meta[name="referrer"]'),p
        for a in soup.select('a[href]'):
            href=a.get('href','')
            assert href.startswith(('/','#','https://','mailto:')),(p,href)
            assert not href.startswith('//'),(p,href)
            if a.get('target')=='_blank':
                assert {'noopener','noreferrer'}.issubset(set(a.get('rel',[]))),(p,href)
        assert not soup.select('iframe, object, embed'),p


def test_evidence_registration_and_explicit_release_holds():
    from datetime import date
    reviewed=date.fromisoformat('2026-11-02')
    assert reviewed.year==2026
    for p in sorted(DIST.rglob('index.html')):
        soup=BeautifulSoup(p.read_text(),'html.parser')
        script=soup.select_one('script#evidence-registry[type="application/json"]')
        assert script,(p,'missing evidence register')
        data=json.loads(script.string)
        assert len(data)==6
        assert all(item['reviewed']=='2026-11-02' for item in data.values())
        assert soup.select_one('#evidence-reviewed'),p
        assert not soup.select('script[onload],img[onerror]')
    for path in ('developers','status','legal/privacy','legal/terms'):
        s=(DIST/path/'index.html').read_text()
        assert 'Pre-publication gate' in s,(path,'missing release hold')
    s=(DIST/'index.html').read_text()
    assert 'noindex,nofollow' in s
    assert 'Cloudflare account' not in s


def test_unique_metadata_and_deterministic_build():
    titles=set()
    for p in sorted(DIST.rglob('index.html')):
        soup=BeautifulSoup(p.read_text(),'html.parser')
        t=soup.title.get_text(strip=True)
        assert t not in titles, (p,'duplicate title')
        titles.add(t)
        description=soup.select_one('meta[name="description"]').get('content','')
        assert 35 <= len(description) <= 180,(p,len(description))
        assert soup.select_one('footer[aria-label]') is None  # footer landmark is native HTML
        assert soup.select_one('nav[aria-label="Footer navigation"]')
    assert len(titles)==22
    assert sorted(p.name for p in DIST.glob('*.html'))==['404.html','index.html']


def test_palette_tokens_meet_normal_text_contrast_for_basic_surfaces():
    # Explicit fixed-color pairs. Gradients, composites, imagery, focus indicators,
    # component states and real AT still require human inspection.
    palettes={
      'dark':{'bg':'#090e1b','surface':'#10192b','surface2':'#14213a','text':'#f0f4ff','muted':'#b0bfd7','faint':'#8193b3','mint':'#72ebc7','violet':'#aaa3ff'},
      'light':{'bg':'#f4f7fd','surface':'#ffffff','surface2':'#e9f0fa','text':'#14213c','muted':'#3c4c65','faint':'#51647e','mint':'#086c5a','violet':'#5044bf'},
    }
    def luminance(color):
        values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
        linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
        return sum(w*v for w,v in zip((.2126,.7152,.0722),linear))
    def contrast(a,b):
        L=sorted((luminance(a),luminance(b)))
        return (L[1]+0.05)/(L[0]+0.05)
    css=(DIST/'assets/site.css').read_text()
    for pal,color in palettes.items():
        for key,value in color.items():
            assert value.lower() in css.lower(),(pal,key,'token lost')
        for foreground in ('text','muted','faint','mint','violet'):
            for background in ('bg','surface','surface2'):
                assert contrast(color[foreground],color[background])>=4.5,(pal,foreground,background)


def test_accessible_progressive_enhancement_and_forced_colors():
    css=(DIST/'assets/site.css').read_text()
    assert '@media (forced-colors: active)' in css
    assert '@media (prefers-contrast: more)' in css
    for p in sorted(DIST.rglob('index.html')):
        soup=BeautifulSoup(p.read_text(),'html.parser')
        assert soup.select_one('noscript nav[aria-label="Navigation without JavaScript"]'),p



def test_claim_register_is_complete_and_traces_public_sources():
    register=json.loads((DIST/'claim-register.json').read_text())
    assert register['schema']=='musitu.corporate.claim-register.v1'
    assert register['release_state']=='NOINDEX_REVIEW_ONLY'
    assert register['reviewed_on']=='2026-11-02'
    assert len(register['families'])==6
    names=[p['name'] for p in register['families']]
    assert len(set(names))==6
    for family in register['families']:
        assert family['maturity'] and family['limits'] and family['claims']
        assert family['evidence']['url'].startswith('https://github.com/')
        body=(DIST/'products'/family['slug']/'index.html').read_text()
        assert family['name'] in body and family['limits'] in html.unescape(body)


def test_first_load_performance_budget_is_bounded_static_assets():
    # Not a runtime CWV claim: this is an enforceable uncompressed transfer budget.
    css=(DIST/'assets/site.css').stat().st_size
    js=(DIST/'assets/site.js').stat().st_size
    html_sizes=[p.stat().st_size for p in DIST.rglob('index.html')]
    assert css <= 36_000,css
    assert js <= 12_000,js
    assert max(html_sizes) <= 32_000,max(html_sizes)
    assert max(html_sizes)+css+js <= 80_000
    assert not list(DIST.rglob('*.woff*'))
    assert not list(DIST.rglob('*.mp4'))


def test_build_is_byte_reproducible():
    import subprocess, sys, hashlib
    def fingerprint():
        return hashlib.sha256((DIST/'build-manifest.json').read_bytes()).hexdigest()
    previous=fingerprint()
    subprocess.run([sys.executable,str(ROOT/'scripts/build.py')],cwd=ROOT,check=True,capture_output=True)
    assert fingerprint()==previous
