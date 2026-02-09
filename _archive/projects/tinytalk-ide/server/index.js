/**
 * TinyTalk IDE Server
 *
 * Express + WebSocket backend providing:
 *   POST /api/parse   → AST + syntax errors
 *   POST /api/verify  → {status: fin|finfr, witness?, violated_laws[]}
 *   POST /api/run     → runs a forge only if verify returns fin
 *   GET  /api/state   → current state of a blueprint instance
 *   GET  /api/omega   → Ω constraint space description
 *   GET  /api/ledger  → append-only ledger entries
 *   POST /api/reset   → reset blueprint instance
 *   GET  /api/examples → list seed examples
 *   GET  /api/examples/:name → get example source
 *   WebSocket /ws     → streaming logs
 */

const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');
const path = require('path');
const fs = require('fs');
const { tokenize } = require('./engine/tokenizer');
const { parse } = require('./engine/parser');
const { Runner } = require('./engine/runner');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

app.use(express.json());

// Serve static frontend (built by Vite)
const distPath = path.join(__dirname, '..', 'dist');
if (fs.existsSync(distPath)) {
  app.use(express.static(distPath));
}

// ── Global Runner ──────────────────────────────────────
const runner = new Runner();

// ── WebSocket Logging ──────────────────────────────────
const wsClients = new Set();

wss.on('connection', (ws) => {
  wsClients.add(ws);
  ws.on('close', () => wsClients.delete(ws));
  broadcastLog({ type: 'info', message: 'Connected to TinyTalk IDE' });
});

function broadcastLog(data) {
  const message = JSON.stringify(data);
  for (const client of wsClients) {
    if (client.readyState === 1) { // OPEN
      client.send(message);
    }
  }
}

// ── API Routes ─────────────────────────────────────────

// POST /api/parse — tokenize + parse, return AST + errors
app.post('/api/parse', (req, res) => {
  const { source } = req.body;
  if (!source) {
    return res.status(400).json({ error: 'Missing source' });
  }

  const { tokens, errors: tokenErrors } = tokenize(source);
  const { ast, errors: parseErrors } = parse(tokens);

  const allErrors = [
    ...tokenErrors.map(e => ({ phase: 'tokenizer', ...e })),
    ...parseErrors.map(e => ({ phase: 'parser', ...e })),
  ];

  broadcastLog({
    type: 'parse',
    message: allErrors.length === 0
      ? `Parsed ${ast.blueprints.length} blueprint(s) successfully`
      : `Parse completed with ${allErrors.length} error(s)`,
    blueprints: ast.blueprints.map(b => b.name),
    errorCount: allErrors.length,
  });

  res.json({
    ast,
    errors: allErrors,
    tokens: tokens.map(t => ({ type: t.type, value: t.value, line: t.line, column: t.column })),
  });
});

// POST /api/verify — load + verify a specific forge
app.post('/api/verify', (req, res) => {
  const { source, blueprint, forge, args } = req.body;
  if (!source) {
    return res.status(400).json({ error: 'Missing source' });
  }

  // Load the source
  const loadResult = runner.load(source);
  if (!loadResult.success) {
    return res.json({
      status: 'finfr',
      errors: loadResult.errors,
      witness: null,
      violated_laws: [],
    });
  }

  // If no blueprint/forge specified, just verify the parse
  if (!blueprint || !forge) {
    return res.json({
      status: 'fin',
      message: 'Source parsed and loaded successfully',
      instances: loadResult.instances,
      omega: loadResult.instances.map(name => ({
        blueprint: name,
        constraints: runner.getOmega(name),
      })),
    });
  }

  const result = runner.verify(blueprint, forge, args || {});

  broadcastLog({
    type: 'verify',
    blueprint,
    forge,
    status: result.status,
    violated: result.violated_laws,
  });

  res.json(result);
});

