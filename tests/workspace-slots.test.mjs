import test from 'node:test';
import assert from 'node:assert/strict';
import {encryptWorkspace,decryptWorkspace,VAULT_KEY,VaultError} from '../assets/musitu-workspace-vault.mjs';
import {slotKey,saveSlot,readSlot,deleteSlot,listSlots,WORKSPACE_SLOT_COUNT} from '../assets/musitu-workspace-slots.mjs';
const pass='multiple workspaces secure passphrase 2026';
const snapshot=text=>({transcript:[{role:'user',content:text},{role:'assistant',content:'I analyzed this question without attachments.'}],history:[]});
function memory(){
 const m=new Map();
 return {m,getItem:key=>m.get(key)??null,setItem:(k,v)=>m.set(k,v),removeItem:k=>m.delete(k)};
}
test('slot 1 exactly reuses original v1 encrypted storage key',()=>{
 assert.equal(slotKey(1),VAULT_KEY);
 assert.match(slotKey(2),/slot\.2\.v2$/);
 assert.equal(WORKSPACE_SLOT_COUNT,5);
 for(const s of [0,-1,6,1.5,'1',null,Infinity]) assert.throws(()=>slotKey(s),VaultError);
});
test('old encrypted workspace remains recoverable without migration or re-encryption',async()=>{
 const storage=memory();
 const original=await encryptWorkspace(snapshot('Original protected conversation'),pass);
 storage.setItem(VAULT_KEY,original);
 assert.equal(readSlot(1,storage),original);
 assert.equal(listSlots(storage).filter(s=>s.occupied).length,1);
 assert.equal(listSlots(storage)[0].slot,1);
 assert.deepEqual(await decryptWorkspace(readSlot(1,storage),pass),snapshot('Original protected conversation'));
 assert.equal(storage.m.size,1,'No automatic migration or duplicate secrets');
});
test('five independent slots can each decrypt distinct transcripts',async()=>{
 const storage=memory();
 for(let i=1;i<=5;i++){
  const encrypted=await encryptWorkspace(snapshot('Distinct session '+i),pass+i);
  saveSlot(i,encrypted,storage);
 }
 assert.equal(listSlots(storage).filter(s=>s.occupied).length,5);
 for(let i=1;i<=5;i++){
  assert.deepEqual(await decryptWorkspace(readSlot(i,storage),pass+i),snapshot('Distinct session '+i));
  await assert.rejects(()=>decryptWorkspace(readSlot(i,storage),pass+'wrong'),error=>error.code==='UNLOCK_FAILED');
 }
 assert.equal(storage.m.size,5);
});
test('deletion is strictly isolated to selected slot, including legacy slot 1',async()=>{
 const storage=memory();
 for(let i=1;i<=5;i++)saveSlot(i,await encryptWorkspace(snapshot('Slot '+i),pass),storage);
 const saved=readSlot(1,storage);
 deleteSlot(3,storage);
 assert.equal(readSlot(3,storage),null);
 assert.equal(readSlot(1,storage),saved);
 assert.equal(listSlots(storage).filter(s=>s.occupied).length,4);
 deleteSlot(1,storage);
 assert.equal(readSlot(1,storage),null);
 assert.ok(readSlot(2,storage));
 assert.ok(readSlot(4,storage));
 assert.ok(readSlot(5,storage));
});
test('malformed, huge or plaintext files cannot be persisted as workspace slots',()=>{
 const storage=memory();
 for(const bad of ['{}','plaintext','{"kind":"legacy"}','x'.repeat(250001)]){
  assert.throws(()=>saveSlot(2,bad,storage),VaultError);
 }
 assert.equal(listSlots(storage).filter(s=>s.occupied).length,0);
});
test('storage failure is not mistaken for empty slots or successful save',async()=>{
 const storage={getItem:()=>{throw Error('blocked')},setItem:()=>{throw Error('quota')},removeItem:()=>{throw Error('blocked')}};
 assert.throws(()=>listSlots(storage),error=>error.code==='STORAGE_UNAVAILABLE');
 const encrypted=await encryptWorkspace(snapshot('A bounded valid snapshot'),pass);
 assert.throws(()=>saveSlot(2,encrypted,storage),error=>error.code==='STORAGE_UNAVAILABLE');
 assert.throws(()=>deleteSlot(2,storage),error=>error.code==='STORAGE_UNAVAILABLE');
});
test('listing only reveals occupancy, never plaintext names, prompts or passphrases',async()=>{
 const storage=memory();
 saveSlot(4,await encryptWorkspace(snapshot('Private exam question'),pass),storage);
 const list=listSlots(storage);
 assert.deepEqual(list.map(x=>x.slot),[1,2,3,4,5]);
 assert.equal(list.find(x=>x.slot===4).occupied,true);
 assert.ok(!JSON.stringify(list).includes('Private exam'));
 assert.ok(!JSON.stringify(list).includes(pass));
});
