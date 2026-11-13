#!/usr/bin/env python3
"""Deterministic, isolated, static-first MUSITU corporate review build.

No network calls, deployment actions, publishing, or external service mutation.
Keep conditional routes noindex; canonical production domain must be approved separately.
"""
from __future__ import annotations
import hashlib, html, json, re, shutil, os
from pathlib import Path
from seo import seo_head, validate_catalog
from phase03_publication import (approved_sources, article_routes, article_info, article_head,
  localize_english_core, french_info, french_head, french_records, hreflang, FR_EN,
  actual_publication_date)

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
PRODUCTION_ORIGIN='https://mftintelligence.com'
# Meta CSP is defense in depth; effective response headers must also be verified on the final host.
META_CSP=("default-src 'none'; script-src 'self'; style-src 'self'; "
          "img-src 'self' data:; font-src 'self'; media-src 'self'; "
          "connect-src 'none'; object-src 'none'; frame-src 'none'; "
          "form-action 'none'; base-uri 'none'")

def hash_bytes(raw:bytes)->str:
 return hashlib.sha256(raw).hexdigest()

def current_build_mode()->str:
 mode=os.environ.get('MUSITU_BUILD_MODE','review').strip().lower()
 if mode not in ('review','production'):raise ValueError('MUSITU_BUILD_MODE must be review or production')
 return mode

def canonical_origin(mode:str)->str|None:
 if mode!='production':return None
 origin=os.environ.get('MUSITU_CANONICAL_ORIGIN','').rstrip('/')
 if origin!=PRODUCTION_ORIGIN:
  raise ValueError('Production build requires canonical origin '+PRODUCTION_ORIGIN)
 return origin

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

def verified_studio_media_ready(mode:str)->bool:
 if mode=='production':
  flag=os.environ.get('MUSITU_INCLUDE_STUDIO_MEDIA','0')
  if flag!='1':raise ValueError('Production build requires MUSITU_INCLUDE_STUDIO_MEDIA=1')
 else:
  flag=os.environ.get('MUSITU_PROTECTED_STAGING_MEDIA','0')
  if flag not in ('0','1'):raise ValueError('Invalid staging media flag')
  if flag!='1':return False
 for name,checksum in [('studio-demo-82s.mp4',STUDIO_VIDEO_SHA256),('studio-poster.png',STUDIO_POSTER_SHA256)]:
  source=ASSETS/name
  if not source.is_file():raise ValueError('Owner media file missing: '+name)
  if hash_bytes(source.read_bytes())!=checksum:raise ValueError('Owner media checksum mismatch: '+name)
 return True

# Backward-compatible review helper used by existing tests.
def protected_studio_media_ready()->bool:
 return verified_studio_media_ready('review')

def add_protected_studio_player(body:str)->str:
 player=('<video class="studio-demo-player" controls playsinline preload="metadata" poster="/assets/studio-poster.png" '
  'aria-label="MUSITU Studio 82-second recorded offline 3D demonstration">'
  '<source src="/assets/studio-demo-82s.mp4" type="video/mp4">'
  'Your browser cannot play the recording. The Studio page provides the demonstration transcript.</video>')
 result,count=re.subn(r'<div class="video-clearance-gate" role="note">.*?</div>',player,body,count=1,flags=re.DOTALL)
 if count!=1:raise ValueError('Studio media gate is missing in target route')
 return result

