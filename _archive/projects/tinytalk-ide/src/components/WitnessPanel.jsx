import React from 'react';

export default function WitnessPanel({ witness, result, state }) {
  if (!result && !witness) {
    return (
      <div className="empty-state">
        <div className="icon">W</div>
        <h3>Witness Panel</h3>
        <p>
          Run or verify a forge to see results here.
          <br />
          Newton will return fin (admissible) or finfr (forbidden) with a witness.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Status card */}
      <div className={`witness-card ${result?.status || 'idle'}`}>
        <div className="witness-header">
          <span className={`witness-badge ${result?.status}`}>
            {result?.status === 'fin' ? 'FIN' : result?.status === 'finfr' ? 'FINFR' : '---'}
          </span>
          <span>
            {result?.status === 'fin'
              ? 'Admissible — transition stays within \u03A9'
              : result?.status === 'finfr'
              ? 'Forbidden — transition exits \u03A9'
              : 'Unknown'}
          </span>
        </div>

        {result?.reply !== null && result?.reply !== undefined && (
          <div className="witness-detail">
            <span className="label">Reply:</span>
            <span style={{ color: 'var(--accent-orange)', fontWeight: 600 }}>
              {typeof result.reply === 'object' ? JSON.stringify(result.reply) : String(result.reply)}
            </span>
          </div>
        )}
      </div>

      {/* Current state */}
      {state && (
        <div className="state-display">
          <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Current State
          </h4>
          {Object.entries(state).map(([key, val]) => (
            <div key={key} className="state-field">
              <span className="field-name">{key}</span>
              <span className="field-value">
                {typeof val === 'object' && val !== null
                  ? `${val.type}(${val.value})`
                  : String(val)}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Witness details (on finfr) */}
      {witness && (
        <div className="witness-card finfr">
          <div className="witness-header">
            <span style={{ color: 'var(--finfr-color)', fontWeight: 600 }}>
              Witness W = (t*, x*, I*, n*)
            </span>
          </div>

          <div className="witness-detail">
            <span className="label">t* (when):</span>
            <span>{witness.t_star}</span>
          </div>

          {witness.x_star && (
            <div className="witness-detail">
              <span className="label">x* (state):</span>
              <span style={{ fontSize: 11 }}>
                {JSON.stringify(witness.x_star, (key, val) => {
                  if (typeof val === 'object' && val?.__type) return `${val.__type}(${val.value})`;
                  return val;
                }, 1)}
              </span>
            </div>
          )}

          {witness.violated && witness.violated.length > 0 && (
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: 11, marginTop: 8, marginBottom: 4 }}>
                I* (violated constraints):
              </div>
              {witness.violated.map((v, i) => (
                <div key={i} className="witness-violation">
                  <div className="law-name">{v.law}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>
                    {v.reason}
                  </div>
                  {v.clauses && v.clauses.length > 0 && (
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                      Clauses: {v.clauses.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {witness.normal_hint && (
            <div className="witness-repair">
              n* (repair hint): {witness.normal_hint}
            </div>
          )}
        </div>
      )}

      {/* Violated laws summary */}
      {result?.violated_laws && result.violated_laws.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 4 }}>
            Violated Laws:
          </div>
          {result.violated_laws.map((law, i) => (
            <span
              key={i}
              style={{
                display: 'inline-block',
                padding: '2px 8px',
                background: 'rgba(255, 68, 68, 0.1)',
                color: 'var(--finfr-color)',
                borderRadius: 3,
                fontSize: 12,
                marginRight: 4,
                marginBottom: 4,
              }}
            >
              {law}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
