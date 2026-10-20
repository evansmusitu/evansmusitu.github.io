import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto,createHash} from 'node:crypto';
import {createPortableReceipt,parsePortableReceipt,verifyPortableReceipt,PortableReceiptError} from '../assets/musitu-portable-receipt.mjs';
globalThis.crypto ??= webcrypto;
const body='Original laboratory notebook with the upper switching threshold measured at six volts.';
const data=new TextEncoder().encode(body);
const file=(name='lab_notes.txt',dataBytes=data)=>({name,size:dataBytes.length,async arrayBuffer(){return Uint8Array.from(dataBytes).buffer;}});
const sha=createHash('sha256').update(data).digest('hex');
const rec=(name='lab_notes.txt',digest=sha)=>({fileName:name,sourceIntegrity:{bytes:data.length,sha256:digest},
  excerpt:'Private source excerpt must not appear in a portable receipt.',localMetadata:{foo:'not exportable'}});
test('deterministic receipt contains only source metadata, never excerpts, questions or content',()=>{
  const out=createPortableReceipt([rec()]);
  assert.equal(out,createPortableReceipt([rec()]));
  assert.equal(parsePortableReceipt(out).sources[0].sha256,sha);
  assert.ok(!out.includes('Private source excerpt'));
  assert.ok(!out.includes(body));
  assert.match(out,/Not signed/);
});
test('offline verification reproduces matching original file digest',async()=>{
  const outcome=await verifyPortableReceipt(createPortableReceipt([rec()]),[file()]);
  assert.equal(outcome.allMatch,true);
  assert.deepEqual(outcome.checked,[{name:'lab_notes.txt',matches:true}]);
});
test('same-size source substitution is detected without falsely marking identity',async()=>{
  const altered=data.slice();altered[5]^=1;
  const result=await verifyPortableReceipt(createPortableReceipt([rec()]),[file('lab_notes.txt',altered)]);
  assert.equal(result.allMatch,false);
});
test('three original files verify independent of selection order',async()=>{
  const names=['alpha.txt','beta.txt','gamma.txt'];
  const result=await verifyPortableReceipt(createPortableReceipt(names.map(n=>rec(n))),
    names.toReversed().map(n=>file(n)));
  assert.equal(result.allMatch,true);
});
test('wrong names, repeated names and missing files are rejected',async()=>{
  const original=createPortableReceipt([rec()]);
  for(const files of [[],[file('wrong.txt')],[file('LAB_NOTES.TXT')],[file(),file()]]){
    await assert.rejects(verifyPortableReceipt(original,files),PortableReceiptError);
  }
  assert.throws(()=>createPortableReceipt([rec('alpha.txt'),rec('ALPHA.TXT')]),PortableReceiptError);
});
test('rejects manipulated JSON, oversized input, extra fields and unknown formats',()=>{
  const baseline=JSON.parse(createPortableReceipt([rec()]));
  for(const item of [
    {...baseline,schema:'musitu.encrypted-workspace.v1'},
    {...baseline,unauthorized:true},
    {...baseline,sources:[{...baseline.sources[0],notSigned:false}]},
    {...baseline,sources:[{...baseline.sources[0],sha256:'f'.repeat(63)}]},
    {...baseline,sources:[{...baseline.sources[0],bytes:2097153}]},
    {...baseline,sources:[{...baseline.sources[0],name:'../path.txt'}]},
    {...baseline,sources:[{...baseline.sources[0],name:'unsupported.exe'}]},
    {...baseline,sources:[{...baseline.sources[0],name:'lab_notes.txt'}, {...baseline.sources[0]}]},
    {...baseline,sources:Array(4).fill(baseline.sources[0])}
  ])assert.throws(()=>parsePortableReceipt(JSON.stringify(item)),PortableReceiptError);
  assert.throws(()=>parsePortableReceipt('x'.repeat(4097)),PortableReceiptError);
  assert.throws(()=>parsePortableReceipt('{not json'),PortableReceiptError);
});
test('source receipt verification does not make network calls',async()=>{
  const oldFetch=globalThis.fetch;
  globalThis.fetch=()=>{throw Error('Unexpected network request');};
  try{assert.equal((await verifyPortableReceipt(createPortableReceipt([rec()]),[file()])).allMatch,true);}
  finally{globalThis.fetch=oldFetch;}
});
test('receipt is explicitly not a digital signature or authenticated identity claim',()=>{
  const copy=JSON.parse(createPortableReceipt([rec()]));
  copy.sources[0].sha256='a'.repeat(64);
  assert.equal(parsePortableReceipt(JSON.stringify(copy)).sources[0].sha256,'a'.repeat(64));
});
