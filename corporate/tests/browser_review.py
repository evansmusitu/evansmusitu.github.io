#!/usr/bin/env python3
"""No-network cross-engine DOM verification for all 34 generated MUSITU review routes.

Managed runners may prohibit loopback navigation. To avoid false claims, this
suite loads each generated HTML document using set_content, substitutes its
local CSS/JS inline and removes staging CSP *for this test only*. HTTP response
headers and production hosted behavior are NOT covered by this test.
"""
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import json, re, time, os, shutil

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
OUT=ROOT/'review-artifacts';OUT.mkdir(exist_ok=True)
ROUTES=json.loads((DIST/'manifest.json').read_text())['routes']
CSS=(ROOT/'assets/site.css').read_text()
DATA=(DIST/'assets/site-data.js').read_text()
APP=(ROOT/'assets/site.js').read_text()

def offline(route,js=True):
    p=DIST/route.lstrip('/')/'index.html'
    html=p.read_text()
    html=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',html)
    html=html.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+CSS+'</style>')
    html=html.replace('<script src="/assets/site-data.js" defer></script>','<script>'+DATA+'</script>' if js else '')
    html=html.replace('<script src="/assets/site.js" defer></script>','<script>'+APP+'</script>' if js else '')
    return html

def main():
  engine=os.environ.get('MUSITU_BROWSER_ENGINE','chromium').strip().lower()
  if engine not in ('chromium','firefox','webkit'):raise ValueError('Invalid browser engine')
  results={'browser_engine':engine,'method':'offline DOM: self-contained content, inline local assets; CSP removed for runner only',
           'production_http_tested':False,'external_services_called':False,
           'routes_tested':0,'responsive_checks':0,'theme_checks':0,'nojs_checks':0,
           'interactions':{},'errors':[],'overflow':[],'runtime_exceptions':[]}
  with sync_playwright() as pw:
    browser_type=getattr(pw,engine)
    launch={'headless':True}
    if engine=='chromium':
      executable=os.environ.get('MUSITU_CHROMIUM_EXECUTABLE') or shutil.which('chromium')
      if executable:launch['executable_path']=executable
      launch['args']=['--no-sandbox']
    browser=browser_type.launch(**launch)
    ctx=browser.new_context(viewport={'width':1280,'height':800},java_script_enabled=True, reduced_motion='reduce')
    page=ctx.new_page();page.set_default_timeout(2500)
    def pageerror(e):results['runtime_exceptions'].append(str(e))
    page.on('pageerror',pageerror)
    page.on('request',lambda request:results['errors'].append('Unexpected network request: '+request.url) if request.url.startswith(('https://','http://')) else None)
    # All routes: true DOM layout at three viewports and light/dark design tokens.
    for idx,route in enumerate(ROUTES):
      if idx % 5 == 0: print(f'Browser layout checkpoint: {idx}/{len(ROUTES)} routes', flush=True)
      if idx:
        page.close()
        page=ctx.new_page()
        page.set_default_timeout(2500)
        page.on('pageerror',pageerror)
      page.set_viewport_size({'width':1280,'height':800})
      page.set_content(offline(route),wait_until='domcontentloaded',timeout=8000)
      assert page.locator('main#main').count()==1,route
      assert page.locator('h1').count()==1,route
      assert page.locator('html.has-js').count()==1,route
      results['routes_tested']+=1
      for width in [320,390,1280]:
        page.set_viewport_size({'width':width,'height':800})
        for theme in ['dark','light']:
          page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
          page.locator('html').evaluate('(el,theme)=>el.dataset.theme=theme',theme)
          measurements=page.evaluate('''() => ({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,
            body:document.body.scrollWidth,theme:document.documentElement.dataset.theme,
            main:document.querySelector('main').getBoundingClientRect().width})''')
          results['theme_checks']+=1
          if measurements['scroll']>measurements['client']+3:
            results['overflow'].append({'route':route,'width':width,'theme':theme,'measure':measurements})
        results['responsive_checks']+=1
    # Showcase homepage screenshots from actual rendered offline DOM.
    page.close();page=ctx.new_page();page.set_default_timeout(2500);page.on('pageerror',pageerror)
    page.set_viewport_size({'width':1280,'height':900})
    page.set_content(offline('/'),wait_until='domcontentloaded',timeout=8000)
    page.screenshot(path=str(OUT/'homepage-desktop-dom.png'),full_page=False,timeout=8000)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(OUT/'homepage-mobile-dom.png'),full_page=False,timeout=8000)
    # Interaction checks are run on a clean desktop DOM to avoid other modal interference.
    page.close();page=ctx.new_page();page.set_default_timeout(2500);page.on('pageerror',pageerror)
    page.set_viewport_size({'width':1280,'height':800})
    page.set_content(offline('/'),wait_until='domcontentloaded',timeout=8000)
    def check(label,fn):
      try:fn();results['interactions'][label]='PASS'
      except Exception as e:results['interactions'][label]='FAIL: '+repr(e)[:330];results['errors'].append(label+' failed: '+repr(e)[:500])
    def search():
      page.get_by_role('button',name='Search the website').click()
      assert page.locator('#search-dialog').evaluate('(e)=>e.open')
      page.locator('#site-search-input').fill('Chemistry')
      assert 'pages' in page.locator('#search-count').inner_text()
      assert page.locator('.search-result:visible').count()>0
      page.keyboard.press('Escape')
      assert not page.locator('#search-dialog').evaluate('(e)=>e.open')
    check('local_search',search)
    def navigator():
      page.locator('[data-goal="foundry"]').first.click()
      assert 'Foundry' in page.locator('[data-goal-title]').first.inner_text()
      assert page.locator('[data-goal-link]').first.get_attribute('href')=='/products/foundry/'
    check('navigator',navigator)
    def atlas():
      page.locator('[data-atlas="worldfabric"]').first.click()
      assert 'WorldFabric' in page.locator('[data-atlas-title]').first.inner_text()
    check('atlas',atlas)
    def evidence():
      page.locator('[data-evidence="axiom"].evidence-open').first.click()
      assert page.locator('#evidence-dialog').evaluate('(e)=>e.open')
      assert 'published' in page.locator('#evidence-dialog-content').inner_text().lower()
      page.locator('#evidence-dialog .dialog-close').click()
    check('evidence_lens',evidence)
    def ask():
      page.get_by_role('button',name='Ask MUSITU').first.click()
      assert page.locator('#ask-dialog').evaluate('(e)=>e.open')
      page.locator('#ask-local-input').fill('Foundry technology')
      page.locator('#ask-local-form button[type="submit"]').click()
      assert 'not an AI-generated answer' in page.locator('#ask-local-result').inner_text()
      page.locator('#ask-dialog .dialog-close').click()
    check('ask_local_only',ask)
    def theme():
      prev=page.locator('html').get_attribute('data-theme')
      page.locator('.header-actions .theme-button').click()
      assert page.locator('html').get_attribute('data-theme')!=prev
    check('desktop_theme_control',theme)
    def mobile():
      page.set_viewport_size({'width':390,'height':844})
      menu=page.locator('.mobile-menu>summary');menu.click()
      assert page.locator('.mobile-menu').evaluate('(el)=>el.open')
      control=page.locator('.mobile-menu-panel .mobile-theme-control')
      assert control.is_visible()
      previous=page.locator('html').get_attribute('data-theme')
      control.click()
      assert page.locator('html').get_attribute('data-theme')!=previous
    check('mobile_theme_and_menu',mobile)
    # Product comparison and filtering.
    page.set_viewport_size({'width':1280,'height':800})
    page.set_content(offline('/products/'),wait_until='domcontentloaded',timeout=8000)
    def catalog():
      assert page.locator('[data-catalog-item]').count()==6
      page.locator('#catalog-query').fill('worldfabric')
      assert page.locator('[data-catalog-item]:visible').count()==1
      page.locator('#catalog-reset').click()
      assert page.locator('[data-catalog-item]:visible').count()==6
    check('product_search_filter_reset',catalog)
    def compare():
      page.locator('[data-compare="axiom"]').first.click()
      page.locator('[data-compare="worldfabric"]').first.click()
      assert page.locator('#compare-output table').count()==1
      assert 'WorldFabric' in page.locator('#compare-output').inner_text()
    check('family_comparison',compare)
    page.set_content(offline('/experiences/lab/'),wait_until='domcontentloaded',timeout=8000)
    def lab():
      assert page.locator('#npv-result').count()==1
      page.locator('#npv-investment').fill('1000')
      page.locator('#npv-flow').fill('450')
      page.locator('#npv-rate').fill('10')
      # NPV = -1000 + 450*(1/1.1 + 1/1.1^2 + 1/1.1^3) ~= 119.08
      assert '$119.08' in page.locator('#npv-result').inner_text(),page.locator('#npv-result').inner_text()
    check('deterministic_npv_example',lab)
    def chemistry():
      page.locator('[data-cell="electrolytic"]').first.click()
      assert 'Electrolytic' in page.locator('#cell-title').first.inner_text()
    check('chemistry_learning_example',chemistry)
    # no-JS checks; this browser context never evaluates scripts.
    noctx=browser.new_context(viewport={'width':320,'height':800},java_script_enabled=False,reduced_motion='reduce')
    nopage=noctx.new_page();nopage.set_default_timeout(2500)
    for route in ROUTES:
      nopage.set_content(offline(route,js=False),wait_until='domcontentloaded',timeout=8000)
      assert nopage.locator('main#main').count()==1,route
      assert nopage.locator('html.has-js').count()==0,route
      assert nopage.locator('.mobile-menu > summary').is_visible(),route
      assert nopage.locator('.search-open').is_hidden(),route
      results['nojs_checks']+=1
    # Native details menu remains accessible without JavaScript.
    nopage.set_content(offline('/',js=False),wait_until='domcontentloaded',timeout=8000)
    def nojsmenu():
      nopage.locator('.mobile-menu > summary').click()
      assert nopage.locator('.mobile-menu').evaluate('(el)=>el.open')
      nopage.locator('.mobile-menu-panel details').first.locator('summary').click()
      assert nopage.locator('.mobile-menu-panel a[href="/products/"]').is_visible()
    check('nojs_mobile_navigation',nojsmenu)
    browser.close()
  results['passed']=not results['errors'] and not results['overflow'] and not results['runtime_exceptions'] and all(x=='PASS' for x in results['interactions'].values())
  (OUT/'browser-dom-results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
  print(json.dumps({k:results[k] for k in ['routes_tested','responsive_checks','theme_checks','nojs_checks','interactions','errors','overflow','runtime_exceptions','passed']},indent=2)[:12000])
  if not results['passed']:raise SystemExit(1)

if __name__=='__main__':main()
