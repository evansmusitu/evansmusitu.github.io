import assert from 'node:assert/strict';

const origin = 'https://musitu-intelligence-studio-ixzlgq.v2.appdeploy.ai';
const health = await fetch(origin + '/api/_healthcheck', {
  headers: { accept: 'application/json' },
  signal: AbortSignal.timeout(25000)
});
console.log('AI Health HTTP:', health.status);
assert.equal(health.status, 200, 'Live backend health endpoint must respond');
const status = await health.json();
assert.equal(status.service, 'MUSITU Intelligence Studio');
assert.equal(status.status, 'ok');

const prompt = 'In three useful sentences, explain why verifying a software product matters before launch.';
const response = await fetch(origin + '/api/assist', {
  method: 'POST',
  headers: { 'content-type': 'application/json', accept: 'application/json' },
  body: JSON.stringify({ mode: 'build', prompt, history: [] }),
  signal: AbortSignal.timeout(85000)
});
console.log('AI Generate HTTP:', response.status);
const payload = await response.text();
let result;
try { result = JSON.parse(payload); } catch { throw new Error('Non-JSON AI response: ' + payload.slice(0, 200)); }
if (response.status !== 200) {
  throw new Error('Live AI generation unavailable: HTTP ' + response.status + ' ' + JSON.stringify(result).slice(0, 600));
}
assert.equal(typeof result.reply, 'string');
assert.ok(result.reply.trim().length > 50, 'Model must return substantive text');
assert.equal(result.liveSearch, false, 'No false claims about live research');
assert.equal(result.mode, 'build');
console.log('AI LIVE GENERATION PASS, reply chars:', result.reply.length);
console.log('Answer excerpt:', result.reply.slice(0, 190));
