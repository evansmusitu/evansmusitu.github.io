import assert from 'node:assert/strict';

const homepage = 'https://evansmusitu.github.io/';
const expected = [
  ['home', homepage, ['id="ai-dialog"', 'assets/musitu-edge-chat.js', 'assets/musitu-edge-chat.css']],
  ['script', homepage + 'assets/musitu-edge-chat.js', ['musitu-intelligence-edge-20261019', 'MUSITUEdge', 'textContent = text']],
  ['style', homepage + 'assets/musitu-edge-chat.css', ['.edge-thread', '.edge-message', '.edge-form']]
];
async function check(label, url, snippets) {
  let latestError = 'no response';
  for (let attempt = 1; attempt <= 10; attempt++) {
    try {
      const response = await fetch(url + (url.includes('?') ? '&' : '?') + 'check=' + Date.now() + '-' + attempt, {
        headers: { 'cache-control': 'no-cache' },
        signal: AbortSignal.timeout(17000)
      });
      const data = await response.text();
      if (response.status === 200 && snippets.every(s => data.includes(s))) {
        console.log('PUBLISHED ' + label + ' PASS: HTTP 200; bytes ' + data.length);
        return;
      }
      latestError = 'HTTP ' + response.status + '; bytes ' + data.length +
        '; missing: ' + snippets.filter(s => !data.includes(s)).join(', ');
    } catch(e) {
      latestError = e instanceof Error ? e.message : String(e);
    }
    if(attempt < 10) await new Promise(r=>setTimeout(r,5000));
  }
  assert.fail('Production verification failed for '+label+': '+latestError);
}
for (const [label,url,snippets] of expected) await check(label,url,snippets);
const r = await fetch('https://musitu-intelligence-edge-20261019.mft-education-nexus-93f395f5.workers.dev/api/health',
  { signal: AbortSignal.timeout(17000) });
assert.equal(r.status,200,'Cloudflare AI backend health check must respond HTTP 200');
const result = await r.json();
assert.equal(result.service,'MUSITU Intelligence Edge');
console.log('PUBLIC SITE FULL DEPLOYMENT PASS — HTML, JS, CSS AND BACKEND REACHABLE');
