import React, { useState, useMemo } from 'react';

export default function ForgeRunner({ ast, currentBlueprint, onVerify, onRun, onRunSequence }) {
  const [selectedForge, setSelectedForge] = useState('');
  const [args, setArgs] = useState({});

  // Extract forges from the current blueprint AST
  const forges = useMemo(() => {
    if (!ast?.blueprints) return [];
    const bp = ast.blueprints.find(b => b.name === currentBlueprint);
    return bp?.forges || [];
  }, [ast, currentBlueprint]);

  const currentForge = forges.find(f => f.name === selectedForge);
  const params = currentForge?.params || [];

  const handleArgChange = (paramName, value) => {
    setArgs(prev => ({ ...prev, [paramName]: parseFloat(value) || 0 }));
  };

  const handleVerify = () => {
    if (!selectedForge) return;
    onVerify(selectedForge, args);
  };

  const handleRun = () => {
    if (!selectedForge) return;
    onRun(selectedForge, args);
  };

  const handleDemo = () => {
    // Demo sequence: reset → add samples → compute mean → try variance
    onRunSequence([
      { forge: 'reset', args: {} },
      { forge: 'add_sample', args: { x: 10 } },
      { forge: 'add_sample', args: { x: 20 } },
      { forge: 'add_sample', args: { x: 30 } },
      { forge: 'mean', args: {} },
      { forge: 'variance', args: {} },
    ]);
  };

  if (forges.length === 0) {
    return (
      <div className="forge-runner">
        <h4>Forge Runner</h4>
        <p style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
          Write a blueprint with forges to run verified actions.
        </p>
      </div>
    );
  }

  return (
    <div className="forge-runner">
      <h4>Forge Runner</h4>

      <select
        className="forge-select"
        value={selectedForge}
        onChange={e => {
          setSelectedForge(e.target.value);
          setArgs({});
        }}
      >
        <option value="">Select a forge...</option>
        {forges.map(f => (
          <option key={f.name} value={f.name}>
            {f.name}({f.params.map(p => `${p.name}: ${p.paramType}`).join(', ')})
            {f.returnType ? ` -> ${f.returnType}` : ''}
          </option>
        ))}
      </select>

      {params.length > 0 && (
        <div className="forge-args">
          {params.map(p => (
            <div key={p.name} className="forge-arg-row">
              <label>{p.name} ({p.paramType})</label>
              <input
                type="number"
                placeholder={`${p.name}`}
                value={args[p.name] || ''}
                onChange={e => handleArgChange(p.name, e.target.value)}
              />
            </div>
          ))}
        </div>
      )}

      <div className="forge-actions">
        <button
          className="toolbar-btn secondary"
          onClick={handleVerify}
          disabled={!selectedForge}
        >
          Verify Only
        </button>
        <button
          className="toolbar-btn primary"
          onClick={handleRun}
          disabled={!selectedForge}
        >
          Run
        </button>
        <button
          className="toolbar-btn secondary"
          onClick={handleDemo}
          style={{ marginLeft: 'auto' }}
        >
          Demo
        </button>
      </div>
    </div>
  );
}
