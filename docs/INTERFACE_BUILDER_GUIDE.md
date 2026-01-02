# Newton Interface Builder Guide

## Complete Implementation Reference

---

## Overview

The Newton Interface Builder is a verified UI generation system that transforms natural language intent and template specifications into production-ready interfaces. Built on the "Tiny Tank" pattern (tinyTalk's "No-First" constraint philosophy), every generated interface passes constraint verification before output.

**Philosophy:** "The interface IS the specification. The template IS the constraint."

---

## Architecture

### Three-Layer System

```
L0: GOVERNANCE (tinyTalk Laws)
    ├── Component limit constraints
    ├── Depth limit constraints
    └── Type validation constraints

L1: EXECUTIVE (Blueprint Forges)
    ├── add_component()
    ├── remove_component()
    └── clear()

L2: APPLICATION (REST API)
    ├── GET  /interface/templates
    ├── GET  /interface/templates/{id}
    ├── POST /interface/build
    ├── GET  /interface/components
    └── GET  /interface/info
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `InterfaceBuilder` | Blueprint class with laws and forges |
| `InterfaceBuilderCartridge` | High-level generation interface |
| `TemplateLibrary` | Pre-built template storage |
| `Component` | Verified UI component specification |
| `InterfaceSpec` | Complete interface definition |

---

## Quick Start

### 1. Build from Template (Easiest)

```bash
curl -X POST https://newton-api.onrender.com/interface/build \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "dashboard-basic",
    "variables": {
      "title": "My Dashboard",
      "metric1_value": "98.4%",
      "metric1_label": "Pass Rate"
    },
    "output_format": "all"
  }'
```

### 2. Build from Specification (Custom)

```bash
curl -X POST https://newton-api.onrender.com/interface/build \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "name": "Contact Form",
      "type": "form",
      "layout": "single_column",
      "components": [
        {"id": "title", "type": "heading", "props": {"content": "Contact Us"}},
        {"id": "email", "type": "input", "props": {"placeholder": "Email", "type": "email"}},
        {"id": "message", "type": "textarea", "props": {"placeholder": "Message"}},
        {"id": "submit", "type": "button", "variant": "primary", "props": {"label": "Send"}}
      ]
    },
    "output_format": "jsx"
  }'
```

---

## Available Templates

| Template ID | Name | Type | Description |
|-------------|------|------|-------------|
| `dashboard-basic` | Basic Dashboard | dashboard | Metrics grid with sidebar navigation |
| `form-contact` | Contact Form | form | Simple contact form with validation |
| `empty-state-basic` | Empty State | empty_state | Placeholder with CTA |
| `settings-basic` | Settings Page | settings | Settings with sections and toggles |
| `data-table-basic` | Data Table | data_table | Table with search and actions |
| `landing-hero` | Landing Hero | landing | Hero section for marketing |
| `wizard-basic` | Step Wizard | wizard | Multi-step form wizard |

### Template Variables

Each template accepts variables for customization:

**dashboard-basic:**
```json
{
  "title": "Dashboard",
  "metric1_value": "0",
  "metric1_label": "Total",
  "metric2_value": "0",
  "metric2_label": "Active",
  "metric3_value": "0",
  "metric3_label": "Pending",
  "metric4_value": "0",
  "metric4_label": "Rate"
}
```

**form-contact:**
```json
{
  "title": "Contact Us",
  "submit_label": "Send Message",
  "name_placeholder": "Your Name",
  "email_placeholder": "your@email.com",
  "message_placeholder": "Your message..."
}
```

---

## Component Types

### Layout Components
| Type | Description |
|------|-------------|
| `container` | Generic container div |
| `grid` | CSS Grid layout |
| `flex` | Flexbox layout |
| `sidebar` | Navigation sidebar |
| `header` | Page header |
| `footer` | Page footer |
| `card` | Content card |
| `modal` | Modal dialog |

### Input Components
| Type | Description |
|------|-------------|
| `button` | Clickable button |
| `input` | Text input field |
| `textarea` | Multi-line text input |
| `select` | Dropdown select |
| `checkbox` | Checkbox input |
| `radio` | Radio button |
| `toggle` | Toggle switch |
| `slider` | Range slider |

### Display Components
| Type | Description |
|------|-------------|
| `text` | Paragraph text |
| `heading` | Heading (h1-h6) |
| `badge` | Status badge |
| `metric` | Metric display |
| `code` | Code block |
| `table` | Data table |
| `list` | List items |
| `image` | Image |
| `icon` | Icon |

### Feedback Components
| Type | Description |
|------|-------------|
| `alert` | Alert message |
| `toast` | Toast notification |
| `progress` | Progress bar |
| `spinner` | Loading spinner |
| `skeleton` | Loading skeleton |

---

## Component Specification

### Basic Component

```json
{
  "id": "my-button",
  "type": "button",
  "props": {
    "label": "Click Me"
  },
  "variant": "primary",
  "size": "md",
  "className": "custom-class"
}
```

### Nested Components

```json
{
  "id": "card",
  "type": "card",
  "props": {"title": "Settings"},
  "children": [
    {"id": "toggle-1", "type": "toggle", "props": {"label": "Dark Mode"}},
    {"id": "toggle-2", "type": "toggle", "props": {"label": "Notifications"}}
  ]
}
```

### Variants

| Variant | Use Case |
|---------|----------|
| `primary` | Primary actions (default) |
| `secondary` | Secondary actions |
| `danger` | Destructive actions |
| `success` | Success states |
| `warning` | Warning states |
| `info` | Informational |
| `ghost` | Minimal styling |
| `outline` | Outlined style |
| `link` | Link-like button |

### Sizes

| Size | Description |
|------|-------------|
| `xs` | Extra small |
| `sm` | Small |
| `md` | Medium (default) |
| `lg` | Large |
| `xl` | Extra large |

---

## Layout Patterns

| Pattern | Description |
|---------|-------------|
| `single_column` | Single centered column |
| `two_column` | Two equal columns |
| `three_column` | Three equal columns |
| `sidebar_content` | Sidebar + main content |
| `header_content` | Header + content area |
| `dashboard_grid` | 4-column metrics grid |
| `card_grid` | Responsive card grid |
| `masonry` | Masonry layout |
| `split` | 50/50 split view |

---

## Output Formats

### JSON (Default)
Returns the component tree as a JSON object:

```json
{
  "verified": true,
  "interface": {
    "id": "dashboard-basic_abc123",
    "name": "My Dashboard",
    "type": "dashboard",
    "layout": "sidebar_content",
    "components": [...]
  },
  "fingerprint": "A7F3B2C8E1D4F5A9",
  "elapsed_us": 45.2
}
```

### JSX
Returns React component code:

```jsx
import React from 'react';
import { Button, Input, Card } from '@/components';

