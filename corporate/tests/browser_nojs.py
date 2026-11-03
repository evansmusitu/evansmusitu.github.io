"""Regression for disabled JavaScript and missing JavaScript asset.

This simulates the final HTML/CSS without loading the site script, not an
independently certified screen-reader or cross-browser test. It prevents mobile
navigation and filter UI from silently breaking when JavaScript fails.
"""
import json,re,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
CSS=(DIST/'assets/site.css').read_text(encoding='utf-8')
OUT=ROOT/'review-artifacts'
OUT.mkdir(exist_ok=True)
ROUTES=sorted(p.relative_to(DIST).as_posix() for p in DIST.rglob('index.html'))

def doc_without_js(path):
    page=(DIST/path).read_text(encoding='utf-8')
    # Test harness only: CSP meta removed to allow embedding local style text.
    page=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', page)
    page=page.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+CSS+'</style>')
    page=page.replace('<script defer src="/assets/site.js"></script>','')
    return page

summary={'routes':len(ROUTES),'viewports':[320,390,1440],'checks':0,'overflow':0,'failures':[]}
with sync_playwright() as pw:
    params={'headless':True,'args':['--no-sandbox']}
    chromium=shutil.which('chromium') or shutil.which('google-chrome')
    if chromium:params['executable_path']=chromium
    browser=pw.chromium.launch(**params)
    try:
        page=browser.new_page()
        for width in summary['viewports']:
            page.set_viewport_size({'width':width,'height':780})
            for route in ROUTES:
                page.set_content(doc_without_js(route),wait_until='load')
                assert not page.locator('html').evaluate("(e)=>e.classList.contains('has-js')")
                if width<=820:
                    assert page.locator('#fallback-nav summary').is_visible(),(route,width,'native menu missing')
                    assert not page.locator('.primary-nav').is_visible(),(route,width,'desktop nav should be hidden')
                    assert not page.locator('#fallback-nav nav').is_visible(),(route,width,'menu unexpectedly open')
                    page.locator('#fallback-nav summary').click()
                    assert page.locator('#fallback-nav nav a:visible').count()==6,(route,width,'fallback link count')
                    page.locator('#fallback-nav summary').click()
                    assert not page.locator('#fallback-nav nav').is_visible()
                else:
                    assert page.locator('.primary-nav').is_visible(),(route,width,'desktop navigation unavailable')
                    assert page.locator('.primary-nav a:visible').count()==5,(route,width,'navigation link count')
                assert not page.locator('.theme-toggle').is_visible(),(route,width,'inert theme control')
                assert not page.locator('.menu-toggle').is_visible(),(route,width,'inert mobile menu')
                assert not page.locator('.search-toggle').is_visible(),(route,width,'inert global search')
                assert not page.locator('.evidence-trigger').first.is_visible(),(route,width,'inert evidence button')
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(route,width,'overflow')
                if route=='products/index.html':
                    assert page.locator('[data-product-card]:visible').count()==6
                    assert not page.locator('.catalog-controls').is_visible()
                summary['checks']+=1
    finally:browser.close()
(OUT/'nojs-browser-results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('PASS missing JavaScript and JavaScript-disabled fallback',json.dumps(summary,sort_keys=True))
