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
  // Zero-network site discovery. Search index is public, deterministic and embedded by the builder.
  const siteSearch=qs('#site-search'),searchToggle=qs('#search-toggle'),searchClose=qs('#search-close');
  const searchBox=qs('#site-search-query'),searchResults=qs('#site-search-results'),searchFeedback=qs('#site-search-feedback');
  const searchIndex=qs('#site-search-index');
  if(siteSearch&&searchToggle&&searchBox&&searchResults&&searchFeedback&&searchIndex){
    const pages=JSON.parse(searchIndex.textContent);
    const normalized=text=>text.toLocaleLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'');
    const score=(page,words)=>{
      const title=normalized(page.title),summary=normalized(page.description),path=normalized(page.url);
      let points=0;
      for(const word of words){
        const value=(title.includes(word)?5:0)+(path.includes(word)?2:0)+(summary.includes(word)?1:0);
        if(!value)return 0;
        points+=value;
      }
      return points;
    };
    const draw=()=>{
      searchResults.replaceChildren();
      const query=normalized(searchBox.value.trim());
      if(!query){searchFeedback.textContent='Type to search public MUSITU pages.';return;}
      const words=query.split(/\s+/).filter(Boolean).slice(0,7);
      const matching=pages.map(page=>({page,rank:score(page,words)})).filter(entry=>entry.rank>0)
        .sort((a,b)=>b.rank-a.rank||a.page.title.localeCompare(b.page.title)).slice(0,8);
      searchFeedback.textContent=matching.length?`${matching.length} matching page${matching.length===1?'':'s'}.`:'No matching pages. Try another word or browse Products.';
      const fragment=document.createDocumentFragment();
      for(const entry of matching){
        const item=document.createElement('a');item.href=entry.page.url;item.className='search-result';
        const title=document.createElement('strong');title.textContent=entry.page.title;
        const summary=document.createElement('span');summary.textContent=entry.page.description;
        item.append(title,summary);
        const listItem=document.createElement('li');listItem.append(item);fragment.append(listItem);
      }
      searchResults.append(fragment);
    };
    const show=()=>{if(siteSearch.open)return;siteSearch.showModal();searchBox.focus();draw();};
    const hide=()=>{if(siteSearch.open)siteSearch.close();};
    searchToggle.addEventListener('click',show);
    searchClose.addEventListener('click',hide);
    searchBox.addEventListener('input',draw);
    searchBox.addEventListener('keydown',event=>{
      if(event.key==='ArrowDown'){
        const first=qs('.search-result',searchResults);
        if(first){event.preventDefault();first.focus();}
      }
    });
    searchResults.addEventListener('keydown',event=>{
      if(event.key==='ArrowUp'){
        const first=qs('.search-result',searchResults);
        if(event.target===first){event.preventDefault();searchBox.focus();}
      }
    });
    // Native dialog Escape and backdrop behavior; restore focus to the trigger.
    siteSearch.addEventListener('click',e=>{if(e.target===siteSearch)hide();});
    // Search inputs may consume Escape to clear text: close the dialog on the first Escape.
    siteSearch.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();hide();}});
    siteSearch.addEventListener('close',()=>{searchToggle.focus();});
    document.addEventListener('keydown',event=>{
      const target=event.target;
      const editable=target instanceof HTMLElement&&(target.isContentEditable||['INPUT','TEXTAREA','SELECT'].includes(target.tagName));
      if((event.key.toLowerCase()==='k'&&(event.ctrlKey||event.metaKey))||(event.key==='/'&&!editable&&!event.ctrlKey&&!event.metaKey&&!event.altKey)){
        event.preventDefault();show();
      }
    });
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
