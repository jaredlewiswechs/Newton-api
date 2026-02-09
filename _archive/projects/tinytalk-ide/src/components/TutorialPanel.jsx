import React, { useState } from 'react';

const TUTORIALS = [
  {
    id: 'welcome',
    title: '👋 Welcome to Newton IDE',
    content: `
# Welcome to the Newton IDE

This is a **constraint-first programming environment**.

In traditional programming:
- You write code → hope it works → test after

In Newton:
- You define **laws** (constraints) → code can't violate them → guaranteed safe

## The Philosophy

> "Invalid states cannot be represented."

Every action must pass through the laws before executing. If a law is violated, the action is **forbidden** (finfr).
    `,
  },
  {
    id: 'blueprint',
    title: '📦 Blueprints',
    content: `
# Blueprints

A **blueprint** is like a class, but with built-in verification.

\`\`\`tinytalk
blueprint Account
  # Fields hold state
  field @balance: Real
  
  # Laws enforce constraints
  law NoOverdraft
    when @balance < Real(0)
    finfr
  end
  
  # Forges are verified actions
  forge deposit(amount: Real)
    @balance = @balance + amount
    reply :ok
  end
end
\`\`\`

## Parts of a Blueprint

| Part | Purpose |
|------|---------|
| \`field\` | Holds typed state |
| \`law\` | Enforces constraints |
| \`forge\` | Verified actions |
    `,
  },
  {
    id: 'fields',
    title: '📊 Fields (State)',
    content: `
# Fields

Fields store typed state. Use \`@\` prefix:

\`\`\`tinytalk
field @balance: Real      # floating point
field @count: Count       # integer
field @name: Text         # string
field @active: Bool       # boolean
\`\`\`

## Types

| Type | Description | Example |
|------|-------------|---------|
| \`Real\` | Decimal numbers | \`Real(3.14)\` |
| \`Count\` | Integers | \`Count(42)\` |
| \`Text\` | Strings | \`Text("hello")\` |
| \`Bool\` | True/False | \`Bool(true)\` |

Fields are always initialized. You can set defaults or initialize in a \`reset\` forge.
    `,
  },
  {
    id: 'laws',
    title: '⚖️ Laws (Constraints)',
    content: `
# Laws

Laws define what **cannot happen**. If violated → \`finfr\` (forbidden).

\`\`\`tinytalk
law NoOverdraft
  when @balance < Real(0)
  finfr
end
\`\`\`

This reads: "When balance goes negative → forbidden"

## Conditional Laws

Laws can check the current request:

\`\`\`tinytalk
law NeedsTwoSamples
  when request is :variance
  and @count < Count(2)
  finfr
end
\`\`\`

This law only triggers when calculating variance.

## The Magic

Laws are checked **before** every forge runs. Invalid actions never execute.
    `,
  },
  {
    id: 'forges',
    title: '🔨 Forges (Actions)',
    content: `
# Forges

Forges are **verified actions**. They only run if all laws pass.

\`\`\`tinytalk
forge withdraw(amount: Real)
  @balance = @balance - amount
  reply :ok
end

forge get_balance() -> Real
  reply @balance
end
\`\`\`

## Anatomy of a Forge

\`\`\`tinytalk
forge name(param: Type) -> ReturnType
  # Set request type for conditional laws
  request = :withdraw
  
  # Modify state
  @balance = @balance - param
  
  # Return result
  reply :success
end
\`\`\`

## Forge Execution Flow

1. Parse the forge call
2. Check **all laws** with current state + proposed changes
3. If any law triggers → \`finfr\` (action blocked)
4. If all laws pass → \`fin\` (action executes)
5. State updated, ledger recorded
    `,
  },
  {
    id: 'fin-finfr',
    title: '✅ fin / ❌ finfr',
    content: `
# Understanding fin and finfr

These are the two possible outcomes:

## ✅ fin (Admissible)

The action is **allowed**. All laws passed.

- State will be updated
- Action recorded in ledger
- Returns the \`reply\` value

## ❌ finfr (Forbidden)

The action is **blocked**. A law was violated.

- State is NOT changed
- Action blocked before execution
- Returns which law was violated

## The Witness

Every verification produces a **witness** — cryptographic proof of what happened:

\`\`\`json
{
  "status": "fin",
  "witness": {
    "pre_state": {...},
    "post_state": {...},
    "laws_checked": ["NoOverdraft"],
    "all_passed": true
  }
}
\`\`\`
    `,
  },
  {
    id: 'try-it',
    title: '🚀 Try It!',
    content: `
# Try It Yourself!

## Step 1: Look at the Code

The editor shows a \`StatsSovereign\` blueprint — a statistics calculator that **cannot divide by zero**.

## Step 2: Run a Forge

1. Find the **Forge Runner** panel (top right)
2. Click \`reset()\` to initialize
3. Click \`add_sample\` with x=10
4. Try \`mean()\` — should work!

## Step 3: Break a Law

1. Click \`reset()\` to clear
2. Immediately try \`mean()\`
3. Watch it get **blocked** (finfr!)

Why? The \`NoDivideByZero\` law prevents mean() when count is 0.

## Step 4: Check the Panels

- **Witness**: See the verification proof
- **AST**: See your code's structure  
- **Ω (Omega)**: See the constraint space
- **Ledger**: See the audit trail
- **Output**: See system logs

## You Got It! 🎉

You just used **verified computation**. The constraint IS the instruction.
    `,
  },
  {
    id: 'examples',
    title: '📚 More Examples',
    content: `
# Example Blueprints

Load these from the file tree (left panel):

## StatsSovereign
Statistics with division-by-zero protection.

## InventorySovereign  
Inventory management — can't go negative.

## RiskGovernor
Risk limits — can't exceed thresholds.

## TemperatureController
HVAC control — bounded ranges.

---

## Create Your Own!

\`\`\`tinytalk
blueprint Counter
  field @value: Count
  
  law NoNegative
    when @value < Count(0)
    finfr
  end
  
  forge reset()
    @value = Count(0)
    reply :ok
  end
  
  forge increment()
    @value = @value + Count(1)
    reply @value
  end
  
  forge decrement()
    @value = @value - Count(1)
    reply @value
  end
end
\`\`\`

Try decrementing past zero — the law blocks it!
    `,
  },
];

