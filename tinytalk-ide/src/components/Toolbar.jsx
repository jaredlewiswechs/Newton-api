import React from 'react';

export default function Toolbar({ onParse, onReset, status, parseErrors }) {
  return (
    <div className="ide-toolbar">
      <button className="toolbar-btn secondary" onClick={onParse}>
        Parse
      </button>
      <button className="toolbar-btn danger" onClick={onReset}>
        Reset State
      </button>

      <div className="toolbar-status">
        {parseErrors.length > 0 ? (
          <span style={{ color: 'var(--finfr-color)', fontSize: 12 }}>
            {parseErrors.length} error{parseErrors.length > 1 ? 's' : ''}
          </span>
        ) : (
          <span style={{ color: 'var(--fin-color)', fontSize: 12 }}>
            Parse OK
          </span>
        )}
      </div>
    </div>
  );
}
