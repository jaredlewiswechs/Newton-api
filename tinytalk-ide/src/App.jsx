import React, { useState, useEffect, useCallback, useRef } from 'react';
import Editor from './components/Editor';
import FileTree from './components/FileTree';
import Toolbar from './components/Toolbar';
import ASTPanel from './components/ASTPanel';
import WitnessPanel from './components/WitnessPanel';
import LedgerPanel from './components/LedgerPanel';
import OutputPanel from './components/OutputPanel';
import OmegaPanel from './components/OmegaPanel';
import ForgeRunner from './components/ForgeRunner';

const DEFAULT_SOURCE = `# ═══════════════════════════════════════════════
# StatsSovereign — No-First Statistics
# "Invalid states cannot be represented"
# ═══════════════════════════════════════════════

blueprint StatsSovereign

  # STATE (typed matter)
  field @n: Count
  field @sum: Real
  field @sum_sq: Real

  # LAWS (vault walls)
  law NonNegativeCount
    when @n < Count(0)
    finfr
  end

  law VarianceNeedsTwoSamples
    when request is :variance
    and @n < Count(2)
    finfr
  end

  law NoDivideByZero
    when request is :mean
    and @n == Count(0)
    finfr
  end

  # FORGES (verified actions)
  forge reset()
    @n = Count(0)
    @sum = Real(0)
    @sum_sq = Real(0)
    reply :ok
  end

  forge add_sample(x: Real)
    @n = @n + Count(1)
    @sum = @sum + x
    @sum_sq = @sum_sq + (x * x)
    reply :added
  end

  forge mean() -> Real
    request = :mean
    reply (@sum / Real(@n))
  end

  forge variance() -> Real
    request = :variance
    mu2 = (@sum * @sum) / Real(@n)
    numerator = @sum_sq - mu2
    denom = Real(@n - Count(1))
    reply (numerator / denom)
  end

end
`;