def render(route:str,info:dict,shared:dict,staged_media:bool=False,mode:str='review',origin:str|None=None,seo_html:str='')->str:
 title=html.escape(info['title'],quote=True)
 desc=html.escape(info['description'],quote=True)
 production=mode=='production'
 if production and origin!=PRODUCTION_ORIGIN:raise ValueError('Production render requires approved canonical origin')
 footer=shared['footer']
 ribbon=shared['review-ribbon']
 if production:
  ribbon=''
  footer=footer.replace('Independent staging preview · noindex · no production release','Official MUSITU corporate website')
  footer=footer.replace('© 2026 MUSITU. Editorial staging specification.','© 2026 MUSITU.')
 robots='noindex,nofollow' if (not production or route=='/404/') else 'index,follow'
 canonical='' if not production or route=='/404/' else f'<link rel="canonical" href="{origin}{route}">\n'
 ogurl='' if not production or route=='/404/' else f'<meta property="og:url" content="{origin}{route}">\n'
 stage='' if production else '<meta name="stage" content="isolated-review-not-published">\n'
 body='\n'.join([shared['skip'],info['header'],ribbon,info['main'],footer,shared['dialogs']])
 if staged_media and route in ('/products/foundry/studio/','/experiences/lab/'):
  body=add_protected_studio_player(body)
 return ('<!doctype html>\n<html lang="en" data-theme="dark">\n<head>\n'
 '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
 f'<meta name="robots" content="{robots}">\n'
 '<meta name="referrer" content="strict-origin-when-cross-origin">\n'
 '<meta name="color-scheme" content="dark light">\n'
 '<meta name="theme-color" content="#090E1B">\n'
 f'<meta name="description" content="{desc}">\n'
 f'<meta property="og:title" content="{title}">\n'
 f'<meta property="og:description" content="{desc}">\n'
 '<meta property="og:type" content="website">\n'
  +ogurl+canonical+stage+seo_html+
 f'<meta http-equiv="Content-Security-Policy" content="{html.escape(META_CSP,quote=True)}">\n'
 f'<title>{title}</title>\n'
 '<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">\n'
 '<link rel="stylesheet" href="/assets/site.css">\n'
 '</head>\n<body>\n'+body+'\n'
 '<script src="/assets/site-data.js" defer></script>\n'
 '<script src="/assets/site.js" defer></script>\n'
 '</body>\n</html>\n')

