/**
 * MUSITU local evidence retrieval, v1.
 *
 * Pure deterministic keyword passage ranking (BM25), not semantic embeddings,
 * not an external search engine, and not proof that any claim is true.
 * Browser calls this only after explicit user action. No storage or fetch here.
 */
const MAX_SOURCE_CHARACTERS=160000;
const MAX_PASSAGES=7;
const STOP=new Set(['about','after','along','also','among','and','are','been','before',
  'between','can','compare','could','does','each','file','files','find','for','from',
  'give','have','how','into','its','notes','our','please','report','reports','say',
  'show','source','sources','summarize','summary','tell','than','that','the','their',
  'there','these','this','those','through','what','when','where','which','while',
  'with','would','your','document','documents','according','explain']);
const TOKEN=/[\p{L}\p{N}]{2,}/gu;

export class EvidenceRetrievalError extends Error {
  constructor(message){super(message);this.name='EvidenceRetrievalError';}
}
function words(value){
  return (String(value??'').normalize('NFKC').toLowerCase().match(TOKEN)||[])
    .filter(word=>word.length<=40&&!STOP.has(word));
}
function windows(text){
  const chunks=[];
  const size=620,overlap=105,step=size-overlap;
  for(let start=0;start<text.length;start+=step){
    let end=Math.min(start+size,text.length);
    // Prefer whitespace to avoid chopping a word. Never lose trailing fragments:
    // overlap with the following window is intentionally maintained.
    if(end<text.length){
      const split=text.lastIndexOf(' ',end);
      if(split>start+450)end=split+1;
    }
    const content=text.slice(start,end).trim();
    if(content.length>=15)chunks.push({start,end,content});
  }
  return chunks;
}
export function rankEvidence(source,query,{maxChars=4800,maxPassages=MAX_PASSAGES}={}){
  if(typeof source!=='string'||source.trim().length<30||
     source.length>MAX_SOURCE_CHARACTERS){
    throw new EvidenceRetrievalError('Readable document text must contain 30–160,000 characters.');
  }
  if(typeof query!=='string'||query.length<3||query.length>900){
    throw new EvidenceRetrievalError('Ask a question between 3 and 900 characters.');
  }
  if(!Number.isInteger(maxChars)||maxChars<150||maxChars>4800||
     !Number.isInteger(maxPassages)||maxPassages<1||maxPassages>7){
    throw new EvidenceRetrievalError('Unsupported excerpt or passage limit.');
  }
  const normalized=source.replace(/\r\n?/g,'\n').replace(/\u0000/g,' ');
  const passages=windows(normalized);
  const question=Array.from(new Set(words(query))).slice(0,35);
  const querySet=new Set(question);
  const frequencies=new Map();
  const length=passages.length||1;
  let totalLength=0;
  const processed=passages.map(p=>{
    const tokens=words(p.content);
    const counts=new Map();
    for(const token of tokens)counts.set(token,(counts.get(token)||0)+1);
    for(const token of querySet)if(counts.has(token))frequencies.set(token,(frequencies.get(token)||0)+1);
    totalLength+=tokens.length;
    return {...p,counts,tokenLength:tokens.length};
  });
  const avgLength=totalLength/length||1;
  for(const item of processed){
    let score=0,matched=0;
    for(const token of question){
      const tf=item.counts.get(token)||0;
      if(!tf)continue;
      matched++;
      const df=frequencies.get(token)||0;
      const idf=Math.log(1+(length-df+0.5)/(df+0.5));
      const k1=1.4,b=0.75;
      score+=idf*(tf*(k1+1))/(tf+k1*(1-b+b*item.tokenLength/avgLength));
    }
    // Coverage helps a contiguous passage answer multi-concept questions.
    item.score=score+(question.length?matched/question.length:0);
    item.matchedTerms=matched;
    item.text=item.content;
    delete item.content;
    delete item.counts;
  }
  const anyMatch=processed.some(p=>p.matchedTerms>0);
  // Deterministic early-document fallback when the lexical query has no match.
  const ranked=processed.slice().sort((a,b)=>b.score-a.score||a.start-b.start);
  const selected=[];
  let used=0;
  for(const item of ranked) {
    if(selected.length>=maxPassages)break;
    const header='[Excerpt at character '+(item.start+1)+']\n';
    const available=maxChars-used-header.length-(selected.length?2:0);
    if(available<75)break;
    const raw=item.text.slice(0,available).trimEnd();
    if(raw.length<30)continue;
    selected.push({...item,text:raw,end:item.start+raw.length});
    used+=header.length+raw.length+(selected.length>1?2:0);
  }
  const ordered=selected.slice().sort((a,b)=>a.start-b.start);
  const excerpt=ordered.map(p=>'[Excerpt at character '+(p.start+1)+']\n'+p.text).join('\n\n');
  if(!excerpt||excerpt.length>maxChars)throw new EvidenceRetrievalError('Unable to select bounded evidence passages.');
  return {
    excerpt,
    passages:ordered.map(p=>({
      start:p.start,end:p.end,text:p.text,matchedTerms:p.matchedTerms,
      relativeRank:Number(p.score.toFixed(5))
    })),
    scannedChunks:passages.length,
    sourceCharacters:normalized.length,
    selectedCharacters:excerpt.length,
    lexicalTerms:question.length,
    keywordMatchFound:anyMatch,
    approach:'Local deterministic BM25 keyword ranking; not semantic understanding or fact verification'
  };
}
