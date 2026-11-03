"""Staging-only HTTP performance observations, not field Core Web Vitals.
Runs in GitHub Actions Chromium; outputs reproducible artifacts and budgets, no
live URLs or external services, no claims of production LCP/INP/CLS.
"""
from __future__ import annotations
import json,shutil,threading
from contextlib import contextmanager
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'; OUT=ROOT/'review-artifacts';OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
@contextmanager
def server():
    srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(DIST)))
    t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
    try:yield f'http://127.0.0.1:{srv.server_port}'
    finally:srv.shutdown();srv.server_close();t.join(timeout=3)

report={'scope':'STAGING localhost chromium lab-only observations; not real-user Core Web Vitals',
        'routes':{},'third_party_requests':[],'errors':[],'layout_shift_violations':[]}
OBSERVER="""(()=>{
 window.__musitu_perf={cls:0,lcp:0};
 try{new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__musitu_perf.cls+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(e){}
 try{new PerformanceObserver(list=>{for(const e of list.getEntries())window.__musitu_perf.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
})();"""
with server() as origin,sync_playwright() as p:
    launch={'headless':True,'args':['--no-sandbox']}
    exe=shutil.which('chromium') or shutil.which('google-chrome')
    if exe:launch['executable_path']=exe
    browser=p.chromium.launch(**launch)
    try:
        for label,width,height in [('mobile',390,844),('desktop',1440,900)]:
            page=browser.new_page(viewport={'width':width,'height':height})
            page.add_init_script(OBSERVER)
            page.on('pageerror',lambda error:report['errors'].append(str(error)))
            page.on('request',lambda req:report['third_party_requests'].append(req.url) if not req.url.startswith(origin+'/') else None)
            for route in ('/','/products/','/products/axiom/','/evidence/'):
                response=page.goto(origin+route,wait_until='load',timeout=12000)
                assert response is not None and response.status==200
                page.wait_for_timeout(350)
                data=page.evaluate("""() => {
                 const nav=performance.getEntriesByType('navigation')[0]||{};
                 const paint=performance.getEntriesByType('paint').find(x=>x.name==='first-contentful-paint');
                 const resources=performance.getEntriesByType('resource');
                 return {dom_content_loaded_ms:+(nav.domContentLoadedEventEnd||0).toFixed(1),
                     load_ms:+(nav.loadEventEnd||0).toFixed(1),
                     fcp_ms:paint?+paint.startTime.toFixed(1):null,
                     lcp_candidate_ms:window.__musitu_perf?.lcp?+window.__musitu_perf.lcp.toFixed(1):null,
                     cls_observed:+(window.__musitu_perf?.cls||0).toFixed(4),
                     resource_count:resources.length,
                     asset_bytes:resources.filter(x=>x.name.includes('/assets/')).reduce((sum,x)=>sum+(x.decodedBodySize||0),0)};
                }""")
                report['routes'][label+route]=data
                if data['cls_observed']>.1:
                    report['layout_shift_violations'].append({'viewport':label,'route':route,'cls_observed':data['cls_observed']})
                assert data['asset_bytes']<150000,(label,route,'asset payload unexpectedly large')
            page.close()
    finally:browser.close()
(OUT/'performance-lab.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not report['third_party_requests'],report['third_party_requests']
assert not report['errors'],report['errors']
assert not report['layout_shift_violations'],report['layout_shift_violations']
print('PASS staging performance lab:',json.dumps(report,sort_keys=True))
