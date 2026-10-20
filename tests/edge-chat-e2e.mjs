import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { chromium } from 'playwright';

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
  assert.ok(await picture.isVisible());
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
        reply:'The source list describes the field. Open the links to verify claims [1].',
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
  assert.equal(await sources.locator('a[target="_blank"][rel="noopener noreferrer"]').count(),2);
  assert.match(await sources.locator('.edge-source-note').innerText(),/NOT general web search/);
  console.log('CLICKABLE ATTRIBUTED WEB RESEARCH BROWSER QA PASSED');


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
