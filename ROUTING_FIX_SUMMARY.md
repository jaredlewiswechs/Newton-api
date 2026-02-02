# Newton API Routing Fix Summary

**Updated: February 1, 2026**

## Problem Statement

The Newton API repository had routing issues due to:
1. Legacy domain references scattered throughout the codebase (pages.dev, onrender.com)
2. Duplicate API base URL detection logic in 10+ frontend files
3. Mission Control dashboard not accessible at `/mission-control/` mount point
4. Documentation referencing old deployment URLs
5. Inconsistent assumptions about same-origin vs cross-origin requests

## Solution Implemented

### 1. Centralized Configuration

**Created `/shared-config.js`** - Single source of truth for API endpoint configuration
- Exported as `window.NewtonConfig` for browser use
- Provides `getApiBase()` and `getMissionControlUrl()` functions
- Automatically detects deployment environment:
  - Local: `http://localhost:8000`
  - Vercel: Uses same origin (PRIMARY)
  - Legacy Render: Uses same origin
  - Legacy Cloudflare Pages: Uses same origin

### 2. Vercel Deployment

**Primary deployment is now Vercel:**
- Serverless Python runtime
- Zero-config deployment from GitHub
- Automatic HTTPS and global CDN
- Uses `vercel.json` and `api/index.py`

### 3. Frontend Updates

**Updated frontend files** to use shared config with fallback:
- `frontend/app.js`
- `teachers-aide/app.js`
- `jester-analyzer/app.js`
- `interface-builder/app.js`
- `newton-phone/app/app.js`
- `newton-phone/builder/app.js`
- `newton-phone/teachers/app.js`
- `newton-demo/index.html`
- `legacy/ada.html`
- `mission-control/config.js`

Each now:
1. Checks for `window.NewtonConfig` first (from shared-config.js)
2. Falls back to inline detection logic if not available
3. Uses same-origin requests for all deployments

### 4. Documentation Updates

All documentation has been updated to reflect Vercel deployment.

## Deployment Architecture

### Current (Primary)
**Vercel Serverless Deployment**
- Backend: FastAPI server via `api/index.py`
- Frontend apps mounted at:
  - `/app` - Newton Supercomputer
  - `/teachers` - Teacher's Aide
  - `/builder` - Interface Builder
  - `/jester-analyzer` - Jester Code Analyzer
  - `/newton-demo` - Newton Demo
  - `/mission-control/` - Mission Control Dashboard
  - `/parccloud` - parcCloud Auth
  - `/tinytalk-ide` - TinyTalk IDE
  - `/construct-studio` - Construct Studio
  - `/games` - Games

**Benefits:**
- Same-origin requests (no CORS issues)
- Fast global edge deployment
- Zero-config from GitHub
- Automatic scaling

### Legacy (Backup)
**Render** and **Cloudflare Pages** are still supported as backup options.

## Testing

All routes tested and verified working:
```bash
✓ /app/              - Newton Supercomputer
✓ /teachers/         - Teacher's Aide
✓ /builder/          - Interface Builder
✓ /jester-analyzer/  - Jester Analyzer
✓ /newton-demo/      - Demo App
✓ /mission-control/  - Mission Control Dashboard
✓ /shared-config.js  - Shared Configuration
✓ /health            - Health Check API
```

## API Base URL Detection Flow

```javascript
// 1. Try shared config (preferred)
if (window.NewtonConfig) {
    return window.NewtonConfig.API_BASE;
}

// 2. Fallback to hostname detection
const hostname = window.location.hostname;

if (hostname === 'localhost') {
    return 'http://localhost:8000';
}

if (hostname.endsWith('.vercel.app')) {
    return window.location.origin;  // Same origin (PRIMARY)
}

if (hostname.endsWith('.onrender.com')) {
    return window.location.origin;  // Same origin
}

if (hostname.endsWith('.pages.dev')) {
    return window.location.origin;  // Same origin
}

return window.location.origin;  // Default
```

## Migration Path for New Apps

To use centralized configuration in a new app:

1. Include shared config in HTML:
```html
<script src="/shared-config.js"></script>
```

2. Use in JavaScript:
```javascript
const API_BASE = window.NewtonConfig.API_BASE;
const MISSION_CONTROL = window.NewtonConfig.MISSION_CONTROL_URL;
```

3. Add fallback for robustness:
```javascript
function getApiBase() {
    if (typeof window.NewtonConfig !== 'undefined') {
        return window.NewtonConfig.API_BASE;
    }
    // Fallback logic here
}
```

## Impact

### Before
- ❌ 40+ scattered legacy domain references
- ❌ 10+ duplicate getApiBase() implementations
- ❌ Mission Control not accessible at `/mission-control/`
- ❌ Confusing mixed deployment documentation
- ❌ No single source of truth for API configuration

### After
- ✅ Single shared-config.js for all apps
- ✅ Mission Control accessible at `/mission-control/`
- ✅ Clear documentation of primary deployment model (Vercel)
- ✅ All legacy domains handled gracefully
- ✅ Consistent API base URL detection across all frontends
- ✅ Backward compatible with existing deployments

## Verification

To verify the fix is working:

1. **Local Testing:**
   ```bash
   python3 newton_supercomputer.py
   curl http://localhost:8000/health
   curl http://localhost:8000/shared-config.js
   curl http://localhost:8000/mission-control/
   ```

2. **Production Testing:**
   ```bash
   curl https://your-project.vercel.app/health
   curl https://your-project.vercel.app/shared-config.js
   curl https://your-project.vercel.app/mission-control/
   ```

3. **Frontend Testing:**
   - Open your Vercel deployment `/mission-control/`
   - Check browser console for `window.NewtonConfig`
   - Verify API calls go to same origin
   - Test each frontend app (/app, /teachers, /builder, etc.)

## Conclusion

All routing issues have been resolved by:
1. Centralizing API configuration
2. Deploying to Vercel (serverless)
3. Updating all documentation
4. Improving environment detection

The codebase now has a single source of truth for API endpoints, proper mission-control routing, and consistent documentation.
