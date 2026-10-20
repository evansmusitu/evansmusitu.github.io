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
    mode = ['explore', 'build', 'learn', 'markets', 'deep', 'calculator'].includes(next) ? next : 'explore';
    const math = mode === 'calculator';
    presets.hidden = !math;
    prompt.maxLength = math ? 140 : 900;
    prompt.placeholder = math ? 'Enter an expression, e.g. 7*(2+3) or sqrt(81)…' :
      mode === 'deep' ? 'Ask a complex question for deliberate analysis…' : 'Ask a question in the selected mode…';
    inputLabel.textContent = math ? 'DETERMINISTIC MATH EXPRESSION' : mode === 'deep' ? 'ASK THE REASONING MODEL' : 'ASK MUSITU AI';
    send.textContent = math ? 'Calculate ↗' : 'Generate answer ↗';
    counter.textContent = prompt.value.length + ' / ' + prompt.maxLength + ' · Enter to send';
    document.querySelectorAll('[data-edge-mode]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.edgeMode === mode));
    });
  }

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
    if ((question.length < (mathMode ? 1 : 10) && !( !mathMode && isShortArithmetic(question))) || question.length > (mathMode ? 140 : 900)) {
      displayError(mathMode ? 'Enter an expression between 1 and 140 characters.' :
        'Enter a question between 10 and 900 characters.');
      prompt.focus();
      return;
    }

    pending = true;
    alert.hidden = true;
    send.disabled = true;
    send.textContent = mathMode ? 'Calculating…' : 'Generating…';
    const earlier = history.slice(-4);
    appendMessage('user', question);
    prompt.value = '';
    counter.textContent = '0 / ' + prompt.maxLength + ' · Enter to send';
    const waiting = document.createElement('p');
    waiting.className = 'edge-waiting';
    waiting.textContent = mathMode ? 'Calculating deterministically…' : 'MUSITU AI is generating…';
    thread.append(waiting);
    thread.scrollTop = thread.scrollHeight;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 75000);
    try {
      const path = mathMode ? '/api/calculate' : '/api/chat';
      const payload = mathMode ? { expression: question } :
        { prompt: question, mode: requestedMode, history: earlier };
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
      } else {
        if (typeof answer.reply !== 'string' || !answer.reply.trim()) throw new Error('The service returned no answer.');
        verifiedTool = answer.toolUsed === 'deterministic_calculator';
        if (verifiedTool && (typeof answer.result !== 'number' || !Number.isFinite(answer.result)))
          throw new Error('An arithmetic answer was returned without verifiable numeric metadata.');
        visibleAnswer = answer.reply;
        health.textContent = verifiedTool ? '● VERIFIED COMPUTATION · NO MODEL' :
          requestedMode === 'deep' ? '● REASONING MODEL RESPONDED' : '● LIVE AI RESPONSE VERIFIED';
      }
      if (!verifiedTool) {
        history.push({ role: 'user', content: question }, { role: 'assistant', content: visibleAnswer });
        history = history.slice(-6);
      }
      transcript.push({role:'user',content:question},{role:verifiedTool?'tool':'assistant',content:visibleAnswer});
      transcript=transcript.slice(-80);
      appendMessage(verifiedTool ? 'tool' : 'assistant', visibleAnswer);
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
      send.textContent = mode === 'calculator' ? 'Calculate ↗' : 'Generate answer ↗';
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