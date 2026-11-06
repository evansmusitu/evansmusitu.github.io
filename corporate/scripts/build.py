#!/usr/bin/env python3
"""Deterministic, isolated, static-first MUSITU corporate review build.

No network calls, deployment actions, publishing, or external service mutation.
Keep conditional routes noindex; canonical production domain must be approved separately.
"""
from __future__ import annotations
import hashlib, html, json, re, shutil, os
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
SRC=BASE/'content/pages.json'
DST=BASE/'dist'
ASSETS=BASE/'assets'
TEMPLATES=BASE/'templates'
ROUTES=[
 '/','/company/','/trust/','/accessibility/','/products/','/products/axiom/',
 '/products/education/','/products/foundry/','/products/markets/','/products/fmi/',
 '/products/worldfabric/','/products/education/chemistry-rescue/',
 '/products/foundry/studio/','/solutions/','/solutions/finance-research/',
 '/solutions/learning/','/solutions/creative-production/','/solutions/enterprise-systems/',
 '/experiences/','/experiences/intelligence/','/experiences/lab/','/ecosystem/',
 '/research/','/evidence/','/resources/','/developers/','/news/',
 '/contact/','/support/','/status/','/legal/privacy/','/legal/terms/',
 '/sitemap/','/404/',
]
GATED={"/status/","/legal/privacy/","/legal/terms/","/developers/","/news/"}
# Meta CSP is a limited staging defense, not a replacement for production response headers.
META_CSP=("default-src 'none'; script-src 'self'; style-src 'self'; "
          "img-src 'self' data:; font-src 'self'; media-src 'self'; "
          "connect-src 'none'; object-src 'none'; frame-src 'none'; "
          "form-action 'none'; base-uri 'none'")

def hash_bytes(raw:bytes)->str:
 return hashlib.sha256(raw).hexdigest()

def validate(records:dict)->None:
 if set(records)!=set(ROUTES):
  raise ValueError('Route inventory mismatch: missing '+str(set(ROUTES)-set(records))+' extras '+str(set(records)-set(ROUTES)))
 if len(ROUTES)!=34:raise ValueError('Master route count changed')
 for route,info in records.items():
  if not(route.startswith('/') and route.endswith('/')):raise ValueError('Route shape '+route)
  for name in ('header','main','title','description'):
   if not isinstance(info.get(name),str) or not info[name].strip():raise ValueError(f'Incomplete page {route} {name}')
  if '<main' not in info['main'] or 'id="main"' not in info['main']:
   raise ValueError('Missing proper page main '+route)
  if '__VIDEO_PLACEHOLDER__' in info['main'] or 'data:video/' in info['main'] or 'data:image/png;base64,' in info['main']:
   raise ValueError('Uncleared media '+route)
  if '<script' in info['main'].lower():raise ValueError('Inline script in content '+route)
  if '<iframe' in info['main'].lower():raise ValueError('Iframe in content '+route)

STUDIO_VIDEO_SHA256='afd6dfd3c73668e544f3f8a857697fed0abaadccd4927202bb3a185612c2dea0'
STUDIO_POSTER_SHA256='0ea5e961d916375029010dbae01bf8a1783e5fd6b90f74c006dc852df1c285d0'

def protected_studio_media_ready()->bool:
 flag=os.environ.get('MUSITU_PROTECTED_STAGING_MEDIA','0')
 if flag not in ('0','1'):raise ValueError('Invalid staging media flag')
 if flag!='1':return False
 for name,checksum in [('studio-demo-82s.mp4',STUDIO_VIDEO_SHA256),('studio-poster.png',STUDIO_POSTER_SHA256)]:
  source=ASSETS/name
  if not source.is_file():raise ValueError('Owner media file missing: '+name)
  if hash_bytes(source.read_bytes())!=checksum:raise ValueError('Owner media checksum mismatch: '+name)
 return True

def add_protected_studio_player(body:str)->str:
 player=('<video class="studio-demo-player" controls playsinline preload="metadata" poster="/assets/studio-poster.png" '
  'aria-label="MUSITU Studio 82-second recorded offline 3D demonstration">'
  '<source src="/assets/studio-demo-82s.mp4" type="video/mp4">'
  'Your browser cannot play the recording. The Studio page provides the demonstration transcript.</video>')
 result,count=re.subn(r'<div class="video-clearance-gate" role="note">.*?</div>',player,body,count=1,flags=re.DOTALL)
 if count!=1:raise ValueError('Studio media gate is missing in target route')
 return result

