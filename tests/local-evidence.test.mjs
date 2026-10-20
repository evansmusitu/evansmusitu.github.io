import test from 'node:test';
import assert from 'node:assert/strict';
import {rankEvidence,EvidenceRetrievalError} from '../assets/musitu-local-evidence.mjs';

function fixture() {
 const intro='These are ordinary laboratory notes about setting up a classroom science experiment. '.repeat(45);
 const middle='The repeated unrelated paragraphs only contain descriptions of safety glasses and procedure. '.repeat(30);
 const answer='The upper hysteresis threshold of the Schmitt trigger was measured at exactly 6 volts and a lower threshold of 3 volts.';
 const outro='The conclusion discusses calibration notes, sensors and uncertainties in the experimental methodology. '.repeat(24);
 return {text:intro+middle+answer+outro,answer,offset:(intro+middle).length};
}
test('long document retrieval locates a relevant factual passage far from the beginning',()=>{
 const {text,offset}=fixture();
 const r=rankEvidence(text,'What is the upper hysteresis threshold of the Schmitt trigger?',{maxChars:1500,maxPassages:2});
 assert.ok(r.passages.some(p=>p.text.includes('6 volts')),'Must retrieve passage containing the answer');
 assert.ok(r.passages.some(p=>p.start>=offset-620),'Must not choose only initial generic passages');
 assert.ok(r.keywordMatchFound);
 assert.ok(r.selectedCharacters<=1500);
 assert.equal(r.sourceCharacters,text.length);
 assert.ok(r.scannedChunks>10);
});
test('passage offsets reproduce precisely the text selected from the underlying document',()=>{
 const {text}=fixture();
 const r=rankEvidence(text,'Find the threshold and Schmitt trigger data.',{maxChars:4800,maxPassages:6});
 for(const p of r.passages){
   assert.equal(text.slice(p.start,p.end),p.text);
   assert.ok(p.relativeRank>=0);
 }
 assert.ok(!r.excerpt.includes('undefined'));
 assert.equal(r.selectedCharacters,r.excerpt.length);
});
test('ranked keyword search handles capitalisation and non-English Unicode terms',()=>{
 const multilingual='The experiment in this class is described in English. '.repeat(20)+
 'Maitiro ekuedza: kupisa kwemvura kuri makumi mana; temperature sensor used in experiment.';
 const r=rankEvidence(multilingual,'kupisa kwemvura temperature sensor',{maxChars:1500,maxPassages:2});
 assert.ok(r.passages.some(p=>p.text.includes('kupisa kwemvura')));
 assert.ok(r.keywordMatchFound);
});
test('unmatched queries provide an honest deterministic fallback rather than claiming relevance',()=>{
 const document='Blue mountains have seasonal rains and rivers.'.repeat(100);
 const r=rankEvidence(document,'intracellular mitochondria crystalography',{maxChars:750,maxPassages:1});
 assert.equal(r.keywordMatchFound,false);
 assert.equal(r.passages.length,1);
 assert.ok(r.passages[0].start<100);
});
test('selection is deterministic and never exceeds the three-file combined budget',()=>{
 const source=fixture().text;
 const query='Schmitt trigger threshold measured in volts';
 const outputs=[1,2,3].map(()=>rankEvidence(source,query,{maxChars:1500,maxPassages:2}));
 assert.deepEqual(outputs[0],outputs[1]);
 assert.ok(outputs.reduce((total,r)=>total+r.excerpt.length,0)<=4500);
});
test('long documents cannot allocate unbounded rankings or source text',()=>{
 assert.throws(()=>rankEvidence('a'.repeat(160001),'find the result'),EvidenceRetrievalError);
 assert.throws(()=>rankEvidence('text '.repeat(40),'q'),EvidenceRetrievalError);
 assert.throws(()=>rankEvidence('text '.repeat(40),'describe this issue',{maxChars:4801}),EvidenceRetrievalError);
 assert.throws(()=>rankEvidence('text '.repeat(40),'describe this issue',{maxPassages:100}),EvidenceRetrievalError);
});
test('overlapping windows retain words split across boundaries',()=>{
 const source='a '.repeat(254)+' uniquehysteresis 6 volts upper threshold '+'b '.repeat(100);
 const r=rankEvidence(source,'uniquehysteresis upper threshold',{maxChars:1000,maxPassages:2});
 assert.ok(r.passages.some(p=>p.text.includes('uniquehysteresis')));
});
test('passage previews retain untrusted strings as inert text, never as HTML',()=>{
 const text='Study: <script>alert(1)</script> An instrument measurement is 6 volts. '+('Other observations were recorded. '.repeat(20));
 const r=rankEvidence(text,'instrument measurement',{maxChars:650,maxPassages:1});
 assert.ok(r.excerpt.includes('<script>'));
 assert.match(r.approach,/not semantic understanding or fact verification/);
});