export default function TutorialPanel({ onLoadExample }) {
  const [currentTutorial, setCurrentTutorial] = useState(0);

  const tutorial = TUTORIALS[currentTutorial];

  const renderMarkdown = (text) => {
    // Simple markdown rendering
    return text
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('# ')) {
          return <h2 key={i} style={{ color: 'var(--accent-color)', marginBottom: 8 }}>{line.slice(2)}</h2>;
        }
        if (line.startsWith('## ')) {
          return <h3 key={i} style={{ color: 'var(--text-primary)', marginTop: 16, marginBottom: 8 }}>{line.slice(3)}</h3>;
        }
        if (line.startsWith('> ')) {
          return <blockquote key={i} style={{ borderLeft: '3px solid var(--accent-color)', paddingLeft: 12, color: 'var(--text-secondary)', fontStyle: 'italic', margin: '8px 0' }}>{line.slice(2)}</blockquote>;
        }
        if (line.startsWith('```')) {
          return null; // Handle code blocks separately
        }
        if (line.startsWith('| ')) {
          return <div key={i} style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--text-secondary)' }}>{line}</div>;
        }
        if (line.startsWith('- ')) {
          return <li key={i} style={{ marginLeft: 16, color: 'var(--text-secondary)' }}>{line.slice(2)}</li>;
        }
        if (line.match(/^\d+\. /)) {
          return <li key={i} style={{ marginLeft: 16, color: 'var(--text-secondary)', listStyleType: 'decimal' }}>{line.replace(/^\d+\. /, '')}</li>;
        }
        if (line.trim() === '') {
          return <br key={i} />;
        }
        // Handle inline formatting
        let formatted = line
          .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
          .replace(/`(.+?)`/g, '<code style="background: var(--bg-secondary); padding: 2px 6px; border-radius: 3px; color: var(--accent-color);">$1</code>');
        return <p key={i} style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }} dangerouslySetInnerHTML={{ __html: formatted }} />;
      });
  };

  // Extract code blocks
  const renderContent = (content) => {
    const parts = content.split(/(```[\s\S]*?```)/g);
    return parts.map((part, i) => {
      if (part.startsWith('```')) {
        const code = part.replace(/```\w*\n?/, '').replace(/```$/, '');
        return (
          <pre key={i} style={{
            background: 'var(--bg-tertiary)',
            padding: 12,
            borderRadius: 6,
            overflow: 'auto',
            fontSize: 12,
            margin: '12px 0',
            border: '1px solid var(--border-color)',
          }}>
            <code style={{ color: 'var(--text-primary)' }}>{code}</code>
          </pre>
        );
      }
      return <div key={i}>{renderMarkdown(part)}</div>;
    });
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', background: 'var(--bg-primary)' }}>
      {/* Tutorial Navigation */}
      <div style={{
        display: 'flex',
        gap: 4,
        padding: '8px 12px',
        borderBottom: '1px solid var(--border-color)',
        overflowX: 'auto',
        flexShrink: 0,
      }}>
        {TUTORIALS.map((t, i) => (
          <button
            key={t.id}
            onClick={() => setCurrentTutorial(i)}
            style={{
              padding: '6px 12px',
              background: currentTutorial === i ? 'var(--accent-color)' : 'var(--bg-secondary)',
              color: currentTutorial === i ? 'white' : 'var(--text-secondary)',
              border: 'none',
              borderRadius: 4,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              fontSize: 12,
              fontWeight: currentTutorial === i ? 600 : 400,
            }}
          >
            {t.title}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
        {renderContent(tutorial.content)}
      </div>

      {/* Navigation */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        padding: 12,
        borderTop: '1px solid var(--border-color)',
        flexShrink: 0,
      }}>
        <button
          onClick={() => setCurrentTutorial(Math.max(0, currentTutorial - 1))}
          disabled={currentTutorial === 0}
          style={{
            padding: '8px 16px',
            background: 'var(--bg-secondary)',
            color: currentTutorial === 0 ? 'var(--text-muted)' : 'var(--text-primary)',
            border: '1px solid var(--border-color)',
            borderRadius: 4,
            cursor: currentTutorial === 0 ? 'not-allowed' : 'pointer',
          }}
        >
          ← Previous
        </button>
        <span style={{ color: 'var(--text-muted)', alignSelf: 'center' }}>
          {currentTutorial + 1} / {TUTORIALS.length}
        </span>
        <button
          onClick={() => setCurrentTutorial(Math.min(TUTORIALS.length - 1, currentTutorial + 1))}
          disabled={currentTutorial === TUTORIALS.length - 1}
          style={{
            padding: '8px 16px',
            background: currentTutorial === TUTORIALS.length - 1 ? 'var(--bg-secondary)' : 'var(--accent-color)',
            color: currentTutorial === TUTORIALS.length - 1 ? 'var(--text-muted)' : 'white',
            border: 'none',
            borderRadius: 4,
            cursor: currentTutorial === TUTORIALS.length - 1 ? 'not-allowed' : 'pointer',
          }}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
