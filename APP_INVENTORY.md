# Newton API - Complete App Inventory

## All Apps Available on Render

This document lists all applications available at **https://newton-api-1.onrender.com/** after consolidating from the Cloudflare Pages deployment.

## Core Applications

### Newton Supercomputer
- **URL**: https://newton-api-1.onrender.com/app
- **Alternative**: https://newton-api-1.onrender.com/frontend
- **Description**: Main Newton verification engine interface
- **Directory**: `frontend/`

### Teacher's Aide
- **URL**: https://newton-api-1.onrender.com/teachers
- **Description**: Educational tools and lesson planning
- **Directory**: `teachers-aide/`

### Interface Builder
- **URL**: https://newton-api-1.onrender.com/builder
- **Description**: Visual interface construction tool
- **Directory**: `interface-builder/`

## Development Tools

### Jester Analyzer
- **URL**: https://newton-api-1.onrender.com/jester-analyzer
- **Description**: Code constraint analyzer - extracts guards, assertions, and constraints from source code
- **Features**: 
  - Multi-language support (Python, JavaScript, Swift, etc.)
  - CDL output generation
  - Constraint visualization
- **Directory**: `jester-analyzer/`

### TinyTalk IDE
- **URL**: https://newton-api-1.onrender.com/tinytalk-ide
- **Description**: Integrated development environment for TinyTalk language
- **Features**:
  - Code editor
  - TinyTalk compiler/interpreter
  - Example programs
- **Directory**: `tinytalk-ide/`

### Construct Studio
- **URL**: https://newton-api-1.onrender.com/construct-studio
- **Alternative**: https://newton-api-1.onrender.com/construct-studio/ui
- **Description**: CAD and construction design tools
- **Features**:
  - UI design interface
  - CAD designer
- **Directory**: `construct-studio/`

## Demos & Examples

### Newton Demo
- **URL**: https://newton-api-1.onrender.com/newton-demo
- **Description**: Interactive demo of Newton verification capabilities
- **Features**:
  - Ask Newton interface
  - Break the Rules demo (finfr)
  - Jester code analysis
  - View Newton Laws
- **Directory**: `newton-demo/`

### Games
- **URL**: https://newton-api-1.onrender.com/games
- **Description**: Collection of games built with Newton
- **Available Games**:
  - **Gravity Wars**: https://newton-api-1.onrender.com/games/gravity_wars
- **Directory**: `games/`

## Additional Apps

### ParcCloud
- **URL**: https://newton-api-1.onrender.com/parccloud
- **Description**: Cloud authentication and services
- **Directory**: `parccloud/`

### Newton Phone (Home)
- **URL**: https://newton-api-1.onrender.com/
- **Description**: Main landing page with app grid (iOS-style interface)
- **File**: `index.html`

## API Endpoints

All API endpoints are available at the same base URL:

### Core API
- `/health` - Health check
- `/metrics` - System metrics
- `/ask` - Newton question answering
- `/verify` - Content verification
- `/calculate` - Verified computation

### Jester API
- `/jester/analyze` - Analyze code for constraints
- `/jester/cdl` - Generate CDL output
- `/jester/info` - Jester capabilities
- `/jester/languages` - Supported languages
- `/jester/constraint-kinds` - Constraint types

### Education API
- `/education/*` - Education cartridge endpoints
- `/teachers/*` - Teacher's Aide API endpoints

### Voice Interface
- `/voice/ask` - Voice query
- `/voice/stream` - Streaming voice
- `/voice/intent` - Intent detection

## Static File Mounts

| Mount Path | Directory | Description |
|------------|-----------|-------------|
| `/frontend` | `frontend/` | Newton Supercomputer app |
| `/teachers` | `teachers-aide/` | Teacher's Aide app |
| `/builder` | `interface-builder/` | Interface Builder |
| `/jester-analyzer` | `jester-analyzer/` | Jester Analyzer |
| `/newton-demo` | `newton-demo/` | Newton Demo |
| `/parccloud` | `parccloud/` | ParcCloud |
| `/tinytalk-ide` | `tinytalk-ide/` | TinyTalk IDE |
| `/construct-studio` | `construct-studio/` | Construct Studio |
| `/games` | `games/` | Games collection |

## Route Handlers

Some routes have dedicated handlers that serve index.html:

- `/` → Root homepage (Newton Phone UI)
- `/app` → Frontend app (Newton Supercomputer)
- `/teachers` → Teacher's Aide
- `/builder` → Interface Builder

These handlers ensure proper Content-Type headers and fallback logic.

## Migration from Cloudflare Pages

All apps previously hosted on `2ec0521e.newton-api.pages.dev` are now available on Render at `newton-api-1.onrender.com`.

### Redirects Handled
The `_redirects` file configured on Cloudflare Pages is no longer needed. All routing is handled by FastAPI:
- Static mounts for directory serving
- Route handlers for main app entry points
- API endpoints for backend functionality

### Benefits of Consolidated Deployment
1. **Single Origin** - No CORS issues
2. **Unified API** - Backend and frontend on same domain
3. **Simpler Deployment** - One deployment instead of two
4. **Consistent URLs** - All apps at newton-api-1.onrender.com

## Testing Checklist

After deployment, verify these URLs work:

- [ ] https://newton-api-1.onrender.com/ (home)
- [ ] https://newton-api-1.onrender.com/app (Newton app)
- [ ] https://newton-api-1.onrender.com/teachers (Teacher's Aide)
- [ ] https://newton-api-1.onrender.com/builder (Builder)
- [ ] https://newton-api-1.onrender.com/jester-analyzer (Jester)
- [ ] https://newton-api-1.onrender.com/tinytalk-ide (TinyTalk IDE)
- [ ] https://newton-api-1.onrender.com/construct-studio (Construct)
- [ ] https://newton-api-1.onrender.com/newton-demo (Demo)
- [ ] https://newton-api-1.onrender.com/games/gravity_wars (Game)
- [ ] https://newton-api-1.onrender.com/parccloud (ParcCloud)
- [ ] https://newton-api-1.onrender.com/health (API health)

## Support

For issues with specific apps:
- Check the app's directory for README.md
- Verify static files exist in the directory
- Check Render logs for mounting errors
- Ensure all dependencies are installed

---

**Last Updated**: 2026-01-31
**Deployment**: https://newton-api-1.onrender.com/
