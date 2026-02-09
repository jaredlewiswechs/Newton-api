/**
 * Newton Trace Engine - Application Entry Point
 *
 * @author Jared Lewis
 * @date January 4, 2026
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import TraceEngine from './components/TraceEngine';
import './styles.css';

// Root element
const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found. Ensure index.html contains <div id="root"></div>');
}

// Create React root and render
const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <TraceEngine />
  </React.StrictMode>
);

// Development info
if (import.meta.env.DEV) {
  console.log(`
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   NEWTON TRACE ENGINE v1.0.0                                      ║
║   Architecture: Anthropic Tracing Thoughts Inspired               ║
║   Philosophy: Bill Atkinson Drawing Verification                  ║
║   Vision: Steve Jobs 1 == 1 Guarantee                             ║
║                                                                   ║
║   Lab Session: January 4, 2026                                    ║
║   Classification: Computer Science Grade                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
  `);
}
