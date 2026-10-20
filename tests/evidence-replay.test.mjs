import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {createEvidenceReplayBundle,parseEvidenceReplayBundle,
  verifyEvidenceReplayBundle,EvidenceReplayError} from '../assets/musitu-evidence-replay.mjs';

globalThis.crypto ??= webcrypto;
const source='Unrelated laboratory background about safety procedures and calibration. '.repeat(35)+
  '\nThe upper Schmitt trigger switching threshold is 6 volts; lower threshold is 3 volts.\n'+
  'Additional calibration procedures and sensor readings are recorded here. '.repeat(20);
const question='What is the Schmitt trigger upper switching threshold in volts?';
function asFile(name='robotics.txt',text=source){
  const bytes=new TextEncoder().encode(text);
  return {name,size:bytes.byteLength,
    async arrayBuffer(){return Uint8Array.from(bytes).buffer;},
    async text(){return text;}};
}
test('reproducible chain contains hashes, question, offsets but never original contents/excerpts',async()=>{
  const bundle=await createEvidenceReplayBundle(question,[asFile()]);
  const parsed=parseEvidenceReplayBundle(bundle);
  assert.equal(parsed.schema,'musitu.reproducible-evidence-chain.v1');
  assert.equal(parsed.sources[0].name,'robotics.txt');
  assert.equal(parsed.sources[0].keywordMatchFound,true);
  assert.ok(parsed.sources[0].scannedChunks>=2);
  assert.ok(!bundle.includes('upper Schmitt trigger switching threshold is 6 volts'));
  assert.ok(!bundle.includes('safety procedures and calibration'));
  assert.match(bundle,/Not encrypted, signed/);
  assert.equal(bundle,await createEvidenceReplayBundle(question,[asFile()]));
});
test('independent original files reproduce the exact evidence after a new session',async()=>{
  const bundle=await createEvidenceReplayBundle(question,[asFile()]);
  const result=await verifyEvidenceReplayBundle(bundle,[asFile()]);
  assert.equal(result.allMatch,true);
  assert.equal(result.sourceBytesMatch,true);
  assert.equal(result.evidenceSelectionMatch,true);
  assert.equal(result.checked.length,1);
});
test('same-size modified local original is detected before reranking',async()=>{
  const bundle=await createEvidenceReplayBundle(question,[asFile()]);
  const altered=source.replace('6 volts','9 volts');
  assert.equal(altered.length,source.length);
  const out=await verifyEvidenceReplayBundle(bundle,[asFile('robotics.txt',altered)]);
  assert.deepEqual([out.allMatch,out.sourceBytesMatch,out.evidenceSelectionMatch],[false,false,false]);
  assert.equal(out.checked[0].matches,false);
});
test('replay is deterministic with two and three originals in any file-picker order',async()=>{
  const files=[asFile('a_notes.txt',source),asFile('b_notes.txt',source),
    asFile('c_notes.txt',source)];
  for(const count of [2,3]){
    const bundle=await createEvidenceReplayBundle(question,files.slice(0,count));
    const checked=await verifyEvidenceReplayBundle(bundle,files.slice(0,count).reverse());
    assert.equal(checked.allMatch,true);
    assert.equal(checked.checked.length,count);
    assert.ok(parseEvidenceReplayBundle(bundle).sources.every(s=>s.selectedCharacters<=1500));
  }
});
test('a falsified valid-looking excerpt digest detects ranking mismatch despite same original files',async()=>{
  const bundle=JSON.parse(await createEvidenceReplayBundle(question,[asFile()]));
  bundle.sources[0].excerptSha256='0'.repeat(64);
  const result=await verifyEvidenceReplayBundle(JSON.stringify(bundle),[asFile()]);
  assert.equal(result.sourceBytesMatch,true);
  assert.equal(result.evidenceSelectionMatch,false);
  assert.equal(result.allMatch,false);
});
test('a falsified valid-looking passage coordinate detects ranking mismatch',async()=>{
  const bundle=JSON.parse(await createEvidenceReplayBundle(question,[asFile()]));
  const p=bundle.sources[0].passages[0];
  p.start+=1;
  const result=await verifyEvidenceReplayBundle(JSON.stringify(bundle),[asFile()]);
  assert.equal(result.allMatch,false);
  assert.equal(result.sourceBytesMatch,true);
});
test('malformed, injected or oversized receipts are rejected before evaluating originals',async()=>{
  const original=JSON.parse(await createEvidenceReplayBundle(question,[asFile()]));
  for(const bad of [
    {...original,schema:'unknown'},
    {...original,method:'untrusted-retriever'},
    {...original,extra:true},
    {...original,sources:[{...original.sources[0],excerpt:'secret injected data'}]},
    {...original,sources:[{...original.sources[0],sourceCharacters:160001}]},
    {...original,sources:[{...original.sources[0],passages:[{start:0,end:200000,sha256:'a'.repeat(64)}]}]},
    {...original,sources:Array(4).fill(original.sources[0])},
    {...original,sources:[{...original.sources[0],sha256:'not a SHA256'}]}
  ])assert.throws(()=>parseEvidenceReplayBundle(JSON.stringify(bad)),EvidenceReplayError);
  assert.throws(()=>parseEvidenceReplayBundle('x'.repeat(12001)),EvidenceReplayError);
  assert.throws(()=>parseEvidenceReplayBundle('not-json'),EvidenceReplayError);
});
test('missing, renamed, repeated and excess originals never silently pass',async()=>{
  const bundle=await createEvidenceReplayBundle(question,[asFile()]);
  for(const files of [[],[asFile('different.txt')],[asFile(),asFile()],
    [asFile('../traversal.txt')]]){
    await assert.rejects(verifyEvidenceReplayBundle(bundle,files),EvidenceReplayError);
  }
});
test('source replay never initiates network requests or creates cloud workspace state',async()=>{
  const oldFetch=globalThis.fetch;
  globalThis.fetch=()=>{throw Error('Network access is forbidden in local source verification');};
  try{
    const bundle=await createEvidenceReplayBundle(question,[asFile()]);
    assert.equal((await verifyEvidenceReplayBundle(bundle,[asFile()])).allMatch,true);
  }finally{globalThis.fetch=oldFetch;}
});
