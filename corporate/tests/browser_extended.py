"""Extended offline Chromium gate: no network calls or live service usage.

Browser is intentionally fed exact generated HTML/CSS/JS via set_content because
navigation to loopback HTTP is blocked in the current sandbox. CSP meta is removed
from the in-memory harness solely to permit inline test injection. Production CSP
remains in generated pages and is separately statically asserted.
"""
import json, re, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
CSS=(DIST/'assets/site.css').read_text()
JS=(DIST/'assets/site.js').read_text()
OUT=ROOT/'review-artifacts'
OUT.mkdir(exist_ok=True)

ROUTES=sorted(p.relative_to(DIST).as_posix() for p in DIST.rglob('index.html'))
SIZES=[(320,720,'zoom-400-320'),(360,780,'small-mobile'),(390,844,'mobile'),(568,320,'landscape'),(768,1024,'tablet'),(820,900,'menu-breakpoint'),(821,900,'nav-breakpoint'),(1024,768,'laptop'),(1440,900,'desktop')]

def doc(path):
    source=(DIST/path).read_text()
    source=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',source)
    return (source.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+CSS+'</style>')
                  .replace('<script defer src="/assets/site.js"></script>','')
                  .replace('</body>','<script>'+JS+'</script></body>'))

results={'routes':len(ROUTES),'viewports':len(SIZES),'total_views':0,'no_overflow':0,'no_js_errors':0,'keyboard':False,'theme_preference':False,'modal_focus':False,'reduced_motion':False,'no_network':False,'errors':[]}
with sync_playwright() as pw:
    kwargs={'headless':True,'args':['--no-sandbox']}
    executable=shutil.which('chromium') or shutil.which('google-chrome')
    if executable:kwargs['executable_path']=executable
    browser=pw.chromium.launch(**kwargs)
    page=browser.new_page()
    requests=[]
    page.on('request',lambda r:requests.append(r.url))
    page.emulate_media(color_scheme='dark',reduced_motion='reduce')
    page.set_content(doc('index.html'),wait_until='load')
    assert page.evaluate("getComputedStyle(document.body).backgroundColor")
    assert page.locator('html').get_attribute('data-theme')=='dark'
    assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") in ('auto','smooth')
    assert page.evaluate("getComputedStyle(document.querySelector('.button')).transitionDuration") in ('1e-05s','0.00001s','0.01ms','0s'), 'prefers-reduced-motion does not suppress transitions'
    results['reduced_motion']=True

    # True keyboard focus flow (not just synthetic click).
    page.keyboard.press('Tab')
    assert page.locator('.skip').evaluate('(e)=>e===document.activeElement'), 'skip-link not first focus target'
    page.keyboard.press('Enter')
    assert page.evaluate('location.hash')=='#main' or page.locator('#main').evaluate('(e)=>e===document.activeElement')
    results['keyboard']=True

    # Initial OS preference, manual choice, and live OS change must be coherent.
    page.emulate_media(color_scheme='light')
    page.wait_for_function("document.documentElement.dataset.theme==='light'",timeout=2500)
    page.locator('#theme-toggle').click()
    assert page.locator('html').get_attribute('data-theme')=='dark'
    page.emulate_media(color_scheme='dark')
    assert page.locator('html').get_attribute('data-theme')=='dark'
    results['theme_preference']=True

    page.set_content(doc('products/index.html'),wait_until='load')
    for slug in ('axiom','education','fmi','foundry','markets','worldfabric'):
        trigger=page.locator('[data-evidence="'+slug+'"]')
        trigger.focus()
        page.keyboard.press('Enter')
        assert page.locator('#evidence-dialog').is_visible(),slug
        assert page.locator('#evidence-reviewed').inner_text().startswith('2026-11-02'),slug
        assert page.locator('#evidence-close').evaluate('(e)=>e===document.activeElement'), slug
        page.keyboard.press('Escape')
        assert not page.locator('#evidence-dialog').is_visible(),slug
        assert trigger.evaluate('(e)=>e===document.activeElement'),slug
    results['modal_focus']=True

    for width,height,name in SIZES:
        page.set_viewport_size({'width':width,'height':height})
        for route in ROUTES:
            errs=[]
            page.on('pageerror',lambda e:errs.append(str(e)))
            page.set_content(doc(route),wait_until='load')
            page.wait_for_timeout(10)
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),(name,route,'horizontal overflow')
            results['no_overflow']+=1
            assert page.locator('h1').count()==1,(name,route,'h1 missing/multiple')
            assert page.locator('main').is_visible(),(name,route,'invisible main')
            assert not errs,(name,route,errs)
            results['no_js_errors']+=1
            results['total_views']+=1
        if width in (320,390,821,1440):
            page.set_content(doc('products/index.html'),wait_until='load')
            page.screenshot(path=str(OUT/f'extended-{name}-products.png'),full_page=True,animations='disabled',timeout=20000)
    results['no_network']=not requests
    assert results['no_network'], requests[:3]
    browser.close()
(OUT/'extended-browser-results.json').write_text(json.dumps(results,indent=2))
print('PASS extended Chromium',json.dumps(results,sort_keys=True))