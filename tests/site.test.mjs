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
for(const id of ['product-grid','product-search','run-demo','goal-input','copy-plan','theme-toggle','menu-toggle','demo-result','toast','product-modal','detail-title','detail-close','ai-studio','launch-ai','ai-dialog','ai-close','edge-thread','edge-input','edge-alert','edge-health','edge-send','edge-export']){
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
assert.match(html,/assets\/musitu-edge-chat\.js/,'Direct AI client must load');
assert.match(html,/assets\/musitu-edge-chat\.css/,'AI interface styles must load');
assert.match(html,/accept="[^"]*\.pdf,[^"]*\.docx/,'PDF and DOCX supported by local file input');
assert.match(html,/comparisons send up to 1,500 per file/,'Multi-document per-file privacy limit disclosure required');
assert.match(html,/id="edge-workspace"/,'Encrypted workspace controls required');
assert.match(html,/id="edge-document-evidence-export"/,'Local evidence export control required');
assert.match(html,/Exported evidence is NOT encrypted/,'Plaintext evidence export warning required');
assert.match(html,/id="edge-workspace-slot"/,'Five-slot workspace selector required');
assert.match(html,/Workspace 1 preserves your existing saved conversation/,'Legacy vault compatibility must be communicated');
const slotsModule=readFileSync('assets/musitu-workspace-slots.mjs','utf8');
assert.match(slotsModule,/WORKSPACE_SLOT_COUNT=5/,'Five isolated vault slots required');
assert.match(slotsModule,/VAULT_KEY/,'Original workspace slot must remain accessible');
assert.match(html,/id="edge-workspace-passphrase" type="password"/,'Passphrase input must be masked');
assert.match(html,/manual save only/,'Do not imply automatic cloud backups');
const vaultModule=readFileSync('assets/musitu-workspace-vault.mjs','utf8');
assert.match(vaultModule,/AES-GCM/,'Authenticated encryption required');
assert.match(vaultModule,/310000/,'Local PBKDF2 key stretching required');
assert.doesNotMatch(vaultModule,/fetch\(/,'Vault module must not initiate network requests');

assert.match(html,/maximum 4,500 combined/,'Aggregate excerpt privacy bound required');
assert.match(html,/type="file" multiple accept=/,'Multi-document local selection required');
assert.match(html,/id="edge-document-preview"/,'Offline source preview button required');
assert.match(html,/id="edge-document-evidence-preview"/,'Offline source inspection region required');
const evidenceModule=readFileSync('assets/musitu-local-evidence.mjs','utf8');
assert.match(evidenceModule,/rankEvidence/,'Keyword retrieval must be installed');
assert.doesNotMatch(evidenceModule,/fetch\(/,'Local evidence ranking must not fetch data');
const documentModule=readFileSync('assets/musitu-document-extract.mjs','utf8');
assert.match(documentModule,/checkZipSafety/,'DOCX ZIP safety preflight required');
assert.match(documentModule,/MAX_PAGES=20/,'Page bounds required');
assert.match(documentModule,/mammoth\.extractRawText/,'DOCX only extracts text, never HTML');
assert.doesNotMatch(html,/ai-frame/,'Legacy iframe must not be used for primary AI');
const edgeClient = readFileSync('assets/musitu-edge-chat.js', 'utf8');
new vm.Script(edgeClient, { filename: 'musitu-edge-chat.js' });
assert.match(edgeClient,/musitu-intelligence-edge-20261019/,'Cloudflare edge backend URL required');
assert.match(edgeClient,/textContent = text/,'Model content must be escaped');
assert.match(edgeClient,/AbortController/,'AI requests must have timeouts');
assert.match(html,/escapeHtml\(p.name\)/,'Product HTML escaping required');
const script=get(/<script>([\s\S]*?)<\/script>/);
assert.ok(script,'Script required');
new vm.Script(script,{filename:'index-inline.js'});
assert.doesNotMatch(html,/<script[^>]+src="https?:/,'Unexpected remote script');

const publishingWorkflow=readFileSync('.github/workflows/musitu-website-pages.yml','utf8');
const pagesArtifactName='musitu-pages-' + '${{ github.run_id }}' + '-' + '${{ github.run_attempt }}';
assert.ok(publishingWorkflow.includes('name: '+pagesArtifactName),
  'The Pages upload must uniquely name its artifact for the workflow run and attempt.');
assert.ok(publishingWorkflow.includes('artifact_name: '+pagesArtifactName),
  'Pages deployment must select the matching unique per-attempt artifact.');

console.log('PASS: Site structure, canonical branding, interaction hooks, accessibility and JS syntax');

assert.match(html,/id="edge-document-verify"/,'Original-file verification action required');
assert.match(html,/id="edge-document-verify-status"/,'Local hash verification status required');
for(const id of ['edge-document-receipt-export','edge-document-receipt-verify','edge-document-receipt-file'])
  assert.ok(html.includes('id="'+id+'"'),'Missing portable source receipt control: '+id);
const receiptModule=readFileSync('assets/musitu-portable-receipt.mjs','utf8');
assert.ok(!receiptModule.includes('fetch('),'Portable receipt must operate entirely offline');
assert.match(receiptModule,/verifyLocalFile/,'Portable verifier must hash and compare source bytes');
for(const id of ['edge-document-chain-save','edge-document-chain-verify','edge-document-chain-file']){
  assert.ok(html.includes('id="'+id+'"'),'Missing evidence-chain control '+id);
}
const chainSource=readFileSync('assets/musitu-evidence-replay.mjs','utf8');
assert.ok(!chainSource.includes('fetch('),'Chain replay must perform no remote requests');
assert.match(chainSource,/rankEvidence/,'Reproducible chain must independently rerank passages');
assert.match(chainSource,/verifyLocalFile/,'Chain replay must first match original source bytes');
const integrityClient=readFileSync('assets/musitu-edge-chat.js','utf8');
assert.match(integrityClient,/verifyLocalFile/,'Original-byte verifier must be wired to user action');
assert.match(integrityClient,/sourceIntegrity/,'Original-file evidence provenance must be retained locally');

const pagesRelease=readFileSync('.github/workflows/musitu-website-pages.yml','utf8');
assert.match(pagesRelease,/cp assets\/musitu-source-integrity\.mjs _site\/assets\/musitu-source-integrity\.mjs/,'Production Pages must bundle integrity verifier');
assert.match(pagesRelease,/cp assets\/musitu-portable-receipt\.mjs _site\/assets\/musitu-portable-receipt\.mjs/,'Production must package portable receipt verifier');
assert.ok(pagesRelease.includes('cp assets/musitu-evidence-replay.mjs _site/assets/musitu-evidence-replay.mjs'),'Production must package independent evidence-chain replay');
