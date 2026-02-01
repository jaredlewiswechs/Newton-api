# Newton Phone

The verification layer for AI. What Apple meant to build.

```
1 == 1
```

## Overview

Newton Phone is the standalone frontend for the Newton Supercomputer - an iPhone-inspired home screen that provides access to:

- **Newton** - The core verification supercomputer
- **Teacher's Aide** - NES-compliant lesson planning
- **Builder** - Verified interface generation

## Deployment

This directory is configured for static site deployment on Render.

### Deploy to Render

1. Create a new **Static Site** on Render
2. Connect your GitHub repository
3. Set the **Publish Directory** to `newton-phone`
4. Deploy

The site will automatically:
- Serve the Newton Phone home screen at `/`
- Route to each app: `/app/`, `/teachers/`, `/builder/`
- Connect to the Newton API at `https://newton-api-1.onrender.com`

### Local Development

```bash
cd newton-phone
python -m http.server 3000
# Open http://localhost:3000
```

## Structure

```
newton-phone/
├── index.html      # Newton Phone home screen
├── app/            # Newton Supercomputer app
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── teachers/       # Teacher's Aide app
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── builder/        # Interface Builder app
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── icons/          # App icons
├── graphics/       # Design assets
├── render.yaml     # Render static site config
└── _redirects      # SPA routing rules
```

## API Connection

All apps connect to the Newton API backend:

- **Production**: `https://newton-api-1.onrender.com`
- **Local**: `http://localhost:8000`

The API URL is configured in each app's `app.js` file.

## Apps

### Newton (Main App)
The core verification supercomputer interface:
- Ask View - Natural language queries
- Voice View - Speech interface
- Calculate View - Verified computation
- Orchestrate View - Constraint management
- Ledger View - Blockchain verification

### Teacher's Aide
NES-compliant education tool:
- Lesson planner (5 NES phases)
- TEKS browser (188 K-8 standards)
- Assessment analyzer
- Student grouping
- Differentiation support

### Interface Builder
Verified UI generation:
- Component templates
- Variable configuration
- Code output (Swift/iOS)
- Design system compliance

---

**Newton** - *The constraint is the instruction.*

© 2026 Jared Lewis · Ada Computing Company
