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
  let pending = false;
  let history = [];

  function selectMode(next) {
    mode = ['explore', 'build', 'learn', 'markets'].includes(next) ? next : 'explore';
    document.querySelectorAll('[data-edge-mode]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.edgeMode === mode));
    });
  }

  function displayError(message) {
    alert.textContent = message;
    alert.hidden = false;
  }

  function appendMessage(role, text) {
    const welcome = thread.querySelector('.edge-welcome');
    if (welcome) welcome.remove();
    const item = document.createElement('article');
    item.className = 'edge-message ' + role;
    const heading = document.createElement('div');
    heading.className = 'edge-message-title';
    const label = document.createElement('span');
    label.textContent = role === 'user' ? 'YOU' : '✦ MUSITU AI';
    heading.append(label);
    if (role === 'assistant') {
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
      heading.append(copy);
    }
    const body = document.createElement('div');
    body.textContent = text; // Never render model output as unsafe HTML.
    item.append(heading, body);
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
      health.textContent = response.ok ? '● EDGE REACHABLE' : '● EDGE LIMITED';
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

  prompt.addEventListener('input', () => {
    counter.textContent = prompt.value.length + ' / 900 · Enter to send';
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
    if (question.length < 10 || question.length > 900) {
      displayError('Enter a question between 10 and 900 characters.');
      prompt.focus();
      return;
    }
    pending = true;
    alert.hidden = true;
    send.disabled = true;
    send.textContent = 'Generating…';
    const earlier = history.slice(-4);
    appendMessage('user', question);
    prompt.value = '';
    counter.textContent = '0 / 900 · Enter to send';
    const waiting = document.createElement('p');
    waiting.className = 'edge-waiting';
    waiting.textContent = 'MUSITU AI is thinking…';
    thread.append(waiting);
    thread.scrollTop = thread.scrollHeight;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 75000);
    try {
      const response = await fetch(service + '/api/chat', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ prompt: question, mode, history: earlier }),
        signal: controller.signal
      });
      const answer = await response.json();
      if (!response.ok || typeof answer.reply !== 'string' || !answer.reply.trim()) {
        if (response.status === 429) throw new Error('The AI request limit was reached. Try again shortly.');
        throw new Error(typeof answer.error === 'string' ? answer.error : 'The AI response was unavailable.');
      }
      history.push({ role: 'user', content: question }, { role: 'assistant', content: answer.reply });
      history = history.slice(-6);
      appendMessage('assistant', answer.reply);
      exportButton.disabled = false;
      health.textContent = '● LIVE AI RESPONSE VERIFIED';
    } catch (error) {
      prompt.value = question;
      counter.textContent = prompt.value.length + ' / 900 · Enter to send';
      displayError(error && error.name === 'AbortError'
        ? 'The request timed out. Please try again.'
        : error instanceof Error ? error.message : 'Network error. Please try again.');
    } finally {
      waiting.remove();
      clearTimeout(timeout);
      pending = false;
      send.disabled = false;
      send.textContent = 'Generate answer ↗';
    }
  });

  exportButton.addEventListener('click', () => {
    if (!history.length) return;
    const transcript = history.map(item => item.role.toUpperCase() + '\n' + item.content).join('\n\n──────\n\n');
    const blob = new Blob(['MUSITU Intelligence Edge\nModel-generated content may be inaccurate.\n\n' + transcript], {type: 'text/plain'});
    const fileURL = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = fileURL;
    anchor.download = 'musitu-intelligence-edge-chat.txt';
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(fileURL), 1000);
  });

  window.MUSITUEdge = { open, close };
})();