#!/usr/bin/env python3
"""Generate a standalone owner REVIEW ONLY HTML; this is NOT a deploy artifact.

CSP is intentionally removed only for embedding approved local CSS/JS in srcdoc.
The site build under dist/ retains its CSP and noindex controls.
"""
from pathlib import Path
import json,re,html
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
OUT=ROOT/'review-artifacts/MUSITU_34_ROUTE_PORTABLE_OWNER_REVIEW_LOCAL_ONLY.html'
manifest=json.loads((DIST/'manifest.json').read_text())
records=json.loads((ROOT/'content/pages.json').read_text())
css=(ROOT/'assets/site.css').read_text()
data=(DIST/'assets/site-data.js').read_text()
app=(ROOT/'assets/site.js').read_text()
shim="""
document.addEventListener('click',e=>{
 const a=e.target.closest('a[href]');if(!a)return;
 const href=a.getAttribute('href');
 if(href && href.startsWith('/') && !href.startsWith('//')){
   e.preventDefault();parent.postMessage({kind:'MUSITU_REVIEW_ROUTE',href},'*');
 }
},true);
"""
pages={}
for route in manifest['routes']:
 src=(DIST/route.lstrip('/')/'index.html').read_text()
 src=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',src)
 src=src.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+css+'</style>')
 src=src.replace('<script src="/assets/site-data.js" defer></script>','<script>'+data+'</script>')
 src=src.replace('<script src="/assets/site.js" defer></script>','<script>'+app+'\n'+shim+'</script>')
 src=src.replace('<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">','')
 pages[route]=src
options=''.join(f'<option value="{html.escape(route,quote=True)}">{html.escape(records[route]["title"])}</option>' for route in manifest['routes'])
enc=json.dumps(pages,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
output='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>MUSITU 34-route portable owner review (NEVER DEPLOY)</title>
<style>*{box-sizing:border-box}body{margin:0;background:#090e1b;color:#f0f4ff;font:14px system-ui,sans-serif}button,select{font:inherit;background:#1b2942;color:#f0f4ff;border:1px solid #536b8e;border-radius:9px;padding:9px}button{cursor:pointer}button:focus-visible,select:focus-visible{outline:3px solid #72ebc7}.bar{background:#14213a;border-bottom:1px solid #536b8e;display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:10px 15px;min-height:70px}.bar label{font-weight:750}.bar .note{font-size:11px;color:#72ebc7;margin-right:auto;flex:1;min-width:160px}.bar select{min-width:180px;max-width:500px;flex:1}iframe{width:100%;height:calc(100dvh - 95px);min-height:400px;display:block;border:0;background:#090e1b}@media(max-width:620px){.bar label{font-size:12px}.bar .note{width:100%;flex-basis:100%;order:2}.bar select{min-width:0}.bar{min-height:120px}iframe{height:calc(100dvh - 130px)}}</style></head><body>
<div class="bar"><label for="routes">MUSITU owner review</label><span class="note">34 routes · local only · NOT DEPLOYABLE · remote AI disabled · unapproved media withheld</span><select id="routes" aria-label="Choose a website route">'''+options+'''</select><button type="button" id="back">Back</button></div>
<iframe title="MUSITU corporate offline review" id="site" referrerpolicy="no-referrer"></iframe><script>const PAGES='''+enc+''';
const frame=document.getElementById('site'),menu=document.getElementById('routes');
function get(){try{const path=decodeURIComponent(location.hash.slice(1)||'/');return path;}catch(_){return '/';}}
function go(target,historyUpdate=true){let [path,...rest]=String(target).split('#');const fragment=rest.join('#');if(!Object.prototype.hasOwnProperty.call(PAGES,path))path='/404/';
 if(historyUpdate){const desired=encodeURIComponent(path+(fragment?'#'+fragment:''));if(location.hash.slice(1)!==desired){location.hash=desired;return;}}
 menu.value=path;frame.onload=()=>{try{frame.contentWindow.scrollTo(0,0);if(fragment){const target=frame.contentDocument.getElementById(fragment);target?.scrollIntoView();}}catch(_){}};frame.srcdoc=PAGES[path];}
window.addEventListener('hashchange',()=>go(get(),false));
window.addEventListener('message',event=>{if(event.source!==frame.contentWindow)return;if(event.data?.kind==='MUSITU_REVIEW_ROUTE'&&typeof event.data.href==='string'){
 const path=event.data.href.split('#')[0];if(Object.prototype.hasOwnProperty.call(PAGES,path)){go(event.data.href);}}});
menu.addEventListener('change',()=>go(menu.value));document.getElementById('back').addEventListener('click',()=>history.back());go(get(),false);
</script></body></html>'''
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(output,encoding='utf-8')
print(f'Portable REVIEW ONLY: {len(pages)} routes, {OUT.stat().st_size} bytes, no unapproved video')