// POST /api/run — load + run a forge (verify-then-execute)
app.post('/api/run', (req, res) => {
  const { source, blueprint, forge, args } = req.body;
  if (!source || !blueprint || !forge) {
    return res.status(400).json({ error: 'Missing source, blueprint, or forge' });
  }

  // Load the source
  const loadResult = runner.load(source);
  if (!loadResult.success) {
    return res.json({
      status: 'finfr',
      errors: loadResult.errors,
      reply: null,
      state: null,
    });
  }

  const result = runner.run(blueprint, forge, args || {});

  broadcastLog({
    type: 'run',
    blueprint,
    forge,
    status: result.status,
    reply: result.reply,
    violated: result.violated_laws,
  });

  res.json(result);
});

// POST /api/run-sequence — run multiple forges in sequence
app.post('/api/run-sequence', (req, res) => {
  const { source, blueprint, sequence } = req.body;
  if (!source || !blueprint || !sequence) {
    return res.status(400).json({ error: 'Missing source, blueprint, or sequence' });
  }

  const loadResult = runner.load(source);
  if (!loadResult.success) {
    return res.json({ status: 'finfr', errors: loadResult.errors, results: [] });
  }

  const results = [];
  for (const step of sequence) {
    const result = runner.run(blueprint, step.forge, step.args || {});
    results.push({
      forge: step.forge,
      args: step.args,
      ...result,
    });

    broadcastLog({
      type: 'run',
      blueprint,
      forge: step.forge,
      status: result.status,
      reply: result.reply,
    });

    // Stop on finfr if configured
    if (result.status === 'finfr' && step.stopOnFinfr !== false) {
      break;
    }
  }

  res.json({ results });
});

// GET /api/state/:blueprint — current state
app.get('/api/state/:blueprint', (req, res) => {
  const state = runner.getState(req.params.blueprint);
  if (!state) {
    return res.status(404).json({ error: 'Blueprint not found' });
  }
  res.json({ blueprint: req.params.blueprint, state });
});

// GET /api/omega/:blueprint — constraint space
app.get('/api/omega/:blueprint', (req, res) => {
  const omega = runner.getOmega(req.params.blueprint);
  if (!omega) {
    return res.status(404).json({ error: 'Blueprint not found' });
  }
  res.json({ blueprint: req.params.blueprint, omega });
});

// GET /api/ledger/:blueprint — append-only ledger
app.get('/api/ledger/:blueprint', (req, res) => {
  const entries = runner.getLedger(req.params.blueprint);
  if (!entries) {
    return res.status(404).json({ error: 'Blueprint not found' });
  }
  res.json({ blueprint: req.params.blueprint, entries });
});

// POST /api/reset/:blueprint — reset state
app.post('/api/reset/:blueprint', (req, res) => {
  const success = runner.resetInstance(req.params.blueprint);
  if (!success) {
    return res.status(404).json({ error: 'Blueprint not found' });
  }
  res.json({ status: 'fin', message: 'State reset to initial' });
});

// GET /api/blueprints — list loaded
app.get('/api/blueprints', (req, res) => {
  res.json({ blueprints: runner.listBlueprints() });
});

// ── Seed Examples ──────────────────────────────────────
const examplesDir = path.join(__dirname, '..', 'examples');

app.get('/api/examples', (req, res) => {
  try {
    const files = fs.readdirSync(examplesDir)
      .filter(f => f.endsWith('.tt'))
      .map(f => ({
        name: f.replace('.tt', ''),
        filename: f,
      }));
    res.json({ examples: files });
  } catch {
    res.json({ examples: [] });
  }
});

app.get('/api/examples/:name', (req, res) => {
  const filename = `${req.params.name}.tt`;
  const filepath = path.join(examplesDir, filename);
  try {
    const source = fs.readFileSync(filepath, 'utf-8');
    res.json({ name: req.params.name, source });
  } catch {
    res.status(404).json({ error: 'Example not found' });
  }
});

// ── SPA Fallback ───────────────────────────────────────
app.get('*', (req, res) => {
  const indexPath = path.join(distPath, 'index.html');
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(404).json({ error: 'Frontend not built. Run: npm run build' });
  }
});

// ── Start Server ───────────────────────────────────────
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`TinyTalk IDE server running on http://localhost:${PORT}`);
  console.log(`WebSocket available at ws://localhost:${PORT}/ws`);
});

module.exports = { app, server };
