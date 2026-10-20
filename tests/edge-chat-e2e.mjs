import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright';
import { PDFDocument, StandardFonts } from 'pdf-lib';
import JSZip from 'jszip';

const browser = await chromium.launch({ headless: true });
const origin = 'https://evansmusitu.github.io';
const worker = 'https://musitu-intelligence-edge-20261019.mft-education-nexus-93f395f5.workers.dev';
const errors = [];

async function launch(width, height) {
  const page = await browser.newPage({ viewport: {width,height} });
  page.on('pageerror', e => errors.push(e.message));
  await page.route(origin + '/**', async route => {
    const pathname = new URL(route.request().url()).pathname;
    let path = 'index.html', type = 'text/html';
    if (pathname === '/assets/musitu-edge-chat.js') { path = 'assets/musitu-edge-chat.js'; type = 'application/javascript'; }
    else if (pathname === '/assets/musitu-edge-chat.css') { path = 'assets/musitu-edge-chat.css'; type = 'text/css'; }
    else if (pathname === '/assets/musitu-document-extract.mjs') { path = 'assets/musitu-document-extract.mjs'; type = 'application/javascript'; }
    else if (pathname === '/assets/musitu-local-evidence.mjs') { path = 'assets/musitu-local-evidence.mjs'; type = 'application/javascript'; }
    else if (pathname === '/assets/musitu-evidence-pack.mjs') { path = 'assets/musitu-evidence-pack.mjs'; type = 'application/javascript'; }
    else if (pathname === '/assets/musitu-source-integrity.mjs') { path = 'assets/musitu-source-integrity.mjs'; type = 'application/javascript'; }
    else if (pathname === '/assets/musitu-portable-receipt.mjs') { path = 'assets/musitu-portable-receipt.mjs'; type = 'application/javascript'; }
    else if (pathname === '/assets/musitu-workspace-vault.mjs') { path = 'assets/musitu-workspace-vault.mjs'; type = 'application/javascript'; }
    else if (pathname === '/assets/musitu-workspace-ui.mjs') { path = 'assets/musitu-workspace-ui.mjs'; type = 'application/javascript'; }
    else if (pathname === '/assets/musitu-workspace-slots.mjs') { path = 'assets/musitu-workspace-slots.mjs'; type = 'application/javascript'; }
    else if (pathname.startsWith('/assets/vendor/')) {
      path = pathname.slice(1);
      type = 'application/javascript';
    }
    await route.fulfill({ status:200, contentType:type, body:readFileSync(path) });
  });
  await page.goto(origin+'/', {waitUntil:'domcontentloaded',timeout:30000});
  return page;
}

