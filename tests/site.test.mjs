import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const html=readFileSync('index.html','utf8');
const get=(pattern)=>html.match(pattern)?.[1];
assert.match(html,/<!doctype html>/i,'HTML document required');
assert.match(html,/<meta name="viewport"/,'Mobile viewport required');
assert.match(html,/<main id="main">/,'Main landmark required');
assert.match(html,/<nav[^>]+aria-label=/,'Accessible navigation required');
assert.match(html,/class="skip"/,'Keyboard skip link required');
assert.match(html,/@media\(max-width:750px\)/,'Mobile layout breakpoint required');
assert.match(html, /prefers-reduced-motion/,'Reduced motion support required');
for(const id of ['product-grid','product-search','run-demo','goal-input','copy-plan','theme-toggle','menu-toggle','demo-result','toast','product-modal','detail-title','detail-close']){
  assert.match(html,new RegExp('id="'+id+'"'),'Missing interactive element: '+id);
}
for(const name of ['MUSITU Axiom','MUSITU Education','MUSITU Frontier Market Intelligence','MUSITU Foundry','MUSITU Markets','MUSITU WorldFabric']){
  assert.ok(html.includes(name),'Missing canonical product: '+name);
}
for(const filter of ['intelligence','education','markets','infrastructure']){
  assert.ok(html.includes('data-filter="'+filter+'"'),'Missing filter: '+filter);
}
assert.match(html,/illustration, not a connection to a deployed AI service/,'Demo honesty statement required');
assert.match(html,/data-product=/,'Product detail entry buttons required');
assert.match(html,/modal.showModal\(\)/,'Interactive product dialog required');
assert.match(html,/escapeHtml\(p.name\)/,'Product HTML escaping required');
const script=get(/<script>([\s\S]*?)<\/script>/);
assert.ok(script,'Script required');
new vm.Script(script,{filename:'index-inline.js'});
assert.doesNotMatch(html,/<script[^>]+src="https?:/,'Unexpected remote script');
console.log('PASS: Site structure, canonical branding, interaction hooks, accessibility and JS syntax');
