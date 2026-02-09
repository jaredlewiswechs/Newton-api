import React, { useRef, useEffect } from 'react';
import MonacoEditor from '@monaco-editor/react';
import { registerTinyTalk } from '../language/tinytalk';

let registered = false;

export default function Editor({ source, onChange, errors }) {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);

  function handleEditorWillMount(monaco) {
    if (!registered) {
      registerTinyTalk(monaco);
      registered = true;
    }
    monacoRef.current = monaco;
  }

  function handleEditorDidMount(editor) {
    editorRef.current = editor;
  }

  // Update error markers
  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) return;

    const model = editorRef.current.getModel();
    if (!model) return;

    const markers = (errors || []).map(err => ({
      severity: monacoRef.current.MarkerSeverity.Error,
      message: err.message,
      startLineNumber: err.line || 1,
      startColumn: err.column || 1,
      endLineNumber: err.line || 1,
      endColumn: (err.column || 1) + 10,
    }));

    monacoRef.current.editor.setModelMarkers(model, 'tinytalk', markers);
  }, [errors]);

  return (
    <MonacoEditor
      height="100%"
      language="tinytalk"
      theme="tinytalk-dark"
      value={source}
      onChange={onChange}
      beforeMount={handleEditorWillMount}
      onMount={handleEditorDidMount}
      options={{
        fontSize: 14,
        fontFamily: "'SF Mono', 'Fira Code', 'Cascadia Code', monospace",
        fontLigatures: true,
        minimap: { enabled: false },
        lineNumbers: 'on',
        renderLineHighlight: 'all',
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        tabSize: 2,
        automaticLayout: true,
        padding: { top: 12 },
        smoothScrolling: true,
        cursorBlinking: 'smooth',
        bracketPairColorization: { enabled: true },
      }}
    />
  );
}
