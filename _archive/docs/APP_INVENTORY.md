# Newton API - Complete App Inventory

## All Apps Available on Vercel

This document lists all applications available at **https://your-project.vercel.app/** after consolidating from the previous deployments.

**Updated: February 1, 2026**

## Core Applications

### Newton Supercomputer
- **URL**: https://your-project.vercel.app/app
- **Alternative**: https://your-project.vercel.app/frontend
- **Description**: Main Newton verification engine interface
- **Directory**: `frontend/`

### Teacher's Aide
- **URL**: https://your-project.vercel.app/teachers
- **Description**: Educational tools and lesson planning
- **Directory**: `teachers-aide/`

### Interface Builder
- **URL**: https://your-project.vercel.app/builder
- **Description**: Visual interface construction tool
- **Directory**: `interface-builder/`

## Development Tools

### Jester Analyzer
- **URL**: https://your-project.vercel.app/jester-analyzer
- **Description**: Code constraint analyzer - extracts guards, assertions, and constraints from source code
- **Features**: 
  - Multi-language support (Python, JavaScript, Swift, etc.)
  - CDL output generation
  - Constraint visualization
- **Directory**: `jester-analyzer/`

### TinyTalk IDE
- **URL**: https://your-project.vercel.app/tinytalk-ide
- **Description**: Integrated development environment for TinyTalk language
- **Features**:
  - Code editor
  - TinyTalk compiler/interpreter
  - Example programs
- **Directory**: `tinytalk-ide/`

### Construct Studio
- **URL**: https://your-project.vercel.app/construct-studio
- **Alternative**: https://your-project.vercel.app/construct-studio/ui
- **Description**: CAD and construction design tools
- **Features**:
  - UI design interface
  - CAD designer
- **Directory**: `construct-studio/`

## Demos & Examples

### Newton Demo
- **URL**: https://your-project.vercel.app/newton-demo
- **Description**: Interactive demo of Newton verification capabilities
- **Features**:
  - Ask Newton interface
  - Break the Rules demo (finfr)
  - Jester code analysis
  - View Newton Laws
- **Directory**: `newton-demo/`

### Games
- **URL**: https://your-project.vercel.app/games
- **Description**: Collection of games built with Newton
- **Available Games**:
  - **Gravity Wars**: https://your-project.vercel.app/games/gravity_wars
- **Directory**: `games/`

## Additional Apps

### ParcCloud
- **URL**: https://your-project.vercel.app/parccloud
- **Description**: Cloud authentication and services
- **Directory**: `parccloud/`

### Newton Phone (Home)
- **URL**: https://your-project.vercel.app/
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

## Deployment Platform

**Primary: Vercel** (as of February 2026)

The Newton API is deployed as a serverless application on Vercel, providing:
- Fast global edge deployment
- Automatic HTTPS
- Zero-config deployments from GitHub
- Serverless functions with Python runtime

### Vercel Configuration

The `vercel.json` file configures the deployment:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/index.py" }
  ]
}
```

### Environment Detection

The API automatically detects when running in a Vercel serverless environment:
- Disables background threads (serverless-safe)
- Uses /tmp for temporary storage
- Optimizes for stateless execution

## Testing Checklist

After deployment, verify these URLs work:

- [ ] https://your-project.vercel.app/ (home)
- [ ] https://your-project.vercel.app/app (Newton app)
- [ ] https://your-project.vercel.app/teachers (Teacher's Aide)
- [ ] https://your-project.vercel.app/builder (Builder)
- [ ] https://your-project.vercel.app/jester-analyzer (Jester)
- [ ] https://your-project.vercel.app/tinytalk-ide (TinyTalk IDE)
- [ ] https://your-project.vercel.app/construct-studio (Construct)
- [ ] https://your-project.vercel.app/newton-demo (Demo)
- [ ] https://your-project.vercel.app/games/gravity_wars (Game)
- [ ] https://your-project.vercel.app/parccloud (ParcCloud)
- [ ] https://your-project.vercel.app/health (API health)

## Support

For issues with specific apps:
- Check the app's directory for README.md
- Verify static files exist in the directory
- Check Vercel deployment logs for errors
- Ensure all dependencies are installed

---

**Last Updated**: February 1, 2026
**Deployment**: Vercel (Serverless)
