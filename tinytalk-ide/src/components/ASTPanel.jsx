import React, { useState } from 'react';

function ASTNode({ node, depth = 0 }) {
  const [expanded, setExpanded] = useState(depth < 3);

  if (!node || typeof node !== 'object') {
    return <span className="ast-value">{JSON.stringify(node)}</span>;
  }

  if (Array.isArray(node)) {
    if (node.length === 0) return <span className="ast-value">[]</span>;
    return (
      <div className="ast-node">
        <span
          className="ast-key"
          style={{ cursor: 'pointer' }}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '\u25BC' : '\u25B6'} [{node.length}]
        </span>
        {expanded && node.map((item, i) => (
          <div key={i} className="ast-node">
            <span className="ast-key">{i}: </span>
            <ASTNode node={item} depth={depth + 1} />
          </div>
        ))}
      </div>
    );
  }

  const { type, ...rest } = node;
  const displayFields = Object.entries(rest).filter(([k]) =>
    !['line', 'column'].includes(k)
  );

  return (
    <div className="ast-node">
      <span
        style={{ cursor: 'pointer' }}
        onClick={() => setExpanded(!expanded)}
      >
        <span className="ast-key">{expanded ? '\u25BC' : '\u25B6'} </span>
        <span className="ast-type">{type}</span>
        {node.name && <span className="ast-name"> {node.name}</span>}
        {node.value !== undefined && !node.name && (
          <span className="ast-value"> = {JSON.stringify(node.value)}</span>
        )}
        {node.line && (
          <span style={{ color: 'var(--text-muted)', fontSize: 10, marginLeft: 6 }}>
            L{node.line}
          </span>
        )}
      </span>
      {expanded && displayFields.map(([key, val]) => {
        if (key === 'name' || key === 'value') return null;
        return (
          <div key={key} className="ast-node">
            <span className="ast-key">{key}: </span>
            {typeof val === 'object' && val !== null
              ? <ASTNode node={val} depth={depth + 1} />
              : <span className="ast-value">{JSON.stringify(val)}</span>
            }
          </div>
        );
      })}
    </div>
  );
}

export default function ASTPanel({ ast, errors }) {
  if (!ast) {
    return (
      <div className="empty-state">
        <div className="icon">{ }</div>
        <h3>AST Viewer</h3>
        <p>Write TinyTalk code to see the Abstract Syntax Tree.</p>
      </div>
    );
  }

  return (
    <div className="ast-tree">
      {errors && errors.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <div style={{ color: 'var(--finfr-color)', fontSize: 12, fontWeight: 600, marginBottom: 4 }}>
            Errors ({errors.length})
          </div>
          {errors.map((err, i) => (
            <div key={i} style={{
              padding: '4px 8px',
              background: 'rgba(255, 68, 68, 0.08)',
              borderLeft: '3px solid var(--finfr-color)',
              marginBottom: 4,
              fontSize: 12,
            }}>
              <span style={{ color: 'var(--text-muted)' }}>
                {err.phase && `[${err.phase}] `}L{err.line}:{err.column}
              </span>{' '}
              {err.message}
            </div>
          ))}
        </div>
      )}

      <ASTNode node={ast} />
    </div>
  );
}
