/**
 * Encrypted workspace slot registry v2, entirely inside the browser.
 * Slot 1 reuses the existing v1 storage key and ciphertext unchanged: users
 * never lose an earlier encrypted workspace due to an automatic migration.
 * Labels are fixed neutral numbers to avoid leaking plaintext titles.
 */
import { VAULT_KEY, VaultError, validateEncryptedEnvelope } from './musitu-workspace-vault.mjs';

export const WORKSPACE_SLOT_COUNT=5;
const PREFIX='musitu.intelligence.encrypted.slot.';
export function slotKey(slot) {
  if(!Number.isInteger(slot)||slot<1||slot>WORKSPACE_SLOT_COUNT) {
    throw new VaultError('Select workspace 1 through 5.','INVALID_WORKSPACE_SLOT');
  }
  return slot===1 ? VAULT_KEY : PREFIX+slot+'.v2';
}
function storageOrError(storage) {
  if(!storage || typeof storage.getItem!=='function'||typeof storage.setItem!=='function'||typeof storage.removeItem!=='function') {
    throw new VaultError('Browser storage is unavailable. Use encrypted backup files instead.','STORAGE_UNAVAILABLE');
  }
  return storage;
}
export function readSlot(slot,storage=globalThis.localStorage) {
  const key=slotKey(slot);
  try{return storageOrError(storage).getItem(key);}catch(error){
    if(error instanceof VaultError)throw error;
    throw new VaultError('Browser storage is unavailable.','STORAGE_UNAVAILABLE');
  }
}
export function saveSlot(slot,encrypted,storage=globalThis.localStorage) {
  const key=slotKey(slot);
  validateEncryptedEnvelope(encrypted);
  try{storageOrError(storage).setItem(key,encrypted);}catch(error){
    if(error instanceof VaultError)throw error;
    throw new VaultError('Unable to save encrypted workspace. Storage may be full or disabled. Export an encrypted backup.','STORAGE_UNAVAILABLE');
  }
}
export function deleteSlot(slot,storage=globalThis.localStorage) {
  const key=slotKey(slot);
  try{storageOrError(storage).removeItem(key);}catch(error){
    if(error instanceof VaultError)throw error;
    throw new VaultError('Unable to delete selected browser workspace.','STORAGE_UNAVAILABLE');
  }
}
export function listSlots(storage=globalThis.localStorage) {
  return Array.from({length:WORKSPACE_SLOT_COUNT},(_,index)=>{
    const slot=index+1;
    return {slot,occupied:readSlot(slot,storage)!==null};
  });
}
