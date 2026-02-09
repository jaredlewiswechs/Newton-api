import React, { useRef, useEffect } from 'react';

export default function OutputPanel({ logs }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  if (!logs || logs.length === 0) {
    return (
      <div className="empty-state">
        <div className="icon">&gt;_</div>
        <h3>Output</h3>
        <p>
          Streaming log from Newton verifier.
          <br />
          Parse, verify, and run events will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="output-log">
      {logs.map((entry, i) => (
        <div key={i} className="output-entry">
          <span className="timestamp">{entry.timestamp}</span>
          <span className={`type-badge ${entry.type || 'info'}`}>
            {entry.type || 'info'}
          </span>
          <span className="message">
            {entry.message}
            {entry.status && (
              <span style={{
                color: entry.status === 'fin' ? 'var(--fin-color)' : 'var(--finfr-color)',
                fontWeight: 600,
                marginLeft: 4,
              }}>
                [{entry.status}]
              </span>
            )}
            {entry.reply !== undefined && entry.reply !== null && (
              <span style={{ color: 'var(--accent-orange)', marginLeft: 4 }}>
                = {String(entry.reply)}
              </span>
            )}
            {entry.violated && entry.violated.length > 0 && (
              <span style={{ color: 'var(--finfr-color)', marginLeft: 4 }}>
                violated: {entry.violated.join(', ')}
              </span>
            )}
          </span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
