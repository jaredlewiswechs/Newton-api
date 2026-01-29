import React from 'react';

export default function FileTree({ examples, onLoadExample, currentBlueprint }) {
  return (
    <div className="ide-sidebar">
      <div className="sidebar-header">Examples</div>
      {examples.map(ex => (
        <div
          key={ex.name}
          className={`sidebar-item ${currentBlueprint === ex.name ? 'active' : ''}`}
          onClick={() => onLoadExample(ex.name)}
        >
          <span className="icon">tt</span>
          <span>{ex.name}</span>
        </div>
      ))}

      {examples.length === 0 && (
        <>
          <div
            className="sidebar-item active"
            onClick={() => {}}
          >
            <span className="icon">tt</span>
            <span>StatsSovereign</span>
          </div>
        </>
      )}

      <div className="sidebar-header" style={{ marginTop: 16 }}>Blueprints</div>
      {currentBlueprint && (
        <div className="sidebar-item active">
          <span className="icon">bp</span>
          <span>{currentBlueprint}</span>
        </div>
      )}

      <div className="sidebar-header" style={{ marginTop: 16 }}>Architecture</div>
      <div className="sidebar-item" style={{ color: 'var(--accent-cyan)', fontSize: 11 }}>
        <span className="icon">N</span>
        <span>Newton (Verifier)</span>
      </div>
      <div className="sidebar-item" style={{ color: 'var(--accent-purple)', fontSize: 11 }}>
        <span className="icon">A</span>
        <span>Ada (Assistant)</span>
      </div>
      <div className="sidebar-item" style={{ color: 'var(--accent-orange)', fontSize: 11 }}>
        <span className="icon">C</span>
        <span>Commander (You)</span>
      </div>
    </div>
  );
}
