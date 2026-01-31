/**
 * TinyTalk Language Definition for Monaco Editor
 *
 * Syntax highlighting, autocomplete, and hover information
 * for the TinyTalk C implementation.
 * 
 * NOTE: This uses C++-style comments (//) instead of hash (#) for compatibility
 * with the C implementation syntax. The C version treats // as comments.
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
      // Core structure
      'blueprint', 'starts', 'can', 'be', 'when', 'and',
      
      // Control flow  
      'block', 'if', 'must', 'otherwise',
      
      // Actions
      'set', 'to', 'make', 'calc', 'as', 'change', 'by', 'memo',
      
      // String operations
      'uppercase', 'lowercase', 'trim',
      
      // Operators (as keywords)
      'plus', 'minus', 'times', 'div', 'mod',
      'is', 'above', 'below', 'within', 'in',
      
      // Termination
      'fin', 'finfr',
      
      // Standard Kit
      'Screen', 'Clock', 'Random', 'Input', 'Storage',
      
      // Reserved
      'empty', 'true', 'false', 'wanted', 'illegal', 'dead',
    ],

    typeKeywords: [
      // Numeric types
      'Count', 'Real', 'Money', 'Celsius', 'Fahrenheit', 'PSI',
      'Meters', 'Kilometers', 'Miles', 'Feet',
      'Seconds', 'Minutes', 'Hours',
      
      // Other types
      'Boolean', 'String', 'Text',
      'Percent', 'Rate', 'Ratio',
      'Vector', 'Point', 'Color',
    ],

    operators: [
      '+', '-', '*', '/', '&', '#',
      '.', ',', '(', ')', '[', ']',
    ],

    symbols: /[=><!~?:&|+\-*\/#.]+/,

    tokenizer: {
      root: [
        // Comments (// style)
        [/\/\/.*$/, 'comment'],
        
        // Field references (object.field)
        [/[A-Z][a-zA-Z0-9]*\.[a-z_][a-zA-Z0-9_]*/, 'variable.field'],
        
        // Keywords - specific highlighting
        [/\b(blueprint)\b/, 'keyword.blueprint'],
        [/\b(starts|can be)\b/, 'keyword.field'],
        [/\b(when)\b/, 'keyword.when'],
        [/\b(must|block)\b/, 'keyword.constraint'],
        [/\b(set|calc|change|make)\b/, 'keyword.action'],
        [/\b(fin|finfr)\b/, 'keyword.fin'],
        [/\b(if|and|otherwise|to|at|by|as|in)\b/, 'keyword'],
        [/\b(plus|minus|times|div|mod)\b/, 'keyword.operator'],
        [/\b(is|above|below|within)\b/, 'keyword.comparison'],
        [/\b(empty|true|false)\b/, 'constant.language'],
        
        // Standard Kit blueprints
        [/\b(Screen|Clock|Random|Input|Storage)\b/, 'type.standard'],
        
        // Type names (PascalCase)
        [/\b[A-Z][a-zA-Z0-9]*\b/, 'type'],
        
        // Numbers (including negatives)
        [/-?\b\d+(\.\d+)?\b/, 'number'],
        
        // Strings
        [/"[^"]*"/, 'string'],
        
        // Operators
        [/[+\-*\/&#]/, 'operator'],
        
        // Identifiers
        [/[a-z_][a-zA-Z0-9_]*/, 'identifier'],
        
        // Delimiters
        [/[(),.:]/, 'delimiter'],
        
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
      { token: 'keyword.field', foreground: '4FC1FF' },
      { token: 'keyword.when', foreground: 'DCDCAA', fontStyle: 'bold' },
      { token: 'keyword.constraint', foreground: 'FF6B6B', fontStyle: 'bold' },
      { token: 'keyword.action', foreground: '569CD6' },
      { token: 'keyword.fin', foreground: '4EC9B0', fontStyle: 'bold' },
      { token: 'keyword.operator', foreground: 'D4D4D4' },
      { token: 'keyword.comparison', foreground: 'CE9178' },
      { token: 'keyword', foreground: 'C586C0' },
      { token: 'type.standard', foreground: '4EC9B0', fontStyle: 'bold' },
      { token: 'type', foreground: '4EC9B0' },
      { token: 'variable.field', foreground: '9CDCFE', fontStyle: 'bold' },
      { token: 'constant.language', foreground: '569CD0' },
      { token: 'number', foreground: 'B5CEA8' },
      { token: 'string', foreground: 'CE9178' },
      { token: 'identifier', foreground: 'D4D4D4' },
      { token: 'operator', foreground: 'D4D4D4' },
      { token: 'delimiter', foreground: '808080' },
    ],
    colors: {
      'editor.background': '#0D1117',
      'editor.foreground': '#E6EDF3',
      'editor.lineHighlightBackground': '#161B22',
      'editorCursor.foreground': '#58A6FF',
      'editor.selectionBackground': '#264F78',
      'editorLineNumber.foreground': '#484F58',
      'editorLineNumber.activeForeground': '#E6EDF3',
      'editorIndentGuide.background': '#21262D',
      'editorIndentGuide.activeBackground': '#30363D',
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
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: [
            'blueprint ${1:Name}',
            '  starts ${2:field} at ${3:0}',
            '',
            'when ${4:action}',
            '  ${0}',
            'finfr "${5:message}"'
          ].join('\n'),
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Create a new blueprint with fields and actions',
          detail: 'TinyTalk Blueprint Template',
          range,
        },
        {
          label: 'starts',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'starts ${1:field} at ${2:value}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Declare a field with initial value',
          detail: 'Field declaration',
          range,
        },
        {
          label: 'can be',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'can be ${1:state}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Declare a possible state',
          detail: 'State declaration',
          range,
        },
        {
          label: 'when',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: [
            'when ${1:action}',
            '  ${0}',
            'finfr "${2:result}"'
          ].join('\n'),
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Define an action/event handler',
          detail: 'Action handler',
          range,
        },
        {
          label: 'set',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'set ${1:field} to ${2:value}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Assign a value to a field',
          detail: 'Set operation',
          range,
        },
        {
          label: 'calc',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'calc ${1:a} ${2|plus,minus,times,div,mod|} ${3:b} as ${4:result}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Perform calculation and store result',
          detail: 'Calculation',
          range,
        },
        {
          label: 'must',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'must ${1:condition} otherwise "${2:error message}"',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Assert constraint - rolls back transaction if false',
          detail: 'Constraint assertion',
          range,
        },
        {
          label: 'block',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'block if ${1:condition}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Prevent execution if condition is true',
          detail: 'Block statement',
          range,
        },
        {
          label: 'make',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'make ${1:field} ${2:value}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Create or modify a value',
          detail: 'Make operation',
          range,
        },
        {
          label: 'change',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'change ${1:field} by ${2:amount}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Increment or decrement a field',
          detail: 'Change operation',
          range,
        },
        {
          label: 'fin',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'fin',
          documentation: 'Normal termination - stays within valid state space',
          detail: 'Admissible completion',
          range,
        },
        {
          label: 'finfr',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'finfr "${1:message}"',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Final termination - commits transaction and returns result',
          detail: 'Final termination',
          range,
        },
        {
          label: 'Screen.text',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Screen.text',
          documentation: 'Display text on screen',
          detail: 'Standard Kit - Screen',
          range,
        },
        {
          label: 'Screen.color',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Screen.color',
          documentation: 'Set screen color',
          detail: 'Standard Kit - Screen',
          range,
        },
        {
          label: 'Screen.brightness',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Screen.brightness',
          documentation: 'Set screen brightness (0-100)',
          detail: 'Standard Kit - Screen',
          range,
        },
        {
          label: 'Clock.time_of_day',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Clock.time_of_day',
          documentation: 'Current time (0-2400)',
          detail: 'Standard Kit - Clock',
          range,
        },
        {
          label: 'Clock.day_of_week',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Clock.day_of_week',
          documentation: 'Day of week (0-6)',
          detail: 'Standard Kit - Clock',
          range,
        },
        {
          label: 'Clock.paused',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Clock.paused',
          documentation: 'Pause/resume clock',
          detail: 'Standard Kit - Clock',
          range,
        },
        {
          label: 'Random.number',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Random.number',
          documentation: 'Random float 0.0-1.0',
          detail: 'Standard Kit - Random',
          range,
        },
        {
          label: 'Random.percent',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Random.percent',
          documentation: 'Random integer 0-100',
          detail: 'Standard Kit - Random',
          range,
        },
        {
          label: 'Random.dice',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Random.dice',
          documentation: 'Random integer 1-6',
          detail: 'Standard Kit - Random',
          range,
        },
        {
          label: 'Input.mouse_x',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Input.mouse_x',
          documentation: 'Mouse X position',
          detail: 'Standard Kit - Input',
          range,
        },
        {
          label: 'Input.mouse_y',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Input.mouse_y',
          documentation: 'Mouse Y position',
          detail: 'Standard Kit - Input',
          range,
        },
        {
          label: 'Input.keys',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Input.keys',
          documentation: 'Keyboard input',
          detail: 'Standard Kit - Input',
          range,
        },
        {
          label: 'Storage.save_file',
          kind: monaco.languages.CompletionItemKind.Property,
          insertText: 'Storage.save_file',
          documentation: 'Save file path',
          detail: 'Standard Kit - Storage',
          range,
        },
        {
          label: 'memo',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'memo ${1:variable} starts "${2:value}"',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Create a temporary variable',
          detail: 'Temporary variable',
          range,
        },
        {
          label: 'uppercase',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'make ${1:variable} uppercase',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Convert string to uppercase',
          detail: 'String operation',
          range,
        },
        {
          label: 'lowercase',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'make ${1:variable} lowercase',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Convert string to lowercase',
          detail: 'String operation',
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
        'blueprint': { 
          contents: [{ 
            value: '**blueprint** — Define a new type\n\nBlueprints contain fields (state), constraints, and actions.\n\n```tinytalk\nblueprint Player\n  starts health at 100\n```' 
          }] 
        },
        'starts': { 
          contents: [{ 
            value: '**starts** — Declare a field\n\nDefines initial state for a blueprint field.\n\n```tinytalk\nstarts score at 0\nstarts name at "Player"\n```' 
          }] 
        },
        'can': {
          contents: [{
            value: '**can be** — Declare possible state\n\nDefines boolean states a blueprint can have.\n\n```tinytalk\ncan be wanted\ncan be dead\n```'
          }]
        },
        'when': { 
          contents: [{ 
            value: '**when** — Event handler\n\nDefines an action that can be triggered. TinyTalk is Turing complete with bounded loops.\n\n```tinytalk\nwhen attack(damage)\n  calc health minus damage as new_health\n  set health to new_health\nfinfr "Damage applied"\n```' 
          }] 
        },
        'set': { 
          contents: [{ 
            value: '**set** — Assign value\n\nSets a field to a new value.\n\n```tinytalk\nset health to 100\nset Screen.text to "Hello"\n```' 
          }] 
        },
        'calc': { 
          contents: [{ 
            value: '**calc** — Calculation\n\nPerform arithmetic and store result.\n\n```tinytalk\ncalc score plus 10 as new_score\ncalc health minus damage as result\n```\n\nOperators: `plus`, `minus`, `times`, `div`, `mod`' 
          }] 
        },
        'make': {
          contents: [{
            value: '**make** — Create/modify\n\nCreate or modify a value.\n\n```tinytalk\nmake temp 42\n```'
          }]
        },
        'change': {
          contents: [{
            value: '**change** — Increment/decrement\n\nChange a field by an amount.\n\n```tinytalk\nchange score by 10\nchange health by -5\n```'
          }]
        },
        'must': { 
          contents: [{ 
            value: '**must** — Constraint\n\nAssertion that rolls back transaction if false.\n\n```tinytalk\nmust balance is above amount\n  otherwise "Insufficient funds"\n```' 
          }] 
        },
        'block': { 
          contents: [{ 
            value: '**block** — Conditional halt\n\nPrevents execution if condition is true.\n\n```tinytalk\nblock if health is below 0\n```' 
          }] 
        },
        'fin': {
          contents: [{
            value: '**fin** — Normal termination\n\nAdmissible completion - stays within valid state space (Ω).\n\n```tinytalk\nfin\n```'
          }]
        },
        'finfr': { 
          contents: [{ 
            value: '**finfr** — Final termination\n\nCommits transaction and returns result. ACID semantics guaranteed.\n\n```tinytalk\nfinfr "Success!"\nfinfr result\n```' 
          }] 
        },
        'plus': {
          contents: [{
            value: '**plus** — Addition operator\n\nAdd numbers or join strings.\n\n```tinytalk\ncalc 5 plus 3 as sum\n```'
          }]
        },
        'minus': {
          contents: [{
            value: '**minus** — Subtraction operator\n\n```tinytalk\ncalc health minus damage as new_health\n```'
          }]
        },
        'times': {
          contents: [{
            value: '**times** — Multiplication operator\n\n```tinytalk\ncalc price times quantity as total\n```'
          }]
        },
        'div': {
          contents: [{
            value: '**div** — Division operator\n\n```tinytalk\ncalc total div count as average\n```'
          }]
        },
        'mod': {
          contents: [{
            value: '**mod** — Modulo operator\n\n```tinytalk\ncalc value mod 10 as remainder\n```'
          }]
        },
        'is': {
          contents: [{
            value: '**is** — Equality comparison\n\n```tinytalk\nmust balance is above 0\n```'
          }]
        },
        'above': {
          contents: [{
            value: '**above** — Greater than comparison\n\n```tinytalk\nblock if health is above max_health\n```'
          }]
        },
        'below': {
          contents: [{
            value: '**below** — Less than comparison\n\n```tinytalk\nblock if score is below 0\n```'
          }]
        },
        'within': {
          contents: [{
            value: '**within** — Range check\n\n```tinytalk\nmust value is within 0 to 100\n```'
          }]
        },
        'Screen': {
          contents: [{ 
            value: '**Screen** — Standard Kit Blueprint\n\n**Fields:**\n- `text`: Display text\n- `color`: Screen color\n- `brightness`: 0-100\n\n```tinytalk\nset Screen.text to "Hello, World!"\nset Screen.color to "green"\n```' 
          }] 
        },
        'Clock': {
          contents: [{ 
            value: '**Clock** — Standard Kit Blueprint\n\n**Fields:**\n- `time_of_day`: 0-2400 (24hr)\n- `day_of_week`: 0-6\n- `paused`: Boolean\n\n```tinytalk\nset Clock.time_of_day to 1200\n```' 
          }] 
        },
        'Random': {
          contents: [{ 
            value: '**Random** — Standard Kit Blueprint\n\n**Fields:**\n- `number`: Float 0.0-1.0\n- `percent`: Int 0-100\n- `dice`: Int 1-6\n\n```tinytalk\nset chance to Random.percent\n```' 
          }] 
        },
        'Input': {
          contents: [{
            value: '**Input** — Standard Kit Blueprint\n\n**Fields:**\n- `mouse_x`: Mouse X position\n- `mouse_y`: Mouse Y position\n- `keys`: Keyboard input\n\n```tinytalk\nset x to Input.mouse_x\n```'
          }]
        },
        'Storage': {
          contents: [{
            value: '**Storage** — Standard Kit Blueprint\n\n**Fields:**\n- `save_file`: Save file path\n\n```tinytalk\nset Storage.save_file to "game.sav"\n```'
          }]
        },
        'memo': {
          contents: [{
            value: '**memo** — Temporary variable\n\nCreate a temporary variable for intermediate calculations.\n\n```tinytalk\nmemo alert starts "WARNING: " & message\nmake alert uppercase\nset Screen.text to alert\n```'
          }]
        },
        'uppercase': {
          contents: [{
            value: '**uppercase** — Convert to uppercase\n\nConvert a string to uppercase letters.\n\n```tinytalk\nmake message uppercase\n```'
          }]
        },
        'lowercase': {
          contents: [{
            value: '**lowercase** — Convert to lowercase\n\nConvert a string to lowercase letters.\n\n```tinytalk\nmake message lowercase\n```'
          }]
        },
        'wanted': {
          contents: [{
            value: '**wanted** — Boolean state\n\nA state that can be set with "can be wanted".\n\n```tinytalk\ncan be wanted\nmake player wanted\n```'
          }]
        },
        'illegal': {
          contents: [{
            value: '**illegal** — Boolean state\n\nA state that can be checked.\n\n```tinytalk\ncan be illegal\nif item is illegal\n  make player wanted\n```'
          }]
        },
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
