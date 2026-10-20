/**
 * MUSITU reproducible local evidence chain v1.
 *
 * Receipt binds original SHA-256 -> extracted text length -> deterministic
 * BM25-selected passage offsets and hashes -> bounded excerpt SHA-256.
 * No document text is stored in the receipt. The original question, file
 * names, sizes and hashes are plaintext metadata. This is NOT a signature,
 * independent factual validation, or authenticated provenance.
 */
import {extractDocumentText,validateDocumentFile} from './musitu-document-extract.mjs';
import {fingerprintLocalFile,verifyLocalFile} from './musitu-source-integrity.mjs';
import {rankEvidence} from './musitu-local-evidence.mjs';

const SCHEMA='musitu.reproducible-evidence-chain.v1';
const METHOD='musitu-local-extract-bm25-v1';
const NOTICE='Plaintext question, filenames and hashes. No original bytes or excerpts. Not encrypted, signed, authenticated, or proof of authorship or accuracy.';
const MAX_JSON=12000,MAX_TEXT=160000;
const MAX_SOURCE_BYTES={txt:65536,md:65536,csv:65536,json:65536,pdf:2097152,docx:1048576};
const HEX=/^[a-f0-9]{64}$/;

export class EvidenceReplayError extends Error{
  constructor(message){super(message);this.name='EvidenceReplayError';}
}
function must(ok,message){if(!ok)throw new EvidenceReplayError(message);}
function exact(v,keys){
  return v!==null&&typeof v==='object'&&!Array.isArray(v)&&
    Object.keys(v).length===keys.length&&keys.every(k=>Object.hasOwn(v,k));
}
function safeName(name){
  const ext=/\.([a-z0-9]+)$/i.exec(name)?.[1]?.toLowerCase();
  return typeof name==='string'&&name.length>=5&&name.length<=100&&
    !/[/\\\u0000-\u001f\u007f]/.test(name)&&Object.hasOwn(MAX_SOURCE_BYTES,ext||'')?ext:null;
}
async function hash(text){
  must(typeof text==='string'&&text.length>=1&&text.length<=4800,'Evidence hash input exceeds bounds.');
  must(globalThis.crypto?.subtle?.digest,'Secure browser SHA-256 is unavailable.');
  const bytes=new TextEncoder().encode(text);
  return Array.from(new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256',bytes)),
    b=>b.toString(16).padStart(2,'0')).join('');
}
function validateQuestion(question){
  must(typeof question==='string'&&question.trim().length>=10&&question.length<=900,
    'Question must have 10–900 characters.');
  return question.trim();
}
function safeFiles(files){
  must(Array.isArray(files)&&files.length>=1&&files.length<=3,
    'Select 1–3 original files.');
  const used=new Set();
  for(const file of files){
    const type=safeName(file?.name);
    must(type,'Invalid original file type or filename.');
    validateDocumentFile(file);
    const key=file.name.toLowerCase();
    must(!used.has(key),'Duplicate original document name.');
    used.add(key);
  }
  return files;
}
function validateSources(sources,count){
  must(Array.isArray(sources)&&sources.length===count,'Receipt source count does not match.');
  const names=new Set();
  const charsLimit=count===1?4800:1500;
  return sources.map(source=>{
    must(exact(source,['name','bytes','sha256','sourceCharacters','scannedChunks',
      'selectedCharacters','excerptSha256','keywordMatchFound','passages']),
      'Invalid evidence-chain source structure.');
    const type=safeName(source.name);
    must(type,'Unsafe receipt filename or type.');
    must(!names.has(source.name.toLowerCase()),'Duplicate evidence-chain file names.');
    names.add(source.name.toLowerCase());
    must(Number.isInteger(source.bytes)&&source.bytes>=30&&source.bytes<=MAX_SOURCE_BYTES[type],
      'Invalid original size in evidence chain.');
    must(typeof source.sha256==='string'&&HEX.test(source.sha256)&&
      typeof source.excerptSha256==='string'&&HEX.test(source.excerptSha256),
      'Invalid evidence fingerprint.');
    must(Number.isInteger(source.sourceCharacters)&&source.sourceCharacters>=30&&source.sourceCharacters<=MAX_TEXT&&
      Number.isInteger(source.scannedChunks)&&source.scannedChunks>=1&&source.scannedChunks<=400&&
      Number.isInteger(source.selectedCharacters)&&source.selectedCharacters>=30&&
      source.selectedCharacters<=charsLimit&&typeof source.keywordMatchFound==='boolean',
      'Invalid evidence extraction coverage.');
    const passageLimit=count===1?6:2;
    must(Array.isArray(source.passages)&&source.passages.length>=1&&source.passages.length<=passageLimit,
      'Invalid evidence passage count.');
    for(const passage of source.passages){
      must(exact(passage,['start','end','sha256'])&&
        Number.isInteger(passage.start)&&passage.start>=0&&
        Number.isInteger(passage.end)&&passage.end>passage.start&&
        passage.end<=source.sourceCharacters&&passage.end-passage.start<=620&&
        typeof passage.sha256==='string'&&HEX.test(passage.sha256),
        'Invalid passage provenance coordinates.');
    }
    return source;
  });
}
export async function createEvidenceReplayBundle(question,files){
  const q=validateQuestion(question);
  safeFiles(files);
  const output=[];
  for(const file of files){
    const sourceIntegrity=await fingerprintLocalFile(file);
    const extracted=await extractDocumentText(file);
    const selected=rankEvidence(extracted.text,q,{
      maxChars:files.length===1?4800:1500,
      maxPassages:files.length===1?6:2
    });
    must(selected.excerpt.length>=30,'Document has insufficient reproducible evidence.');
    const passages=[];
    for(const passage of selected.passages){
      passages.push({start:passage.start,end:passage.end,sha256:await hash(passage.text)});
    }
    output.push({
      name:file.name,bytes:sourceIntegrity.bytes,sha256:sourceIntegrity.sha256,
      sourceCharacters:selected.sourceCharacters,scannedChunks:selected.scannedChunks,
      selectedCharacters:selected.selectedCharacters,excerptSha256:await hash(selected.excerpt),
      keywordMatchFound:selected.keywordMatchFound,passages
    });
  }
  validateSources(output,files.length);
  const bundle={schema:SCHEMA,method:METHOD,notice:NOTICE,question:q,sources:output};
  const serialized=JSON.stringify(bundle,null,2)+'\n';
  must(serialized.length<=MAX_JSON,'Evidence chain exceeds the 12,000-character limit.');
  return serialized;
}
export function parseEvidenceReplayBundle(input){
  must(typeof input==='string'&&input.length>=60&&input.length<=MAX_JSON,
    'Evidence chain must be a bounded JSON receipt.');
  let data;
  try{data=JSON.parse(input);}catch{throw new EvidenceReplayError('Evidence chain is not valid JSON.');}
  must(exact(data,['schema','method','notice','question','sources'])&&
    data.schema===SCHEMA&&data.method===METHOD&&data.notice===NOTICE,
    'Unsupported evidence-chain schema or method.');
  data.question=validateQuestion(data.question);
  must(Array.isArray(data.sources)&&data.sources.length>=1&&data.sources.length<=3,
    'Evidence chain must contain 1–3 files.');
  validateSources(data.sources,data.sources.length);
  return data;
}
export async function verifyEvidenceReplayBundle(input,files){
  const bundle=parseEvidenceReplayBundle(input);
  safeFiles(files);
  must(files.length===bundle.sources.length,'Original file count differs from evidence chain.');
  const byName=new Map(files.map(f=>[f.name,f]));
  must(bundle.sources.every(s=>byName.has(s.name)),
    'Select the original files with exactly matching names.');
  const ordered=bundle.sources.map(s=>byName.get(s.name));
  // Refuse to re-rank a modified original; first require exact original bytes.
  const originalMatches=[];
  for(let i=0;i<ordered.length;i++){
    const checked=await verifyLocalFile(ordered[i],bundle.sources[i]);
    originalMatches.push(checked.matches);
  }
  if(originalMatches.some(x=>!x)){
    return {allMatch:false,sourceBytesMatch:false,evidenceSelectionMatch:false,
      checked:bundle.sources.map((s,i)=>({name:s.name,matches:originalMatches[i]}))};
  }
  const actual=parseEvidenceReplayBundle(await createEvidenceReplayBundle(bundle.question,ordered));
  const matches=actual.sources.map((src,i)=>JSON.stringify(src)===JSON.stringify(bundle.sources[i]));
  return {allMatch:matches.every(Boolean),sourceBytesMatch:true,
    evidenceSelectionMatch:matches.every(Boolean),
    checked:bundle.sources.map((s,i)=>({name:s.name,matches:matches[i]}))};
}
