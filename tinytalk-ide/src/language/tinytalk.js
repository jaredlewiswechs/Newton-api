/**
 * TinyTalk Language Definition for Monaco Editor
 *
 * Syntax highlighting, autocomplete, and hover information
 * for the frozen TinyTalk lexicon.
 */

export function registerTinyTalk(monaco) {
  // Register the language
  monaco.languages.register({
    id: 'tinytalk',
    extensions: ['.tt'],
    aliases: ['TinyTalk', 'tinytalk'],
  });

  // Monarch tokenizer (syntax highlighting)
  monaco.languages.setMonarchTokensProvider('tinytalk', {
    keywords: [
      'blueprint', 'field', 'law', 'when', 'and',
      'fin', 'finfr', 'forge', 'reply', 'end', 'ground',
      'is', 'request',
    ],

    typeKeywords: [
      'Count', 'Real', 'Money', 'Celsius', 'PSI',
      'Meters', 'Seconds', 'Boolean', 'String', 'Percent',
      'Rate', 'Ratio', 'Vector', 'Point',
    ],

    operators: [
      '=', '==', '!=', '<', '<=', '>', '>=',
      '+', '-', '*', '/', '->'
    ],

    symbols: /[=><!~?:&|+\-*/^%]+/,

    tokenizer: {
      root: [
        // Comments
        [/#.*$/, 'comment'],

        // Field references (@name)
        [/@[a-zA-Z_]\w*/, 'variable.field'],

        // Symbols (:name)
        [/:[a-zA-Z_]\w*/, 'string.symbol'],

        // Keywords
        [/\b(blueprint|field|law|when|and|fin|finfr|forge|reply|end|ground|is|request)\b/, {
          cases: {
            'blueprint': 'keyword.blueprint',
            'field': 'keyword.field',
            'law': 'keyword.law',
            'when': 'keyword.when',
            'and': 'keyword.when',
            'fin': 'keyword.fin',
            'finfr': 'keyword.finfr',
            'forge': 'keyword.forge',
            'reply': 'keyword.reply',
            'end': 'keyword.end',
            'ground': 'keyword.ground',
            '@default': 'keyword',
          }
        }],

        // Type names (PascalCase)
        [/\b[A-Z][a-zA-Z0-9]*\b/, {
          cases: {
            '@typeKeywords': 'type',
            '@default': 'type.identifier',
          }
        }],

        // Numbers
        [/\b\d+(\.\d+)?\b/, 'number'],

        // Strings
        [/"[^"]*"/, 'string'],
        [/'[^']*'/, 'string'],

        // Identifiers
        [/[a-z_]\w*/, 'identifier'],

        // Operators
        [/->/, 'operator.arrow'],
        [/[=<>!]+/, 'operator'],
        [/[+\-*/]/, 'operator'],

        // Delimiters
        [/[(),:.]/, 'delimiter'],

        // Whitespace
        [/\s+/, 'white'],
      ],
    },
  });

  // Theme
  monaco.editor.defineTheme('tinytalk-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
      { token: 'keyword.blueprint', foreground: 'C586C0', fontStyle: 'bold' },
      { token: 'keyword.field', foreground: '4EC9B0' },
      { token: 'keyword.law', foreground: 'FF6B6B', fontStyle: 'bold' },
      { token: 'keyword.when', foreground: 'DCDCAA' },
      { token: 'keyword.fin', foreground: '4EC9B0', fontStyle: 'bold' },
      { token: 'keyword.finfr', foreground: 'FF4444', fontStyle: 'bold' },
      { token: 'keyword.forge', foreground: '569CD6', fontStyle: 'bold' },
      { token: 'keyword.reply', foreground: '9CDCFE' },
      { token: 'keyword.end', foreground: 'C586C0' },
      { token: 'keyword.ground', foreground: 'CE9178' },
      { token: 'keyword', foreground: 'C586C0' },
      { token: 'type', foreground: '4EC9B0' },
      { token: 'type.identifier', foreground: '4EC9B0' },
      { token: 'variable.field', foreground: '9CDCFE', fontStyle: 'bold' },
      { token: 'string.symbol', foreground: 'CE9178' },
      { token: 'number', foreground: 'B5CEA8' },
      { token: 'string', foreground: 'CE9178' },
      { token: 'identifier', foreground: 'D4D4D4' },
      { token: 'operator', foreground: 'D4D4D4' },
      { token: 'operator.arrow', foreground: 'C586C0' },
      { token: 'delimiter', foreground: 'D4D4D4' },
    ],
    colors: {
      'editor.background': '#0D1117',
      'editor.foreground': '#E6EDF3',
      'editor.lineHighlightBackground': '#161B22',
      'editorCursor.foreground': '#58A6FF',
      'editor.selectionBackground': '#264F78',
      'editorLineNumber.foreground': '#484F58',
      'editorLineNumber.activeForeground': '#E6EDF3',
    },
  });

  // Autocomplete
  monaco.languages.registerCompletionItemProvider('tinytalk', {
    provideCompletionItems: (model, position) => {
      const word = model.getWordUntilPosition(position);
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn,
      };

      const suggestions = [
        {
          label: 'blueprint',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'blueprint ${1:Name}\n\n  ${0}\n\nend',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          detail: 'Define a new blueprint',
          documentation: 'Blueprints are the top-level containers in TinyTalk. They hold fields (state), laws (constraints), and forges (actions).',
          range,
        },
        {
          label: 'field',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'field @${1:name}: ${2:Real}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          detail: 'Declare a typed field (state)',
          documentation: 'Fields define the state of a blueprint. Each field has a name and a type.',
          range,
        },
        {
          label: 'law',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'law ${1:Name}\n    when ${2:condition}\n    finfr\n  end',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          detail: 'Define a constraint/invariant',
          documentation: 'Laws define what is FORBIDDEN. When the condition is true, the outcome (fin or finfr) applies.',
          range,
        },
        {
          label: 'when',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'when ${1:condition}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          detail: 'Declare a fact (membership predicate)',
          range,
        },
        {
          label: 'forge',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'forge ${1:name}(${2:params})\n    ${0}\n    reply ${3:value}\n  end',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          detail: 'Define a verified action',
          documentation: 'Forges are actions that mutate state. Newton verifies all laws BEFORE and AFTER execution.',
          range,
        },
        {
          label: 'reply',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'reply ${1:value}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          detail: 'Return a value from a forge',
          range,
        },
        {
          label: 'fin',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'fin',
          detail: 'Admissible completion',
          documentation: 'The state transition is admissible — it stays within Ω.',
          range,
        },
        {
          label: 'finfr',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'finfr',
          detail: 'Forbidden / ontological death',
          documentation: 'The state transition exits Ω — it is structurally forbidden, not an error.',
          range,
        },
        {
          label: 'end',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'end',
          detail: 'Close a block',
          range,
        },
        {
          label: 'ground',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'ground(${1:claim})',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          detail: 'Ground a claim to reality',
          range,
        },
      ];

      return { suggestions };
    },
  });

  // Hover provider
  monaco.languages.registerHoverProvider('tinytalk', {
    provideHover: (model, position) => {
      const word = model.getWordAtPosition(position);
      if (!word) return null;

      const hovers = {
        'blueprint': { contents: [{ value: '**blueprint** — Top-level container\n\nHolds `field` (state), `law` (constraints), and `forge` (actions).' }] },
        'field': { contents: [{ value: '**field** — State declaration\n\n`field @name: Type`\n\nDefines typed state within a blueprint.' }] },
        'law': { contents: [{ value: '**law** — Constraint / Invariant\n\nDefines what is FORBIDDEN. Contains `when`/`and` clauses and a `fin` or `finfr` outcome.' }] },
        'when': { contents: [{ value: '**when** — Membership predicate\n\nDeclares a fact: "when THIS is true..."' }] },
        'and': { contents: [{ value: '**and** — Conjunction\n\nAdditional condition: "...and THIS is also true..."' }] },
        'fin': { contents: [{ value: '**fin** — Admissible completion ✓\n\nThe state transition stays within Ω (admissible constraint space).' }] },
        'finfr': { contents: [{ value: '**finfr** — Forbidden / ontological death ✗\n\nThe state transition exits Ω. This is not an error — it is structurally impossible.' }] },
        'forge': { contents: [{ value: '**forge** — Verified action\n\nAn action that mutates state. Newton verifies all laws BEFORE and AFTER execution.' }] },
        'reply': { contents: [{ value: '**reply** — Return value\n\nReturns a value from a forge execution.' }] },
        'end': { contents: [{ value: '**end** — Block terminator\n\nCloses a `blueprint`, `law`, or `forge` block.' }] },
        'ground': { contents: [{ value: '**ground** — Reality anchor\n\nGrounds a claim to observable reality. Calls are recorded and sourced.' }] },
      };

      const hover = hovers[word.word];
      if (hover) {
        return {
          range: new monaco.Range(position.lineNumber, word.startColumn, position.lineNumber, word.endColumn),
          ...hover,
        };
      }
      return null;
    },
  });
}
