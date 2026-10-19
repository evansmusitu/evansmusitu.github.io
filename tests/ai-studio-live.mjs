import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';

const url = 'https://musitu-intelligence-studio-ixzlgq.v2.appdeploy.ai/?mode=learn';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 850 } });
const errors = [];
page.on('pageerror', error => errors.push(error.message));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
try {
  const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  console.log('Frontend HTTP:', response?.status());
  assert.ok(response?.ok(), 'AI Studio frontend must load');
  await page.locator('#studio-prompt').waitFor({ timeout: 30000 });
  const header = await page.locator('.eyebrow').innerText();
  console.log('Experience mode:', header);
  assert.match(header, /LEARN/, 'Deep link must select the Learning mode');
  await page.getByRole('button', { name: /Master a concept/ }).click();
  const prompt = await page.locator('#studio-prompt').inputValue();
  assert.ok(prompt.length >= 10, 'Example should populate prompt');
  await page.getByRole('button', { name: /Generate answer/ }).click();
  await page.locator('.chat-entry.assistant .chat-bubble').first().waitFor({ timeout: 100000 });
  const responseText = await page.locator('.chat-entry.assistant .chat-bubble').first().innerText();
  assert.ok(responseText.length >= 65, 'Real AI answer should be substantive');
  assert.match(responseText.toLowerCase(), /feedback|control|sensor|signal|system|output|loop/, 'AI answer must relate to the question');
  console.log('LIVE AI BROWSER TEST PASSED, reply chars:', responseText.length);
  console.log('Answer excerpt:', responseText.slice(0, 240));
  const homepage = readFileSync('index.html', 'utf8');
  const server = createServer((_request, res) => {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(homepage);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const address = server.address();
    assert.ok(address && typeof address !== 'string');
    const site = await browser.newPage({ viewport: { width: 1080, height: 840 } });
    try {
      await site.goto('http://127.0.0.1:' + address.port + '/', { waitUntil: 'domcontentloaded' });
      await site.locator('#launch-ai').click();
      await site.locator('#ai-dialog[open]').waitFor({ timeout: 7000 });
      await site.frameLocator('#ai-frame').locator('#studio-prompt').waitFor({ timeout: 35000 });
      console.log('LIVE AI HOMEPAGE EMBED TEST PASSED');
      await site.locator('#ai-close').click();
      assert.equal(await site.locator('#ai-dialog').getAttribute('open'), null, 'Studio dialog should close');
    } finally { await site.close(); }
  } finally { await new Promise(resolve => server.close(resolve)); }
  if (errors.length) console.log('Browser warnings:', errors.slice(0, 3));
} catch (error) {
  console.error('Browser test failure:', String(error));
  console.error('Visible alerts:', await page.locator('[role="alert"]').allTextContents().catch(() => []));
  console.error('Status:', await page.locator('[role="status"]').allTextContents().catch(() => []));
  console.error('Browser errors:', errors.slice(0, 8));
  throw error;
} finally { await browser.close(); }
