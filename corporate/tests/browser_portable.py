"""The one-file reviewer must behave as a website, including route changes via search.
It is never a production artifact and intentionally embeds CSS/JavaScript. No network.
"""
from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review-artifacts';OUT.mkdir(exist_ok=True)
PREVIEW=OUT/'MUSITU_portable_interactive_preview.html'
assert PREVIEW.exists(), 'Generate portable preview before test'
html=PREVIEW.read_text(encoding='utf-8')
summary={'portable_html_bytes':len(html.encode('utf-8')),'results':{},'external_requests':[],'javascript_errors':[]}
with sync_playwright() as pw:
    opts={'headless':True,'args':['--no-sandbox']}
    exe=shutil.which('chromium') or shutil.which('google-chrome')
    if exe:opts['executable_path']=exe
    browser=pw.chromium.launch(**opts)
    try:
        page=browser.new_page(viewport={'width':390,'height':800})
        page.on('request',lambda req:summary['external_requests'].append(req.url))
        page.on('pageerror',lambda err:summary['javascript_errors'].append(str(err)))
        page.set_content(html,wait_until='load')
        assert page.locator('h1').count()==1
        page.locator('#search-toggle').click()
        page.locator('#site-search-query').fill('education')
        result=page.locator('.search-result').first
        assert result.get_attribute('href')=='/products/education/'
        result.click()
        page.wait_for_function("document.querySelector('h1')?.textContent.includes('MUSITU Education')",timeout=1500)
        assert not page.locator('#site-search').is_visible(), 'Search dialog must close on navigation'
        page.wait_for_function("document.activeElement===document.getElementById('main')",timeout=1500)
        assert 'Education' in page.title()
        summary['results']['search_route_navigation']=True
        page.locator('#menu-toggle').click()
        page.locator('#mobile-nav').get_by_role('link',name='Products').click()
        page.wait_for_function("document.querySelector('h1')?.textContent.includes('portfolio')",timeout=1500)
        assert page.locator('[data-product-card]:visible').count()==6
        page.locator('#catalog-query').fill('axiom')
        assert page.locator('[data-product-card]:visible').count()==1
        summary['results']['catalog_rerender']=True
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
        page.screenshot(path=str(OUT/'portable-mobile-search-navigation.png'))
    finally:browser.close()
assert not summary['external_requests'],summary['external_requests']
assert not summary['javascript_errors'],summary['javascript_errors']
(OUT/'portable-browser-results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('PASS portable reviewer navigation:',json.dumps(summary,sort_keys=True))
