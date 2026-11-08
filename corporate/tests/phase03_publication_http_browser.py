#!/usr/bin/env python3
"""Real-CSP loopback browser smoke tests of 15 opt-in publication pages only.

No authenticated Cloudflare access, real device or manual WCAG certification asserted.
"""
from __future__ import annotations
import argparse,json,threading,os
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from phase03_production_http_browser import ROOT,DIST,OUTPUT,ORIGIN,Handler,parse_headers

def audit(engine:str)->dict:
    if engine not in {"chromium","firefox","webkit"}:
        raise ValueError("Unsupported Playwright engine")
    manifest=json.loads((DIST/"manifest.json").read_text())
    routes=manifest.get("phase03_publication_routes",[])
    assert manifest.get("build_mode")=="production" and manifest.get("route_count")==49
    assert len(routes)==15 and len(set(routes))==15
    response_headers=parse_headers()
    handler=type("Phase03PublicationHandler",(Handler,),{"response_headers":response_headers})
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(handler,directory=str(DIST)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f"http://127.0.0.1:{server.server_port}"
    report={"classification":"LOCAL_HTTP_PUBLICATION_PRODUCTION_SIMULATION_ONLY",
            "engine":engine,"pages":0,"viewport_checks":0,"headers_checked":0,
            "schema_checked":0,"js_errors":[],"console_errors":[],"off_origin_requests":[],
            "horizontal_overflow":[],"hosted_cloudflare_verified":False,
            "manual_wcag_22_aa_certified":False,"deployed":False,"passed":False}
    try:
      with sync_playwright() as pw:
        browser=getattr(pw,engine).launch(headless=True,**({"args":["--no-sandbox"]} if engine=="chromium" else {}))
        context=browser.new_context(viewport={"width":1280,"height":820},reduced_motion="reduce")
        page=context.new_page()
        page.on("pageerror",lambda error:report["js_errors"].append(str(error)))
        page.on("console",lambda msg:report["console_errors"].append(msg.text) if msg.type=="error" else None)
        def track(req):
            parsed=urlsplit(req.url)
            if parsed.scheme in ("http","https") and parsed.netloc != urlsplit(base).netloc:
                report["off_origin_requests"].append(parsed.hostname or "external")
        page.on("request",track)
        for path in routes:
            for width in (390,1280):
                page.set_viewport_size({"width":width,"height":820})
                response=page.goto(base+path,wait_until="load",timeout=20000)
                assert response and response.status==200,(path,width)
                headers={k.lower():v for k,v in response.headers.items()}
                for key,value in response_headers.items():
                    assert headers.get(key)==value,(path,key)
                report["headers_checked"]+=1
                assert page.locator("main#main").count()==1,path
                assert page.locator("h1").count()==1,path
                assert page.locator("html.has-js").count()==1,path
                assert page.evaluate("() => document.styleSheets.length")>=1,path
                assert page.locator('link[rel="canonical"]').get_attribute("href")==ORIGIN+path,path
                assert page.locator('meta[name="robots"]').get_attribute("content")=="index,follow",path
                assert page.locator('script[type="application/ld+json"]').count()==1,path
                payload=json.loads(page.locator('script[type="application/ld+json"]').inner_text())
                assert payload.get("@context")=="https://schema.org" and payload.get("@graph"),path
                report["schema_checked"]+=1
                language="fr" if path.startswith("/fr/") else "en"
                assert page.locator("html").get_attribute("lang")==language,path
                if language=="fr":
                    assert page.locator('link[hreflang="fr"]').count()==1,path
                    assert page.locator('link[hreflang="en"]').count()==1,path
                    assert page.locator('link[hreflang="x-default"]').count()==1,path
                for theme in ("dark","light"):
                    page.locator("html").evaluate("(node,theme)=>node.dataset.theme=theme",theme)
                    overflow=page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
                    if overflow>3:
                        report["horizontal_overflow"].append({"route":path,"width":width,"theme":theme,"overflow_px":overflow})
                    report["viewport_checks"]+=1
            report["pages"]+=1
        context.close()
        browser.close()
    finally:
      server.shutdown();server.server_close()
    report["passed"]=(report["pages"]==15 and report["viewport_checks"]==60 and
        report["headers_checked"]==30 and report["schema_checked"]==30 and
        not report["js_errors"] and not report["console_errors"] and
        not report["off_origin_requests"] and not report["horizontal_overflow"])
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--engine",choices=["chromium","firefox","webkit"],required=True)
    args=parser.parse_args()
    out=audit(args.engine)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT/f"phase03-publication-http-{args.engine}.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
    if not out["passed"]:
        raise SystemExit(1)
