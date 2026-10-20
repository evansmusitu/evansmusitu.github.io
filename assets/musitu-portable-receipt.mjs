/**
 * Portable, browser-only source fingerprints. No network, sync, storage,
 * identity assertion, signed records, authoritative clocks, or uploaded bytes.
 */
import {verifyLocalFile} from './musitu-source-integrity.mjs';
export class PortableReceiptError extends Error{
  constructor(message){super(message);this.name='PortableReceiptError';}
}
const SCHEMA='musitu.source-fingerprint-receipt.v1';
const LIMITS=Object.freeze({txt:65536,md:65536,csv:65536,json:65536,pdf:2097152,docx:1048576});
const NOTICE='Plaintext filenames and hashes only. Not signed, encrypted, authenticated, timestamp-authoritative, or proof of original publisher or factual accuracy.';
function valid(ok,message){if(!ok)throw new PortableReceiptError(message);}
function exactKeys(value,keys){
  return value!==null&&typeof value==='object'&&!Array.isArray(value)&&
    Object.keys(value).length===keys.length&&keys.every(key=>Object.hasOwn(value,key));
}
function checkSources(sources){
  valid(Array.isArray(sources)&&sources.length>=1&&sources.length<=3,'A receipt needs 1–3 original file fingerprints.');
  const found=new Set();
  return sources.map(source=>{
    valid(exactKeys(source,['name','bytes','sha256']),'Invalid receipt source fields.');
    const name=source.name;
    valid(typeof name==='string'&&name.length>=5&&name.length<=100&&
      !/[/\\\u0000-\u001f\u007f]/.test(name),'Unsafe receipt filename.');
    const suffix=/\.([a-z0-9]+)$/i.exec(name)?.[1]?.toLowerCase();
    valid(Object.hasOwn(LIMITS,suffix||''),'Unsupported receipt file type.');
    const key=name.toLowerCase();
    valid(!found.has(key),'Duplicate receipt filename.');
    found.add(key);
    valid(Number.isInteger(source.bytes)&&source.bytes>=30&&source.bytes<=LIMITS[suffix],
      'Receipt source size exceeds the accepted file limits.');
    valid(typeof source.sha256==='string'&&/^[a-f0-9]{64}$/.test(source.sha256),
      'Invalid SHA-256 source fingerprint.');
    return {name,bytes:source.bytes,sha256:source.sha256};
  });
}
export function createPortableReceipt(records){
  valid(Array.isArray(records),'Source selection missing.');
  const sources=checkSources(records.map(r=>({
    name:r?.fileName,bytes:r?.sourceIntegrity?.bytes,sha256:r?.sourceIntegrity?.sha256
  })));
  return JSON.stringify({schema:SCHEMA,notice:NOTICE,sources},null,2)+'\n';
}
export function parsePortableReceipt(input){
  valid(typeof input==='string'&&input.length>20&&input.length<=4096,
    'Receipt is missing or too large (4,096 characters maximum).');
  let decoded;
  try{decoded=JSON.parse(input);}catch{throw new PortableReceiptError('Receipt is not valid JSON.');}
  valid(exactKeys(decoded,['schema','notice','sources'])&&
    decoded.schema===SCHEMA&&decoded.notice===NOTICE,'Not a supported MUSITU source receipt.');
  return {schema:SCHEMA,notice:NOTICE,sources:checkSources(decoded.sources)};
}
export async function verifyPortableReceipt(input,files){
  const receipt=parsePortableReceipt(input);
  valid(Array.isArray(files)&&files.length===receipt.sources.length,'Select the exact original files listed in the saved receipt.');
  const byName=new Map();
  for(const file of files){
    valid(file&&typeof file.name==='string','Missing original document.');
    const key=file.name.toLowerCase();
    valid(!byName.has(key),'Duplicate selected original file.');
    byName.set(key,file);
  }
  valid(receipt.sources.every(source=>byName.has(source.name.toLowerCase())),
    'Selected file names do not match the saved receipt.');
  const checked=[];
  for(const source of receipt.sources){
    const original=byName.get(source.name.toLowerCase());
    valid(original.name===source.name,'Selected file name differs from the saved receipt.');
    const outcome=await verifyLocalFile(original,{bytes:source.bytes,sha256:source.sha256});
    checked.push({name:source.name,matches:outcome.matches});
  }
  return {allMatch:checked.every(x=>x.matches),checked};
}