def build()->dict:
 mode=current_build_mode()
 origin=canonical_origin(mode)
 records=json.loads(SRC.read_text(encoding='utf-8'))
 publication_flag=os.environ.get('MUSITU_PUBLISH_PHASE03','0')
 if publication_flag not in ('0','1'):raise ValueError('MUSITU_PUBLISH_PHASE03 must be 0 or 1')
 publication_enabled=publication_flag=='1'
 publication_date=actual_publication_date() if publication_enabled and mode=='production' else None
 articles=approved_sources() if publication_enabled else []
 french=french_records() if publication_enabled else {}
 extra_routes=article_routes(articles)+list(french)
 if len(extra_routes)!=len(set(extra_routes)) or any(route in ROUTES for route in extra_routes):
  raise ValueError('Publication route collision')
 validate(records)
 if mode=='production':validate_catalog(ROUTES)
 shared={p.stem:p.read_text(encoding='utf-8') for p in TEMPLATES.glob('*.html')}
 if set(shared)!={'skip','review-ribbon','footer','dialogs'}:raise ValueError('Unexpected shared templates')
 if DST.exists():shutil.rmtree(DST)
 DST.mkdir(parents=True)
 asset_dest=DST/'assets';asset_dest.mkdir()
 for name in ('site.css','site.js','favicon.svg'):
  shutil.copyfile(ASSETS/name,asset_dest/name)
 staged_media=verified_studio_media_ready(mode)
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
  info=localize_english_core(route,records[route],articles) if publication_enabled else records[route]
  seo_html=seo_head(route,info,records,origin) if mode=='production' else ''
  if publication_enabled and mode=='production':seo_html+=hreflang(route)
  dest.write_text(render(route,info,shared,staged_media=staged_media,mode=mode,origin=origin,seo_html=seo_html),encoding='utf-8')
 if publication_enabled:
  for article in articles:
   route='/research/articles/'+article['slug']+'/'
   info=article_info(article,records['/research/']['header'],publication_date)
   dest=DST/route.lstrip('/')/'index.html'
   dest.parent.mkdir(parents=True,exist_ok=True)
   seo_html=article_head(article) if mode=='production' else ''
   dest.write_text(render(route,info,shared,mode=mode,origin=origin,seo_html=seo_html),encoding='utf-8')
  shared_fr={**shared,
    'skip':'<a class="skip-link" href="#main">Aller au contenu principal</a>',
    'review-ribbon':'<div class="review-ribbon" role="note">Aperçu protégé · non indexé</div>',
    'dialogs':'',
    'footer':('<footer class="site-footer"><div class="shell footer-main"><div class="footer-col">'
      '<h2>MUSITU</h2><p>Intelligence fondée sur des preuves. Technologie au service d’un objectif.</p>'
      '<a href="/fr/">Accueil</a><a href="/fr/research/">Recherche</a>'
      '<a href="/fr/products/axiom/">Axiom</a></div>'
      '<div class="footer-col"><h2>Informations et contact</h2>'
      '<a href="/contact/" lang="en">Contact (English)</a>'
      '<a href="/legal/privacy/" lang="en">Privacy Policy (English)</a>'
      '<a href="/legal/terms/" lang="en">Terms (English)</a>'
      '<a href="/accessibility/" lang="en">Accessibility (English)</a></div></div>'
      '<div class="shell footer-bottom"><span>© 2026 MUSITU.</span></div></footer>')}
  for route,pilot in french.items():
   info=french_info(route,records[FR_EN[route]],pilot)
   dest=DST/route.lstrip('/')/'index.html'
   dest.parent.mkdir(parents=True,exist_ok=True)
   seo_html=french_head(route,info) if mode=='production' else ''
   rendered=render(route,info,shared_fr,mode=mode,origin=origin,seo_html=seo_html)
   rendered=rendered.replace('<html lang="en"','<html lang="fr"',1)
   dest.write_text(rendered,encoding='utf-8')
 # Cloudflare Pages requires a top-level 404.html to disable its automatic
 # HTTP 200 single-page-application fallback for unknown static routes.
 # Keep the existing /404/ page, but use this noindex copy for actual 404s.
 (DST/'404.html').write_bytes((DST/'404'/'index.html').read_bytes())
 if mode=='production':
  (DST/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {origin}/sitemap.xml\n',encoding='utf-8')
  urls=''.join(f'<url><loc>{origin}{route}</loc></url>' for route in [r for r in ROUTES if r!='/404/']+extra_routes)
  (DST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>\n',encoding='utf-8')
  (DST/'_headers').write_text(
   "/*\n"
   "  Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; media-src 'self'; connect-src 'none'; object-src 'none'; frame-src 'none'; frame-ancestors 'none'; form-action 'none'; base-uri 'none'\n"
   "  X-Content-Type-Options: nosniff\n"
   "  Referrer-Policy: strict-origin-when-cross-origin\n"
   "  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()\n"
   "  X-Frame-Options: DENY\n",encoding='utf-8')
 else:
  (DST/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
 compiled={p.relative_to(DST).as_posix():hash_bytes(p.read_bytes()) for p in sorted(DST.rglob('*')) if p.is_file() and p.name!='manifest.json'}
 manifest={'document':'MUSITU-WEB-MASTER-1.0','authorization':'Package A production candidate' if mode=='production' else 'Package A local only',
    'build_mode':mode,'canonical_origin':origin,'indexing_enabled':mode=='production',
    'production_approved':False,'media_publication_approved':True,'brand_master_approved':True,'brand_master_sha256':'f0e73478176b335bf3cfb5afd8bd7249d5aa39f2627798af7c71d9f13972c2fd','protected_staging_media_included':staged_media if mode=='review' else False,'studio_media_included':staged_media,'route_count':len(ROUTES)+len(extra_routes),
    'phase03_publication_source_approved':publication_enabled,
    'phase03_publication_routes':extra_routes,
    'phase03_publication_indexable':publication_enabled and mode=='production',
    'phase03_article_publication_date':publication_date,
    'routes':ROUTES,'gated_routes':sorted(GATED),'files':compiled}
 (DST/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return manifest

if __name__=='__main__':
 x=build()
 if x['build_mode']=='production':
  print(f'MUSITU corporate PRODUCTION CANDIDATE build: {x["route_count"]} routes, {len(x["files"])} hashed files; canonical={x["canonical_origin"]}; NOT DEPLOYED')
 else:
  print(f'MUSITU corporate LOCAL REVIEW build: {x["route_count"]} routes, {len(x["files"])} hashed files; noindex, no deployment')
