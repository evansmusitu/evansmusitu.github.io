(() => {
  'use strict';

  const service = 'https://musitu-intelligence-edge-20261019.mft-education-nexus-93f395f5.workers.dev';
  const dialog = document.getElementById('ai-dialog');
  const thread = document.getElementById('edge-thread');
  const prompt = document.getElementById('edge-input');
  const send = document.getElementById('edge-send');
  const alert = document.getElementById('edge-alert');
  const health = document.getElementById('edge-health');
  const exportButton = document.getElementById('edge-export');
  const counter = document.getElementById('edge-counter');
  let mode = 'explore';
  const documentControls=document.getElementById('edge-document-controls');
  const documentFile=document.getElementById('edge-document-file');
  const documentInfo=document.getElementById('edge-document-info');
  const documentClear=document.getElementById('edge-document-clear');
  const presets = document.getElementById('edge-calculator-presets');
  const inputLabel = document.querySelector('#edge-form label[for="edge-input"]');
  let pending = false;
  let history = [];
  let transcript = []; // Display/export only; tool results are not inserted as model memories.

  function isShortArithmetic(value) {
    const text = value.trim();
    if (!text || text.length > 140 || !/\d/.test(text)) return false;
    if (/^[0-9eE.+\-*/^%()\s]+$/.test(text) && /[+\-*/^%()]/.test(text)) return true;
    return /^(?:sqrt|abs|floor|ceil|round)\(\d+(?:\.\d+)?\)$/i.test(text);
  }

  function selectMode(next) {
    mode = ['explore', 'build', 'learn', 'markets', 'deep', 'calculator', 'image', 'research', 'scholar', 'document'].includes(next) ? next : 'explore';
    const math = mode === 'calculator';
    const imageMode = mode === 'image';
    const researchMode = mode === 'research';
    const scholarMode = mode === 'scholar';
    const documentMode = mode === 'document';
    documentControls.hidden = !documentMode;
    presets.hidden = !math;
    prompt.maxLength = math ? 140 : imageMode ? 450 : (researchMode || scholarMode) ? 180 : 900;
    prompt.placeholder = math ? 'Enter an expression, e.g. 7*(2+3) or sqrt(81)…' :
      imageMode ? 'Describe an image to generate, including subject, setting and style…' :
      researchMode ? 'Search Wikipedia and Hacker News, e.g. quantum computing in education…' :
      scholarMode ? 'Find DOI-registered papers, e.g. physics robotics feedback control…' :
      documentMode ? 'Ask a question about the text file you selected…' :
      mode === 'deep' ? 'Ask a complex question for deliberate analysis…' : 'Ask a question in the selected mode…';
    inputLabel.textContent = math ? 'DETERMINISTIC MATH EXPRESSION' : imageMode ? 'IMAGE DESCRIPTION' : researchMode ? 'LIVE SOURCE-RESEARCH QUERY' : scholarMode ? 'SCHOLARLY DOI RESEARCH QUERY' : documentMode ? 'QUESTION ABOUT THE SELECTED EXCERPT' : mode === 'deep' ? 'ASK THE REASONING MODEL' : 'ASK MUSITU AI';
    send.textContent = math ? 'Calculate ↗' : imageMode ? 'Generate image ↗' : researchMode ? 'Research sources ↗' : scholarMode ? 'Find academic papers ↗' : documentMode ? 'Analyze excerpt ↗' : 'Generate answer ↗';
    counter.textContent = prompt.value.length + ' / ' + prompt.maxLength + ' · Enter to send';
    document.querySelectorAll('[data-edge-mode]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.edgeMode === mode));
    });
  }

  // No file bytes are sent before the user explicitly submits a document question.
  const SUPPORTED=/\.(txt|md|csv|json)$/i;
  const MAX_FILE_SIZE=64*1024;
  function selectDocumentExcerpt(content,question) {
    const normalized=content.replace(/\r\n?/g,'\n').replace(/\u0000/g,'');
    const words=new Set((question.toLowerCase().match(/[a-z0-9]{3,}/g)||[]).filter(x=>!['the','this','that','from','with','what','does','please','your','about','into','have'].includes(x)));
    const pieces=[];
    for(let pos=0;pos<normalized.length;pos+=650){
      const fragment=normalized.slice(pos,pos+650);
      const lowered=fragment.toLowerCase();
      const score=[...words].reduce((total,word)=>total+(lowered.includes(word)?1:0),0);
      pieces.push({pos,fragment,score:score+(pos===0?0.4:0)});
    }
    const winners=pieces.slice().sort((a,b)=>b.score-a.score||a.pos-b.pos).slice(0,7).sort((a,b)=>a.pos-b.pos);
    let selected='';
    for(const item of winners){
      const snippet='[Text excerpt, character '+(item.pos+1)+']\n'+item.fragment+'\n';
      if(selected.length+snippet.length>4650){
        selected+=snippet.slice(0,Math.max(0,4650-selected.length));
        break;
      }
      selected+=snippet;
    }
    return selected.trim().slice(0,4800);
  }
  documentFile.addEventListener('change',()=>{
    const file=documentFile.files?.[0];
    if(!file){
      documentInfo.textContent='Choose a local UTF-8 .txt, .md, .csv or .json file (64 KiB maximum). No file is stored or uploaded until you analyze a selected excerpt.';
      return;
    }
    documentInfo.textContent=SUPPORTED.test(file.name)&&file.size<=MAX_FILE_SIZE&&file.name.length<=100
      ? 'Selected: '+file.name+' ('+file.size+' bytes). Only a relevance-selected excerpt of up to 4,800 characters will be sent when you press Analyze. The file is not stored by the server.'
      : 'Unsupported file, invalid filename, or file exceeds 64 KiB. Choose a small UTF-8 text document.';
  });
  documentClear.addEventListener('click',()=>{
    documentFile.value='';
    documentInfo.textContent='Selection cleared. The website has not saved the file.';
  });

  function displayError(message) {
    alert.textContent = message;
    alert.hidden = false;
  }

  function writeInline(parent, value) {
    const pieces = value.split(/(\*\*[^*]{1,160}\*\*|\x60[^\x60]{1,160}\x60)/g);
    for (const piece of pieces) {
      if (!piece) continue;
      if (piece.startsWith('**') && piece.endsWith('**')) {
        const strong = document.createElement('strong');
        strong.textContent = piece.slice(2,-2);
        parent.append(strong);
      } else if (piece.charCodeAt(0) === 96 && piece.charCodeAt(piece.length - 1) === 96) {
        const code = document.createElement('code');
        code.textContent = piece.slice(1,-1);
        parent.append(code);
      } else {
        parent.append(document.createTextNode(piece));
      }
    }
  }

  function renderAnswer(text) {
    // Construct DOM nodes instead of using innerHTML. Model output is untrusted.
    const body = document.createElement('div');
    body.className = 'edge-rich';
    const lines = text.replace(/\r\n?/g,'\n').split('\n').slice(0,500);
    let list = null;
    let pre = null;
    let code = null;

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.charCodeAt(0) === 96 && trimmed.charCodeAt(1) === 96 && trimmed.charCodeAt(2) === 96) {
        list = null;
        if (pre) { pre = null; code = null; }
        else {
          pre = document.createElement('pre');
          code = document.createElement('code');
          pre.append(code);
          body.append(pre);
        }
        continue;
      }
      if (pre && code) {
        code.textContent += line + '\n';
        continue;
      }
      if (!trimmed) { list = null; continue; }

      const heading = trimmed.match(/^#{1,4}\s+(.+)$/);
      if (heading) {
        list = null;
        const h = document.createElement('h4');
        writeInline(h,heading[1]);
        body.append(h);
        continue;
      }
      const bullet = trimmed.match(/^([-*]|\d+[.)])\s+(.+)$/);
      if (bullet) {
        const ordered = /^\d/.test(bullet[1]);
        const listTag = ordered ? 'OL' : 'UL';
        if (!list || list.tagName !== listTag) {
          list = document.createElement(ordered ? 'ol' : 'ul');
          body.append(list);
        }
        const li = document.createElement('li');
        writeInline(li,bullet[2]);
        list.append(li);
        continue;
      }
      list = null;
      const paragraph = document.createElement('p');
      writeInline(paragraph,line);
      body.append(paragraph);
    }
    return body;
  }

  function extractChecklistItems(text) {
    const items = [];
    for (const line of text.split(/\r?\n/)) {
      const match = line.trim().match(/^(?:\d{1,2}[.)]|[-*])\s+(.{9,170})$/);
      if (!match) continue;
      const label = match[1].replace(/\*\*/g,'').replace(/\x60/g,'').trim();
      if (label && !items.includes(label)) items.push(label);
      if (items.length === 8) break;
    }
    return items.length >= 2 ? items : [];
  }

  function installChecklist(message, heading, items) {
    const action = document.createElement('button');
    action.type = 'button';
    action.className = 'edge-copy edge-board-toggle';
    action.textContent = 'Make checklist';
    heading.append(action);
    let board = null;

    action.addEventListener('click', () => {
      if (board) {
        board.hidden = !board.hidden;
        action.textContent = board.hidden ? 'Show checklist' : 'Hide checklist';
        return;
      }
      board = document.createElement('section');
      board.className = 'edge-action-board';
      board.setAttribute('aria-label','Checklist extracted from AI response');
      const title = document.createElement('div');
      title.className = 'edge-board-title';
      title.textContent = 'YOUR ACTION CHECKLIST';
      const progress = document.createElement('div');
      progress.className = 'edge-board-progress';
      progress.setAttribute('role','status');
      progress.textContent = '0 of ' + items.length + ' checked';
      const list = document.createElement('div');
      list.className = 'edge-board-items';
      const checks = [];
      items.forEach((labelText,index) => {
        const row = document.createElement('label');
        row.className = 'edge-board-row';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.setAttribute('aria-label','Checklist item ' + (index+1));
        const label = document.createElement('span');
        label.textContent = labelText;
        row.append(checkbox,label);
        list.append(row);
        checks.push(checkbox);
        checkbox.addEventListener('change', () => {
          const done = checks.filter(c => c.checked).length;
          progress.textContent = done + ' of ' + items.length + ' checked';
          row.classList.toggle('done',checkbox.checked);
        });
      });
      const note = document.createElement('p');
      note.className = 'edge-board-note';
      note.textContent = 'Extracted from AI-generated points. Confirm each item is appropriate before acting.';
      board.append(title,progress,list,note);
      message.append(board);
      action.textContent = 'Hide checklist';
    });
  }

  function appendMessage(role, text) {
    const welcome = thread.querySelector('.edge-welcome');
    if (welcome) welcome.remove();

    const item = document.createElement('article');
    item.className = 'edge-message ' + role;
    const heading = document.createElement('div');
    heading.className = 'edge-message-title';
    const label = document.createElement('span');
    label.textContent = role === 'user' ? 'YOU' : role === 'tool' ? '✓ VERIFIED COMPUTATION' : '✦ MUSITU AI';
    heading.append(label);

    if (role !== 'user') {
      const tools = document.createElement('div');
      tools.className = 'edge-reply-tools';
      const checklist = role === 'assistant' ? extractChecklistItems(text) : [];
      if (checklist.length >= 2) installChecklist(item,tools,checklist);
      const copy = document.createElement('button');
      copy.type = 'button';
      copy.className = 'edge-copy';
      copy.textContent = 'Copy';
      copy.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(text);
          copy.textContent = 'Copied ✓';
        } catch {
          copy.textContent = 'Copy unavailable';
        }
      });
      tools.append(copy);
      heading.append(tools);
    }
    const body = role !== 'user' ? renderAnswer(text) : document.createElement('div');
    if (role === 'user') body.textContent = text;
    item.append(heading,body);
    thread.append(item);
    thread.scrollTop = thread.scrollHeight;
  }

  function attachGeneratedImage(data) {
    const item = thread.lastElementChild;
    if (!item || !item.classList.contains('assistant')) return;
    if (typeof data.image !== 'string' || !/^data:image\/(?:jpeg|png);base64,[A-Za-z0-9+/=]+$/.test(data.image)) {
      throw new Error('The generated image was not a valid JPEG data URI.');
    }
    const figure = document.createElement('figure');
    figure.className = 'edge-generated-figure';
    const picture = document.createElement('img');
    picture.src = data.image;
    picture.alt = 'AI-generated image from your description: ' + String(data.prompt || '').slice(0,160);
    picture.loading = 'lazy';
    picture.decoding = 'async';
    const caption = document.createElement('figcaption');
    caption.textContent = 'Generated by ' + String(data.model || 'Cloudflare Workers AI') + ' · AI-created, not an authenticated photograph';
    const download = document.createElement('a');
    download.className = 'edge-download-image';
    download.href = data.image;
    download.download = data.image.startsWith('data:image/png;') ? 'musitu-ai-image.png' : 'musitu-ai-image.jpg';
    download.textContent = '↓ Download image';
    figure.append(picture,caption,download);
    item.append(figure);
    thread.scrollTop = thread.scrollHeight;
  }

  function makeBibliography(records) {
    const escape = value => String(value ?? '').slice(0,220)
      .replace(/\\/g,'\\textbackslash{}')
      .replace(/[{}%$#&_]/g,character=>'\\'+character)
      .replace(/\^/g,'\\^{}').replace(/~/g,'\\~{}')
      .replace(/[\u0000-\u001f\u007f]/g,' ').trim();
    const blocks=[];
    const known=new Set();
    for (const source of records.slice(0,7)) {
      if (source?.source !== 'Crossref' || typeof source.doi !== 'string') continue;
      const doi=source.doi.trim().toLowerCase();
      if(!/^10\.\d{4,9}\/[a-z0-9\-._;()/:]+$/i.test(doi) || known.has(doi))continue;
      known.add(doi);
      const key='musitu_'+doi.replace(/[^a-z0-9]/gi,'_').slice(0,75);
      const type=source.workType==='journal-article'?'article':source.workType==='book'?'book':'misc';
      const fields=[
        ['title',source.title],['doi',doi],['url','https://doi.org/'+doi],
        ['year',Number.isInteger(source.year)?String(source.year):''],
        ['author',Array.isArray(source.authors)?source.authors.slice(0,6).join(' and '):''],
        ['journal',type==='article'?source.journal:''],
        ['publisher',type==='book'?source.publisher:'']
      ];
      blocks.push('@'+type+'{'+key+',\n'+fields.filter(([,value])=>value!==''&&value!==null&&value!==undefined)
        .map(([name,value])=>'  '+name+' = {'+escape(value)+'}').join(',\n')+'\n}');
    }
    return blocks.join('\n\n')+'\n';
  }

  function attachSources(items, scope, citationAudit) {
    const item = thread.lastElementChild;
    if (!item || !item.classList.contains('assistant') || !Array.isArray(items)) return;
    const section = document.createElement('section');
    section.className = 'edge-sources';
    const title = document.createElement('h4');
    const isScholar=items.some(source=>source?.source==='Crossref');
    title.textContent = isScholar ? 'CROSSREF · DOI-REGISTERED PUBLICATIONS' : 'LIVE SOURCES · LINKS YOU CAN VERIFY';
    section.append(title);
    for (const [index, source] of items.slice(0,7).entries()) {
      if (!source || typeof source.url !== 'string') continue;
      let url;
      try { url = new URL(source.url); } catch { continue; }
      if (url.protocol !== 'https:') continue;
      const wikipedia = url.hostname === 'en.wikipedia.org' && url.pathname.startsWith('/wiki/');
      const hackerNews = url.hostname === 'news.ycombinator.com' && url.pathname === '/item';
      const scholar = url.hostname === 'doi.org' && /^\/10\.\d{4,9}\//i.test(url.pathname) && source.source === 'Crossref';
      if (!wikipedia && !hackerNews && !scholar) continue;
      const row = document.createElement('div');
      row.className = 'edge-source-row';
      const link = document.createElement('a');
      link.href = url.href;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = '[' + (index+1) + '] ' + String(source.title || 'View original source').slice(0,150) + ' ↗';
      const provider = document.createElement('small');
      provider.textContent = String(source.source || 'Public website').slice(0,45);
      const summary = document.createElement('p');
      summary.textContent = String(source.snippet || '').slice(0,300);
      row.append(link,provider,summary);
      section.append(row);
    }
    if (isScholar) {
      const entries=makeBibliography(items);
      if(entries.trim()) {
        const button=document.createElement('button');
        button.type='button';
        button.className='edge-export edge-scholar-bibtex';
        button.textContent='↓ Download references (.bib)';
        button.setAttribute('aria-label','Download scholarly references as BibTeX');
        button.addEventListener('click',()=>{
          const blob=new Blob([
            '% Crossref bibliographic metadata only. Not verified full-text findings or confirmed peer review.\n',
            entries
          ],{type:'text/plain;charset=utf-8'});
          const downloadURL=URL.createObjectURL(blob);
          const link=document.createElement('a');
          link.href=downloadURL;
          link.download='musitu-scholar-references.bib';
          link.click();
          setTimeout(()=>URL.revokeObjectURL(downloadURL),1000);
        });
        section.append(button);
      }
    }
    const disclaimer = document.createElement('p');
    disclaimer.className = 'edge-source-note';
    disclaimer.textContent = scope || 'Results are restricted to identified public providers and may be incomplete.';
    section.append(disclaimer);

    if (citationAudit && typeof citationAudit === 'object') {
      const report=document.createElement('div');
      report.className='edge-citation-report';
      const heading=document.createElement('strong');
      heading.className='edge-citation-head';
      const status=String(citationAudit.status || '');
      if (status === 'invalid-indices-removed') {
        heading.textContent='⚠ UNSUPPORTED REFERENCE NUMBERS REMOVED';
        report.dataset.status='warning';
      } else if (status === 'indices-linked') {
        heading.textContent='✓ SOURCE NUMBERS MATCHED';
        report.dataset.status='linked';
      } else {
        heading.textContent='○ NO NUMBERED SOURCE REFERENCES IN ANSWER';
        report.dataset.status='uncited';
      }
      report.append(heading);

      if (status === 'invalid-indices-removed' && Array.isArray(citationAudit.invalidSourceNumbersRemoved)) {
        const removed=document.createElement('p');
        removed.textContent='Unlinked indices: ' + citationAudit.invalidSourceNumbersRemoved.slice(0,8).join(', ') +
          '. These were removed from the AI reply rather than presented as sources.';
        report.append(removed);
      }
      const explanation=document.createElement('p');
      explanation.textContent='Reference numbers were checked against retrieved links ONLY. AI claims and source reliability are NOT fact-checked.';
      report.append(explanation);
      section.append(report);
    }
    item.append(section);
    thread.scrollTop = thread.scrollHeight;
  }

  async function inspectHealth() {
    health.textContent = '● CHECKING';
    try {
      const response = await fetch(service + '/api/health', {
        cache: 'no-store',
        signal: AbortSignal.timeout(12000)
      });
      if (response.ok) {
        const details = await response.json();
        health.textContent = '● EDGE REACHABLE';
        if (details.rateLimit) {
          health.title = details.rateLimit.visitorPerMinute + ' requests/minute per visitor · ' +
            details.rateLimit.regionPerMinute + ' per minute per Cloudflare location';
        }
      } else {
        health.textContent = '● EDGE LIMITED';
      }
    } catch {
      health.textContent = '● CONNECTION UNAVAILABLE';
    }
  }

  function open(modeName = 'explore') {
    selectMode(modeName);
    if (typeof dialog.showModal === 'function') {
      if (!dialog.open) dialog.showModal();
      prompt.focus();
      void inspectHealth();
    } else {
      displayError('Your browser needs dialog support to use the assistant.');
      document.getElementById('ai-studio').scrollIntoView();
    }
  }

  function close() {
    if (dialog.open) dialog.close();
  }

  document.querySelectorAll('[data-ai-mode]').forEach(button => {
    button.addEventListener('click', () => open(button.dataset.aiMode));
  });
  document.querySelectorAll('[data-edge-mode]').forEach(button => {
    button.addEventListener('click', () => selectMode(button.dataset.edgeMode));
  });
  document.getElementById('ai-close').addEventListener('click', close);
  document.querySelectorAll('[data-calc-expression]').forEach(button => {
    button.addEventListener('click', () => {
      selectMode('calculator');
      prompt.value = button.dataset.calcExpression || '';
      prompt.dispatchEvent(new Event('input'));
      prompt.focus();
    });
  });

  prompt.addEventListener('input', () => {
    counter.textContent = prompt.value.length + ' / ' + prompt.maxLength + ' · Enter to send';
  });
  prompt.addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      document.getElementById('edge-form').requestSubmit();
    }
  });

  document.getElementById('edge-form').addEventListener('submit', async event => {
    event.preventDefault();
    if (pending) return;
    const question = prompt.value.trim();
    const requestedMode = mode;
    const mathMode = requestedMode === 'calculator';
    const imageMode = requestedMode === 'image';
    const researchMode = requestedMode === 'research';
    const scholarMode = requestedMode === 'scholar';
    const documentMode = requestedMode === 'document';
    const minimum = mathMode ? 1 : imageMode ? 12 : scholarMode ? 5 : 10;
    const maximum = mathMode ? 140 : imageMode ? 450 : (researchMode || scholarMode) ? 180 : 900;
    if ((question.length < minimum && !( !mathMode && !imageMode && !researchMode && !scholarMode && !documentMode && isShortArithmetic(question))) || question.length > maximum) {
      displayError(mathMode ? 'Enter an expression between 1 and 140 characters.' :
        imageMode ? 'Describe an image between 12 and 450 characters.' :
        researchMode ? 'Search between 10 and 180 characters.' :
        scholarMode ? 'Search scholarly metadata with a 5–180 character topic or title.' :
        'Enter a question between 10 and 900 characters.');
      prompt.focus();
      return;
    }

    if (documentMode) {
      const chosen=documentFile.files?.[0];
      if(!chosen || !SUPPORTED.test(chosen.name) || chosen.name.length>100 || chosen.size<30 || chosen.size>MAX_FILE_SIZE){
        displayError('Choose a UTF-8 .txt, .md, .csv or .json file between 30 bytes and 64 KiB before analyzing.');
        documentFile.focus();return;
      }
    }
    pending = true;
    alert.hidden = true;
    send.disabled = true;
    send.textContent = mathMode ? 'Calculating…' : imageMode ? 'Creating image…' : researchMode ? 'Searching sources…' : scholarMode ? 'Searching DOI metadata…' : documentMode ? 'Analyzing excerpt…' : 'Generating…';
    const earlier = history.slice(-4);
    appendMessage('user', question);
    prompt.value = '';
    counter.textContent = '0 / ' + prompt.maxLength + ' · Enter to send';
    const waiting = document.createElement('p');
    waiting.className = 'edge-waiting';
    waiting.textContent = mathMode ? 'Calculating deterministically…' : imageMode ? 'FLUX is creating your image…' : researchMode ? 'Fetching sources and grounding an answer…' : scholarMode ? 'Retrieving Crossref DOI metadata and synthesizing an overview…' : documentMode ? 'Selecting relevant text locally and analyzing the excerpt with AI…' : 'MUSITU AI is generating…';
    thread.append(waiting);
    thread.scrollTop = thread.scrollHeight;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 75000);
    try {
      let excerptPayload=null;
      if(documentMode){
        const chosen=documentFile.files?.[0];
        if(!chosen || chosen.size>MAX_FILE_SIZE) throw new Error('Invalid or missing file selection.');
        const raw=await chosen.text();
        if(raw.includes('\uFFFD') || /[\u0000-\u0008\u000e-\u001f]/.test(raw)) throw new Error('The file contains binary or undecodable text. Use UTF-8 plain text.');
        const excerpt=selectDocumentExcerpt(raw,question);
        if(excerpt.length<30) throw new Error('Not enough readable text to analyze.');
        excerptPayload={excerpt,fileName:chosen.name};
      }
      const path = mathMode ? '/api/calculate' : imageMode ? '/api/image' : '/api/chat';
      const payload = mathMode ? { expression: question } : imageMode ? { prompt: question } :
        { prompt: question, mode: requestedMode, history: documentMode ? [] : earlier, ...(excerptPayload||{}) };
      const response = await fetch(service + path, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload), signal: controller.signal
      });
      const answer = await response.json();
      if (!response.ok) {
        if (response.status === 429) throw new Error('The service is busy. Try again after about a minute.');
        throw new Error(typeof answer.error === 'string' ? answer.error : 'The operation is unavailable.');
      }
      let visibleAnswer;
      let verifiedTool = mathMode;
      if (mathMode) {
        if (answer.tool !== 'calculator' || typeof answer.result !== 'number' || !Number.isFinite(answer.result))
          throw new Error('The calculator returned an invalid result.');
        visibleAnswer = '### Deterministic result\n' +
          '**Expression:** ' + answer.expression + '\n' +
          '**Result:** ' + String(answer.result) + '\n' +
          '**Verified by:** ' + answer.verifiedBy + '\n' +
          '**Precision:** IEEE-754 double precision (approximate, not exact).';
        health.textContent = '● VERIFIED CALCULATION';
      } else if (imageMode) {
        if (answer.tool !== 'image' || typeof answer.image !== 'string' ||
            !/^data:image\/(?:jpeg|png);base64,/.test(answer.image)) throw new Error('No valid generated image returned.');
        visibleAnswer = '### Image generated\n**Prompt:** ' + question + '\n**Engine:** ' +
          String(answer.model || 'Cloudflare Workers AI') + ' (free-allocation inference).';
        health.textContent = '● REAL AI IMAGE GENERATED';
      } else {
        if (typeof answer.reply !== 'string' || !answer.reply.trim()) throw new Error('The service returned no answer.');
        verifiedTool = answer.toolUsed === 'deterministic_calculator';
        if (verifiedTool && (typeof answer.result !== 'number' || !Number.isFinite(answer.result)))
          throw new Error('An arithmetic answer was returned without verifiable numeric metadata.');
        visibleAnswer = documentMode ? '### Selected text excerpt analysis\n'+answer.reply+'\n\n**Analyzed:** '+String(answer.documentReview?.analyzedCharacters??'unknown')+' characters from '+String(answer.documentReview?.fileName||'selected text')+'. The full file was not analyzed, and AI output may be inaccurate.' : answer.reply;
        health.textContent = verifiedTool ? '● VERIFIED COMPUTATION · NO MODEL' :
          requestedMode === 'deep' ? '● REASONING MODEL RESPONDED' : researchMode ? '● REAL SOURCES RETRIEVED' : scholarMode ? '● SCHOLARLY DOI RECORDS RETRIEVED' : documentMode ? '● SELECTED EXCERPT ANALYZED' : '● LIVE AI RESPONSE VERIFIED';
      }
      if (!verifiedTool && !imageMode && !documentMode) {
        history.push({ role: 'user', content: question }, { role: 'assistant', content: visibleAnswer });
        history = history.slice(-6);
      }
      transcript.push({role:'user',content:question},{role:verifiedTool?'tool':'assistant',content:visibleAnswer});
      transcript=transcript.slice(-80);
      appendMessage(verifiedTool ? 'tool' : 'assistant', visibleAnswer);
      if (imageMode) attachGeneratedImage(answer);
      if (researchMode || scholarMode) attachSources(answer.sources,answer.sourceScope,answer.citationAudit);
      exportButton.disabled = false;
    } catch (failure) {
      prompt.value = question;
      counter.textContent = prompt.value.length + ' / ' + prompt.maxLength + ' · Enter to send';
      displayError(failure && failure.name === 'AbortError' ? 'Request timed out. Try again.' :
        failure instanceof Error ? failure.message : 'Network error. Try again.');
    } finally {
      waiting.remove();
      clearTimeout(timeout);
      pending = false;
      send.disabled = false;
      send.textContent = mode === 'calculator' ? 'Calculate ↗' : mode === 'image' ? 'Generate image ↗' : mode === 'research' ? 'Research sources ↗' : mode === 'scholar' ? 'Find academic papers ↗' : mode === 'document' ? 'Analyze excerpt ↗' : 'Generate answer ↗';
    }
  });

  exportButton.addEventListener('click', () => {
    if (!transcript.length) return;
    const plainText = transcript.map(item => item.role.toUpperCase() + '\n' + item.content).join('\n\n──────\n\n');
    const blob = new Blob(['MUSITU Intelligence Edge\nModel-generated content may be inaccurate; deterministic calculations use IEEE-754 floating point.\n\n' + plainText], {type: 'text/plain'});
    const fileURL = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = fileURL;
    anchor.download = 'musitu-intelligence-edge-chat.txt';
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(fileURL), 1000);
  });

  window.MUSITUEdge = { open, close };
})();