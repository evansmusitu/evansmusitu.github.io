#!/usr/bin/env python3
"""Offline owner-preview UX smoke test; no network or deployment."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
ART=BASE/'review-artifacts'
FILE=ART/'MUSITU_34_ROUTE_PORTABLE_OWNER_REVIEW_LOCAL_ONLY.html'

def main():
  assert FILE.exists()
  record={'kind':'review-only portable srcdoc', 'routes':0,'initial_page':None,'select_navigation':False,'internal_navigation':False,'errors':[],'passed':False}
  with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':900});page.set_default_timeout(6000)
    page.on('pageerror',lambda error:record['errors'].append(str(error)))
    page.on('request',lambda req:record['errors'].append('Unexpected outbound request '+req.url) if req.url.startswith(('http://','https://')) else None)
    page.set_content(FILE.read_text(),wait_until='domcontentloaded',timeout=15000)
    frame=page.frame_locator('#site')
    record['routes']=page.locator('#routes option').count()
    record['initial_page']=frame.locator('h1').first.inner_text().strip()[:80]
    page.locator('#routes').select_option('/products/')
    frame.locator('#catalog-items').wait_for()
    record['select_navigation']='ecosystem' in frame.locator('h1').first.inner_text().lower()
    frame.locator('#catalog-items a[href="/products/axiom/"]').first.click()
    page.wait_for_function("document.querySelector('#routes').value === '/products/axiom/'",timeout=6000)
    record['internal_navigation']=('Axiom' in frame.locator('main').inner_text() and 'Complex questions' in frame.locator('h1').first.inner_text())
    record['passed']=record['routes']==34 and record['select_navigation'] and record['internal_navigation'] and not record['errors']
    browser.close()
  (ART/'portable-browser-results.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps(record,indent=2))
  if not record['passed']:raise SystemExit(1)

if __name__=='__main__':main()
