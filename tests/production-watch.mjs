/**
 * No-model-inference synthetic production monitor.
 * Checks published website, browser CORS, input validation and deterministic calculator.
 * DOES NOT call text/image inference: a healthy GET is not proof model inference is available.
 */
import assert from 'node:assert/strict';
import { appendFile } from 'node:fs/promises';

const SITE = 'https://evansmusitu.github.io';
const HOME = SITE + '/';
const EDGE = 'https://musitu-intelligence-edge-20261019.mft-education-nexus-93f395f5.workers.dev';
const results = [];
const started = new Date().toISOString();
const output = process.env.GITHUB_STEP_SUMMARY || '';
const retryDelay = ms => new Promise(resolve => setTimeout(resolve,ms));

async function fetchWithRetry(url, init = {}, maxAttempts = 3) {
  let lastFailure;
  for (let attempt=1; attempt<=maxAttempts; attempt++) {
    try {
      const requestUrl = url + (url.includes('?') ? '&' : '?') + 'musitu_watch=' + Date.now() + '_' + attempt;
      const response = await fetch(requestUrl, {
        ...init, redirect:'follow',
        signal: AbortSignal.timeout(15000),
        headers: { 'cache-control': 'no-cache', ...(init.headers || {}) }
      });
      if (response.status < 500 || attempt === maxAttempts) return response;
      lastFailure = new Error('HTTP '+response.status);
    } catch (failure) { lastFailure = failure; }
    if (attempt < maxAttempts) await retryDelay(1100 * attempt);
  }
  throw lastFailure ?? new Error('Network request failed');
}
async function check(label, run) {
  const start=performance.now();
  try {
    const detail=await run();
    const ms=Math.round(performance.now()-start);
    results.push({label,status:'PASS',ms,detail:detail || ''});
    console.log('PASS',label,'duration',ms+'ms',detail || '');
  } catch(failure) {
    const ms=Math.round(performance.now()-start);
    const reason=failure instanceof Error ? failure.message : String(failure);
    results.push({label,status:'FAIL',ms,detail:reason.slice(0,240)});
    console.error('FAIL',label,'duration',ms+'ms',reason);
  }
}
async function jsonPost(path,input,origin=SITE) {
  return fetchWithRetry(EDGE+path, {
    method:'POST',
    headers: {
      'content-type':'application/json',
      ...(origin === null ? {} : { origin })
    },
    body:JSON.stringify(input)
  },1);
}
const paths=['/api/chat','/api/calculate','/api/image'];

