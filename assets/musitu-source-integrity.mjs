/**
 * Browser-only original-file provenance for document evidence packs.
 *
 * SHA-256 binds a receipt to exact original local file bytes, without upload,
 * persistence, authentication, or assertions about the file's authenticity.
 * Invoked only by an explicit user action (Preview or Analyze).
 */
const MAX_BYTES=2*1024*1024;
export class SourceIntegrityError extends Error {
  constructor(message){super(message);this.name='SourceIntegrityError';}
}
export async function fingerprintLocalFile(file){
  if(!file||typeof file.size!=='number'||!Number.isInteger(file.size)||
      file.size<30||file.size>MAX_BYTES||typeof file.arrayBuffer!=='function'){
    throw new SourceIntegrityError('Select a supported local file of 30 bytes–2 MiB before fingerprinting.');
  }
  if(!globalThis.crypto?.subtle?.digest){
    throw new SourceIntegrityError('This browser cannot calculate SHA-256 provenance.');
  }
  const bytes=await file.arrayBuffer();
  if(!(bytes instanceof ArrayBuffer)||bytes.byteLength!==file.size){
    throw new SourceIntegrityError('File changed while computing its fingerprint. Select it again.');
  }
  const digest=new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256',bytes));
  return {bytes:file.size,sha256:Array.from(digest,b=>b.toString(16).padStart(2,'0')).join('')};
}
export async function verifyLocalFile(file,receipt){
  if(!receipt||!Number.isInteger(receipt.bytes)||receipt.bytes<30||receipt.bytes>MAX_BYTES||
      !/^[a-f0-9]{64}$/.test(receipt.sha256||'')){
    throw new SourceIntegrityError('Invalid source integrity receipt.');
  }
  const actual=await fingerprintLocalFile(file);
  return {matches:actual.bytes===receipt.bytes&&actual.sha256===receipt.sha256,
    actual,expected:{bytes:receipt.bytes,sha256:receipt.sha256}};
}
