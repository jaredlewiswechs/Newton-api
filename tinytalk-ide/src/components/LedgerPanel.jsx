import React from 'react';

export default function LedgerPanel({ entries }) {
  if (!entries || entries.length === 0) {
    return (
      <div className="empty-state">
        <div className="icon">L</div>
        <h3>Ledger</h3>
        <p>
          Append-only commit log for verified computations.
          <br />
          Each entry records: forge, state before/after, fin/finfr, witness, timestamp.
          <br /><br />
          "Commit only if verified."
        </p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 8 }}>
        {entries.length} ledger entries (append-only, hash-chained)
      </div>

      {[...entries].reverse().map((entry, i) => (
        <div key={i} className="ledger-entry">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
            <span className="forge-name">{entry.forge}</span>
            <span className={`status-tag ${entry.status}`}>{entry.status}</span>
          </div>

          <div className="hash">
            #{entry.index} | {entry.hash} | {entry.timestamp}
          </div>

          {entry.reply !== null && entry.reply !== undefined && (
            <div style={{ marginTop: 4, fontSize: 12 }}>
              <span style={{ color: 'var(--text-secondary)' }}>Reply: </span>
              <span style={{ color: 'var(--accent-orange)' }}>
                {typeof entry.reply === 'object' ? JSON.stringify(entry.reply) : String(entry.reply)}
              </span>
            </div>
          )}

          {entry.args && Object.keys(entry.args).length > 0 && (
            <div style={{ marginTop: 2, fontSize: 11, color: 'var(--text-muted)' }}>
              Args: {JSON.stringify(entry.args)}
            </div>
          )}

          {entry.witness && (
            <div style={{ marginTop: 4, fontSize: 11 }}>
              <span style={{ color: 'var(--finfr-color)' }}>Witness: </span>
              {entry.witness.violated?.map((v, j) => (
                <span key={j} style={{ color: 'var(--text-secondary)' }}>
                  {v.law}{j < entry.witness.violated.length - 1 ? ', ' : ''}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
