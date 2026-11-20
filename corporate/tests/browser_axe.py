#!/usr/bin/env python3
"""Automated accessibility sampling of review-built MUSITU corporate routes.

Uses local review HTML and locally pinned axe-core, not the public website.
Automated findings never constitute full human WCAG certification.
"""
from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_review import ROOT, ROUTES, OUT, offline

AXE = ROOT / 'qa-deps' / 'node_modules' / 'axe-core' / 'axe.min.js'
TAGS = ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']
SAMPLE = ['/', '/products/', '/products/axiom/', '/contact/', '/ecosystem/', '/experiences/lab/']

def main():
    if not AXE.is_file():
        raise SystemExit('Pinned local axe-core script unavailable: '+str(AXE))
    report={'method':'offline generated DOM; CSP removed in review runner only',
            'all_routes_mobile_dark':0,'representative_responsive_theme_scans':0,
            'violations':[],'scan_errors':[],'passed':False}
    cases=[(route,390,'dark') for route in ROUTES]
    cases.extend((route,width,theme) for route in SAMPLE for width in (320,1280) for theme in ('dark','light'))
    with sync_playwright() as pw:
        chromium_path=next((p for p in ('/usr/bin/chromium','/usr/bin/chromium-browser') if Path(p).is_file()),None)
        kwargs={'headless':True,'args':['--no-sandbox']}
        if chromium_path:kwargs['executable_path']=chromium_path
        browser=pw.chromium.launch(**kwargs)
        ctx=browser.new_context(viewport={'width':390,'height':800},reduced_motion='reduce')
        page=ctx.new_page()
        page.set_default_timeout(10000)
        for i,(route,width,theme) in enumerate(cases):
            try:
                page.set_viewport_size({'width':width,'height':800})
                page.set_content(offline(route),wait_until='domcontentloaded',timeout=15000)
                page.locator('html').evaluate('(node,theme)=>node.dataset.theme=theme',theme)
                page.add_script_tag(path=str(AXE))
                result=page.evaluate('''async tags => {
                  const outcome=await window.axe.run(document,{
                    runOnly:{type:'tag',values:tags},
                    resultTypes:['violations']
                  });
                  return outcome.violations.map(v=>({id:v.id,impact:v.impact,node_count:v.nodes.length,
                    targets:v.nodes.slice(0,3).map(n=>n.target.join(' '))}));
                }''',TAGS)
                if result:report['violations'].append({'route':route,'width':width,'theme':theme,'issues':result})
                if i < len(ROUTES):report['all_routes_mobile_dark']+=1
                else:report['representative_responsive_theme_scans']+=1
            except Exception as e:
                report['scan_errors'].append({'route':route,'width':width,'theme':theme,'error':str(e)[:230]})
        browser.close()
    report['passed']=not report['violations'] and not report['scan_errors']
    (OUT/'axe-review-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False)[:14500])
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':
    main()
