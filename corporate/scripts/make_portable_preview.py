"""Create an all-in-one offline review preview; no change to the production build."""
import json,re,sys
from pathlib import Path
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]
dist=root/'dist'
home=(dist/'index.html').read_text()
pages={}
for p in sorted(dist.rglob('index.html')):
    path=str(p.relative_to(dist).parent).replace('\\','/')
    if path=='.':path=''
    soup=BeautifulSoup(p.read_text(), 'html.parser')
    pages['/'+path+('/' if path else '')]={'main':str(soup.find('main')),'title':soup.title.text,'description':soup.find('meta',attrs={'name':'description'})['content']}
css=(root/'assets/site.css').read_text()
js=(root/'assets/site.js').read_text()
router=r'''
/* Portable, zero-network preview: no changes to source deployment or live browser storage. */
(()=>{
 const data=JSON.parse(document.getElementById('portable-routes').textContent);
 function pathFromHash(){
  if(!location.hash.startsWith('#!'))return '/';
  try{return decodeURIComponent(location.hash.slice(2))}catch{return '/'}
 }
 function bindCatalog(){
  const query=document.getElementById('catalog-query'),category=document.getElementById('catalog-category'),state=document.getElementById('catalog-state');
  if(!query||!category||!state)return;
  const cards=Array.from(document.querySelectorAll('#catalog-grid [data-product-card]'));
  const count=document.getElementById('catalog-count'),empty=document.getElementById('catalog-empty');
  const apply=()=>{
   let n=0;const q=query.value.trim().toLocaleLowerCase();
   for(const card of cards){const shown=card.dataset.search.includes(q)&&(category.value==='all'||category.value===card.dataset.category)&&(state.value==='all'||state.value===card.dataset.state);card.hidden=!shown;if(shown)n++;}
   count.textContent=`Showing ${n} of ${cards.length} product families`;empty.hidden=n!==0;
  };
  query.addEventListener('input',apply);category.addEventListener('change',apply);state.addEventListener('change',apply);apply();
 }
 function render(){
  const route=pathFromHash(); const entry=data[route]||data['/404/'];
  document.getElementById('main').outerHTML=entry.main;
  document.title=entry.title+' · Portable preview';
  const desc=document.querySelector('meta[name="description"]');if(desc)desc.content=entry.description;
  document.querySelectorAll('a[aria-current="page"]').forEach(a=>a.removeAttribute('aria-current'));
  document.querySelectorAll('.primary-nav a,.mobile-nav a').forEach(a=>{if(a.getAttribute('href')===route)a.setAttribute('aria-current','page')});
  document.getElementById('mobile-nav').hidden=true;
  document.getElementById('menu-toggle').setAttribute('aria-expanded','false');
  document.getElementById('menu-toggle').setAttribute('aria-label','Open navigation');
  bindCatalog();
  window.scrollTo({top:0,behavior:'instant'});
 }
 document.addEventListener('click',e=>{
   const a=e.target.closest('a[href]');if(!a||e.defaultPrevented||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||a.target)return;
   const url=a.getAttribute('href');
   if(url.startsWith('#') && !url.startsWith('#!')){
     const target=document.getElementById(url.slice(1));if(target){e.preventDefault();target.scrollIntoView();}
     return;
   }
   if(url.startsWith('/') && !url.startsWith('//')){
     const path=url.split('#')[0]; if(!data[path] && path!=='/')return;
     e.preventDefault();
     if(pathFromHash()===path)render();else location.hash='!'+encodeURIComponent(path);
   }
 });
 window.addEventListener('hashchange',render);
 if(location.hash.startsWith('#!'))render();
})();
'''
# The portable single-file artifact must intentionally relax the production CSP
# because its CSS and scripts are inlined for offline review. It is NOT deployable.
home=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>',
            '<!-- PORTABLE REVIEW ONLY: CSP omitted; never serve this file as production -->',home)
# Move all styles and JS inline to make it portable.
home=home.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+css+'</style>')
home=home.replace('<script defer src="/assets/site.js"></script>','')
registry=json.dumps(pages,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
home=home.replace('</body></html>','<script type="application/json" id="portable-routes">'+registry+'</script><script>'+js+'\n'+router+'</script></body></html>')
out=Path(sys.argv[1]) if len(sys.argv)>1 else (root/'review-artifacts'/'MUSITU_portable_interactive_preview.html')
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(home,encoding='utf-8')
print(f'Portable HTML preview: {out.stat().st_size} bytes, {len(pages)} navigable routes; no network dependencies.')
