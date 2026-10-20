import test from 'node:test';
import assert from 'node:assert/strict';
import {
  encryptWorkspace,decryptWorkspace,validateWorkspace,
  getEncryptedLocal,saveEncryptedLocal,deleteEncryptedLocal,VAULT_KEY,VaultError
} from '../assets/musitu-workspace-vault.mjs';
const PASS='Correct Horse Battery Staple 2026';
const SESSION={
  transcript:[
    {role:'user',content:'Compare laboratory sensor measurements.'},
    {role:'assistant',content:'The first source [D1] reports 6 volts. The second [D2] reports 8 volts.'}
  ],
  history:[{role:'user',content:'Compare laboratory sensor measurements.'}]
};
test('AES-256-GCM encrypts and decrypts the exact allowed transcript',async()=>{
 const ciphertext=await encryptWorkspace(SESSION,PASS);
 const envelope=JSON.parse(ciphertext);
 assert.equal(envelope.kind,'musitu-local-encrypted-workspace');
 assert.equal(envelope.cipher,'AES-256-GCM');
 assert.equal(envelope.kdf,'PBKDF2-SHA-256');
 assert.equal(envelope.iterations,310000);
 assert.ok(!ciphertext.includes('laboratory sensor measurements'));
 assert.ok(!ciphertext.includes('8 volts'));
 assert.deepEqual(await decryptWorkspace(ciphertext,PASS),SESSION);
});
test('separate saves never use the same salt or IV',async()=>{
 const first=JSON.parse(await encryptWorkspace(SESSION,PASS));
 const second=JSON.parse(await encryptWorkspace(SESSION,PASS));
 assert.notEqual(first.salt,second.salt);
 assert.notEqual(first.iv,second.iv);
 assert.notEqual(first.ciphertext,second.ciphertext);
});
test('wrong passphrase never unlocks the stored plaintext',async()=>{
 const data=await encryptWorkspace(SESSION,PASS);
 await assert.rejects(()=>decryptWorkspace(data,'a different incorrect password'),error=>error.code==='UNLOCK_FAILED');
});
test('authenticated decryption rejects tampered ciphertext and metadata',async()=>{
 const envelope=JSON.parse(await encryptWorkspace(SESSION,PASS));
 const changed={...envelope,ciphertext:envelope.ciphertext.slice(0,-4)+'AAAA'};
 await assert.rejects(()=>decryptWorkspace(JSON.stringify(changed),PASS),VaultError);
 const versionChanged={...envelope,iterations:1};
 await assert.rejects(()=>decryptWorkspace(JSON.stringify(versionChanged),PASS),error=>error.code==='INVALID_ENVELOPE');
 const tamperedSalt={...envelope,salt:envelope.salt.slice(0,-3)+'AAA'};
 await assert.rejects(()=>decryptWorkspace(JSON.stringify(tamperedSalt),PASS),VaultError);
});
test('file parser refuses large, malformed or untrusted envelopes',async()=>{
 await assert.rejects(()=>decryptWorkspace('not json',PASS),error=>error.code==='INVALID_ENVELOPE');
 await assert.rejects(()=>decryptWorkspace('x'.repeat(250001),PASS),error=>error.code==='INVALID_ENVELOPE');
 await assert.rejects(()=>encryptWorkspace(SESSION,'short'),error=>error.code==='WEAK_PASSPHRASE');
});
test('untrusted restored content must pass strict roles, message lengths and limits',()=>{
 const valid=validateWorkspace(SESSION);
 assert.deepEqual(valid,SESSION);
 assert.throws(()=>validateWorkspace({transcript:[{role:'admin',content:'unsafe'}],history:[]}),VaultError);
 assert.throws(()=>validateWorkspace({transcript:[{role:'user',content:'x'.repeat(10001)}],history:[]}),VaultError);
 assert.throws(()=>validateWorkspace({transcript:[],history:[]}),VaultError);
 assert.throws(()=>validateWorkspace({transcript:SESSION.transcript,history:[{role:'tool',content:'unexpected'}]}),VaultError);
 assert.throws(()=>validateWorkspace({transcript:Array.from({length:81},()=>({role:'assistant',content:'hello'})),history:[]}),VaultError);
});
test('local storage receives ciphertext only and deletes only its own key',async()=>{
 const values=new Map([['unrelated','do not touch']]);
 const storage={
  getItem:key=>values.get(key)??null,
  setItem:(key,value)=>values.set(key,value),
  removeItem:key=>values.delete(key)
 };
 const encrypted=await encryptWorkspace(SESSION,PASS);
 saveEncryptedLocal(encrypted,storage);
 assert.equal(getEncryptedLocal(storage),encrypted);
 assert.ok(!values.get(VAULT_KEY).includes('laboratory sensor measurements'));
 assert.deepEqual(await decryptWorkspace(getEncryptedLocal(storage),PASS),SESSION);
 deleteEncryptedLocal(storage);
 assert.equal(getEncryptedLocal(storage),null);
 assert.equal(values.get('unrelated'),'do not touch');
});
