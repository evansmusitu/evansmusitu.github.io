"""Cross-engine website regression: Chromium, Firefox and WebKit at 3 sizes.
CI must install Playwright browsers. Locally, pass --engines chromium if only that
engine exists; never claim skipped engines passed. Offline DOM, no external calls.
"""
from __future__ import annotations
import json,os,re,shutil,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
OUT=ROOT/'review-artifacts';OUT.mkdir(exist_ok=True)
CSS=(DIST/'assets/site.css').read_text(encoding='utf-8')
JS=(DIST/'assets/site.js').read_text(encoding='utf-8')
ROUTES=sorted(p.relative_to(DIST).as_posix() for p in DIST.rglob('index.html'))
assert len(ROUTES)==22
ENGINES=['chromium','firefox','webkit']
if '--engines' in sys.argv:
    ENGINES=sys.argv[sys.argv.index('--engines')+1].split(',')
assert all(x in ('chromium','firefox','webkit') for x in ENGINES)
def render(path):
    s=(DIST/path).read_text(encoding='utf-8')
    s=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',s)
    return (s.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+CSS+'</style>')
            .replace('<script defer src="/assets/site.js"></script>','')
            .replace('</body>','<script>'+JS+'</script></body>'))
report={'scope':'offline DOM layout + functional acceptance, NOT hosted HTTP','engines':{},'errors':[]}
with sync_playwright() as pw:
    for engine in ENGINES:
        cfg={'headless':True}
        if engine=='chromium':
            cfg['args']=['--no-sandbox']
            path=shutil.which('chromium') or shutil.which('google-chrome')
            if path:cfg['executable_path']=path
        browser=getattr(pw,engine).launch(**cfg)
        engine_report={'responsive_views':0,'sizes':[320,390,1440],'search':False,'navigation':False,'no_network':True,'js_errors':[]}
        try:
            page=browser.new_page()
            page.on('pageerror',lambda e:engine_report['js_errors'].append(str(e)))
            page.on('request',lambda request:report['errors'].append(engine+' unexpected network: '+request.url))
            for width in engine_report['sizes']:
                page.set_viewport_size({'width':width,'height':780})
                for route in ROUTES:
                    page.set_content(render(route),wait_until='load')
                    assert page.locator('h1').count()==1,(engine,width,route)
                    assert page.locator('#search-toggle').is_visible(),(engine,width,route)
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(engine,width,route,'overflow')
                    engine_report['responsive_views']+=1
            page.set_viewport_size({'width':390,'height':800})
            page.set_content(render('index.html'),wait_until='load')
            page.locator('#search-toggle').click()
            page.locator('#site-search-query').fill('WorldFabric')
            assert page.locator('.search-result').first.get_attribute('href')=='/products/worldfabric/'
            page.locator('#search-close').click()
            page.wait_for_function("document.activeElement===document.getElementById('search-toggle')",timeout=1500)
            engine_report['search']=True
            page.locator('#menu-toggle').click()
            assert page.locator('#mobile-nav').is_visible()
            page.keyboard.press('Escape')
            assert not page.locator('#mobile-nav').is_visible()
            engine_report['navigation']=True
            assert not engine_report['js_errors'],(engine,engine_report['js_errors'])
            if engine!='chromium':page.screenshot(path=str(OUT/f'crossengine-{engine}-homepage.png'))
        finally:
            browser.close()
        report['engines'][engine]=engine_report
assert not report['errors'],report['errors']
assert len(report['engines'])==len(ENGINES)
(OUT/'crossengine-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS cross-engine acceptance:',json.dumps(report,sort_keys=True))
