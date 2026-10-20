/**
 * Browser-only workspace controls. Secrets only live in the password field for
 * the active operation; never placed in localStorage, analytics, URLs or logs.
 */
import {
  encryptWorkspace,decryptWorkspace,
  getEncryptedLocal,saveEncryptedLocal,deleteEncryptedLocal,VaultError
} from './musitu-workspace-vault.mjs';

function downloadEncrypted(encoded) {
  const blob=new Blob([encoded],{type:'application/json;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  const link=document.createElement('a');
  link.href=url;
  link.download='musitu-encrypted-workspace.json';
  link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1200);
}
export function attachWorkspaceControls(adapter) {
  const by=id=>document.getElementById(id);
  const pass=by('edge-workspace-passphrase'),status=by('edge-workspace-status');
  const importer=by('edge-workspace-import');
  const root=by('edge-workspace');
  if(!root||!pass||!status||!importer){
    throw new Error('Workspace controls missing in the website.');
  }
  const buttonIds=['edge-workspace-save','edge-workspace-unlock','edge-workspace-export',
    'edge-workspace-import-button','edge-workspace-clear','edge-workspace-delete'];
  const buttons=buttonIds.map(by);
  if(buttons.some(x=>!x))throw new Error('Workspace action buttons missing.');
  let operating=false;
  function say(message,failed=false) {
    status.textContent=message;
    status.dataset.state=failed?'error':'ok';
  }
  function secret() {
    if(pass.value.length<12||pass.value.length>256){
      throw new VaultError('Enter a passphrase between 12 and 256 characters.','WEAK_PASSPHRASE');
    }
    return pass.value;
  }
  async function perform(action,{needsPassphrase=true}={}) {
    if(operating)return;
    if(adapter.busy()) {say('Finish the current AI request before changing the saved workspace.',true);return;}
    operating=true;
    buttons.forEach(b=>b.disabled=true);
    try {
      const value=needsPassphrase?secret():null;
      await action(value);
    }catch(error) {
      say(error instanceof VaultError||error instanceof Error ? error.message : 'Unable to use workspace.',true);
    }finally{
      pass.value='';
      buttons.forEach(b=>b.disabled=false);
      operating=false;
    }
  }
  by('edge-workspace-save').addEventListener('click',()=>perform(async password=>{
    const snapshot=adapter.snapshot();
    if(!snapshot.transcript.length)throw new VaultError('Start a conversation before saving.','EMPTY_SESSION');
    const encrypted=await encryptWorkspace(snapshot,password);
    saveEncryptedLocal(encrypted);
    say('Encrypted local copy saved. New messages are NOT saved automatically; save again to update it.');
  }));
  by('edge-workspace-unlock').addEventListener('click',()=>perform(async password=>{
    const encrypted=getEncryptedLocal();
    if(!encrypted)throw new VaultError('No locally saved workspace exists on this browser.','NO_SAVED_WORKSPACE');
    const opened=await decryptWorkspace(encrypted,password);
    if(adapter.hasSession() && !confirm('Replace the current visible session with the unlocked saved session?')) {
      say('Unlock cancelled; current session unchanged.');return;
    }
    adapter.restore(opened);
    say('Decrypted session restored in this browser. Source cards and image previews are not included.');
  }));
  by('edge-workspace-export').addEventListener('click',()=>perform(async()=>{
    const encrypted=getEncryptedLocal();
    if(!encrypted)throw new VaultError('Save an encrypted workspace locally before downloading a backup.','NO_SAVED_WORKSPACE');
    downloadEncrypted(encrypted);
    say('Encrypted backup downloaded. Keep your passphrase separately; no one can recover it for you.');
  },{needsPassphrase:false}));
  by('edge-workspace-import-button').addEventListener('click',()=>{
    if(operating)return;
    if(adapter.busy()){say('Finish the AI request before restoring a saved conversation.',true);return;}
    importer.click();
  });
  importer.addEventListener('change',()=>perform(async password=>{
    const file=importer.files?.[0];
    if(!file) return;
    if(file.size>250000||file.size<100)throw new VaultError('Encrypted backup must be smaller than 250 KB.','INVALID_ENVELOPE');
    // Do not store encrypted input or change visible state until authentication succeeds.
    const encoded=await file.text();
    const opened=await decryptWorkspace(encoded,password);
    if(adapter.hasSession()&&!confirm('Replace the current conversation with the imported encrypted backup?')){
      say('Restore cancelled; current conversation unchanged.');return;
    }
    saveEncryptedLocal(encoded);
    adapter.restore(opened);
    say('Encrypted backup verified, stored locally and unlocked. Save after new messages to update it.');
  }).finally(()=>{importer.value='';}));
  by('edge-workspace-clear').addEventListener('click',()=>perform(async()=>{
    if(adapter.hasSession()&&!confirm('Clear the visible conversation and file selection? The encrypted local copy, if any, will remain.'))return;
    adapter.clear();
    say('Visible session cleared. Any encrypted local copy remains until you delete it.');
  },{needsPassphrase:false}));
  by('edge-workspace-delete').addEventListener('click',()=>perform(async()=>{
    const encrypted=getEncryptedLocal();
    if(!encrypted){say('There is no locally saved encrypted copy on this browser.');return;}
    if(!confirm('Delete the locally saved encrypted copy? This cannot be undone without an exported backup.'))return;
    deleteEncryptedLocal();
    say('Local encrypted copy removed from browser storage. Current visible conversation is unchanged.');
  },{needsPassphrase:false}));
  say('Nothing is saved automatically. Use a strong passphrase, then select Encrypt & save locally.');
}