try {
  const health = await fetch(worker + '/api/health', { signal:AbortSignal.timeout(20000) });
  assert.equal(health.status,200,'Cloudflare Worker must be healthy');

  const page = await launch(1280,900);
  await page.locator('#product-search').fill('education');
  assert.equal(await page.locator('#product-grid .product').count(),1,'Search should filter products');
  await page.locator('#product-search').fill('');
  await page.locator('#launch-ai').click();
  await page.locator('#ai-dialog[open]').waitFor({timeout:10000});
  assert.ok(await page.locator('#edge-input').isVisible(),'Native AI input must be visible');
  assert.equal(await page.locator('#ai-frame').count(),0,'Legacy iframe must be absent');
  await page.locator('#edge-send').click();
  await page.locator('#edge-alert').waitFor({state:'visible'});
  assert.match(await page.locator('#edge-alert').innerText(),/10 and 900/,'Invalid questions must be rejected before HTTP request');

  await page.locator('[data-edge-mode="learn"]').click();
  assert.equal(await page.locator('[data-edge-mode="learn"]').getAttribute('aria-pressed'),'true');
  const prompt = 'Explain why feedback control systems are useful, with a practical example for a student.';
  await page.locator('#edge-input').fill(prompt);
  await page.locator('#edge-send').click();
  await page.locator('.edge-message.assistant').waitFor({timeout:80000});
  const reply = await page.locator('.edge-message.assistant').innerText();
  assert.ok(reply.length>70,'AI must provide a substantive generated response');
  assert.match(reply.toLowerCase(),/feedback|control|system|sensor|output|loop/,'Response must be relevant');
  assert.equal(await page.locator('#edge-export').isDisabled(),false,'Conversation should be exportable');
  console.log('MUSITU EDGE PRODUCTION INFERENCE PASS, answer characters:',reply.length);
  console.log('Excerpt:',reply.slice(0,200));

  // Deterministic visual QA of Markdown, safety and interactive checklist.
  // This route is mocked to avoid extra AI inference charges.
  await page.route(worker + '/api/chat', async route => {
    const cors = {
      'access-control-allow-origin': origin,
      'access-control-allow-methods': 'POST,OPTIONS',
      'access-control-allow-headers': 'content-type'
    };
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({ status:204, headers:cors });
      return;
    }
    await route.fulfill({
      status:200,
      contentType:'application/json',
      headers:cors,
      body:JSON.stringify({
        mode:'build',
        reply:'## Build plan\n1. **Define the project scope** with clear acceptance criteria.\n2. **Test the most important flow** with real users.\n\nNever execute <script>window.__musituInjected=1</script> or paste untrusted code.',
        model:'test-fixture',liveSearch:false
      })
    });
  });
  await page.locator('#edge-input').fill('Help me create a two-step plan to validate a digital product before launch.');
  await page.locator('#edge-send').click();
  const formatted=page.locator('.edge-message.assistant').nth(1);
  await formatted.waitFor({timeout:15000});
  assert.equal(await formatted.locator('.edge-rich h4').count(),1,'Markdown heading should render');
  assert.equal(await formatted.locator('.edge-rich ol li').count(),2,'Numbered points should render as semantic list');
  assert.equal(await formatted.locator('.edge-rich strong').count(),2,'Emphasis should become semantic strong nodes');
  assert.equal(await formatted.locator('.edge-rich script').count(),0,'Model-provided HTML must not be executed');
  assert.equal(await page.evaluate(() => window.__musituInjected),undefined,'Injected script must not run');

  await formatted.getByRole('button',{name:'Make checklist'}).click();
  const board=formatted.locator('.edge-action-board');
  assert.ok(await board.isVisible(),'AI action checklist must be visible');
  assert.equal(await board.getByRole('checkbox').count(),2,'Checklist has two extracted steps');
  await board.getByRole('checkbox').first().check();
  assert.match(await board.locator('.edge-board-progress').innerText(),/1 of 2 checked/,'Checklist progress updates');
  await formatted.getByRole('button',{name:'Hide checklist'}).click();
  assert.equal(await board.isVisible(),false,'Checklist can be collapsed');
  await formatted.getByRole('button',{name:'Show checklist'}).click();
  assert.ok(await board.isVisible(),'Checklist can be reopened');
  assert.match(await board.locator('.edge-board-progress').innerText(),/1 of 2 checked/,'State survives collapsing the checklist');
  console.log('SAFE RICH ANSWERS + ACTION CHECKLIST QA PASS');

  // The real second model is qualified by the Cloudflare canary suite.
  // Test client mode routing with a deterministic response to avoid duplicate paid inference.
  await page.unroute(worker + '/api/chat');
  let deepModeRequested = false;
  await page.route(worker + '/api/chat', async route => {
    const request = route.request();
    if (request.method() === 'OPTIONS') {
      await route.fulfill({status:204,headers:{'access-control-allow-origin':origin,'access-control-allow-methods':'POST,OPTIONS','access-control-allow-headers':'content-type'}});
      return;
    }
    const data = request.postDataJSON();
    deepModeRequested = data.mode === 'deep';
    await route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':origin},body:JSON.stringify({mode:'deep',model:'@cf/qwen/qwen3-30b-a3b-fp8',reply:'A measured technical conclusion with assumptions and verification steps.'})});
  });
  await page.locator('[data-edge-mode="deep"]').click();
  assert.equal(await page.locator('[data-edge-mode="deep"]').getAttribute('aria-pressed'),'true');
  await page.locator('#edge-input').fill('Explain the tradeoffs of two database architectures with testing recommendations.');
  await page.locator('#edge-send').click();
  await page.getByText('REASONING MODEL RESPONDED').waitFor({timeout:12000});
  assert.equal(deepModeRequested,true,'UI must request actual deep model route');
  assert.match(await page.locator('.edge-message.assistant').last().innerText(),/technical conclusion/);

  let expressionSent = null;
  await page.route(worker + '/api/calculate', async route => {
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({status:204,headers:{'access-control-allow-origin':origin,'access-control-allow-methods':'POST,OPTIONS','access-control-allow-headers':'content-type'}});
      return;
    }
    expressionSent = route.request().postDataJSON().expression;
    await route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':origin},body:JSON.stringify({tool:'calculator',expression:expressionSent,result:36,numericType:'IEEE-754 double precision',verifiedBy:'deterministic parser v1',exact:false})});
  });
  await page.locator('[data-edge-mode="calculator"]').click();
  assert.equal(await page.locator('#edge-input').getAttribute('maxlength'),'140');
  assert.ok(await page.locator('#edge-calculator-presets').isVisible());
  await page.locator('[data-calc-expression="(8+4)*sqrt(9)"]').click();
  assert.equal(await page.locator('#edge-input').inputValue(),'(8+4)*sqrt(9)');
  await page.locator('#edge-send').click();
  await page.getByText('VERIFIED CALCULATION').waitFor({timeout:12000});
  assert.equal(expressionSent,'(8+4)*sqrt(9)','Client must invoke deterministic math tool');
  assert.match(await page.locator('.edge-message.tool').last().innerText(),/Result:\s*36/);
  assert.match(await page.locator('.edge-message.tool').last().innerText(),/approximate, not exact/);
  console.log('REASONING MODE + DETERMINISTIC CALCULATOR UI PASS');
  // Natural arithmetic in an ordinary AI mode is also verified by the same safe calculator.
  let sawToolPayload = false;
  await page.route(worker + '/api/chat', async route => {
    if (route.request().method() === 'OPTIONS') {
      await route.fulfill({status:204,headers:{
        'access-control-allow-origin':origin,'access-control-allow-methods':'POST,OPTIONS',
        'access-control-allow-headers':'content-type'
      }});
      return;
    }
    const posted=route.request().postDataJSON();
    if (posted.prompt === '40+2') {
      sawToolPayload = true;
      await route.fulfill({status:200,contentType:'application/json',
        headers:{'access-control-allow-origin':origin},
        body:JSON.stringify({reply:'**Deterministically verified arithmetic**\\nResult: 42',
          toolUsed:'deterministic_calculator',result:42,model:null,mode:posted.mode,liveSearch:false})});
    } else {
      assert.equal(posted.history.some(item => item.content.includes('40+2')),false,
        'Calculator output must not pollute model conversation memory');
      await route.fulfill({status:200,contentType:'application/json',
        headers:{'access-control-allow-origin':origin},
        body:JSON.stringify({reply:'A clear plan starts by identifying the user problem.',mode:posted.mode,model:'mock',liveSearch:false})});
    }
  });
  await page.locator('[data-edge-mode="explore"]').click();
  await page.locator('#edge-input').fill('40+2');
  await page.locator('#edge-send').click();
  await page.getByText('VERIFIED COMPUTATION · NO MODEL').waitFor({timeout:12000});
  assert.ok(sawToolPayload,'Short arithmetic must pass client validation');
  const verified=page.locator('.edge-message.tool').last();
  assert.match(await verified.innerText(),/42/);
  assert.match(await verified.locator('.edge-message-title').innerText(),/VERIFIED COMPUTATION/);
  await page.locator('#edge-input').fill('Explain two key testing steps before launching a website.');
  await page.locator('#edge-send').click();
  await page.locator('.edge-message.assistant').last().getByText('A clear plan starts').waitFor({timeout:12000});
  console.log('AUTO-ROUTED VERIFIED ARITHMETIC + UNCONTAMINATED CHAT QA PASS');
  // Prevent extra inference expense while verifying the new UI against realistic response shapes.
  let generatedImagePrompt=null;
  await page.route(worker + '/api/image',async route=>{
    if(route.request().method()==='OPTIONS'){
      await route.fulfill({status:204,headers:{'access-control-allow-origin':origin,'access-control-allow-methods':'POST,OPTIONS','access-control-allow-headers':'content-type'}});return;
    }
    generatedImagePrompt=route.request().postDataJSON().prompt;
    await route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':origin},
      body:JSON.stringify({tool:'image',model:'@cf/black-forest-labs/flux-1-schnell',prompt:generatedImagePrompt,
        image:'data:image/jpeg;base64,/9j/'+'A'.repeat(2400)})});
  });
  await page.locator('[data-edge-mode="image"]').click();
  assert.equal(await page.locator('#edge-input').getAttribute('maxlength'),'450');
  assert.match(await page.locator('#edge-input').getAttribute('placeholder'),/Describe an image/);
  const imagePrompt='A futuristic library above an African hillside under a bright purple moon.';
  await page.locator('#edge-input').fill(imagePrompt);
  await page.locator('#edge-send').click();
  await page.getByText('REAL AI IMAGE GENERATED').waitFor({timeout:15000});
  assert.equal(generatedImagePrompt,imagePrompt);
  const picture=page.locator('.edge-generated-figure img').last();
  assert.equal(await picture.count(),1,'Image preview element must be created. The mocked image bytes are not a valid photograph.');
  assert.match(await picture.getAttribute('src'),/^data:image\/jpeg;base64,/);
  assert.equal(await page.locator('.edge-generated-figure a[download="musitu-ai-image.jpg"]').count(),1);
  console.log('IMAGE PREVIEW + DOWNLOAD BROWSER QA PASSED');

  await page.unroute(worker + '/api/chat');
  let webQuery=null;
  await page.route(worker + '/api/chat',async route=>{
    if(route.request().method()==='OPTIONS'){
      await route.fulfill({status:204,headers:{'access-control-allow-origin':origin,'access-control-allow-methods':'POST,OPTIONS','access-control-allow-headers':'content-type'}});return;
    }
    webQuery=route.request().postDataJSON();
    await route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':origin},
      body:JSON.stringify({mode:'research',model:'@cf/meta/llama-3.1-8b-instruct-fp8',liveSearch:true,
        reply:'The source list describes the field [1]. An unsupported claim [unlinked reference] was not linked.',
        citationAudit:{status:'invalid-indices-removed',retrievedSourceCount:2,linkedSourceNumbers:[1],invalidSourceNumbersRemoved:[8],adjustedCitationGroups:1},
        sourceScope:'English Wikipedia and Hacker News only; NOT general web search',
        sources:[{title:'Quantum computing',url:'https://en.wikipedia.org/wiki/Quantum_computing',source:'Wikipedia',snippet:'Quantum computing overview'},
          {title:'Quantum discussion',url:'https://news.ycombinator.com/item?id=123456',source:'Hacker News',snippet:'Technology discussion'}]})});
  });
  await page.locator('[data-edge-mode="research"]').click();
  assert.equal(await page.locator('#edge-input').getAttribute('maxlength'),'180');
  await page.locator('#edge-input').fill('Research quantum computing for secondary-school education.');
  await page.locator('#edge-send').click();
  await page.getByText('REAL SOURCES RETRIEVED').waitFor({timeout:15000});
  assert.equal(webQuery.mode,'research');
  const sources=page.locator('.edge-message.assistant').last().locator('.edge-sources');
  assert.ok(await sources.isVisible());
  assert.equal(await sources.locator('.edge-source-row a').count(),2);
  assert.match(await sources.locator('.edge-source-row a').first().innerText(),/^\[1\] Quantum computing/,'Source number is mapped visibly to the source card');
  const audit=sources.locator('.edge-citation-report');
  assert.ok(await audit.isVisible(),'Research provenance audit is visible');
  assert.equal(await audit.getAttribute('data-status'),'warning','Unsupported source IDs must produce a caution state');
  assert.match(await audit.innerText(),/UNSUPPORTED REFERENCE NUMBERS REMOVED/);
  assert.match(await audit.innerText(),/Unlinked indices: 8/);
  assert.match(await audit.innerText(),/NOT fact-checked/,'Index validation must not be mistaken for factual verification');
  assert.equal(await sources.locator('a[target="_blank"][rel="noopener noreferrer"]').count(),2);
  assert.match(await sources.locator('.edge-source-note').innerText(),/NOT general web search/);
  console.log('CLICKABLE ATTRIBUTED WEB RESEARCH BROWSER QA PASSED');

  await page.unroute(worker + '/api/chat');
  let observedScholar=null;
  await page.route(worker + '/api/chat',async route=>{
    if(route.request().method()==='OPTIONS'){
      await route.fulfill({status:204,headers:{'access-control-allow-origin':origin,'access-control-allow-methods':'POST,OPTIONS','access-control-allow-headers':'content-type'}});return;
    }
    observedScholar=route.request().postDataJSON();
    await route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':origin},
      body:JSON.stringify({
        mode:'scholar',model:'@cf/meta/llama-3.1-8b-instruct-fp8',liveSearch:true,
        reply:'Crossref metadata identifies the following records [1], [2]. Their results were NOT independently checked.',
        sourceScope:'Crossref DOI registration metadata only. Not full text, peer-review verification, or a complete literature review.',
        sources:[
          {title:'Robotics learning evaluation',doi:'10.1234/robotics.2025',url:'https://doi.org/10.1234/robotics.2025',source:'Crossref',year:2025,workType:'journal-article',authors:['Jane Doe','Sam Ncube'],journal:'Teaching Review',snippet:'Published 2025 · Teaching Review · Authors: Jane Doe, Sam Ncube · DOI 10.1234/robotics.2025'},
          {title:'Feedback system design',doi:'10.5678/feedback.2024',url:'https://doi.org/10.5678/feedback.2024',source:'Crossref',year:2024,workType:'journal-article',authors:['Amina Ali'],journal:'Engineering Review',snippet:'Published 2024 · Engineering Review · Authors: Amina Ali · DOI 10.5678/feedback.2024'}
        ],
        citationAudit:{status:'indices-linked',retrievedSourceCount:2,linkedSourceNumbers:[1,2],invalidSourceNumbersRemoved:[],adjustedCitationGroups:0}
      })
    });
  });
  await page.locator('[data-edge-mode="scholar"]').click();
  assert.equal(await page.locator('[data-edge-mode="scholar"]').getAttribute('aria-pressed'),'true');
  assert.equal(await page.locator('#edge-input').getAttribute('maxlength'),'180');
  assert.match(await page.locator('#edge-input').getAttribute('placeholder'),/DOI-registered/);
  await page.locator('#edge-input').fill('robotics education');
  await page.locator('#edge-send').click();
  await page.getByText('SCHOLARLY DOI RECORDS RETRIEVED').waitFor({timeout:15000});
  assert.equal(observedScholar.mode,'scholar');
  const scholars=page.locator('.edge-message.assistant').last().locator('.edge-sources');
  assert.ok(await scholars.isVisible());
  assert.match(await scholars.locator('h4').innerText(),/CROSSREF/);
  assert.equal(await scholars.locator('.edge-source-row a').count(),2);
  assert.equal(await scholars.locator('a[href^="https://doi.org/"]').count(),2);
  assert.equal(await scholars.locator('.edge-citation-report').getAttribute('data-status'),'linked');
  assert.match(await scholars.locator('.edge-source-note').innerText(),/Not full text/);
  const save=scholars.getByRole('button',{name:'Download scholarly references as BibTeX'});
  assert.ok(await save.isVisible());
  const [bib]=await Promise.all([page.waitForEvent('download'),save.click()]);
  assert.equal(bib.suggestedFilename(),'musitu-scholar-references.bib');
  console.log('REAL DOI SOURCE LINKS + BIBTEX EXPORT BROWSER QA PASSED');

  // Deterministic private file-analysis QA: browser selects a relevant bounded excerpt.
  await page.unroute(worker + '/api/chat');
  let documentRequest=null;
  await page.route(worker + '/api/chat',async route=>{
    if(route.request().method()==='OPTIONS'){
      await route.fulfill({status:204,headers:{'access-control-allow-origin':origin,'access-control-allow-methods':'POST,OPTIONS','access-control-allow-headers':'content-type'}});return;
    }
    documentRequest=route.request().postDataJSON();
    await route.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':origin},
      body:JSON.stringify(documentRequest.mode==='compare'
        ? {reply:'Document one reports six volts [D1]. Document two reports eight volts [D2]. Unlinked [unlinked document].',
          mode:'compare',model:'@cf/meta/llama-3.1-8b-instruct-fp8',liveSearch:false,
          citationAudit:{status:'invalid-document-indices-removed',linkedSourceNumbers:[1,2],invalidSourceNumbersRemoved:[9],retrievedSourceCount:documentRequest.documents.length},
          documentReview:{comparedDocuments:documentRequest.documents.map((d,i)=>({label:'D'+(i+1),fileName:d.fileName,analyzedCharacters:d.excerpt.length})),analyzedCharacters:documentRequest.documents.reduce((sum,d)=>sum+d.excerpt.length,0),fullFileAnalyzed:false,storedOnServer:false,modelOutputMayBeInaccurate:true}}
        : {reply:'The selected excerpt says the upper hysteresis threshold is 6 volts. I cannot confirm details outside the excerpt.',
          mode:'document',model:'@cf/meta/llama-3.1-8b-instruct-fp8',liveSearch:false,
          documentReview:{fileName:documentRequest.fileName,analyzedCharacters:documentRequest.excerpt.length,fullFileAnalyzed:false,storedOnServer:false,modelOutputMayBeInaccurate:true}})
    });
  });
  await page.locator('[data-edge-mode="document"]').click();
  assert.ok(await page.locator('#edge-document-controls').isVisible());
  assert.match(await page.locator('#edge-input').getAttribute('placeholder'),/selected files/);
  await page.locator('#edge-input').fill('What is the upper hysteresis threshold according to the selected notes?');
  await page.locator('#edge-send').click();
  assert.match(await page.locator('#edge-alert').innerText(),/Choose 1–3 distinct files/);
  assert.equal(documentRequest,null,'No file may be transmitted before explicit selection');
  const localText='Background notes only.\n'+('This preliminary document covers several broad study topics.\n'.repeat(200))+
    '\nThe upper hysteresis threshold is exactly 6 volts in the experiment. Lower switching threshold was not specified.\n';
  await page.locator('#edge-document-file').setInputFiles({name:'notes.md',mimeType:'text/markdown',buffer:Buffer.from(localText,'utf8')});
  assert.match(await page.locator('#edge-document-info').innerText(),/1 selected: notes.md/);
  documentRequest=null;
  await page.locator('#edge-document-preview').click();
  const localPreview=page.locator('#edge-document-evidence-preview');
  await localPreview.waitFor({state:'visible',timeout:20000});
  assert.equal(documentRequest,null,'Local evidence preview must not send an AI request');
  const verifyOriginals=page.locator('#edge-document-verify');
  assert.ok(await verifyOriginals.isEnabled(),'Original-byte verification requires a successful preview');
  await verifyOriginals.click();
  await page.waitForFunction(()=>document.getElementById('edge-document-verify-status')?.textContent.includes('match this evidence preview'),{timeout:10000});
  assert.match(await page.locator('#edge-document-verify-status').innerText(),/match this evidence preview/);
  assert.match(await localPreview.innerText(),new RegExp(createHash('sha256').update(localText,'utf8').digest('hex')));
  assert.equal(documentRequest,null,'Local SHA-256 verification must never invoke external AI');
  assert.match(await localPreview.innerText(),/NO AI REQUEST/);
  assert.match(await localPreview.innerText(),/notes.md/);
  await localPreview.locator('details').first().locator('summary').click();
  assert.match(await localPreview.innerText(),/6 volts/,'Ranked first passage should find relevant deep document text');

  const localEvidenceExport=page.locator('#edge-document-evidence-export');
  assert.ok(await localEvidenceExport.isEnabled(),'Plaintext evidence export should require local preview first');
  const localEvidenceDownload=page.waitForEvent('download');
  await localEvidenceExport.click();
  const evidenceFile=await localEvidenceDownload;
  assert.equal(evidenceFile.suggestedFilename(),'musitu-local-evidence-pack.md');
  const evidenceText=readFileSync(await evidenceFile.path(),'utf8');
  assert.match(evidenceText,/MUSITU Local Document Evidence Pack/);
  assert.match(evidenceText,/Plaintext export/,'Privacy warning must be in the downloaded report');
  assert.match(evidenceText,/\[D1\] notes\\\.md/,'Source label must be included');
  assert.match(evidenceText,/upper hysteresis threshold/i);
  assert.match(evidenceText,/SHA-256 of selected text excerpt/);
  assert.ok(evidenceText.includes(createHash('sha256').update(localText,'utf8').digest('hex')),
    'Export must bind evidence to exact original local file bytes');
  assert.match(evidenceText,/[a-f0-9]{64}/,'SHA-256 fingerprint must be in the evidence pack');
  assert.ok(evidenceText.length<15000,'Export only bounded excerpt, not the entire input');
  assert.equal(documentRequest,null,'Local evidence preview and export must not make an AI call');
  const receiptDownloadEvent=page.waitForEvent('download');
  await page.locator('#edge-document-receipt-export').click();
  const receiptDownload=await receiptDownloadEvent;
  assert.equal(receiptDownload.suggestedFilename(),'musitu-source-fingerprint-receipt.json');
  const portableReceiptBytes=readFileSync(await receiptDownload.path());
  const portableReceipt=JSON.parse(portableReceiptBytes.toString('utf8'));
  assert.equal(portableReceipt.sources.length,1);
  assert.equal(portableReceipt.sources[0].name,'notes.md');
  assert.equal(portableReceipt.sources[0].sha256,createHash('sha256').update(localText,'utf8').digest('hex'));
  assert.ok(!portableReceiptBytes.toString('utf8').includes('hysteresis threshold'));
  assert.ok(!portableReceiptBytes.toString('utf8').includes(localText),'Portable receipt cannot contain private original content');
  await page.locator('#edge-document-receipt-file').setInputFiles({
    name:'musitu-source-fingerprint-receipt.json',mimeType:'application/json',buffer:portableReceiptBytes
  });
  await page.waitForFunction(()=>document.getElementById('edge-document-verify-status')?.textContent.includes('Saved receipt verified'));
  assert.match(await page.locator('#edge-document-verify-status').innerText(),/1 local original file match/);
  const forged={...portableReceipt,sources:[{...portableReceipt.sources[0],sha256:'0'.repeat(64)}]};
  await page.locator('#edge-document-receipt-file').setInputFiles({
    name:'musitu-source-fingerprint-receipt.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(forged))
  });
  await page.waitForFunction(()=>document.getElementById('edge-document-verify-status')?.textContent.includes('Saved receipt mismatch'));
  assert.match(await page.locator('#edge-document-verify-status').innerText(),/Original bytes are different/);
  assert.equal(documentRequest,null,'Portable verification must not transmit any bytes to the AI service');
  console.log('PORTABLE ORIGINAL-FILE RECEIPT SAVE/REPLAY/MISMATCH + ZERO AI REQUEST QA PASS');
  console.log('LOCAL EVIDENCE PACK DOWNLOAD + SHA-256 + ZERO AI REQUEST QA PASS');

  await page.locator('#edge-send').click();
  await page.getByText('SELECTED EXCERPT ANALYZED').waitFor({timeout:15000});
  assert.equal(documentRequest.mode,'document');
  assert.equal(documentRequest.fileName,'notes.md');
  assert.equal(documentRequest.history.length,0,'Document questions must be isolated from previous chat history');
  assert.ok(documentRequest.excerpt.length<=4800,'Never send the entire file or overlarge excerpt');
  assert.ok(documentRequest.excerpt.includes('6 volts'),'Relevant passage from later in document selected');
  assert.ok(documentRequest.excerpt.length<localText.length,'Only a bounded excerpt may be uploaded');
  assert.match(await page.locator('#edge-document-evidence-preview').innerText(),/EVIDENCE SELECTED FOR AI/);
  assert.match(await page.locator('.edge-message.assistant').last().innerText(),/full file was not analyzed/);
  assert.match(await page.locator('.edge-message.assistant').last().innerText(),/notes.md/);
  await page.locator('#edge-document-clear').click();
  assert.equal(await page.locator('#edge-document-file').inputValue(),'');
  assert.match(await page.locator('#edge-document-info').innerText(),/Selection cleared/);
  console.log('PRIVATE TEXT DOCUMENT EXCERPT + NO FILE STORAGE BROWSER QA PASS');

  // Real PDF.js: create an actual selectable-text PDF locally and verify only
  // the extracted excerpt is sent to the already-mocked AI endpoint.
  const pdf=await PDFDocument.create();
  const font=await pdf.embedFont(StandardFonts.Helvetica);
  const pdfPage=pdf.addPage([612,792]);
  pdfPage.drawText('Physics robotics experiment: upper hysteresis threshold is 6 volts.',{
    x:40,y:720,size:14,font
  });
  pdfPage.drawText('The sensor and relay are part of the feedback control loop.',{
    x:40,y:695,size:12,font
  });
  pdfPage.drawText('The complete lab report is not provided here.',{
    x:40,y:675,size:12,font
  });
  const pdfBytes=Buffer.from(await pdf.save());
  documentRequest=null;
  await page.locator('#edge-document-file').setInputFiles({
    name:'robotics_notes.pdf',mimeType:'application/pdf',buffer:pdfBytes
  });
  assert.match(await page.locator('#edge-document-info').innerText(),/1 selected: robotics_notes.pdf/);
  await page.locator('#edge-input').fill('What is the hysteresis threshold in this PDF robotics experiment?');
  const pdfRequest=page.waitForResponse(
    response => response.url()===worker+'/api/chat' && response.request().method()==='POST',
    {timeout:25000}
  );
  await page.locator('#edge-send').click();
  await pdfRequest;
  assert.equal(documentRequest.fileName,'robotics_notes.pdf','PDF file must be analyzed by existing document endpoint');
  assert.ok(documentRequest.excerpt.includes('hysteresis threshold'),'Actual PDF text extraction required');
  assert.ok(documentRequest.excerpt.includes('6 volts'),'Selected PDF text must reach the model');
  assert.ok(documentRequest.excerpt.length<=4800,'PDF extracted excerpt must be bounded');
  console.log('REAL PDF.js SELECTABLE PDF LOCAL PARSING QA PASS');

  // Real Mammoth browser parser: build a minimal valid Office OpenXML DOCX.
  const zip=new JSZip();
  zip.file('[Content_Types].xml',
    '<?xml version="1.0" encoding="utf-8"?>' +
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
    '<Default Extension="xml" ContentType="application/xml"/>' +
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>' +
    '</Types>');
  zip.folder('_rels').file('.rels',
    '<?xml version="1.0" encoding="utf-8"?>' +
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>' +
    '</Relationships>');
  zip.folder('word').file('document.xml',
    '<?xml version="1.0" encoding="utf-8"?>' +
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">' +
    '<w:body><w:p><w:r><w:t>Word robotics experiment documented an LDR sensor and servo actuator.</w:t></w:r></w:p>' +
    '<w:p><w:r><w:t>The experimental lower Schmitt trigger threshold is 3 volts.</w:t></w:r></w:p>' +
    '<w:p><w:r><w:t>No results were recorded beyond these notes.</w:t></w:r></w:p>' +
    '</w:body></w:document>');
  const docxBytes=await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE'});
  documentRequest=null;
  await page.locator('#edge-document-file').setInputFiles({
    name:'robotics_notes.docx',
    mimeType:'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    buffer:docxBytes
  });
  await page.locator('#edge-input').fill('What does this Word document state about the lower Schmitt trigger threshold?');
  const docxRequest=page.waitForResponse(
    response => response.url()===worker+'/api/chat' && response.request().method()==='POST',
    {timeout:25000}
  );
  await page.locator('#edge-send').click();
  await docxRequest;
  assert.equal(documentRequest.fileName,'robotics_notes.docx');
  assert.ok(documentRequest.excerpt.includes('3 volts'),'Actual DOCX extraction must include the paragraph');
  assert.ok(documentRequest.excerpt.includes('Schmitt trigger'),'DOCX text should include the correct topic');
  assert.ok(documentRequest.excerpt.length<=4800);
  console.log('REAL Mammoth DOCX LOCAL TEXT PARSING QA PASS');

  // Invalid and scanned PDF: must fail with a clear explanation and no HTTP
  // transmission of user file bytes.
  documentRequest=null;
  await page.locator('#edge-document-file').setInputFiles({
    name:'damaged.pdf',mimeType:'application/pdf',
    buffer:Buffer.from('%PDF-not-a-valid-document-but-padding-padding-padding')
  });
  await page.locator('#edge-input').fill('Please analyze the damaged PDF source file.');
  await page.locator('#edge-send').click();
  await page.locator('#edge-alert').waitFor({state:'visible'});
  assert.match(await page.locator('#edge-alert').innerText(),/Unable to extract selectable PDF text|Invalid PDF signature/);
  assert.equal(documentRequest,null,'Damaged PDF must never trigger an AI request');
  await page.locator('#edge-document-clear').click();





  // Image-only PDF: reject without claiming OCR or sending an empty excerpt.
  const scanned=await PDFDocument.create();
  scanned.addPage([612,792]);
  documentRequest=null;
  await page.locator('#edge-document-file').setInputFiles({
    name:'image_only.pdf',mimeType:'application/pdf',buffer:Buffer.from(await scanned.save())
  });
  await page.locator('#edge-input').fill('Can you summarize this image-only scanned PDF file?');
  await page.locator('#edge-send').click();
  await page.locator('#edge-alert').waitFor({state:'visible'});
  assert.match(await page.locator('#edge-alert').innerText(),/Scanned\/image-only PDFs need OCR/);
  assert.equal(documentRequest,null,'Image-only PDF must not send a model request without OCR');

  // Bound page counts independently of file size.
  const longPdf=await PDFDocument.create();
  for(let index=0;index<21;index++){
    const pg=longPdf.addPage([400,400]);
    pg.drawText('Page '+(index+1)+' of this oversized sample.',{x:35,y:340,size:13});
  }
  documentRequest=null;
  await page.locator('#edge-document-file').setInputFiles({
    name:'too_many_pages.pdf',mimeType:'application/pdf',buffer:Buffer.from(await longPdf.save())
  });
  await page.locator('#edge-input').fill('Give a summary of every page of this long PDF file.');
  await page.locator('#edge-send').click();
  await page.locator('#edge-alert').waitFor({state:'visible'});
  assert.match(await page.locator('#edge-alert').innerText(),/PDF exceeds 20 pages/);
  assert.equal(documentRequest,null,'Overlong PDF must not reach the model');

  // ZIP-bomb preflight: tiny compressed DOCX with unsafe uncompressed entry.
  const bomb=new JSZip();
  bomb.file('[Content_Types].xml','<Types/>');
  bomb.file('word/document.xml','x'.repeat(2400000));
  const compressedBomb=await bomb.generateAsync({type:'nodebuffer',compression:'DEFLATE',compressionOptions:{level:9}});
  assert.ok(compressedBomb.length<1048576,'Fixture must fit DOCX compressed-size bound');
  documentRequest=null;
  await page.locator('#edge-document-file').setInputFiles({
    name:'compressed_bomb.docx',
    mimeType:'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    buffer:compressedBomb
  });
  await page.locator('#edge-input').fill('Can you extract this Word file and explain it?');
  await page.locator('#edge-send').click();
  await page.locator('#edge-alert').waitFor({state:'visible'});
  assert.match(await page.locator('#edge-alert').innerText(),/unsafe ZIP data|expansion limit/);
  assert.equal(documentRequest,null,'DOCX ZIP expansion bomb must not reach the model');
  await page.locator('#edge-document-clear').click();
  console.log('SCANNED PDF + PAGE-COUNT + DOCX ZIP BOMB REJECTION QA PASS');

  // Real browser multi-file selection and bounded source-annotated comparison.
  documentRequest=null;
  await page.locator('#edge-document-file').setInputFiles([
    {name:'lab_first.txt',mimeType:'text/plain',buffer:Buffer.from('Laboratory A notes: upper switching threshold was measured as six volts. The sensor was calibrated before testing.','utf8')},
    {name:'lab_second.md',mimeType:'text/markdown',buffer:Buffer.from('Laboratory B notes: upper switching threshold was measured as eight volts. No calibration evidence was given in this excerpt.','utf8')}
  ]);
  assert.match(await page.locator('#edge-document-info').innerText(),/2 selected:/);
  await page.locator('#edge-input').fill('Compare the two experiments: which threshold was higher and which source documented calibration?');
  documentRequest=null;
  await page.locator('#edge-document-preview').click();
  await page.locator('#edge-document-evidence-preview').waitFor({state:'visible',timeout:20000});
  assert.equal(documentRequest,null,'Two-document preview must not send AI request');
  assert.equal(await page.locator('#edge-document-evidence-preview .edge-local-evidence-source').count(),2);

  const compareReceived=page.waitForResponse(response=>response.url()===worker+'/api/chat'&&response.request().method()==='POST',{timeout:20000});
  await page.locator('#edge-send').click();
  await compareReceived;
  assert.equal(documentRequest.mode,'compare','Two files must opt in to comparison mode');
  assert.equal(documentRequest.history.length,0,'Comparisons must not send previous chat history');
  assert.equal(documentRequest.documents.length,2);
  assert.equal(documentRequest.documents[0].fileName,'lab_first.txt');
  assert.equal(documentRequest.documents[1].fileName,'lab_second.md');
  assert.ok(documentRequest.documents.every(d=>d.excerpt.length<=1500),'Each file sends at most 1,500 characters');
  assert.ok(documentRequest.documents.reduce((sum,d)=>sum+d.excerpt.length,0)<=4800);
  const compared=page.locator('.edge-message.assistant').last();
  const evidence=compared.locator('.edge-document-evidence');
  await evidence.waitFor({timeout:13000});
  assert.equal(await evidence.locator('li').count(),2);
  assert.match(await evidence.innerText(),/\[D1\] lab_first.txt/);
  assert.match(await evidence.innerText(),/\[D2\] lab_second.md/);
  assert.match(await evidence.innerText(),/Unsupported document citations removed: 9/);
  assert.match(await compared.innerText(),/full file was not analyzed/);
  console.log('TWO-DOCUMENT BOUNDED SOURCE COMPARISON + EVIDENCE LABEL UI QA PASS');

  // Three files are accepted; a fourth is rejected before network/model use.
  documentRequest=null;
  await page.locator('#edge-document-file').setInputFiles([
    {name:'first.txt',mimeType:'text/plain',buffer:Buffer.from('One valid study report excerpt contains a measured threshold of six volts and feedback conditions.','utf8')},
    {name:'second.txt',mimeType:'text/plain',buffer:Buffer.from('The second valid report excerpt compares threshold conditions at eight volts.','utf8')},
    {name:'third.txt',mimeType:'text/plain',buffer:Buffer.from('The third valid report excerpt contains calibration checks and monitoring data.','utf8')},
    {name:'fourth.txt',mimeType:'text/plain',buffer:Buffer.from('A fourth document must not be accepted by this application.','utf8')}
  ]);
  await page.locator('#edge-input').fill('Compare the switching threshold from all four reports.');
  await page.locator('#edge-send').click();
  await page.locator('#edge-alert').waitFor({state:'visible'});
  assert.match(await page.locator('#edge-alert').innerText(),/Choose 1–3 distinct files/);
  assert.equal(documentRequest,null,'Fourth file must not trigger an AI request');
  await page.locator('#edge-document-clear').click();



  page.on('dialog', async d => d.accept());
  // Opt-in encrypted local workspace: no plaintext session in localStorage.
  const panel=page.locator('#edge-workspace');
  await panel.locator('summary').click();
  const secret=page.locator('#edge-workspace-passphrase');
  await page.locator('#edge-workspace-save').click();
  assert.match(await page.locator('#edge-workspace-status').innerText(),/12 and 256/,'Weak passphrases must be rejected before storage');
  const pw='MUSITU-only local vault password 2026!';
  await secret.fill(pw);
  await page.locator('#edge-workspace-save').click();
  await page.getByText('Workspace 1 saved with encryption',{exact:false}).waitFor({timeout:15000});
  assert.equal(await secret.inputValue(),'','Passphrase must be cleared after use');
  const envelope=await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.v1'));
  assert.ok(envelope?.includes('AES-256-GCM'),'Stored value must identify strong authenticated encryption');
  assert.equal(envelope.includes('hysteresis threshold'),false,'Plaintext chat must not be saved to localStorage');
  assert.equal(envelope.includes('six volts'),false,'Plaintext facts must not be saved to localStorage');
  const exportPromise=page.waitForEvent('download');
  await page.locator('#edge-workspace-export').click();
  const encryptedBackup=await exportPromise;
  assert.equal(encryptedBackup.suggestedFilename(),'musitu-encrypted-workspace.json');
  const backupBytes=readFileSync(await encryptedBackup.path());
  await page.locator('#edge-workspace-clear').click();
  await page.getByText('Visible session cleared',{exact:false}).waitFor({timeout:10000});
  assert.equal(await page.locator('.edge-message').count(),0);
  assert.equal(await page.locator('#edge-export').isDisabled(),true);
  assert.equal(await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.v1')),envelope,'Clearing memory cannot destroy an encrypted copy');
  await secret.fill('This is the incorrect password');
  await page.locator('#edge-workspace-unlock').click();
  await page.getByText('Unable to unlock',{exact:false}).waitFor({timeout:12000});
  assert.equal(await page.locator('.edge-message').count(),0,'Wrong passphrase must not restore conversation');
  await secret.fill(pw);
  await page.locator('#edge-workspace-unlock').click();
  await page.getByText('Decrypted session restored',{exact:false}).waitFor({timeout:12000});
  assert.ok(await page.locator('.edge-message').count()>2,'Encrypted conversation should round-trip in UI');
  assert.equal(await page.locator('#edge-document-file').inputValue(),'','Document bytes must never be restored');
  assert.ok(await page.locator('#edge-export').isEnabled(),'Recovered text conversation can be exported');
  assert.equal(await secret.inputValue(),'','Unlock must not retain secret in form');

  // Reload actually discards live state; only ciphertext persists on origin.
  await page.reload({waitUntil:'domcontentloaded',timeout:30000});
  await page.locator('#launch-ai').click();
  await page.locator('#ai-dialog[open]').waitFor({timeout:10000});
  assert.equal(await page.locator('.edge-message').count(),0,'Reload should not auto-decrypt or auto-restore');
  await page.locator('#edge-workspace summary').click();
  await page.waitForFunction(()=>document.getElementById('edge-workspace-status')?.textContent.includes('Select a workspace slot'),{timeout:12000});
  await page.locator('#edge-workspace-passphrase').fill(pw);
  await page.locator('#edge-workspace-unlock').click();
  await page.getByText('Decrypted session restored',{exact:false}).waitFor({timeout:12000});
  assert.ok(await page.locator('.edge-message').count()>2,'Saved ciphertext survives browser reload and decrypts');
  await page.locator('#edge-workspace-delete').click();
  await page.getByText('Saved encrypted Workspace 1 deleted',{exact:false}).waitFor({timeout:10000});
  assert.equal(await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.v1')),null,'Delete should remove only workspace key');
  assert.ok(await page.locator('.edge-message').count()>2,'Deleting saved copy does not silently destroy unlocked chat');
  // Restore an encrypted portable backup. A wrong secret must not mutate either
  // the current conversation or browser storage; correct passphrase can recover.
  await page.locator('#edge-workspace-clear').click();
  await page.getByText('Visible session cleared',{exact:false}).waitFor({timeout:12000});
  assert.equal(await page.locator('.edge-message').count(),0);
  await page.locator('#edge-workspace-passphrase').fill('An incorrect recovery passphrase!');
  await page.locator('#edge-workspace-import').setInputFiles({
    name:'musitu-encrypted-workspace.json',mimeType:'application/json',buffer:backupBytes
  });
  await page.getByText('Unable to unlock',{exact:false}).waitFor({timeout:12000});
  assert.equal(await page.locator('.edge-message').count(),0);
  assert.equal(await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.v1')),null);
  await page.locator('#edge-workspace-passphrase').fill(pw);
  await page.locator('#edge-workspace-import').setInputFiles({
    name:'musitu-encrypted-workspace.json',mimeType:'application/json',buffer:backupBytes
  });
  await page.getByText('Encrypted backup verified',{exact:false}).waitFor({timeout:12000});
  assert.ok(await page.locator('.edge-message').count()>2,'Portable encrypted backup must restore conversations');
  assert.ok((await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.v1')))?.includes('AES-256-GCM'));
  assert.equal(await page.locator('#edge-workspace-passphrase').inputValue(),'','Backup restore must clear secret');
  console.log('PORTABLE ENCRYPTED BACKUP WRONG-PASSWORD AND VERIFIED RESTORE QA PASS');
  console.log('AES-GCM OPT-IN LOCAL SAVE, WRONG PASSWORD, RESTORE, RELOAD AND DELETE BROWSER QA PASS');

  // A second encrypted workspace remains isolated from Workspace 1.
  const slots=page.locator('#edge-workspace-slot');
  assert.equal(await slots.locator('option').count(),5);
  await slots.selectOption('2');
  assert.match(await page.locator('#edge-workspace-slot-status').innerText(),/Workspace 2 · Empty/);
  await page.locator('#edge-workspace-passphrase').fill('Independent second workspace password 2026');
  await page.locator('#edge-workspace-save').click();
  await page.getByText('Workspace 2 saved with encryption',{exact:false}).waitFor({timeout:15000});
  const slot2=await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.slot.2.v2'));
  assert.ok(slot2?.includes('AES-256-GCM'),'Second slot must be independently encrypted');
  const slot1=await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.v1'));
  assert.ok(slot1?.includes('AES-256-GCM'),'Legacy Workspace 1 must remain compatible');
  assert.notEqual(slot1,slot2,'Independent slots must use unique randomized encryption');

  // Reload, unlock two independently and delete only selected slot 2.
  await page.reload({waitUntil:'domcontentloaded',timeout:30000});
  await page.locator('#launch-ai').click();
  await page.locator('#ai-dialog[open]').waitFor({timeout:10000});
  await page.locator('#edge-workspace summary').click();
  await page.waitForFunction(()=>document.querySelector('#edge-workspace-slot option[value="2"]')?.textContent.includes('Encrypted copy saved'),{timeout:12000});
  assert.equal(await page.locator('.edge-message').count(),0,'No auto-unlock after page reload');
  await page.locator('#edge-workspace-slot').selectOption('2');
  await page.locator('#edge-workspace-passphrase').fill(pw);
  await page.locator('#edge-workspace-unlock').click();
  await page.getByText('Unable to unlock',{exact:false}).waitFor({timeout:12000});
  assert.equal(await page.locator('.edge-message').count(),0,'Wrong workspace passphrase may not unlock another slot');
  await page.locator('#edge-workspace-passphrase').fill('Independent second workspace password 2026');
  await page.locator('#edge-workspace-unlock').click();
  await page.getByText('Decrypted session restored from Workspace 2',{exact:false}).waitFor({timeout:12000});
  assert.ok(await page.locator('.edge-message').count()>2);
  await page.locator('#edge-workspace-delete').click();
  await page.getByText('Saved encrypted Workspace 2 deleted',{exact:false}).waitFor({timeout:12000});
  assert.equal(await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.slot.2.v2')),null);
  assert.equal(await page.evaluate(()=>localStorage.getItem('musitu.intelligence.encrypted.v1')),slot1,
    'Deleting Workspace 2 must preserve Workspace 1 and its original ciphertext');
  assert.ok(await page.locator('.edge-message').count()>2,'Deleting local ciphertext does not unexpectedly clear unlocked chat');
  console.log('FIVE SLOT SELECTOR, LEGACY COMPATIBILITY, ISOLATED DELETION AND PER-SLOT PASSWORD QA PASS');


  await page.locator('#ai-close').click();
  assert.equal(await page.locator('#ai-dialog').getAttribute('open'),null,'Dialog should close');
  await page.close();

  const mobile = await launch(390,844);
  await mobile.locator('#launch-ai').click();
  await mobile.locator('#ai-dialog[open]').waitFor({timeout:10000});
  assert.ok(await mobile.locator('#edge-input').isVisible(),'Mobile AI interface should be usable');
  await mobile.locator('#ai-close').click();
  await mobile.close();
  assert.deepEqual(errors,[],'No unhandled frontend errors permitted');
  console.log('MUSITU EDGE DESKTOP + MOBILE + ACCESSIBLE CHAT TESTS PASSED');
} catch (failure) {
  console.error('MUSITU AI E2E FAILURE:',failure);
  console.error('JS errors:',errors);
  throw failure;
} finally {
  await browser.close();
}