export const MyDashboard = () => {
  return (
    <div className="newton-layout">
      <Sidebar productName="My Dashboard">
        <Button variant="ghost">Dashboard</Button>
      </Sidebar>
      <main className="newton-main">
        <header className="newton-header">
          <h1>My Dashboard</h1>
        </header>
      </main>
    </div>
  );
};
```

### HTML
Returns production-ready HTML:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>My Dashboard - Newton Interface Builder</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
    <div class="newton-layout">
        <aside class="newton-sidebar">
            <button class="newton-button newton-button--ghost">Dashboard</button>
        </aside>
        <main class="newton-main">
            <header class="newton-header">My Dashboard</header>
        </main>
    </div>
</body>
</html>
```

### All
Returns all formats in a single response.

---

## API Reference

### GET /interface/templates

List available templates with optional filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query |
| `type` | string | Filter by interface type |
| `tags` | string | Comma-separated tags |

**Example:**
```bash
GET /interface/templates?type=dashboard
GET /interface/templates?query=form
GET /interface/templates?tags=settings,preferences
```

### GET /interface/templates/{template_id}

Get a specific template by ID.

**Response:**
```json
{
  "template": {
    "id": "dashboard-basic",
    "name": "Basic Dashboard",
    "description": "A simple dashboard with metrics and activity feed",
    "type": "dashboard",
    "layout": "sidebar_content",
    "tags": ["dashboard", "metrics", "analytics"],
    "variables": ["title", "metric1_value", "metric1_label", ...]
  }
}
```

### POST /interface/build

Build a verified interface.

**Request Body:**
```json
{
  "template_id": "dashboard-basic",  // OR spec
  "variables": {"title": "My App"},
  "spec": {...},                     // OR template_id
  "output_format": "all"             // json, jsx, html, all
}
```

**Response:**
```json
{
  "verified": true,
  "interface": {...},
  "jsx": "...",
  "html": "...",
  "fingerprint": "A7F3B2C8E1D4F5A9",
  "elapsed_us": 45.2,
  "engine": "Newton Supercomputer 1.0.0"
}
```

### GET /interface/components

List all available component types.

**Response:**
```json
{
  "components": [
    {"value": "button", "name": "BUTTON", "category": "input"},
    {"value": "input", "name": "INPUT", "category": "input"},
    {"value": "card", "name": "CARD", "category": "layout"},
    ...
  ]
}
```

### GET /interface/info

Get Interface Builder capabilities and documentation.

---

## Verification & Constraints

Every interface build is verified against these constraints:

