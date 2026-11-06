/* MUSITU corporate site: no external requests, no inference, no telemetry. */
(()=>{'use strict';
  document.documentElement.classList.add('has-js');
  const data=window.MUSITU_PUBLIC||{families:[],evidence:[],routes:[]};
  const $=(s,root=document)=>root.querySelector(s);
  const $$=(s,root=document)=>Array.from(root.querySelectorAll(s));
  const safe=(fn)=>{try{return fn()}catch(_){return null}};
  const getFamily=id=>data.families.find(x=>x.id===id);
  const escapeSet=(el,value)=>{if(el)el.textContent=value==null?'':String(value)};
  // Theme is a tab-scoped preference only. Missing/blocked storage never blocks display.
  const readTheme=safe(()=>sessionStorage.getItem('musitu_corporate_theme_v1'));
  if(readTheme==='light'||readTheme==='dark')document.documentElement.dataset.theme=readTheme;
  $$('.theme-button').forEach(b=>b.addEventListener('click',()=>{
    const next=document.documentElement.dataset.theme==='dark'?'light':'dark';
    document.documentElement.dataset.theme=next;
    safe(()=>sessionStorage.setItem('musitu_corporate_theme_v1',next));
    $$('.theme-button').forEach(x=>x.setAttribute('aria-label','Switch to '+(next==='dark'?'light':'dark')+' theme'));
  }));
  // Native details still works with JavaScript disabled. Close other menus on new selection.
  $$('.nav-group').forEach(item=>item.addEventListener('toggle',()=>{
    if(item.open)$$('.nav-group').filter(x=>x!==item).forEach(x=>x.open=false);
  }));
  document.addEventListener('click',e=>{
    if(!e.target.closest('.desktop-nav'))$$('.nav-group').forEach(x=>x.open=false);
    if(!e.target.closest('.mobile-menu')){const m=$('.mobile-menu');if(m)m.open=false;}
  });
  // Dialog focus returns to exactly the control that opened it.
  const opener=new WeakMap();
  const showDialog=(d,source)=>{if(!d)return;opener.set(d,source||document.activeElement);if(typeof d.showModal==='function'){d.showModal();}else d.setAttribute('open','');const input=$('input',d);const close=$('.dialog-close',d);(input||close)?.focus();};
  $$('[data-open]').forEach(b=>b.addEventListener('click',()=>showDialog(document.getElementById(b.dataset.open),b)));
  $$('.modal').forEach(d=>{
    $('.dialog-close',d)?.addEventListener('click',()=>d.close());
    d.addEventListener('close',()=>opener.get(d)?.focus());
    d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}});
  });
  document.addEventListener('keydown',e=>{
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();const d=$('#search-dialog');if(d.open){d.close();return;}showDialog(d,$('.search-open'));}
  });
  // Local page search with a fully server-rendered index; no network fetch.
  const search=$('#site-search-input');const results=$('#site-search-results');const count=$('#search-count');
  if(search&&results){
    const all=$$('.search-result',results);
    const apply=()=>{const q=search.value.trim().toLowerCase().slice(0,120);const tokens=q.split(/\s+/).filter(Boolean);
      let n=0;all.forEach(x=>{const hay=x.dataset.search||'';const show=tokens.every(t=>hay.includes(t));x.hidden=!show;if(show)n++;});
      escapeSet(count,n+' of '+all.length+' pages'+(n===0?' · Try another term':''));
    };
    search.addEventListener('input',apply);apply();
    search.addEventListener('keydown',e=>{if(e.key==='ArrowDown'){const first=all.find(x=>!x.hidden);if(first){e.preventDefault();first.focus();}}});
    results.addEventListener('keydown',e=>{if(e.key!=='ArrowDown'&&e.key!=='ArrowUp')return;const visible=all.filter(x=>!x.hidden);let idx=visible.indexOf(document.activeElement);if(idx===-1)return;e.preventDefault();idx+=(e.key==='ArrowDown'?1:-1);if(idx<0){search.focus();return;}visible[Math.min(idx,visible.length-1)]?.focus();});
  }
  // Consistent Escape dismissal, including browser search inputs that otherwise consume Escape.
  document.addEventListener('keydown',e=>{
    if(e.key!=='Escape')return;
    const open=$$('.modal').find(x=>x.open);
    if(open){e.preventDefault();open.close();}
  },true);
  // Goal-based Navigator. Uses approved public facts and explicit reasons, no user profiling.
  $$('[data-navigator]').forEach(n=>{
    $$('[data-goal]',n).forEach(b=>b.addEventListener('click',()=>{
      const f=getFamily(b.dataset.goal);if(!f)return;
      $$('[data-goal]',n).forEach(el=>el.setAttribute('aria-pressed',String(el===b)));
      escapeSet($('[data-goal-title]',n),f.name);
      escapeSet($('[data-goal-description]',n),f.intro);
      const link=$('[data-goal-link]',n);if(link)link.href=f.path;
    }));
  });
  // Portfolio catalog, including empty result and reset.
  const catalog=$('#catalog-items');const cq=$('#catalog-query');const cf=$('#catalog-filter');
  if(catalog&&cq&&cf){const items=$$('[data-catalog-item]',catalog);const ccount=$('#catalog-count');const empty=$('#catalog-empty');
    const apply=()=>{const text=cq.value.toLowerCase().trim();const tokens=text.split(/\s+/).filter(Boolean);let n=0;
      items.forEach(el=>{let ok=(cf.value==='all'||cf.value===el.dataset.category)&&tokens.every(t=>(el.dataset.search||'').includes(t));el.hidden=!ok;if(ok)n++;});
      escapeSet(ccount,n+' of '+items.length+' families');if(empty)empty.hidden=n>0;
    };
    cq.addEventListener('input',apply);cf.addEventListener('change',apply);$('#catalog-reset')?.addEventListener('click',()=>{cq.value='';cf.value='all';apply();cq.focus();});apply();
  }
  // Product comparison uses actual documented family attributes and enforces 3 selections.
  const comparePanel=$('#compare-panel');
  if(comparePanel){
    const selection=[];const out=$('#compare-output');const status=$('#compare-status');
    function redraw(){
      $$('[data-compare]').forEach(b=>{const on=selection.includes(b.dataset.compare);b.setAttribute('aria-pressed',String(on));b.textContent=on?'✓ Comparing':'+ Compare';});
      escapeSet(status,selection.length?selection.length+' of 3 selected. Click a selected family to remove it.':'Select up to three families for a structured comparison.');
      out.replaceChildren();
      if(selection.length<2)return;
      const table=document.createElement('table');table.className='compare-table';
      const caption=document.createElement('caption');caption.textContent='Comparison of documented MUSITU product families';table.appendChild(caption);
      const head=document.createElement('thead');const hr=document.createElement('tr');const corner=document.createElement('th');corner.scope='col';corner.textContent='Property';hr.appendChild(corner);
      selection.forEach(id=>{const th=document.createElement('th');th.scope='col';th.textContent=getFamily(id)?.name||id;hr.appendChild(th);});head.appendChild(hr);table.appendChild(head);
      const body=document.createElement('tbody');
      [['Focus','category'],['Purpose','intro'],['Evidence','evidence'],['Limits','limits']].forEach(([label,key])=>{const tr=document.createElement('tr');const th=document.createElement('th');th.scope='row';th.textContent=label;tr.appendChild(th);selection.forEach(id=>{const td=document.createElement('td');td.textContent=getFamily(id)?.[key]||'Not documented';tr.appendChild(td);});body.appendChild(tr);});
      table.appendChild(body);const wrap=document.createElement('div');wrap.className='compare-table-scroll';wrap.appendChild(table);out.appendChild(wrap);
    }
    $$('[data-compare]').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.compare;const i=selection.indexOf(id);if(i>=0)selection.splice(i,1);else if(selection.length<3)selection.push(id);else{escapeSet(status,'Maximum three families. Remove one before adding another.');return;}redraw();}));redraw();
  }
  // Atlas: selection updates public copy; the connections are conceptual, never operational telemetry.
  $$('[data-atlas-component]').forEach(atlas=>{
    $$('[data-atlas]',atlas).forEach(node=>node.addEventListener('click',()=>{
      const f=getFamily(node.dataset.atlas);if(!f)return;
      $$('[data-atlas]',atlas).forEach(n=>n.setAttribute('aria-pressed',String(node===n)));
      escapeSet($('[data-atlas-title]',atlas),f.name);escapeSet($('[data-atlas-desc]',atlas),f.intro);escapeSet($('[data-atlas-note]',atlas),f.evidence);
      const link=$('[data-atlas-link]',atlas);if(link)link.href=f.path;
    }));
  });
  // Evidence Lens: only approved static records, no HTML insertion of source text.
  $$('.evidence-open').forEach(button=>button.addEventListener('click',()=>{
    const rec=data.evidence.find(x=>x.id===button.dataset.evidence);if(!rec)return;
    const holder=$('#evidence-dialog-content');if(!holder)return;holder.replaceChildren();
    const h=document.createElement('h3');h.textContent=rec.title;holder.appendChild(h);
    const dl=document.createElement('dl');holder.appendChild(dl);
    [['Associated technology',rec.family],['Evidence type',rec.kind],['Reviewed',rec.date],['Public claim',rec.claim],['What was established',rec.establishes],['What was not established',rec.limits]].forEach(([label,value])=>{
      const dt=document.createElement('dt');dt.textContent=label;const dd=document.createElement('dd');dd.textContent=value;dl.append(dt,dd);
    });
    const allowed=data.routes.some(p=>p.path===rec.link)||['https://evansmusitu.github.io/','https://payments.mftintelligence.com/chemistry/releases'].includes(rec.link);
    if(allowed){const link=document.createElement('a');link.className='text-link';link.textContent='Read related public information ↗';link.href=rec.link;if(rec.link.startsWith('https://')){link.rel='noopener noreferrer';link.target='_blank';}holder.appendChild(link);}
    showDialog($('#evidence-dialog'),button);
  }));
  // Lab deterministic arithmetic: no remote request, no claim that it invokes Axiom.
  const rate=$('#npv-rate'), inv=$('#npv-investment'), flow=$('#npv-flow');
  if(rate&&inv&&flow){const update=()=>{
    const r=Math.max(0,Math.min(.3,Number(rate.value)/100));const i=Math.max(0,Number(inv.value)||0);const c=Math.max(0,Number(flow.value)||0);
    const npv=-i+[1,2,3].reduce((sum,t)=>sum+c/Math.pow(1+r,t),0);
    escapeSet($('#npv-rate-output'),rate.value+'%');escapeSet($('#npv-result'),new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2}).format(npv));
  };[rate,inv,flow].forEach(x=>x.addEventListener('input',update));update();}
  // Chemistry learning concept. Illustrative-only; not connected to the app.
  $$('[data-chemistry]').forEach(el=>$$('[data-cell]',el).forEach(b=>b.addEventListener('click',()=>{
    const gal=b.dataset.cell==='galvanic';$$('[data-cell]',el).forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
    escapeSet($('#cell-title',el),gal?'Galvanic cell':'Electrolytic cell');
    escapeSet($('#cell-desc',el),gal?'In a galvanic cell, the anode is negative. Oxidation releases electrons at the anode; a spontaneous reaction drives the circuit.':'In an electrolytic cell, the anode is positive. An external power source drives the nonspontaneous reaction, and oxidation still occurs at the anode.');
  })));
  // Optional Ask MUSITU: intentionally a local guide until AI backend/operator/provider gates are met.
  const form=$('#ask-local-form');const input=$('#ask-local-input');const output=$('#ask-local-result');
  if(form&&input&&output){const stop=new Set(['what','does','do','can','how','i','is','the','a','an','and','or','about','me','to','of','are','for','please','tell','with','musitu']);
    function find(question){const q=question.trim().toLowerCase().slice(0,200);const tokens=q.split(/[^a-z0-9]+/).filter(t=>t.length>=2&&!stop.has(t));
      const matches=(data.routes||[]).map(page=>{
        const text=(page.title+' '+page.headline+' '+page.lead+' '+page.path).toLowerCase();
        const score=tokens.reduce((s,t)=>s+(text.includes(t)?1:0)+(page.title.toLowerCase().includes(t)?2:0),0);return{page,score};
      }).filter(x=>x.score>0).sort((a,b)=>b.score-a.score).slice(0,5);
      output.replaceChildren();const lead=document.createElement('p');lead.textContent=matches.length?'Local guide: these approved site pages may help. This is not an AI-generated answer.':'No confident local match. Try the full website search or the Products Overview.';output.appendChild(lead);
      if(matches.length){const ul=document.createElement('ul');matches.forEach(({page})=>{const li=document.createElement('li');const a=document.createElement('a');a.href=page.path;a.textContent=page.title;li.appendChild(a);ul.appendChild(li);});output.appendChild(ul);}
    }
    form.addEventListener('submit',e=>{e.preventDefault();find(input.value);});
    $$('[data-suggestion]').forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.suggestion;find(input.value);input.focus();}));
  }
})();
