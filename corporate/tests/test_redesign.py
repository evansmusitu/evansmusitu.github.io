"""Regression checks for the evidence-led MUSITU corporate redesign.

These assertions supplement the existing route, CSP, sitemap and browser suites.
They verify built artifacts only; they do not certify public-host performance.
"""
from pathlib import Path
import json
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
RECORDS = json.loads((ROOT / 'content/pages.json').read_text(encoding='utf-8'))
ROUTES = list(RECORDS)
GROUPS = {
    'Products': ('/products/',),
    'Solutions': ('/solutions/',),
    'Experiences': ('/experiences/', '/ecosystem/'),
    'Research': ('/research/', '/evidence/', '/news/'),
    'Company': ('/company/', '/trust/', '/accessibility/', '/contact/'),
    'Resources': ('/resources/', '/developers/', '/support/', '/sitemap/'),
}

def soup(route):
    return BeautifulSoup((DIST / route.lstrip('/') / 'index.html').read_text(encoding='utf-8'), 'html.parser')

def test_shared_header_source_and_content_contract():
    assert len(RECORDS) == 34
    assert all('header' not in record for record in RECORDS.values())
    template = (ROOT / 'templates/header.html').read_text(encoding='utf-8')
    assert template.count('class="site-header"') == 1
    assert template.count('class="desktop-nav"') == 1
    assert 'aria-label="Mobile navigation"' in template
    assert not any('<header' in page['main'] for page in RECORDS.values())

def test_navigation_generated_consistently_across_all_routes():
    for route in ROUTES:
        b = soup(route)
        assert len(b.select('header.site-header')) == 1, route
        assert len(b.select('nav.desktop-nav')) == 1, route
        assert len(b.select('nav.mobile-menu-panel')) == 1, route
        assert len(b.select('main#main')) == 1, route
        current = b.select('header.site-header a[aria-current="page"]')
        desktop = b.select('nav.desktop-nav a[aria-current="page"]')
        mobile = b.select('nav.mobile-menu-panel a[aria-current="page"]')
        expected = route != '/' and bool(b.select(f'nav.desktop-nav a[href="{route}"]'))
        assert len(current) == (2 if expected else 0), route
        assert len(desktop) == (1 if expected else 0), route
        assert len(mobile) == (1 if expected else 0), route
        groups = [name for name, prefixes in GROUPS.items() if any(route.startswith(prefix) for prefix in prefixes)]
        if groups:
            label = groups[0]
            summaries = b.select('nav.desktop-nav .nav-group > summary.active')
            assert len(summaries) == 1, route
            assert summaries[0].get_text(' ', strip=True).startswith(label), route

def test_homepage_is_a_distinct_editorial_journey():
    b = soup('/')
    main = b.select_one('main#main')
    assert len(main.select('h1')) == 1
    assert len(main.select('section')) == 6
    assert len(main.get_text(' ', strip=True).split()) < 650
    assert not main.select('[data-atlas-component], [data-navigator], [data-catalog-item]')
    assert 'ILLUSTRATIVE' in main.get_text(' ',strip=True)
    assert 'Illustrative workflow' in main.get_text(' ',strip=True)
    for path in ('/products/', '/products/axiom/', '/products/education/', '/products/foundry/',
                 '/products/foundry/studio/', '/products/education/chemistry-rescue/',
                 '/evidence/', '/trust/', '/contact/'):
        assert main.select_one(f'a[href="{path}"]'),path
    assert not main.select('iframe, script, form')

def test_dedicated_interactive_journeys_are_preserved():
    assert soup('/products/').select_one('[data-navigator]')
    assert soup('/products/').select_one('[data-catalog-item]')
    assert soup('/ecosystem/').select_one('[data-atlas-component]')
    assert soup('/experiences/lab/').select_one('#npv-result')
    manifest = json.loads((DIST.parent / 'review-artifacts' / 'build-manifest.json').read_text(encoding='utf-8'))
    studio = soup('/products/foundry/studio/')
    if manifest['studio_media_included']:
        assert studio.select_one('video.studio-demo-player')
    else:
        assert studio.select_one('.video-clearance-gate')
        assert not studio.select_one('video.studio-demo-player')
