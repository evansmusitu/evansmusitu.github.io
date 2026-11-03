"""Static, DOM-based accessibility regression checks for all 22 review pages.

NOT an axe or independent WCAG conformance audit. Uses actual Chromium layout with
inline test CSS/JS, because the container browser blocks localhost navigation.
This provides named-controls, semantic relationships, reflow, focus and spacing
regressions, while independent screen reader testing remains a launch gate.
"""
from __future__ import annotations
import json,re,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
CSS=(DIST/'assets/site.css').read_text(encoding='utf-8')
JS=(DIST/'assets/site.js').read_text(encoding='utf-8')
OUT=ROOT/'review-artifacts'
OUT.mkdir(exist_ok=True)
ROUTES=sorted(p.relative_to(DIST).as_posix() for p in DIST.rglob('index.html'))

# The script is from this codebase; external content is not injected here.
def render(path):
    s=(DIST/path).read_text(encoding='utf-8')
    s=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', s)
    return (s.replace('<link rel="stylesheet" href="/assets/site.css">', '<style>'+CSS+'</style>')
             .replace('<script defer src="/assets/site.js"></script>', '')
             .replace('</body>', '<script>'+JS+'</script></body>'))

AUDIT_JS="""() => {
  const all=Array.from(document.querySelectorAll('*'));
  const duplicates=[];
  const ids=new Map();
  for(const e of all){if(!e.id)continue;ids.set(e.id,(ids.get(e.id)||0)+1)}
  for(const [id,n] of ids)if(n>1)duplicates.push(id);
  const problems=[];
  const controls=Array.from(document.querySelectorAll('a, button, input, select, textarea'));
  const name=e=>{
    const label=e.getAttribute('aria-label');if(label)return label.trim();
    const labelled=e.getAttribute('aria-labelledby');
    if(labelled){const txt=labelled.split(/\\s+/).map(id=>document.getElementById(id)?.textContent||'').join(' ').trim();if(txt)return txt}
    if(e.labels && e.labels.length)return Array.from(e.labels).map(x=>x.textContent).join(' ').trim();
    if(e.tagName==='INPUT' && e.type==='submit')return e.value||'';
    return (e.innerText||e.textContent||e.getAttribute('title')||'').trim();
  };
  for(const c of controls){
    if(!name(c))problems.push(`unnamed:${c.tagName}#${c.id}`);
    if(c.hasAttribute('aria-controls') && !document.getElementById(c.getAttribute('aria-controls'))) problems.push(`bad aria-controls:${c.id}`);
    if(c.hasAttribute('aria-labelledby'))for(const id of c.getAttribute('aria-labelledby').split(/\\s+/))if(id&&!document.getElementById(id))problems.push(`bad aria-labelledby:${c.id}:${id}`);
    if(c.tagName==='A' && !c.getAttribute('href'))problems.push('anchor missing href');
  }
  for(const img of document.querySelectorAll('img'))if(!img.hasAttribute('alt'))problems.push('img missing alt');
  for(const e of document.querySelectorAll('[aria-hidden="true"]'))if(e.matches('a,button,input,select,textarea') || e.querySelector('a,button,input,select,textarea'))problems.push('interactive under aria-hidden');
  const landmarks={main:document.querySelectorAll('main').length, h1:document.querySelectorAll('h1').length};
  if(landmarks.main!==1||landmarks.h1!==1)problems.push('invalid landmarks');
  return {controls:controls.length,duplicates,problems,landmarks};
}"""

TEXT_SPACING="""*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}"""
results={'routes':len(ROUTES),'viewport_checks':0,'named_controls_checked':0,'duplicate_ids':0,'unnamed_controls':0,'text_spacing_overflows':0,'issues':[]}

with sync_playwright() as pw:
    args={'headless':True,'args':['--no-sandbox']}
    executable=shutil.which('chromium') or shutil.which('google-chrome')
    if executable:args['executable_path']=executable
    browser=pw.chromium.launch(**args)
    try:
        page=browser.new_page()
        for size in [(320,720),(390,844),(1440,900)]:
            page.set_viewport_size({'width':size[0],'height':size[1]})
            for route in ROUTES:
                page.set_content(render(route),wait_until='load')
                audit=page.evaluate(AUDIT_JS)
                results['named_controls_checked']+=audit['controls']
                results['duplicate_ids']+=len(audit['duplicates'])
                results['unnamed_controls']+=len([x for x in audit['problems'] if x.startswith('unnamed:')])
                assert not audit['duplicates'],(size,route,'duplicate ids',audit['duplicates'])
                assert not audit['problems'],(size,route,'a11y semantics',audit['problems'])
                assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth'),(size,route,'horizontal overflow')
                if size[0]==320:
                    page.add_style_tag(content=TEXT_SPACING)
                    if page.evaluate('document.documentElement.scrollWidth > window.innerWidth'):
                        results['text_spacing_overflows']+=1
                        results['issues'].append({'route':route,'problem':'horizontal overflow with WCAG text-spacing override'})
                results['viewport_checks']+=1
        assert results['text_spacing_overflows']==0,results['issues']
        # Explicit audit of keyboard-accessible jump link.
        page.set_viewport_size({'width':1440,'height':900})
        page.set_content(render('index.html'),wait_until='load')
        page.keyboard.press('Tab')
        assert page.locator('.skip').evaluate('(e)=>e===document.activeElement')
        page.keyboard.press('Enter')
        assert page.locator('main#main').evaluate('(e)=>e===document.activeElement'), 'skip target must receive focus'
    finally:
        browser.close()
(OUT/'accessibility-regressions.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('PASS accessibility DOM regression:',json.dumps(results,sort_keys=True))