### Component Limit
```python
@law
def component_limit(self):
    """Cannot exceed 100 components."""
    when(len(self.components) > self.max_components, finfr)
```

### Depth Limit
```python
@law
def depth_limit(self):
    """Cannot exceed 10 levels of nesting."""
    when(max_depth > self.max_depth, finfr)
```

### Valid Types
```python
@law
def valid_types(self):
    """All components must have valid types."""
    when(component.type not in allowed_types, finfr)
```

If any constraint is violated, the build fails:

```json
{
  "verified": false,
  "error": "Law violation: component_limit prevents this state",
  "law": "component_limit",
  "elapsed_us": 12.5
}
```

---

## Frontend Deployment

### Cloudflare Pages

```bash
# Navigate to interface-builder directory
cd interface-builder

# Deploy to Cloudflare Pages
npx wrangler pages deploy . --project-name=newton-interface-builder
```

### Local Development

```bash
# Start the API server
cd Newton-api
python newton_supercomputer.py

# Serve the frontend (in another terminal)
cd interface-builder
python -m http.server 3000

# Open http://localhost:3000
```

---

## Integration Examples

### React App

```jsx
import { useState, useEffect } from 'react';

const API_BASE = 'https://newton-api.onrender.com';

function Dashboard() {
  const [interface, setInterface] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/interface/build`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template_id: 'dashboard-basic',
        variables: { title: 'My Dashboard' },
        output_format: 'json'
      })
    })
      .then(res => res.json())
      .then(data => setInterface(data.interface));
  }, []);

  return <DynamicRenderer spec={interface} />;
}
```

### Python Script

```python
import requests

response = requests.post(
    'https://newton-api.onrender.com/interface/build',
    json={
        'template_id': 'form-contact',
        'variables': {'title': 'Contact Us'},
        'output_format': 'html'
    }
)

result = response.json()

if result['verified']:
    with open('contact.html', 'w') as f:
        f.write(result['html'])
    print(f"Generated in {result['elapsed_us']}μs")
else:
    print(f"Error: {result['error']}")
```

### Node.js

```javascript
const fetch = require('node-fetch');

async function buildInterface() {
  const response = await fetch('https://newton-api.onrender.com/interface/build', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      template_id: 'dashboard-basic',
      variables: { title: 'My Dashboard' },
      output_format: 'jsx'
    })
  });

  const result = await response.json();
  console.log(result.jsx);
}
```

---

## Creating Custom Templates

Templates are defined in `tinytalk_py/interface_builder.py`:

```python
self._add_template(Template(
    id="my-custom-template",
    name="My Custom Template",
    description="A custom template for my use case",
    type=InterfaceType.FORM,
    layout=LayoutPattern.SINGLE_COLUMN,
    tags=["custom", "form"],
    variables={
        "title": "Default Title",
        "button_label": "Submit"
    },
    components=[
        Component(
            id="title",
            type=ComponentType.HEADING,
            props={"content": "{{title}}"}
        ),
        Component(
            id="submit",
            type=ComponentType.BUTTON,
            props={"label": "{{button_label}}"},
            variant=Variant.PRIMARY
        )
    ]
))
```

---

## Design System

The Interface Builder uses the Newton Design System:

### Colors
| Token | Value | Use |
|-------|-------|-----|
| `--surface-primary` | #0d0d0d | Background |
| `--accent-primary` | #da7756 | Primary accent (Claude) |
| `--newton-primary` | #4ecdc4 | Verification teal |
| `--success` | #34c759 | Success states |
| `--error` | #ff3b30 | Error states |

### Typography
| Token | Value |
|-------|-------|
| `--font-sans` | SF Pro, Inter, system-ui |
| `--font-mono` | SF Mono, JetBrains Mono |

### Spacing
Based on 4px increments: `--space-1` (4px) through `--space-10` (64px)

### Border Radius
| Token | Value |
|-------|-------|
| `--radius-sm` | 10px |
| `--radius-md` | 14px |
| `--radius-lg` | 20px |

---

## Performance

| Metric | Value |
|--------|-------|
| Template build | ~50μs |
| Custom spec build | ~100μs |
| Max components | 100 |
| Max nesting depth | 10 |

---

## Troubleshooting

### Build Fails with "Law violation"

The interface exceeds a constraint. Check:
- Component count < 100
- Nesting depth < 10
- All component types are valid

### Template Not Found

Verify the template ID exists:
```bash
GET /interface/templates
```

### Connection Issues

Check API health:
```bash
GET /health
```

---

## Support

- **API Docs:** https://newton-api.onrender.com/docs
- **GitHub:** https://github.com/Newton-api
- **Philosophy:** "1 == 1. The cloud is weather. We're building shelter."

---

*© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas*
