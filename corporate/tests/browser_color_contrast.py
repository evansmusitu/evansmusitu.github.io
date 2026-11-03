"""Staging browser contrast regression for text on solid, resolved backgrounds.

This is NOT a WCAG certification: gradients, translucency, image-backed text,
pseudo-elements, non-text contrast and assistive technology need manual review.
Uses offline Chromium, no network or site deployment.
"""
from __future__ import annotations
import json,re,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
OUT=ROOT/'review-artifacts'; OUT.mkdir(exist_ok=True)
CSS=(DIST/'assets/site.css').read_text(encoding='utf-8')
JS=(DIST/'assets/site.js').read_text(encoding='utf-8')
ROUTES=sorted(p.relative_to(DIST).as_posix() for p in DIST.rglob('index.html'))
assert len(ROUTES)==22

def inline_page(route):
    html=(DIST/route).read_text(encoding='utf-8')
    html=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',html)
    return (html.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+CSS+'</style>')
            .replace('<script defer src="/assets/site.js"></script>','')
            .replace('</body>','<script>'+JS+'</script></body>'))

AUDIT_JS=r'''() => {
  const parseColor=s=>{
    const m=String(s).match(/rgba?\((\d+)[, ]+(\d+)[, ]+(\d+)(?:[,/ ]+([.\d]+))?\)/);
    return m?[+m[1],+m[2],+m[3],m[4]?+m[4]:1]:null;
  };
  const luminance=a=>{
    const v=a.slice(0,3).map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);
    return .2126*v[0]+.7152*v[1]+.0722*v[2];
  };
  const contrast=(a,b)=>{const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
  let measured=0,skipped=0;const failed=[];
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()){
    const node=walker.currentNode,elt=node.parentElement;
    if(!elt||!node.textContent.trim()||elt.closest('dialog:not([open])'))continue;
    const cs=getComputedStyle(elt),box=elt.getBoundingClientRect();
    if(!box.width||!box.height||cs.display==='none'||cs.visibility==='hidden')continue;
    const fg=parseColor(cs.color);if(!fg||fg[3]<.999){skipped++;continue;}
    let bg=null,paint=elt;
    while(paint){const s=getComputedStyle(paint);
      if(s.backgroundImage!=='none'){skipped++;break;}
      const value=parseColor(s.backgroundColor);
      if(value&&value[3]>=.999){bg=value;break;}
      paint=paint.parentElement;
    }
    if(!bg)continue;
    const px=parseFloat(cs.fontSize),w=parseInt(cs.fontWeight,10)||400;
    const threshold=px>=24||(px>=18.66&&w>=700)?3:4.5;
    const ratio=contrast(fg,bg);measured++;
    if(ratio+0.005<threshold)failed.push({text:node.textContent.trim().slice(0,60),
      tag:elt.tagName,className:String(elt.className||'').slice(0,65),
      color:cs.color,background:getComputedStyle(paint).backgroundColor,
      ratio:+ratio.toFixed(2),threshold});
  }
  return {measured,skipped,failed};
}'''

report={'scope':'solid-background computed text contrast regression; not WCAG conformance',
        'routes':len(ROUTES),'themes':['light','dark'],'widths':[320,1440],
        'views':0,'measured_text_samples':0,'skipped_due_to_complex_background':0,'failures':[]}
with sync_playwright() as pw:
    settings={'headless':True,'args':['--no-sandbox']}
    executable=shutil.which('chromium') or shutil.which('google-chrome')
    if executable:settings['executable_path']=executable
    browser=pw.chromium.launch(**settings)
    try:
        page=browser.new_page()
        page.emulate_media(reduced_motion='reduce')
        for width in report['widths']:
            page.set_viewport_size({'width':width,'height':850})
            for route in ROUTES:
                page.set_content(inline_page(route),wait_until='load')
                page.add_style_tag(content='*,*::before,*::after{transition:none!important;animation:none!important}')
                for theme in report['themes']:
                    page.evaluate('(v)=>{document.documentElement.dataset.theme=v}',theme)
                    page.wait_for_timeout(35) # let color-scheme styles resolve without transitions
                    outcome=page.evaluate(AUDIT_JS)
                    report['views']+=1
                    report['measured_text_samples']+=outcome['measured']
                    report['skipped_due_to_complex_background']+=outcome['skipped']
                    for item in outcome['failed']:
                        report['failures'].append({'width':width,'route':route,'theme':theme,**item})
    finally:
        browser.close()
(OUT/'color-contrast-regressions.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert report['views']==88
assert report['measured_text_samples']>1000
assert not report['failures'],json.dumps(report['failures'][:15],indent=2)
print('PASS browser contrast:',json.dumps({key:report[key] for key in ('views','measured_text_samples','skipped_due_to_complex_background','failures')},sort_keys=True))
