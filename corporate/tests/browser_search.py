"""Offline Chromium audit of accessible, zero-network corporate site-wide search.
Runs on 22 generated routes at desktop, mobile and small-mobile. No live network.
"""
from __future__ import annotations
import json,re,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
OUT=ROOT/'review-artifacts';OUT.mkdir(exist_ok=True)
CSS=(DIST/'assets/site.css').read_text(encoding='utf-8')
JS=(DIST/'assets/site.js').read_text(encoding='utf-8')
ROUTES=sorted(p.relative_to(DIST).as_posix() for p in DIST.rglob('index.html'))
assert len(ROUTES)==22

def render(path):
    src=(DIST/path).read_text(encoding='utf-8')
    src=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',src)
    return (src.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+CSS+'</style>')
        .replace('<script defer src="/assets/site.js"></script>','')
        .replace('</body>','<script>'+JS+'</script></body>'))

summary={'routes':22,'viewports':[320,390,1440],'checks':0,'query_tests':0,'errors':[]}
with sync_playwright() as pw:
    cfg={'headless':True,'args':['--no-sandbox']}
    exe=shutil.which('chromium') or shutil.which('google-chrome')
    if exe:cfg['executable_path']=exe
    browser=pw.chromium.launch(**cfg)
    try:
        page=browser.new_page()
        page.on('pageerror',lambda err:summary['errors'].append(str(err)))
        for width in summary['viewports']:
            page.set_viewport_size({'width':width,'height':820})
            for route in ROUTES:
                page.set_content(render(route),wait_until='load')
                toggle=page.locator('#search-toggle')
                assert toggle.is_visible(),(width,route,'search opener hidden')
                toggle.click()
                assert page.locator('#site-search').is_visible(),(width,route,'dialog failed open')
                assert page.locator('#site-search-query').evaluate('(e)=>e===document.activeElement')
                assert page.locator('#site-search-results').count()==1
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                page.locator('#site-search-query').fill('axiom')
                assert page.locator('.search-result').first.get_attribute('href')=='/products/axiom/'
                assert 'matching page' in page.locator('#site-search-feedback').inner_text()
                page.locator('#site-search-query').press('ArrowDown')
                assert page.locator('.search-result').first.evaluate('(e)=>document.activeElement===e'),(width,route,'ArrowDown focus')
                page.locator('.search-result').first.press('ArrowUp')
                assert page.locator('#site-search-query').evaluate('(e)=>document.activeElement===e'),(width,route,'ArrowUp focus')
                page.locator('#site-search-query').fill('impossible_zxyv_not_a_page')
                assert page.locator('.search-result').count()==0
                assert 'No matching pages' in page.locator('#site-search-feedback').inner_text()
                page.keyboard.press('Escape')
                page.locator('#site-search').wait_for(state='hidden',timeout=2000)
                page.wait_for_function("document.activeElement===document.getElementById('search-toggle')",timeout=1500)
                summary['checks']+=1
            page.set_content(render('index.html'),wait_until='load')
            page.keyboard.press('Control+k')
            assert page.locator('#site-search').is_visible(),width
            page.locator('#site-search-query').fill('education')
            assert page.locator('.search-result').first.get_attribute('href')=='/products/education/'
            page.locator('#search-close').click()
            page.wait_for_function("document.activeElement===document.getElementById('search-toggle')",timeout=1500)
            summary['query_tests']+=1
        page.set_viewport_size({'width':1440,'height':800})
        page.set_content(render('index.html'),wait_until='load')
        page.keyboard.press('/')
        assert page.locator('#site-search').is_visible()
        page.locator('#site-search-query').fill('WorldFabric')
        assert page.locator('.search-result').first.get_attribute('href')=='/products/worldfabric/'
        page.screenshot(path=str(OUT/'search-dialog-desktop.png'))
        summary['query_tests']+=1
    finally:
        browser.close()
assert summary['checks']==66
assert not summary['errors'],summary['errors']
(OUT/'search-regressions.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('PASS corporate search:',json.dumps(summary,sort_keys=True))