await check('Public homepage and AI launcher',async()=>{
  const response=await fetchWithRetry(HOME);
  assert.equal(response.status,200);
  assert.match(response.headers.get('content-type') || '',/text\/html/i);
  const html=await response.text();
  for(const item of ['id="ai-dialog"','assets/musitu-edge-chat.js','assets/musitu-edge-chat.css','data-edge-mode="deep"','data-edge-mode="research"','data-edge-mode="image"','data-edge-mode="document"','id="edge-document-file"']) {
    assert.ok(html.includes(item),'Missing site capability: '+item);
  }
  return 'page '+html.length+' chars';
});
await check('Published JS and backend URL alignment',async()=>{
  const response=await fetchWithRetry(HOME+'assets/musitu-edge-chat.js');
  assert.equal(response.status,200);
  const js=await response.text();
  for(const term of [EDGE,'/api/chat','/api/calculate','/api/image','research','AbortController']) {
    assert.ok(js.includes(term),'Missing client capability: '+term);
  }
  return 'script '+js.length+' chars';
});
await check('Published responsive AI stylesheet',async()=>{
  const response=await fetchWithRetry(HOME+'assets/musitu-edge-chat.css');
  assert.equal(response.status,200);
  const css=await response.text();
  for(const rule of ['.edge-thread','.edge-message','.edge-form']) {
    assert.ok(css.includes(rule),'Missing interface style: '+rule);
  }
  return 'stylesheet '+css.length+' chars';
});
for (const [label,path,marker,minLength] of [
  ['Local PDF/DOCX extractor','assets/musitu-document-extract.mjs','extractDocumentText',3000],
  ['Self-hosted PDF.js browser module','assets/vendor/pdf.mjs','getDocument',100000],
  ['Self-hosted PDF.js worker','assets/vendor/pdf.worker.mjs',null,100000],
  ['Self-hosted Word document parser','assets/vendor/mammoth.browser.min.js',null,100000]
]) {
  await check('Published '+label,async()=>{
    const response=await fetchWithRetry(HOME+path);
    assert.equal(response.status,200);
    assert.match(response.headers.get('content-type')||'',/javascript|text\/plain|octet-stream/i);
    const code=await response.text();
    assert.ok(code.length>=minLength,'Extracted library unexpectedly small or missing');
    if(marker)assert.ok(code.includes(marker),'Missing expected parser function');
    return 'asset '+code.length+' chars; no user files transmitted';
  });
}
if(process.env.GITHUB_EVENT_NAME!=='pull_request') {
for(const [name,path,marker] of [
  ['Encrypted local vault','assets/musitu-workspace-vault.mjs','encryptWorkspace'],
  ['Local workspace interface','assets/musitu-workspace-ui.mjs','attachWorkspaceControls']
]) {
  await check(name+' is published',async()=>{
    const response=await fetchWithRetry(HOME+path);
    assert.equal(response.status,200);
    const body=await response.text();
    assert.ok(body.length>3000 && body.includes(marker),'Local workspace module was missing or incomplete');
    return 'module '+body.length+' chars; no model inference';
  });
}
}
else console.log('PR watch: new static workspace modules are tested by CI and checked on production only after merge.');
if (process.env.GITHUB_EVENT_NAME !== 'pull_request') {
  await check('Published offline evidence retrieval module',async()=>{
    const response=await fetchWithRetry(HOME+'assets/musitu-local-evidence.mjs');
    assert.equal(response.status,200);
    const body=await response.text();
    assert.ok(body.includes('rankEvidence') && body.includes('BM25') && body.length>3000);
    return 'self-hosted offline retrieval '+body.length+' chars';
  });
}
await check('Cloudflare backend advertised capabilities',async()=>{
  const response=await fetchWithRetry(EDGE+'/api/health',{headers:{origin:SITE}});
  assert.equal(response.status,200);
  assert.match(response.headers.get('content-type') || '',/application\/json/i);
  assert.equal(response.headers.get('access-control-allow-origin'),SITE);
  assert.equal(response.headers.get('cache-control'),'no-store');
  const health=await response.json();
  assert.equal(health.service,'MUSITU Intelligence Edge');
  assert.equal(health.status,'ok');
  assert.equal(health.curatedLiveSources,true);
  assert.equal(health.availableModels.standard,'@cf/meta/llama-3.1-8b-instruct-fp8');
  assert.equal(health.availableModels.deeperAnalysis,'@cf/qwen/qwen3-30b-a3b-fp8');
  for(const tool of ['calculator','image','research','document','multidocument']) {
    assert.ok(health.tools.some(t=>t.id===tool),'Backend missing tool '+tool);
  }
  assert.match(health.rateLimit.scope,/location/i);
  assert.equal(health.tools.find(x=>x.id==='document').maxExcerptCharacters,4800);
  assert.equal(health.tools.find(x=>x.id==='multidocument').maximumDocuments,3);
  assert.equal(health.tools.find(x=>x.id==='multidocument').maxCombinedExcerptCharacters,4800);
  return 'service metadata available; inference intentionally not tested';
});
for(const path of paths) {
  await check('Authorized CORS preflight '+path,async()=>{
    const response=await fetchWithRetry(EDGE+path,{
      method:'OPTIONS',
      headers:{
        origin:SITE,
        'access-control-request-method':'POST',
        'access-control-request-headers':'content-type'
      }
    },1);
    assert.equal(response.status,204);
    assert.equal(response.headers.get('access-control-allow-origin'),SITE);
    assert.match(response.headers.get('access-control-allow-methods') || '',/POST/);
    return '204; same-origin browser requests permitted';
  });
}
for(const path of paths) {
  await check('Disallowed browser origins rejected '+path,async()=>{
    for(const origin of [null,'https://untrusted.example']) {
      const response=await jsonPost(path,{prompt:'Test rejection before any inference.',expression:'40+2'},origin);
      assert.equal(response.status,403);
      const data=await response.json();
      assert.equal(data.code,'ORIGIN_DENIED');
      assert.equal(response.headers.get('access-control-allow-origin'),null);
    }
    return '403; no inference requested';
  });
}
await check('Deterministic calculation, no LLM call',async()=>{
  const response=await jsonPost('/api/calculate',{expression:'(12+9)*2'});
  assert.equal(response.status,200);
  const result=await response.json();
  assert.equal(result.tool,'calculator');
  assert.equal(result.result,42);
  assert.equal(result.exact,false);
  assert.equal(result.verifiedBy,'deterministic parser v1');
  return '42; deterministic floating-point parser';
});
await check('Calculator denies invalid expression safely',async()=>{
  const response=await jsonPost('/api/calculate',{expression:'process.exit()'});
  assert.equal(response.status,400);
  assert.equal((await response.json()).code,'CALCULATION_INVALID');
  return '400; arbitrary code cannot execute';
});
await check('Image endpoint rejects malformed requests before inference',async()=>{
  const response=await jsonPost('/api/image',{prompt:'short'});
  assert.equal(response.status,400);
  assert.equal((await response.json()).code,'INVALID_IMAGE_PROMPT');
  return '400; zero image inference';
});
await check('Multi-document mode rejects absent sources without model inference',async()=>{
 const response=await jsonPost('/api/chat',{mode:'compare',prompt:'Compare the reported switching thresholds in these reports.',documents:[]});
 assert.equal(response.status,400);
 assert.equal((await response.json()).code,'INVALID_DOCUMENT_COLLECTION');
 return '400; no model inference';
});
await check('Multi-document mode rejects unsupported source names before inference',async()=>{
 const response=await jsonPost('/api/chat',{
   mode:'compare',prompt:'Compare these two excerpts without any external data.',
   documents:[
    {fileName:'one.pdf',excerpt:'The first report contains a measurement of six volts.'},
    {fileName:'malware.exe',excerpt:'The second report contains a measurement of eight volts.'}
   ]
 });
 assert.equal(response.status,400);
 assert.equal((await response.json()).code,'INVALID_DOCUMENT_NAME');
 return '400; no external code or AI inference';
});
await check('Document mode rejects absent text before inference',async()=>{
  const response=await jsonPost('/api/chat',{mode:'document',prompt:'Summarize this selected text.',fileName:'my_notes.txt'});
  assert.equal(response.status,400);
  assert.equal((await response.json()).code,'INVALID_DOCUMENT_EXCERPT');
  return '400; no document text sent and no inference';
});
await check('Document mode rejects binary text before inference',async()=>{
  const response=await jsonPost('/api/chat',{mode:'document',prompt:'Summarize this selected text.',fileName:'my_notes.txt',excerpt:'Random binary content'+String.fromCharCode(0)+' and some follow-up text is rejected.'});
  assert.equal(response.status,400);
  assert.equal((await response.json()).code,'INVALID_DOCUMENT_EXCERPT');
  return '400; invalid text refused before model inference';
});
await check('Chat endpoint rejects malformed requests before inference',async()=>{
  const response=await jsonPost('/api/chat',{mode:'research',prompt:'short'});
  assert.equal(response.status,400);
  assert.equal((await response.json()).code,'INVALID_INPUT');
  return '400; zero model inference';
});

const failed=results.filter(x=>x.status==='FAIL');
const safe = value => String(value).replace(/\|/g,'\\|').replace(/[\r\n]/g,' ').slice(0,250);
const summary = [
  '## MUSITU live production watch',
  '',
  '**Run:** '+started+' UTC · **Result:** '+(failed.length===0?'PASS':'FAIL')+' · **No AI inference:** no model generation calls were made; standard Worker requests still count as usage.',
  '',
  '| Live capability | Result | Duration | Detail |',
  '|---|---|---:|---|',
  ...results.map(x=>'| '+safe(x.label)+' | '+(x.status==='PASS'?'✅ PASS':'❌ FAIL')+' | '+x.ms+' ms | '+safe(x.detail)+' |'),
  '',
  '> Scope: connectivity, published assets, CORS, public capability metadata, and deterministic input handling. This monitor **cannot prove** text/image inference is available, that the website meets WCAG, or that AI answers are accurate.',
  ''
].join('\n');
if(output) await appendFile(output,summary+'\n','utf8');
console.log('WATCH SUMMARY',results.length-failed.length,'passed /',results.length,'checks',started);
assert.equal(failed.length,0,failed.length+' independent production checks failed: '+failed.map(x=>x.label).join('; '));
