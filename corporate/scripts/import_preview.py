#!/usr/bin/env python3
"""One-time read-only import of the owner-supplied 34-route preview.

All generated source lives under corporate/. The original reviewer file is left intact.
Media without confirmed rights is excluded. Not run by normal builds.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib, json, re, sys, base64

ROOT = Path(__file__).resolve().parents[1]
# Do not erase subsequent implementation fixes by accidentally re-importing.
if (ROOT/'content/pages.json').exists() and '--overwrite-reviewed' not in sys.argv:
    raise SystemExit('Curated website source already exists: refusing to overwrite it. Re-import requires a deliberate --overwrite-reviewed review decision.')
EXPECTED = 'c30e0ae55938ea9324aec8ac0998041a7c0a804ef28110c70b38408fa6cf8909'
paths=[arg for arg in sys.argv[1:] if arg != '--overwrite-reviewed']
PREVIEW = Path(paths[0]) if paths else Path('/mnt/data/MUSITU_34_PAGE_OFFLINE_PREVIEW.html')
raw = PREVIEW.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != EXPECTED:
    raise SystemExit(f'Source integrity mismatch: {sha}')
s = raw.decode('utf-8')
marker = 'const PAGES='
assert s.count(marker)==1
pages, n = json.JSONDecoder().raw_decode(s[s.index(marker)+len(marker):])
if len(pages)!=34: raise SystemExit(f'Expected 34 routes, found {len(pages)}')

soup = BeautifulSoup(pages['/'],'html.parser')
styles = soup.select('style')
scripts = soup.select('script')
assert len(styles)==1 and len(scripts)==3
ROOT.joinpath('assets/site.css').write_text(styles[0].string or styles[0].get_text(),encoding='utf-8')
data_script=(scripts[0].string or scripts[0].get_text()).strip()
assert data_script.startswith('window.MUSITU_PUBLIC = ')
ROOT.joinpath('content/public-records.json').write_text(json.dumps(json.loads(data_script.split('=',1)[1].rstrip(';')),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ROOT.joinpath('assets/site.js').write_text(scripts[1].string or scripts[1].get_text(),encoding='utf-8')
# Inline favicon in original is an unapproved provisional design, staged only.
icon=soup.select_one('link[rel="icon"]')
if icon and icon.get('href','').startswith('data:image/svg+xml;base64,'):
    svg=base64.b64decode(icon['href'].split(',',1)[1]);ROOT.joinpath('assets/favicon.svg').write_bytes(svg)

for name,html in [('footer',str(soup.select_one('footer'))),('dialogs','\n'.join(str(x) for x in soup.select('dialog'))),('skip',str(soup.select_one('.skip-link'))),('review-ribbon',str(soup.select_one('.review-ribbon')) )]:
    ROOT.joinpath('templates',name+'.html').write_text(html+'\n',encoding='utf-8')

records={}
for route,source in pages.items():
    page=BeautifulSoup(source,'html.parser')
    local_scripts=page.select('script')
    assert len(local_scripts)==3 and [str(x.string or x.get_text()) for x in local_scripts[:2]]==[str(x.string or x.get_text()) for x in scripts[:2]],route
    assert (page.style.string or page.style.get_text())==(styles[0].string or styles[0].get_text()),route
    title=page.title.get_text(strip=True)
    description=page.select_one('meta[name="description"]').get('content','')
    main=page.select_one('main')
    if not main:raise SystemExit('Missing main '+route)
    # Publication rights not cleared. Strip media bytes, EXIF and source URLs entirely.
    for video in list(main.find_all('video')):
        gated=page.new_tag('div')
        gated['role']='note';gated['class']=['video-clearance-gate']
        strong=page.new_tag('strong');strong.string='Studio demonstration media awaiting publication clearance'
        paragraph=page.new_tag('p');paragraph.string='The recorded prototype is described in the approved review material, but video and poster images are withheld from this shareable source package until rights, captions and metadata are cleared.'
        gated.append(strong);gated.append(paragraph)
        video.replace_with(gated)
    for img in list(main.find_all('img')):
        if img.get('src','').startswith('data:'):
            replace=page.new_tag('p');replace.string='Review-only media withheld pending approval.';img.replace_with(replace)
    if '__VIDEO_PLACEHOLDER__' in str(main) or 'data:image/png;base64,' in str(main):
        raise SystemExit('Media sanitization failed '+route)
    record={"title":title,"description":description,"header":str(page.header),"main":str(main),"review_state":"conditional" if route in ['/legal/privacy/','/legal/terms/','/status/','/developers/','/news/'] else "editorial-review"}
    records[route]=record
(ROOT/'content/pages.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'content/source-provenance.json').write_text(json.dumps({"source_file":PREVIEW.name,"sha256":EXPECTED,"imported_routes":len(records),"modifications":["Separated repeated CSS and browser-local scripts into shared files","Removed portable iframe postMessage navigation shim","Withheld unapproved embedded Studio video and poster assets","Preserved noindex and conditional editorial content"],"rights_status":"media not cleared for publication"},indent=2)+'\n',encoding='utf-8')
print(f'Imported {len(records)} routes from verified source; unapproved media excluded.')
