import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {buildLocalEvidencePack,EvidenceExportError} from '../assets/musitu-evidence-pack.mjs';

const QUESTION='Which threshold did the laboratory measure?';
function record(name='lab_a.md',text='[Excerpt at character 1]\nUpper Schmitt trigger threshold in this study is 6 volts.') {
  return {
    fileName:name,
    excerpt:text,
    localMetadata:{
      keywordMatchFound:true,
      passages:[{start:0,end:54,text:'Upper Schmitt trigger threshold in this study is 6 volts.',relativeRank:1.5}]
    }
  };
}
test('export labels selected sources and uses SHA-256 over selected excerpt bytes',async()=>{
  const source=record();
  const data=await buildLocalEvidencePack({question:QUESTION,records:[source]});
  const actual=createHash('sha256').update(source.excerpt,'utf8').digest('hex');
  assert.match(data,/^# MUSITU Local Document Evidence Pack/);
  assert.ok(data.includes('lab'+String.fromCharCode(92)+'_a'+String.fromCharCode(92)+'.md'));
  assert.ok(data.includes(actual),'SHA-256 fingerprint matches selected excerpt exactly');
  assert.match(data,/Passage 1 · original extracted character 1/);
  assert.match(data,/> Upper Schmitt trigger threshold/);
  assert.match(data,/not original full file/);
  assert.match(data,/Plaintext export/);
  assert.match(data,/not a full-file integrity signature/);
});
test('multiple sources maintain source-number ordering and 1,500 character budget',async()=>{
  const data=await buildLocalEvidencePack({
    question:QUESTION,
    records:[record('one.txt'),record('two.docx'),record('three.pdf')]
  });
  assert.ok(data.indexOf('[D1]')<data.indexOf('[D2]'));
  assert.ok(data.indexOf('[D2]')<data.indexOf('[D3]'));
  assert.match(data,/Sources:\*\* 3/);
  assert.equal((data.match(/SHA-256 of selected text excerpt/g)||[]).length,3);
});
test('unsafe source labels are escaped to prevent forged report headings',async()=>{
  const data=await buildLocalEvidencePack({question:'Can this file contain unsafe formatting?',
    records:[record('heading#unsafe.md')]});
  assert.match(data,/heading\\#unsafe\\\.md/);
  assert.ok(!data.includes('## [D1] heading#unsafe.md'));
});
test('untrusted question and passage lines remain quoted',async()=>{
  const source=record();
  source.localMetadata.passages[0].text='Important result\n## Fake top-level heading\nResult remains an untrusted quoted passage.';
  const data=await buildLocalEvidencePack({question:'Question about the results\n# Forged heading',records:[source]});
  assert.ok(data.includes('> # Forged heading'));
  assert.ok(data.includes('> ## Fake top-level heading'));
  assert.ok(!data.includes('\n## Fake top-level heading\n'));
});
test('invalid documents or malformed oversized evidence fail closed before export',async()=>{
  const fixture=record();
  for(const records of [[],[fixture,fixture],Array(4).fill(fixture),
    [record('../hidden.pdf')],[{...fixture,excerpt:'x'.repeat(4801)}],
    [{...fixture,localMetadata:{passages:[{start:-1,end:1,text:'invalid',relativeRank:1}]}}]]) {
    await assert.rejects(()=>buildLocalEvidencePack({question:QUESTION,records}),EvidenceExportError);
  }
  await assert.rejects(()=>buildLocalEvidencePack({question:'few',records:[fixture]}),EvidenceExportError);
});
test('no external network or model calls are necessary to create an evidence pack',async()=>{
  const originalFetch=globalThis.fetch;
  globalThis.fetch=()=>{throw Error('Evidence export must never access a remote service');};
  try {
    const result=await buildLocalEvidencePack({question:QUESTION,records:[record()]});
    assert.ok(result.includes('lab'+String.fromCharCode(92)+'_a'));
  } finally {
    globalThis.fetch=originalFetch;
  }
});
