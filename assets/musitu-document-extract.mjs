/**
 * Local-only document parsing for MUSITU Intelligence Edge.
 * No file bytes leave the browser through this module.
 * Only the calling chat UI may submit a bounded user-selected excerpt.
 */
const LIMITS=Object.freeze({
  '.txt':65536,'.md':65536,'.csv':65536,'.json':65536,
  '.pdf':2097152,'.docx':1048576
});
const MAX_TEXT=160000;
const MAX_PAGES=20;
export const SUPPORTED_FORMATS=Object.keys(LIMITS);

export class DocumentExtractError extends Error {
  constructor(message){super(message);this.name='DocumentExtractError';}
}
function ext(name){
  return /\.([a-z0-9]+)$/i.exec(String(name||''))?.[0].toLowerCase()||'';
}
export function validateDocumentFile(file) {
  if(!file || !file.name || typeof file.size !== 'number') {
    throw new DocumentExtractError('Choose a document before analyzing.');
  }
  const suffix=ext(file.name);
  if(!Object.hasOwn(LIMITS,suffix)) {
    throw new DocumentExtractError('Supported formats: TXT, MD, CSV, JSON, PDF and DOCX.');
  }
  if(file.name.length>100 || file.name.length<5 || /[/\\\u0000-\u001f]/.test(file.name)) {
    throw new DocumentExtractError('The selected filename is invalid or too long.');
  }
  if(file.size<30 || file.size>LIMITS[suffix]) {
    const label=suffix==='.pdf'?'2 MiB':suffix==='.docx'?'1 MiB':'64 KiB';
    throw new DocumentExtractError('The selected '+suffix+' file must be between 30 bytes and '+label+'.');
  }
  return {suffix,limit:LIMITS[suffix],size:file.size};
}
function normalize(text){
  return String(text||'').replace(/\r\n?/g,'\n')
    .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,' ')
    .slice(0,MAX_TEXT);
}
async function binary(file){
  // Never read bytes until the user explicitly clicks Analyze.
  return new Uint8Array(await file.arrayBuffer());
}
function checkZipSafety(bytes){
  // A ZIP can be tiny yet expand to huge memory. Inspect the central directory
  // before invoking a third-party DOCX extraction library.
  if(bytes.length<50 || bytes[0]!==0x50 || bytes[1]!==0x4b || bytes[2]!==3 || bytes[3]!==4){
    throw new DocumentExtractError('Not a valid ZIP-based DOCX document.');
  }
  const data=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  let eocd=-1;
  for(let i=bytes.length-22;i>=Math.max(0,bytes.length-65557);i--){
    if(data.getUint32(i,true)===0x06054b50){eocd=i;break;}
  }
  if(eocd<0) throw new DocumentExtractError('The DOCX ZIP directory is missing.');
  const entries=data.getUint16(eocd+10,true);
  const directoryBytes=data.getUint32(eocd+12,true);
  const directoryOffset=data.getUint32(eocd+16,true);
  if(entries<1||entries>250||directoryBytes>1048576||directoryOffset+directoryBytes>bytes.length){
    throw new DocumentExtractError('DOCX archive exceeded safe entry limits.');
  }
  let position=directoryOffset,expanded=0,foundDocument=false;
  const decoder=new TextDecoder();
  for(let i=0;i<entries;i++){
    if(position+46>bytes.length||data.getUint32(position,true)!==0x02014b50)
      throw new DocumentExtractError('Invalid DOCX ZIP directory entry.');
    const flags=data.getUint16(position+8,true);
    const compression=data.getUint16(position+10,true);
    const compressed=data.getUint32(position+20,true);
    const uncompressed=data.getUint32(position+24,true);
    const nameLength=data.getUint16(position+28,true);
    const extraLength=data.getUint16(position+30,true);
    const commentLength=data.getUint16(position+32,true);
    const end=position+46+nameLength+extraLength+commentLength;
    if(end>bytes.length||(flags&1)!==0||(compression!==0&&compression!==8)||
      compressed===0xffffffff||uncompressed===0xffffffff||uncompressed>2097152) {
      throw new DocumentExtractError('DOCX archive uses unsupported or unsafe ZIP data.');
    }
    expanded+=uncompressed;
    if(expanded>8388608) throw new DocumentExtractError('DOCX compressed contents exceeded the 8 MiB expansion limit.');
    const name=decoder.decode(bytes.subarray(position+46,position+46+nameLength));
    if(name==='word/document.xml')foundDocument=true;
    position=end;
  }
  if(!foundDocument)throw new DocumentExtractError('DOCX main text document is missing.');
}
async function readPDF(file){
  const bytes=await binary(file);
  if(bytes[0]!==37 || bytes[1]!==80 || bytes[2]!==68 || bytes[3]!==70 || bytes[4]!==45){
    throw new DocumentExtractError('Invalid PDF signature.');
  }
  let pdf;
  try{
    const pdfjs=await import('/assets/vendor/pdf.mjs');
    pdfjs.GlobalWorkerOptions.workerSrc='/assets/vendor/pdf.worker.mjs';
    const loading=pdfjs.getDocument({
      data:bytes,
      isEvalSupported:false,
      disableFontFace:true,
      useSystemFonts:false,
      useWorkerFetch:false,
      stopAtErrors:true
    });
    pdf=await loading.promise;
    if(pdf.numPages>MAX_PAGES) throw new DocumentExtractError('PDF exceeds 20 pages; select a shorter document.');
    let text='';
    for(let index=1;index<=pdf.numPages;index++){
      const page=await pdf.getPage(index);
      const extracted=await page.getTextContent();
      const rows=(extracted.items||[]).map(item=>typeof item.str==='string'?item.str:'');
      const segment='[Page '+index+']\n'+rows.join(' ')+'\n';
      if(text.length+segment.length>MAX_TEXT){
        throw new DocumentExtractError('PDF text exceeds the 160,000-character extraction limit.');
      }
      text+=segment;
      page.cleanup();
    }
    if(text.replace(/\[Page \d+\]/g,'').trim().length<30){
      throw new DocumentExtractError('PDF has insufficient selectable text. Scanned/image-only PDFs need OCR, which is not supported.');
    }
    return {text:normalize(text),pageCount:pdf.numPages,format:'PDF',textOnly:true};
  }catch(error){
    if(error instanceof DocumentExtractError)throw error;
    throw new DocumentExtractError('Unable to extract selectable PDF text. Encrypted or damaged PDFs are not supported.');
  }finally{
    if(pdf)try{await pdf.destroy();}catch{}
  }
}
function loadMammoth(){
  if(globalThis.mammoth?.extractRawText) return Promise.resolve(globalThis.mammoth);
  return new Promise((resolve,reject)=>{
    const element=document.createElement('script');
    element.src='/assets/vendor/mammoth.browser.min.js';
    element.async=true;
    element.onload=()=>{
      if(globalThis.mammoth?.extractRawText)resolve(globalThis.mammoth);
      else reject(new DocumentExtractError('DOCX parser did not initialize.'));
    };
    element.onerror=()=>reject(new DocumentExtractError('DOCX parser asset could not be loaded.'));
    document.head.append(element);
  });
}
async function readDOCX(file){
  const bytes=await binary(file);
  checkZipSafety(bytes);
  try{
    const mammoth=await loadMammoth();
    const buffer=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);
    // extractRawText, never convertToHtml: untrusted source HTML is never rendered.
    const extracted=await mammoth.extractRawText({arrayBuffer:buffer});
    const text=normalize(extracted.value);
    if(text.trim().length<30)throw new DocumentExtractError('DOCX has insufficient accessible text.');
    return {text,format:'DOCX',textOnly:true};
  }catch(error){
    if(error instanceof DocumentExtractError)throw error;
    throw new DocumentExtractError('Unable to read the DOCX text. The file may be damaged or unsupported.');
  }
}
export async function extractDocumentText(file){
  const {suffix}=validateDocumentFile(file);
  if(suffix==='.pdf')return readPDF(file);
  if(suffix==='.docx')return readDOCX(file);
  const raw=await file.text();
  if(raw.includes('\ufffd')||/[\u0000-\u0008\u000e-\u001f]/.test(raw))
    throw new DocumentExtractError('Text document contains undecodable or binary content.');
  const text=normalize(raw);
  if(text.trim().length<30)throw new DocumentExtractError('Text document has insufficient readable content.');
  return {text,format:suffix.slice(1).toUpperCase(),textOnly:true};
}
