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
