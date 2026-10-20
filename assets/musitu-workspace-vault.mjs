/**
 * MUSITU local encrypted workspace v1.
 * Explicit user-initiated save only. No external fetch, no cookies, no backend account,
 * no plaintext browser persistence and no storage of selected document/image bytes.
 *
 * Threat model: AES-GCM protects stored data at rest against someone reading the local
 * storage ciphertext without its passphrase. It DOES NOT protect the unlocked page
 * from malicious scripts, a compromised browser/device or weak passphrases.
 */
export const VAULT_KEY='musitu.intelligence.encrypted.v1';
export const VAULT_VERSION=1;
const KDF_ITERATIONS=310000;
const MAX_ENVELOPE=250000;
const MAX_PLAINTEXT=160000;
const AAD=new TextEncoder().encode('MUSITU-INTELLIGENCE-LOCAL-VAULT-v1');

export class VaultError extends Error {
  constructor(message,code='VAULT_ERROR'){super(message);this.name='VaultError';this.code=code;}
}
function fail(message,code){throw new VaultError(message,code);}
function to64(bytes) {
  let binary='';
  for(let i=0;i<bytes.length;i+=8192) {
    binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
  }
  return btoa(binary);
}
function from64(value,maxBytes) {
  if(typeof value!=='string'||value.length===0||value.length>Math.ceil(maxBytes*4/3)+8||
      !/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value)){
    fail('Invalid encrypted workspace encoding.','INVALID_ENVELOPE');
  }
  try {
    const binary=atob(value);
    if(binary.length>maxBytes)fail('Encrypted workspace exceeds the size limit.','INVALID_ENVELOPE');
    return Uint8Array.from(binary,ch=>ch.charCodeAt(0));
  }catch(error){
    if(error instanceof VaultError)throw error;
    fail('Invalid encrypted workspace data.','INVALID_ENVELOPE');
  }
}
function passphrase(value) {
  if(typeof value!=='string'||value.length<12||value.length>256){
    fail('Enter a passphrase of at least 12 characters (maximum 256).','WEAK_PASSPHRASE');
  }
  return value;
}
function validateMessage(item, maxLength) {
  return item&&typeof item==='object'&&!Array.isArray(item)&&
    ['user','assistant','tool'].includes(item.role)&&
    typeof item.content==='string'&&item.content.length>0&&item.content.length<=maxLength&&
    !/[\u0000-\u0008\u000e-\u001f]/.test(item.content);
}
export function validateWorkspace(data) {
  if(!data||typeof data!=='object'||Array.isArray(data)){
    fail('Invalid workspace structure.','INVALID_WORKSPACE');
  }
  const transcript=data.transcript,history=data.history;
  if(!Array.isArray(transcript)||transcript.length<1||transcript.length>80||
     !transcript.every(item=>validateMessage(item,10000))){
    fail('Workspace requires 1–80 valid conversation messages.','INVALID_WORKSPACE');
  }
  if(!Array.isArray(history)||history.length>6||
     !history.every(item=>validateMessage(item,950)&&item.role!=='tool')){
    fail('Workspace history exceeds the safe conversation limit.','INVALID_WORKSPACE');
  }
  const safe={
    transcript:transcript.map(item=>({role:item.role,content:item.content})),
    history:history.map(item=>({role:item.role,content:item.content}))
  };
  if(new TextEncoder().encode(JSON.stringify(safe)).length>MAX_PLAINTEXT){
    fail('Workspace is too large to save. Export or start a smaller session.','WORKSPACE_TOO_LARGE');
  }
  return safe;
}
function readEnvelope(value) {
  if(typeof value!=='string'||value.length>MAX_ENVELOPE)fail('Encrypted workspace file too large.','INVALID_ENVELOPE');
  let envelope;
  try{envelope=JSON.parse(value);}catch{fail('Encrypted workspace file is not valid JSON.','INVALID_ENVELOPE');}
  if(!envelope||typeof envelope!=='object'||Array.isArray(envelope)||
     envelope.kind!=='musitu-local-encrypted-workspace'||envelope.version!==VAULT_VERSION||
     envelope.kdf!=='PBKDF2-SHA-256'||envelope.iterations!==KDF_ITERATIONS||
     envelope.cipher!=='AES-256-GCM'){
    fail('Unsupported or invalid encrypted workspace format.','INVALID_ENVELOPE');
  }
  const salt=from64(envelope.salt,16),iv=from64(envelope.iv,12),encrypted=from64(envelope.ciphertext,MAX_PLAINTEXT+96);
  if(salt.length!==16||iv.length!==12||encrypted.length<17)fail('Malformed encrypted workspace.','INVALID_ENVELOPE');
  return {salt,iv,encrypted};
}
async function keyFor(secret,salt){
  const imported=await crypto.subtle.importKey('raw',new TextEncoder().encode(passphrase(secret)),
    {name:'PBKDF2'},false,['deriveKey']);
  return crypto.subtle.deriveKey({name:'PBKDF2',salt,iterations:KDF_ITERATIONS,hash:'SHA-256'},
    imported,{name:'AES-GCM',length:256},false,['encrypt','decrypt']);
}
export async function encryptWorkspace(data,secret) {
  passphrase(secret);
  const safe=validateWorkspace(data);
  if(!globalThis.crypto?.subtle||!globalThis.crypto?.getRandomValues){
    fail('This browser does not support secure local encryption.','UNSUPPORTED_BROWSER');
  }
  const salt=crypto.getRandomValues(new Uint8Array(16));
  const iv=crypto.getRandomValues(new Uint8Array(12));
  const key=await keyFor(secret,salt);
  const cipher=await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:AAD,tagLength:128},
    key,new TextEncoder().encode(JSON.stringify(safe)));
  const envelope={
    kind:'musitu-local-encrypted-workspace',
    version:VAULT_VERSION,
    cipher:'AES-256-GCM',
    kdf:'PBKDF2-SHA-256',
    iterations:KDF_ITERATIONS,
    salt:to64(salt),
    iv:to64(iv),
    ciphertext:to64(new Uint8Array(cipher))
  };
  const encoded=JSON.stringify(envelope);
  if(encoded.length>MAX_ENVELOPE)fail('Encrypted workspace exceeds its size limit.','WORKSPACE_TOO_LARGE');
  return encoded;
}
export async function decryptWorkspace(encoded,secret) {
  passphrase(secret);
  const {salt,iv,encrypted}=readEnvelope(encoded);
  if(!globalThis.crypto?.subtle){
    fail('This browser does not support secure local decryption.','UNSUPPORTED_BROWSER');
  }
  try {
    const key=await keyFor(secret,salt);
    const decrypted=await crypto.subtle.decrypt({name:'AES-GCM',iv,additionalData:AAD,tagLength:128},
      key,encrypted);
    const clear=new TextDecoder('utf-8',{fatal:true}).decode(decrypted);
    return validateWorkspace(JSON.parse(clear));
  }catch(error){
    if(error instanceof VaultError)throw error;
    fail('Unable to unlock. Check your passphrase or the encrypted file.','UNLOCK_FAILED');
  }
}
export function getEncryptedLocal(storage=globalThis.localStorage) {
  try{return storage.getItem(VAULT_KEY);}catch{
    fail('Private browsing or storage restrictions prevent saving here.','STORAGE_UNAVAILABLE');
  }
}
export function saveEncryptedLocal(encoded,storage=globalThis.localStorage) {
  readEnvelope(encoded);
  try {storage.setItem(VAULT_KEY,encoded);} catch {
    fail('Local browser storage is unavailable or full. Export the encrypted file instead.','STORAGE_UNAVAILABLE');
  }
}
export function deleteEncryptedLocal(storage=globalThis.localStorage) {
  try{storage.removeItem(VAULT_KEY);}catch{
    fail('Unable to delete the locally saved workspace.','STORAGE_UNAVAILABLE');
  }
}
