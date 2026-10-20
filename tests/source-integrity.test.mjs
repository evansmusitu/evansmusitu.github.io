import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash,webcrypto} from 'node:crypto';
import {fingerprintLocalFile,verifyLocalFile,SourceIntegrityError} from '../assets/musitu-source-integrity.mjs';
import {buildLocalEvidencePack,EvidenceExportError} from '../assets/musitu-evidence-pack.mjs';

globalThis.crypto ??= webcrypto;
const bytes=new TextEncoder().encode('A confidential local test document with a reproducible scientific observation.');
function file(data=bytes,name='observations.txt'){
  return {name,size:data.byteLength,async arrayBuffer(){return Uint8Array.from(data).buffer;}};
}
function record(integrity){
  return {fileName:'observations.txt',excerpt:'A scientific observation found in this local document.',
    localMetadata:{keywordMatchFound:true,passages:[{start:0,end:51,text:'A scientific observation found in this local document.',relativeRank:2}]},
    sourceIntegrity:integrity};
}
test('SHA-256 fingerprint covers original local bytes, not only selected excerpt',async()=>{
  const result=await fingerprintLocalFile(file());
  assert.equal(result.bytes,bytes.length);
  assert.equal(result.sha256,createHash('sha256').update(bytes).digest('hex'));
});
test('replay verification detects changed local file bytes with equal lengths',async()=>{
  const receipt=await fingerprintLocalFile(file());
  assert.equal((await verifyLocalFile(file(),receipt)).matches,true);
  const altered=bytes.slice();altered[7]^=1;
  assert.equal((await verifyLocalFile(file(altered),receipt)).matches,false);
});
test('refuses inconsistent byte counts and oversized file before hashing',async()=>{
  let reads=0;
  await assert.rejects(fingerprintLocalFile({size:2097153,arrayBuffer(){reads++;return new ArrayBuffer(0);}}),SourceIntegrityError);
  assert.equal(reads,0);
  await assert.rejects(fingerprintLocalFile({size:40,async arrayBuffer(){return new ArrayBuffer(35);}}),/File changed/);
  await assert.rejects(verifyLocalFile(file(),{sha256:'1234',bytes:4}),SourceIntegrityError);
});
test('evidence export binds original file digest without claiming identity',async()=>{
  const receipt=await fingerprintLocalFile(file());
  const markdown=await buildLocalEvidencePack({question:'What was observed in these scientific notes?',records:[record(receipt)]});
  assert.match(markdown,/SHA-256 of original local file bytes/);
  assert.ok(markdown.includes(receipt.sha256));
  assert.match(markdown,/not source authenticity/);
});
test('invalid or forged source receipt must fail closed',async()=>{
  const fake={bytes:0,sha256:'f'.repeat(64)};
  await assert.rejects(buildLocalEvidencePack({question:'What was observed in these scientific notes?',records:[record(fake)]}),EvidenceExportError);
});
