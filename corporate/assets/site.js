/* MUSITU corporate shell: no analytics, storage, remote requests or third-party dependencies. */
(()=>{
  'use strict';
  document.documentElement.classList.add('has-js');
  const qs=(s,root=document)=>root.querySelector(s);
  const qsa=(s,root=document)=>Array.from(root.querySelectorAll(s));
  const themeBtn=qs('#theme-toggle');
  const menuBtn=qs('#menu-toggle');
  const mobile=qs('#mobile-nav');
  if(themeBtn){
    const preference=window.matchMedia('(prefers-color-scheme: light)');
    // This tab-scoped visual preference contains no identity or user content.
    const themeKey='musitu_corporate_theme_v1';
    let storedTheme=null;
    try{storedTheme=window.sessionStorage.getItem(themeKey);}catch(_){/* unavailable storage is fine */}
    let explicitChoice=storedTheme==='light'||storedTheme==='dark';
    const setTheme=(next)=>{
      document.documentElement.dataset.theme=next;
      themeBtn.setAttribute('aria-label',`Switch to ${next==='dark'?'light':'dark'} mode`);
      themeBtn.setAttribute('aria-pressed',String(next==='light'));
      themeBtn.title=`Switch to ${next==='dark'?'light':'dark'} mode`;
      const bar=qs('meta[name="theme-color"]');
      if(bar)bar.content=next==='light'?'#f4f7fd':'#090e1b';
    };
    setTheme(explicitChoice?storedTheme:(preference.matches?'light':'dark'));
    themeBtn.addEventListener('click',()=>{
      explicitChoice=true;
      const next=document.documentElement.dataset.theme==='dark'?'light':'dark';
      setTheme(next);
      try{window.sessionStorage.setItem(themeKey,next);}catch(_){/* preference is optional */}
    });
    preference.addEventListener('change',event=>{
      if(!explicitChoice)setTheme(event.matches?'light':'dark');
    });
  }
  if(menuBtn&&mobile){
    const close=()=>{
      mobile.hidden=true;
      menuBtn.setAttribute('aria-expanded','false');
      menuBtn.setAttribute('aria-label','Open navigation');
    };
    menuBtn.addEventListener('click',()=>{
      const open=menuBtn.getAttribute('aria-expanded')==='true';
      mobile.hidden=open;
      menuBtn.setAttribute('aria-expanded',String(!open));
      menuBtn.setAttribute('aria-label',open?'Open navigation':'Close navigation');
      if(!open){const first=qs('a',mobile);if(first)first.focus();}
    });
    mobile.addEventListener('click',e=>{if(e.target.closest('a'))close();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!mobile.hidden){close();menuBtn.focus();}});
    window.matchMedia('(min-width:821px)').addEventListener('change',event=>{if(event.matches)close();});
  }
  const normalizedPath=location.pathname.replace(/\/?$/,'/');
  for(const a of qsa('.primary-nav a,.mobile-nav a')){
    if(a.getAttribute('href')===normalizedPath)a.setAttribute('aria-current','page');
  }
  const evidenceDialog=qs('#evidence-dialog'), evidenceRegistry=qs('#evidence-registry');
  if(evidenceDialog&&evidenceRegistry){
    const data=JSON.parse(evidenceRegistry.textContent);
    let trigger=null;
    document.addEventListener('click',event=>{
      const btn=event.target.closest('[data-evidence]');
      if(!btn||!data[btn.dataset.evidence])return;
      trigger=btn;
      const rec=data[btn.dataset.evidence];
      qs('#evidence-title').textContent=rec.name;
      qs('#evidence-maturity').textContent=rec.maturity;
      qs('#evidence-limits').textContent=rec.limits;
      qs('#evidence-reviewed').textContent=rec.reviewed+' (source review, not certification)';
      const url=qs('#evidence-source'); url.href=rec.url; url.textContent=rec.proof+' ↗';
      evidenceDialog.showModal();
      qs('#evidence-close').focus();
    });
    const close=()=>{if(evidenceDialog.open)evidenceDialog.close();};
    evidenceDialog.addEventListener('cancel',event=>{event.preventDefault();close();});
    qs('#evidence-close').addEventListener('click',close);
    evidenceDialog.addEventListener('click',event=>{if(event.target===evidenceDialog)close();});
    evidenceDialog.addEventListener('close',()=>{if(trigger)requestAnimationFrame(()=>trigger.focus());});
  }
  const search=qs('#catalog-query'),category=qs('#catalog-category'),state=qs('#catalog-state');
  const count=qs('#catalog-count'),empty=qs('#catalog-empty');
  if(search&&category&&state){
    const cards=qsa('#catalog-grid [data-product-card]');
    const apply=()=>{
      const query=search.value.trim().toLocaleLowerCase();
      let visible=0;
      for(const card of cards){
        const ok=card.dataset.search.includes(query)&&(category.value==='all'||card.dataset.category===category.value)&&(state.value==='all'||card.dataset.state===state.value);
        card.hidden=!ok;
        if(ok)visible++;
      }
      if(count)count.textContent=`Showing ${visible} of ${cards.length} product families`;
      if(empty)empty.hidden=visible!==0;
    };
    search.addEventListener('input',apply);
    category.addEventListener('change',apply);
    state.addEventListener('change',apply);
    apply();
  }
})();
