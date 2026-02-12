const urlInput = document.getElementById('news-url');
const textInput = document.getElementById('news-text');
const btn = document.getElementById('analyze-btn');
const statusEl = document.getElementById('status');
const resultCard = document.getElementById('result-card');

function setStatus(msg) {
  statusEl.textContent = msg;
}

function getAnalyzeEndpoint() {
  if (window.NEO_ANALYZE_ENDPOINT) return window.NEO_ANALYZE_ENDPOINT;

  const path = window.location.pathname;
  if (path.startsWith('/neo')) return '/neo/analyze';
  return '/api/analyze';
}

btn.addEventListener('click', async () => {
  const url = urlInput.value.trim();
  const text = textInput.value.trim();

  if (!url && !text) {
    setStatus('Enter a URL or paste article text.');
    return;
  }

  btn.disabled = true;
  setStatus('Neo is scraping and summarizing...');

  try {
    const res = await fetch(getAnalyzeEndpoint(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url || null, text: text || null })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Analysis failed');

    document.getElementById('article-title').textContent = data.title;
    document.getElementById('agent-response').textContent = data.agent_response;
    document.getElementById('summary').textContent = data.summary;

    const highlights = document.getElementById('highlights');
    highlights.innerHTML = '';
    data.highlights.forEach((item) => {
      const li = document.createElement('li');
      li.textContent = item;
      highlights.appendChild(li);
    });

    const terms = document.getElementById('terms');
    terms.innerHTML = '';
    data.key_terms.forEach((term) => {
      const chip = document.createElement('span');
      chip.textContent = term;
      terms.appendChild(chip);
    });

    document.getElementById('meta').textContent = `Tone: ${data.tone} · Words analyzed: ${data.word_count}`;
    resultCard.hidden = false;
    setStatus('Done.');
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  } finally {
    btn.disabled = false;
  }
});
