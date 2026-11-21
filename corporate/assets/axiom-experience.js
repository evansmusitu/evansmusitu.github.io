/* Axiom customer explorer — progressive enhancement, local only. No analytics or network calls. */
(() => {
  'use strict';
  const search = document.getElementById('axiom-capability-search');
  if (search) {
    const items = Array.from(document.querySelectorAll('#axiom-directory-results .axiom-operation'));
    const domains = Array.from(document.querySelectorAll('#axiom-directory-results .axiom-domain'));
    const count = document.getElementById('axiom-search-count');
    const empty = document.getElementById('axiom-search-empty');
    const clear = document.getElementById('axiom-search-clear');
    const refresh = () => {
      const terms = search.value.toLowerCase().normalize('NFKD').trim().split(/\s+/).filter(Boolean);
      let shown = 0;
      for (const entry of items) {
        const haystack = (entry.dataset.search || '').normalize('NFKD');
        const match = terms.every(term => haystack.includes(term));
        entry.hidden = !match;
        if (match) shown++;
      }
      for (const section of domains) section.hidden = !section.querySelector('.axiom-operation:not([hidden])');
      empty.hidden = shown !== 0;
      count.textContent = terms.length ? shown + ' of 74 matching capabilities' : 'Showing all 74 capabilities';
    };
    search.addEventListener('input', refresh);
    clear.addEventListener('click', () => {search.value = ''; refresh(); search.focus();});
    refresh();
  }
  const status = document.querySelector('.axiom-copy-status');
  for (const button of document.querySelectorAll('button[data-copy-axiom-prompt]')) {
    button.addEventListener('click', async () => {
      const prompt = button.getAttribute('data-copy-axiom-prompt') || '';
      if (!prompt) return;
      const before = button.textContent;
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('clipboard unavailable');
        await navigator.clipboard.writeText(prompt);
        button.textContent = 'Prompt copied';
        if (status) status.textContent = 'Prompt copied. Paste it into Axiom in ChatGPT.';
      } catch {
        if (status) status.textContent = 'Clipboard access is unavailable. Select and copy the visible starter prompt.';
        button.textContent = before;
        return;
      }
      button.addEventListener('blur', () => {button.textContent = before;}, {once:true});
    });
  }
})();