def render(route:str,info:dict,shared:dict,staged_media:bool=False)->str:
 title=html.escape(info['title'],quote=True)
 desc=html.escape(info['description'],quote=True)
 body='\n'.join([shared['skip'],info['header'],shared['review-ribbon'],info['main'],shared['footer'],shared['dialogs']])
 if staged_media and route in ('/products/foundry/studio/','/experiences/lab/'):
  body=add_protected_studio_player(body)
 return ('<!doctype html>\n<html lang="en" data-theme="dark">\n<head>\n'
 '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
 '<meta name="robots" content="noindex,nofollow">\n'
 '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
 '<meta name="color-scheme" content="dark light">\n'
 '<meta name="theme-color" content="#090E1B">\n'
 f'<meta name="description" content="{desc}">\n'
 f'<meta property="og:title" content="{title}">\n'
 f'<meta property="og:description" content="{desc}">\n'
 '<meta property="og:type" content="website">\n'
 '<meta name="stage" content="isolated-review-not-published">\n'
 f'<meta http-equiv="Content-Security-Policy" content="{html.escape(META_CSP,quote=True)}">\n'
 f'<title>{title}</title>\n'
 '<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">\n'
 '<link rel="stylesheet" href="/assets/site.css">\n'
 '</head>\n<body>\n'+body+'\n'
 '<script src="/assets/site-data.js" defer></script>\n'
 '<script src="/assets/site.js" defer></script>\n'
 '</body>\n</html>\n')

def build()->dict:
 records=json.loads(SRC.read_text(encoding='utf-8'))
 validate(records)
 shared={p.stem:p.read_text(encoding='utf-8') for p in TEMPLATES.glob('*.html')}
 if set(shared)!={'skip','review-ribbon','footer','dialogs'}:raise ValueError('Unexpected shared templates')
 if DST.exists():shutil.rmtree(DST)
 DST.mkdir(parents=True)
 asset_dest=DST/'assets';asset_dest.mkdir()
 for name in ('site.css','site.js','favicon.svg'):
  shutil.copyfile(ASSETS/name,asset_dest/name)
 staged_media=protected_studio_media_ready()
 if staged_media:
  for name in ('studio-demo-82s.mp4','studio-poster.png'):
   shutil.copyfile(ASSETS/name,asset_dest/name)
 public=json.loads((BASE/'content/public-records.json').read_text(encoding='utf-8'))
 if len(public.get('families',[]))!=6 or len(public.get('routes',[]))!=34:
  raise ValueError('Public record content does not match the authorized six families / 34 routes')
 public_routes={x.get('path') for x in public['routes']}
 if public_routes!=set(ROUTES):raise ValueError('Public routes index out of sync with master')
 if len({x.get('id') for x in public['evidence']})!=len(public['evidence']):
  raise ValueError('Duplicate evidence record ID')
 if any(not all(x.get(k) for k in ('claim','limits','kind','date','link','establishes')) for x in public['evidence']):
  raise ValueError('Incomplete evidence source record')
 (asset_dest/'site-data.js').write_text('window.MUSITU_PUBLIC = '+json.dumps(public,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
 (DST/'claim-register.json').write_text(json.dumps(public['evidence'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for route in ROUTES:
  dest=DST/route.lstrip('/')/'index.html'
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(render(route,records[route],shared,staged_media=staged_media),encoding='utf-8')
 (DST/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
 # A production XML sitemap is not generated without the owner-approved canonical domain.
 # The human-readable /sitemap/ is present. Keep all files excluded from indexing.
 compiled={p.relative_to(DST).as_posix():hash_bytes(p.read_bytes()) for p in sorted(DST.rglob('*')) if p.is_file() and p.name!='manifest.json'}
 manifest={'document':'MUSITU-WEB-MASTER-1.0','authorization':'Package A local only',
    'production_approved':False,'media_publication_approved':False,'protected_staging_media_included':staged_media,'route_count':len(ROUTES),
    'routes':ROUTES,'gated_routes':sorted(GATED),'files':compiled}
 (DST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return manifest

if __name__=='__main__':
 x=build()
 print(f'MUSITU corporate LOCAL REVIEW build: {x["route_count"]} routes, {len(x["files"])} hashed files; noindex, no deployment')
