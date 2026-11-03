"""Actual localhost HTTP + Chromium acceptance. This is CI-only in environments that
permit browser loopback navigation; the local ChatGPT browser sandbox blocks it.
No DNS, Cloudflare, GitHub Pages, user accounts or external network is contacted.
"""
from __future__ import annotations
import json
import shutil
import threading
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
OUT = ROOT / 'review-artifacts'
OUT.mkdir(exist_ok=True)
ROUTES = sorted('/' if p.parent == DIST else '/' + p.parent.relative_to(DIST).as_posix() + '/' for p in DIST.rglob('index.html'))
assert len(ROUTES) == 22, ROUTES

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        return

@contextmanager
def website_server():
    srv = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(DIST)))
    worker = threading.Thread(target=srv.serve_forever, daemon=True)
    worker.start()
    try:
        yield f'http://127.0.0.1:{srv.server_port}'
    finally:
        srv.shutdown(); srv.server_close(); worker.join(timeout=2)

results = {'scope': 'real HTTP Chromium on CI localhost', 'route_count': len(ROUTES),
           'viewports': {}, 'html_responses': 0, 'asset_responses': 0, 'external_requests': [],
           'page_errors': [], 'failed_requests': [], 'csp_rejected_inline': False,
           'navigation': False, 'catalog': False, 'modal': False, 'mobile_menu': False,
           'javascript_disabled_navigation': False, 'javascript_disabled_desktop': False}

with website_server() as origin, sync_playwright() as playwright:
    kwargs = {'headless': True, 'args': ['--no-sandbox']}
    chrome_path = shutil.which('chromium') or shutil.which('google-chrome')
    if chrome_path:
        kwargs['executable_path'] = chrome_path
    browser = playwright.chromium.launch(**kwargs)
    try:
        for name, size in [('desktop', (1440, 900)), ('mobile', (390, 844)), ('small-mobile', (320, 720))]:
            page = browser.new_page(viewport={'width': size[0], 'height': size[1]})
            page.on('pageerror', lambda error: results['page_errors'].append(str(error)))
            page.on('requestfailed', lambda request: results['failed_requests'].append(f'{request.url} {request.failure}'))
            def on_request(request):
                if not request.url.startswith(origin + '/'):
                    results['external_requests'].append(request.url)
            page.on('request', on_request)
            def on_response(response):
                if response.url.startswith(origin+'/assets/') and response.status == 200:
                    results['asset_responses'] += 1
            page.on('response', on_response)
            for route in ROUTES:
                response = page.goto(origin + route, wait_until='load', timeout=12000)
                assert response is not None and response.status == 200, (name, route, response.status if response else 'no response')
                assert page.locator('main').is_visible(), (name, route)
                assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth'), (name, route)
                assert page.locator('h1').count() == 1, (name, route)
                assert page.locator('html').get_attribute('lang') == 'en'
                results['html_responses'] += 1
            results['viewports'][name] = len(ROUTES)
            if name == 'desktop':
                page.goto(origin+'/products/',wait_until='load')
                page.locator('#catalog-query').fill('axiom')
                assert page.locator('[data-product-card]:visible').count() == 1
                page.locator('#catalog-query').fill('')
                page.locator('#catalog-state').select_option('prototype')
                assert page.locator('[data-product-card]:visible').count() == 2
                page.locator('#catalog-state').select_option('all')
                results['catalog'] = True
                button=page.locator('[data-evidence="axiom"]');button.click()
                assert page.locator('#evidence-dialog').is_visible()
                assert page.locator('#evidence-source').get_attribute('href').startswith('https://github.com/')
                page.keyboard.press('Escape')
                assert not page.locator('#evidence-dialog').is_visible()
                page.wait_for_timeout(80)
                assert button.evaluate('(e)=>document.activeElement===e')
                results['modal'] = True
                page.get_by_role('link', name='MUSITU Education', exact=True).first.click()
                assert page.url.endswith('/products/education/')
                assert page.locator('h1').inner_text().strip().startswith('MUSITU')
                results['navigation'] = True
                page.goto(origin+'/',wait_until='load')
                original=page.locator('html').get_attribute('data-theme')
                page.locator('#theme-toggle').click()
                selected=page.locator('html').get_attribute('data-theme')
                assert selected in ('light','dark') and selected!=original
                expectedBar='#f4f7fd' if selected=='light' else '#090e1b'
                assert page.locator('meta[name="theme-color"]').get_attribute('content')==expectedBar
                page.goto(origin+'/products/',wait_until='load')
                assert page.locator('html').get_attribute('data-theme')==selected, 'Theme not retained across page navigation'
                page.reload(wait_until='load')
                assert page.locator('html').get_attribute('data-theme')==selected, 'Theme not retained on reload'
                page.goto(origin+'/',wait_until='load')
                page.evaluate("""() => {const e=document.createElement('script');e.textContent='window.__injected_inline_js=true';document.body.append(e);}""")
                assert page.evaluate('window.__injected_inline_js !== true'), 'Meta CSP failed to block inline injected JavaScript'
                results['csp_rejected_inline'] = True
            else:
                page.goto(origin+'/',wait_until='load')
                menu = page.locator('#menu-toggle'); menu.click()
                assert menu.get_attribute('aria-expanded') == 'true'
                assert page.locator('#mobile-nav').is_visible()
                page.locator('#mobile-nav').get_by_role('link', name='Products').click()
                assert page.url.endswith('/products/')
                results['mobile_menu'] = True
            page.close()
        # Separate browser context proves nav works without JavaScript.
        page = browser.new_page(java_script_enabled=False,viewport={'width':390,'height':844})
        response=page.goto(origin+'/products/',wait_until='load')
        assert response and response.status==200
        assert page.locator('nav[aria-label="Main navigation"]').is_visible()
        assert not page.locator('#menu-toggle').is_visible()
        assert not page.locator('#theme-toggle').is_visible()
        assert not page.locator('.catalog-controls').is_visible()
        assert not page.locator('.evidence-trigger').first.is_visible()
        page.locator('nav[aria-label="Main navigation"]').get_by_role('link',name='Company').click()
        assert page.url.endswith('/company/')
        results['javascript_disabled_navigation'] = True
        page.close()
        page = browser.new_page(java_script_enabled=False,viewport={'width':1440,'height':900})
        page.goto(origin+'/products/',wait_until='load')
        assert page.locator('nav[aria-label="Main navigation"]').is_visible()
        assert page.locator('nav[aria-label="Main navigation"]').is_visible()
        page.locator('nav[aria-label="Main navigation"]').get_by_role('link',name='Company').click()
        assert page.url.endswith('/company/')
        results['javascript_disabled_desktop']=True
        page.close()
    finally:
        browser.close()
assert not results['external_requests'], results['external_requests']
assert not results['page_errors'], results['page_errors']
assert not results['failed_requests'], results['failed_requests']
assert results['asset_responses'] >= 132, results['asset_responses']
(OUT/'hosted-browser-results.json').write_text(json.dumps(results,indent=2))
print('PASS real HTTP Chromium',json.dumps(results,sort_keys=True))
