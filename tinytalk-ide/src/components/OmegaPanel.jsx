import React from 'react';

export default function OmegaPanel({ omega }) {
  if (!omega || omega.length === 0) {
    return (
      <div className="empty-state">
        <div className="icon">{'\u03A9'}</div>
        <h3>Constraint Space ({'\u03A9'})</h3>
        <p>
          {'\u03A9'} = {'{ x \u2208 S : \u2200 c \u2208 C, c(x) = true }'}
          <br /><br />
          Run or verify to see the admissible constraint space.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>
          {'\u03A9'} = {'{ x \u2208 S : \u2200 c \u2208 C, c(x) = true }'}
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          {omega.length} constraint{omega.length !== 1 ? 's' : ''} define the admissible space
        </div>
      </div>

      {omega.map((constraint, i) => (
        <div key={i} className="omega-constraint">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="name">{constraint.name}</span>
            <span
              className="outcome"
              style={{
                color: constraint.outcome === 'finfr' ? 'var(--finfr-color)' : 'var(--fin-color)',
                fontWeight: 600,
              }}
            >
              {'\u2192'} {constraint.outcome}
            </span>
          </div>
          {constraint.clauses && constraint.clauses.length > 0 && (
            <div className="clauses">
              {constraint.clauses.map((clause, j) => (
                <div key={j} style={{ marginTop: 2 }}>
                  <span style={{ color: 'var(--accent-orange)' }}>
                    {j === 0 ? 'when' : 'and'}
                  </span>{' '}
                  {clause}
                </div>
              ))}
            </div>
          )}
          {constraint.description && (
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              {constraint.description}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
