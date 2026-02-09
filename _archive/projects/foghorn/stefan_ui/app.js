const e = React.createElement;

function App() {
  const [prompt, setPrompt] = React.useState('');
  const [omegaJson, setOmegaJson] = React.useState(null);
  const [draft, setDraft] = React.useState('');
  const [verify, setVerify] = React.useState(null);

  async function callIntake() {
    const res = await fetch('/api/intake', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({prompt}) });
    const j = await res.json();
    setOmegaJson(j);
  }

  async function callVerify() {
    if (!omegaJson) return;
    const body = { omega: omegaJson, draft_text: draft };
    const res = await fetch('/api/verify/live', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
    const j = await res.json();
    setVerify(j);
  }

  return e('div', {className:'container'},
    e('h1', null, 'Stefan — Envelope Editor (MVP)'),
    e('textarea', {placeholder:'Paste assignment prompt here', value:prompt, onChange:(ev)=>setPrompt(ev.target.value), rows:4, className:'prompt'}),
    e('div', {className:'controls'},
      e('button', {onClick:callIntake}, 'Extract Ω'),
    ),
    omegaJson && e('pre', {className:'omega'}, JSON.stringify(omegaJson, null, 2)),
    e('h2', null, 'Draft'),
    e('textarea', {placeholder:'Write here...', value:draft, onChange:(ev)=>setDraft(ev.target.value), rows:8, className:'draft'}),
    e('div', {className:'controls'}, e('button', {onClick:callVerify}, 'Run Live Check')),
    verify && e('pre', {className:'verify'}, JSON.stringify(verify, null, 2))
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(e(App));
