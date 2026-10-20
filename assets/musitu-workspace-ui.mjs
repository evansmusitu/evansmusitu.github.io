/**
 * Browser-only workspace controls. Secrets only live in the password field for
 * the active operation; never placed in localStorage, analytics, URLs or logs.
 */
import {encryptWorkspace,decryptWorkspace,VaultError} from './musitu-workspace-vault.mjs';
import {readSlot,saveSlot,deleteSlot,listSlots} from './musitu-workspace-slots.mjs';

function downloadEncrypted(encoded,slot) {
  const blob=new Blob([encoded],{type:'application/json;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  const link=document.createElement('a');
  link.href=url;
  link.download=slot===1?'musitu-encrypted-workspace.json':'musitu-encrypted-workspace-'+slot+'.json';
  link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1200);
}
export function attachWorkspaceControls(adapter) {
  const by=id=>document.getElementById(id);
  const pass=by('edge-workspace-passphrase'),status=by('edge-workspace-status');
  const importer=by('edge-workspace-import');
  const slotControl=by('edge-workspace-slot');
  const slotStatus=by('edge-workspace-slot-status');
  const root=by('edge-workspace');
  if(!root||!pass||!status||!importer||!slotControl||!slotStatus){
    throw new Error('Workspace controls missing in the website.');
  }
  const buttonIds=['edge-workspace-save','edge-workspace-unlock','edge-workspace-export',
    'edge-workspace-import-button','edge-workspace-clear','edge-workspace-delete'];
  const buttons=buttonIds.map(by);
  if(buttons.some(x=>!x))throw new Error('Workspace action buttons missing.');
  let operating=false;
  const selectedSlot=()=>Number(slotControl.value);
  function refreshSlots() {
    const slots=listSlots();
    for(const entry of slots){
      const option=slotControl.querySelector('option[value="'+entry.slot+'"]');
      if(option)option.textContent='Workspace '+entry.slot+(entry.occupied?' · Encrypted copy saved':' · Empty');
    }
    const selected=slots.find(entry=>entry.slot===selectedSlot());
    slotStatus.textContent='Workspace '+selectedSlot()+' · '+(selected?.occupied?'Encrypted copy available to unlock or export':'Empty: save a conversation to create an encrypted copy');
  }
  slotControl.addEventListener('change',()=>{
    try{refreshSlots();say('Workspace '+selectedSlot()+' selected. Current visible chat is unchanged; unlock to open this slot.');}
    catch(error){say(error instanceof Error?error.message:'Browser storage unavailable.',true);}
  });
  window.addEventListener('storage',event=>{
    if(event.key===null || event.key==='musitu.intelligence.encrypted.v1'||event.key.startsWith('musitu.intelligence.encrypted.slot.')){
      try{refreshSlots();say('Saved workspace slots changed in another tab. Refresh your view before overwriting.');}catch{}
    }
  });
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
    slotControl.disabled=true;
    try {
      const value=needsPassphrase?secret():null;
      await action(value);
    }catch(error) {
      say(error instanceof VaultError||error instanceof Error ? error.message : 'Unable to use workspace.',true);
    }finally{
      pass.value='';
      buttons.forEach(b=>b.disabled=false);
      slotControl.disabled=false;
      try{refreshSlots();}catch{};
      operating=false;
    }
  }
  by('edge-workspace-save').addEventListener('click',()=>perform(async password=>{
    const snapshot=adapter.snapshot();
    if(!snapshot.transcript.length)throw new VaultError('Start a conversation before saving.','EMPTY_SESSION');
    const encrypted=await encryptWorkspace(snapshot,password);
    const slot=selectedSlot();
    if(readSlot(slot) && !confirm('Replace the existing encrypted Workspace '+slot+' with this visible conversation?')) {
      say('Save cancelled; existing encrypted workspace '+slot+' was not changed.');return;
    }
    saveSlot(slot,encrypted);
    say('Workspace '+slot+' saved with encryption. New messages are NOT saved automatically.');
  }));
  by('edge-workspace-unlock').addEventListener('click',()=>perform(async password=>{
    const slot=selectedSlot();
    const encrypted=readSlot(slot);
    if(!encrypted)throw new VaultError('Workspace '+slot+' is empty on this browser.','NO_SAVED_WORKSPACE');
    const opened=await decryptWorkspace(encrypted,password);
    if(adapter.hasSession() && !confirm('Replace the current visible session with the unlocked saved session?')) {
      say('Unlock cancelled; current session unchanged.');return;
    }
    adapter.restore(opened);
    say('Decrypted session restored from Workspace '+slot+'. Source cards and image previews are not included.');
  }));
  by('edge-workspace-export').addEventListener('click',()=>perform(async()=>{
    const slot=selectedSlot();
    const encrypted=readSlot(slot);
    if(!encrypted)throw new VaultError('Workspace '+slot+' is empty. Save before downloading an encrypted backup.','NO_SAVED_WORKSPACE');
    downloadEncrypted(encrypted,slot);
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
    const slot=selectedSlot();
    if(readSlot(slot) && !confirm('Replace the saved encrypted Workspace '+slot+' with this authenticated backup?')){
      say('Import cancelled; saved Workspace '+slot+' was not overwritten.');return;
    }
    saveSlot(slot,encoded);
    adapter.restore(opened);
    say('Encrypted backup verified, stored in Workspace '+slot+' and unlocked. Save again after new messages.');
  }).finally(()=>{importer.value='';}));
  by('edge-workspace-clear').addEventListener('click',()=>perform(async()=>{
    if(adapter.hasSession()&&!confirm('Clear the visible conversation and file selection? The encrypted local copy, if any, will remain.'))return;
    adapter.clear();
    say('Visible session cleared. Any encrypted local copy remains until you delete it.');
  },{needsPassphrase:false}));
  by('edge-workspace-delete').addEventListener('click',()=>perform(async()=>{
    const slot=selectedSlot();
    const encrypted=readSlot(slot);
    if(!encrypted){say('Workspace '+slot+' has no saved encrypted copy.');return;}
    if(!confirm('Permanently delete saved encrypted Workspace '+slot+'? The other four slots will not be affected.'))return;
    deleteSlot(slot);
    say('Saved encrypted Workspace '+slot+' deleted. The other slots and current visible conversation are unchanged.');
  },{needsPassphrase:false}));
  try{refreshSlots();}catch(error){say(error instanceof Error?error.message:'Browser storage unavailable.',true);}
  say('Nothing is saved automatically. Select a workspace slot and use a strong passphrase.');
}