export default function App() {
  const [source, setSource] = useState(DEFAULT_SOURCE);
  const [ast, setAst] = useState(null);
  const [parseErrors, setParseErrors] = useState([]);
  const [witness, setWitness] = useState(null);
  const [lastRunResult, setLastRunResult] = useState(null);
  const [ledger, setLedger] = useState([]);
  const [omega, setOmega] = useState([]);
  const [logs, setLogs] = useState([]);
  const [activePanel, setActivePanel] = useState('witness');
  const [status, setStatus] = useState('idle'); // idle | fin | finfr
  const [currentBlueprint, setCurrentBlueprint] = useState(null);
  const [examples, setExamples] = useState([]);
  const [currentState, setCurrentState] = useState(null);
  const wsRef = useRef(null);

  // WebSocket connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        addLog(data);
      } catch { /* ignore */ }
    };

    ws.onclose = () => {
      setTimeout(() => {
        // Reconnect silently
      }, 3000);
    };

    return () => ws.close();
  }, []);

  // Load examples on mount
  useEffect(() => {
    fetch('/api/examples')
      .then(r => r.json())
      .then(data => setExamples(data.examples || []))
      .catch(() => {});
  }, []);

  const addLog = useCallback((entry) => {
    setLogs(prev => [...prev.slice(-100), {
      ...entry,
      timestamp: new Date().toLocaleTimeString(),
    }]);
  }, []);

  // Parse on source change (debounced)
  useEffect(() => {
    const timer = setTimeout(() => {
      handleParse();
    }, 500);
    return () => clearTimeout(timer);
  }, [source]);

  const handleParse = async () => {
    try {
      const res = await fetch('/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source }),
      });
      const data = await res.json();
      setAst(data.ast);
      setParseErrors(data.errors || []);

      if (data.ast?.blueprints?.length > 0) {
        setCurrentBlueprint(data.ast.blueprints[0].name);
      }
    } catch (err) {
      addLog({ type: 'error', message: `Parse failed: ${err.message}` });
    }
  };

  const handleVerify = async (forgeName, args) => {
    if (!currentBlueprint) return;

    try {
      const res = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          blueprint: currentBlueprint,
          forge: forgeName,
          args: args || {},
        }),
      });
      const data = await res.json();

      setStatus(data.status || 'idle');
      setWitness(data.witness || null);
      setLastRunResult(data);

      if (data.omega) {
        const bpOmega = data.omega.find(o => o.blueprint === currentBlueprint);
        if (bpOmega) setOmega(bpOmega.constraints);
      }

      setActivePanel('witness');
    } catch (err) {
      addLog({ type: 'error', message: `Verify failed: ${err.message}` });
    }
  };

  const handleRun = async (forgeName, args) => {
    if (!currentBlueprint || !forgeName) return;

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          blueprint: currentBlueprint,
          forge: forgeName,
          args: args || {},
        }),
      });
      const data = await res.json();

      setStatus(data.status || 'idle');
      setWitness(data.witness || null);
      setLastRunResult(data);
      setCurrentState(data.state);

      if (data.ledgerEntry) {
        setLedger(prev => [...prev, data.ledgerEntry]);
      }

      // Refresh omega
      fetchOmega();

      setActivePanel('witness');
    } catch (err) {
      addLog({ type: 'error', message: `Run failed: ${err.message}` });
    }
  };

  const handleRunSequence = async (sequence) => {
    if (!currentBlueprint) return;

    try {
      const res = await fetch('/api/run-sequence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          blueprint: currentBlueprint,
          sequence,
        }),
      });
      const data = await res.json();

      if (data.results && data.results.length > 0) {
        const last = data.results[data.results.length - 1];
        setStatus(last.status);
        setWitness(last.witness);
        setLastRunResult(last);
        setCurrentState(last.state);

        const newEntries = data.results
          .filter(r => r.ledgerEntry)
          .map(r => r.ledgerEntry);
        setLedger(prev => [...prev, ...newEntries]);
      }

      fetchOmega();
    } catch (err) {
      addLog({ type: 'error', message: `Run sequence failed: ${err.message}` });
    }
  };

  const fetchOmega = async () => {
    if (!currentBlueprint) return;
    try {
      const res = await fetch(`/api/omega/${currentBlueprint}`);
      const data = await res.json();
      setOmega(data.omega || []);
    } catch { /* ignore */ }
  };

  const handleReset = async () => {
    if (!currentBlueprint) return;
    try {
      await fetch(`/api/reset/${currentBlueprint}`, { method: 'POST' });
      setWitness(null);
      setLastRunResult(null);
      setStatus('idle');
      setCurrentState(null);
      setLedger([]);
      addLog({ type: 'info', message: `${currentBlueprint} state reset` });
    } catch { /* ignore */ }
  };

  const handleLoadExample = async (name) => {
    try {
      const res = await fetch(`/api/examples/${name}`);
      const data = await res.json();
      if (data.source) {
        setSource(data.source);
        setWitness(null);
        setLastRunResult(null);
        setLedger([]);
        setStatus('idle');
        setCurrentState(null);
      }
    } catch { /* ignore */ }
  };

  const panels = {
    witness: <WitnessPanel witness={witness} result={lastRunResult} state={currentState} />,
    ast: <ASTPanel ast={ast} errors={parseErrors} />,
    omega: <OmegaPanel omega={omega} />,
    ledger: <LedgerPanel entries={ledger} />,
    output: <OutputPanel logs={logs} />,
  };

  return (
    <div className="ide-container">
      <header className="ide-header">
        <h1>
          <span className="logo">TinyTalk</span>
          <span className="subtitle">No-First Programming Environment</span>
        </h1>
        <div className="toolbar-status">
          <span className={`status-dot ${status}`} />
          <span style={{ color: status === 'fin' ? 'var(--fin-color)' : status === 'finfr' ? 'var(--finfr-color)' : 'var(--text-muted)' }}>
            {status === 'fin' ? 'Admissible' : status === 'finfr' ? 'Forbidden' : 'Ready'}
          </span>
          {currentBlueprint && (
            <span style={{ color: 'var(--text-secondary)', marginLeft: 8 }}>
              [{currentBlueprint}]
            </span>
          )}
        </div>
      </header>

      <div className="ide-body">
        <FileTree
          examples={examples}
          onLoadExample={handleLoadExample}
          currentBlueprint={currentBlueprint}
        />

        <div className="ide-main">
          <Toolbar
            onParse={handleParse}
            onReset={handleReset}
            status={status}
            parseErrors={parseErrors}
          />

          <div className="ide-split">
            <div className="editor-pane">
              <Editor source={source} onChange={setSource} errors={parseErrors} />
            </div>

            <div className="panels-pane">
              <ForgeRunner
                ast={ast}
                currentBlueprint={currentBlueprint}
                onVerify={handleVerify}
                onRun={handleRun}
                onRunSequence={handleRunSequence}
              />

              <div className="panel-tabs">
                {['witness', 'ast', 'omega', 'ledger', 'output'].map(tab => (
                  <button
                    key={tab}
                    className={`panel-tab ${activePanel === tab ? 'active' : ''}`}
                    onClick={() => setActivePanel(tab)}
                  >
                    {tab === 'witness' ? 'Witness' :
                     tab === 'ast' ? 'AST' :
                     tab === 'omega' ? '\u03A9' :
                     tab === 'ledger' ? 'Ledger' : 'Output'}
                  </button>
                ))}
              </div>

              <div className="panel-content">
                {panels[activePanel]}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
