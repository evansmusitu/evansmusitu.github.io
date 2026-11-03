"""Offline Chromium audit using in-memory DOM. No network or production effects.

In this sandbox Chromium cannot navigate to local HTTP/file URLs. The generated
HTML and exact stylesheet/JS are loaded with set_content, allowing real layout,
DOM events and interaction checks without weakening network restrictions.
"""
from pathlib import Path
import shutil
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
ART = ROOT / 'review-artifacts'
ART.mkdir(exist_ok=True)
css = (DIST/'assets/site.css').read_text()
js = (DIST/'assets/site.js').read_text()

def document(path):
    html = (DIST/path).read_text()
    assert '<link rel="stylesheet" href="/assets/site.css">' in html
    assert '<script defer src="/assets/site.js"></script>' in html
    html=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', html)  # inline test harness only
    return (html.replace('<link rel="stylesheet" href="/assets/site.css">', '<style>'+css+'</style>')
                .replace('<script defer src="/assets/site.js"></script>', '').replace('</body>','<script>'+js+'</script></body>'))

with sync_playwright() as pw:
    browser_opts={'headless':True, 'args':['--no-sandbox']}
    if shutil.which('chromium'):browser_opts['executable_path']=shutil.which('chromium')
    elif shutil.which('google-chrome'):browser_opts['executable_path']=shutil.which('google-chrome')
    browser = pw.chromium.launch(**browser_opts)
    for width,height,name in ((1440,900,'desktop'),(390,844,'mobile'),(320,720,'small-mobile')):
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        page.set_default_timeout(6000)
        print('VIEWPORT',name,flush=True)
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(document('index.html'),wait_until='load')
        assert page.title().startswith('MUSITU'),name
        assert page.locator('main h1').count()==1,name
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),(name,'homepage horizontal overflow')
        assert page.locator('main').is_visible(),name
        page.screenshot(path=str(ART/f'{name}-homepage.png'),full_page=True,animations='disabled',timeout=10000)
        print('HOME SCREENSHOT',flush=True)
        initial=page.locator('html').get_attribute('data-theme')
        page.locator('#theme-toggle').click()
        assert page.locator('html').get_attribute('data-theme')!=initial,name
        if width<=820:
            button=page.locator('#menu-toggle')
            button.click()
            assert button.get_attribute('aria-expanded')=='true',name
            assert page.locator('#mobile-nav').is_visible(),name
            page.keyboard.press('Escape')
            assert not page.locator('#mobile-nav').is_visible(),name
        print('THEME AND MENU PASS',flush=True)
        page.set_content(document('products/index.html'),wait_until='load')
        print('CATALOG LOADED',flush=True)
        assert page.locator('[data-product-card]:visible').count()==6,name
        page.locator('#catalog-query').fill('education')
        assert page.locator('[data-product-card]:visible').count()==1,name
        page.locator('#catalog-query').fill('')
        page.locator('#catalog-state').select_option('research')
        assert page.locator('[data-product-card]:visible').count()==3,name
        page.locator('#catalog-state').select_option('all')
        print('FILTER PASS',flush=True)
        page.locator('[data-evidence="axiom"]').click()
        print('DIALOG OPEN',flush=True)
        assert page.locator('#evidence-dialog').is_visible(),name
        assert 'Axiom' in page.locator('#evidence-title').inner_text(),name
        page.keyboard.press('Escape')
        assert not page.locator('#evidence-dialog').is_visible(),name
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),(name,'catalog horizontal overflow')
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path=str(ART/f'{name}-products.png'),full_page=True,animations='disabled',timeout=10000)
        assert not errors,(name,errors)
        page.close()
    browser.close()
print('PASS offline Chromium: 3 viewports, theme, mobile menu, catalog search/filters, evidence dialog, no overflow/JS errors.')