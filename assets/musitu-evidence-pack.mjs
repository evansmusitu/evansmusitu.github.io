/**
 * Local-only source evidence pack for MUSITU Documents.
 * Generates a plaintext Markdown artifact from excerpts already explicitly
 * selected in the browser. No fetch, storage, AI calls, or full file uploads.
 * SHA-256 fingerprints verify exported excerpt bytes only, not full files,
 * factual correctness, or authentic provenance.
 */
export class EvidenceExportError extends Error {
  constructor(message){super(message);this.name='EvidenceExportError';}
}
function valid(condition,message) {if(!condition)throw new EvidenceExportError(message);}
const HEX=bytes=>Array.from(bytes,byte=>byte.toString(16).padStart(2,'0')).join('');
const escapeLabel=value=>String(value)
  .replace(/[\u0000-\u001f\u007f]/g,' ')
  .replace(/([\\*_{}\[\]()#+.!|>~\u0060])/g,'\\$1')
  .slice(0,220);
const blockQuote=value=>String(value).replace(/\r\n?/g,'\n').split('\n').map(line=>'> '+line).join('\n');
async function fingerprint(text) {
  valid(typeof text==='string' && text.length>=30 && text.length<=4800,'Only bounded selected source excerpts can be fingerprinted.');
  valid(globalThis.crypto?.subtle?.digest,'This browser does not support SHA-256 evidence fingerprints.');
  return HEX(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text))));
}
export async function buildLocalEvidencePack({question,records}={}) {
  valid(typeof question==='string' && question.trim().length>=10 && question.length<=900,'Enter a document question of 10–900 characters.');
  valid(Array.isArray(records) && records.length>=1 && records.length<=3,'Select 1–3 local source excerpts.');
  const names=new Set();
  let total=0;
  const sections=[];
  for(const [index,source] of records.entries()){
    valid(source&&typeof source==='object'&&typeof source.fileName==='string'&&
      source.fileName.length>=5&&source.fileName.length<=100 &&
      /\.(txt|md|csv|json|pdf|docx)$/i.test(source.fileName) &&
      !/[/\\\u0000-\u001f]/.test(source.fileName),'Invalid evidence source filename.');
    const canonical=source.fileName.toLowerCase();
    valid(!names.has(canonical),'Duplicate source names cannot be exported.');
    names.add(canonical);
    const text=source.excerpt;
    valid(typeof text==='string'&&text.trim().length>=30 &&
      text.length<=(records.length===1?4800:1500),'A selected evidence excerpt exceeds the documented limit.');
    total+=text.length;
    valid(total<=4800,'Combined evidence exceeds 4,800 characters.');
    const meta=source.localMetadata;
    valid(meta && typeof meta==='object' && Array.isArray(meta.passages) &&
      meta.passages.length>=1 && meta.passages.length<=7,'Missing local passage provenance.');
    const fingerprintSha=await fingerprint(text);
    const tick=String.fromCharCode(96);
    const parts=[
      '## [D'+(index+1)+'] '+escapeLabel(source.fileName),
      '',
      '- Selected excerpt characters: '+text.length,
      '- SHA-256 of selected text excerpt (not original full file): '+tick+fingerprintSha+tick,
      '- Keyword match found: '+(meta.keywordMatchFound===true?'yes':meta.keywordMatchFound===false?'no (early-document fallback)':'unknown'),
      '- Passages selected: '+meta.passages.length,
      '',
    ];
    for(const [pi,p] of meta.passages.entries()){
      valid(p&&Number.isInteger(p.start)&&p.start>=0&&Number.isInteger(p.end)&&p.end>=p.start&&
        typeof p.text==='string'&&p.text.length>=30&&p.text.length<=650,
        'Invalid selected passage position or text length.');
      valid(Number.isFinite(p.relativeRank)&&p.relativeRank>=0,
        'Invalid local evidence relevance score.');
      parts.push('### Passage '+(pi+1)+' · original extracted character '+(p.start+1),
        '',blockQuote(p.text),'');
    }
    sections.push(parts.join('\n'));
  }
  const header=[
    '# MUSITU Local Document Evidence Pack',
    '',
    '**Plaintext export.** It contains user-selected document excerpts and may include private information. Keep it private; it is not encrypted.',
    '',
    '> Scope: browser-local deterministic keyword selection only. Position numbers refer to extracted text, not PDF page coordinates. SHA-256 checks selected excerpt bytes only. This is not a full-file integrity signature, a guarantee of source authenticity, or independent fact verification.',
    '',
    '**Question asked**',
    '',
    blockQuote(question.trim()),
    '',
    '**Sources:** '+records.length+' · **Selected excerpt characters:** '+total,
    '',
    '---',
    ''
  ].join('\n');
  return header+sections.join('\n\n---\n\n')+'\n';
}
