# Newton API Routing Fix Summary

## Problem Statement

The Newton API repository had routing issues due to:
1. Legacy domain references scattered throughout the codebase (pages.dev, newton-api-sicp.onrender.com)
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
  - Render: Uses same origin (e.g., `https://newton-api-1.onrender.com`)
  - Legacy Cloudflare Pages: Points to Render API

### 2. Server Updates

**Updated `newton_supercomputer.py`:**
- Added `/mission-control/` StaticFiles mount point
- Added `/shared-config.js` endpoint to serve shared configuration
- Maintained backward compatibility with root-level mission-control files
- All frontend apps are now properly mounted with `html=True` for SPA support

### 3. Frontend Updates

**Updated 10 frontend files** to use shared config with fallback:
- `frontend/app.js`
- `teachers-aide/app.js`
- `jester-analyzer/app.js`
- `interface-builder/app.js`
- `newton-phone/app/app.js`
- `newton-phone/builder/app.js`
- `newton-phone/teachers/app.js`
- `newton-demo/index.html`
- `legacy/ada.html`
- `mission-control/config.js` (already had correct logic)

Each now:
1. Checks for `window.NewtonConfig` first (from shared-config.js)
2. Falls back to inline detection logic if not available
3. Consistently uses `newton-api-1.onrender.com` as production API

### 4. Documentation Updates

**Replaced ~40+ references** to legacy domains:
- ❌ `75ac0fae.newton-api.pages.dev` → ✅ `newton-api-1.onrender.com`
- ❌ `2ec0521e.newton-api.pages.dev` → ✅ `newton-api-1.onrender.com`
- ❌ `newton-api-sicp.onrender.com` → ✅ `newton-api-1.onrender.com`
- ❌ `newton-api.pages.dev` → ✅ `newton-api-1.onrender.com`
- ❌ `newton-teachers-aide.pages.dev` → ✅ `newton-api-1.onrender.com/teachers`
- ❌ `newton-interface-builder.pages.dev` → ✅ `newton-api-1.onrender.com/builder`

**Updated files:**
- `DEPLOYMENT.md` - Fixed production URLs section
- `mission-control/README.md` - Updated example code
- `docs/HELLO_WORLD.md`, `docs/NEWTON_ON_ACID.md`, `docs/NEWTON_STEVE_JOBS_CRYSTALLIZATION.md` - Fixed URLs
- `docs/WWDC_PREPARATION.md` - Updated deployment table
- `teachers-aide/README.md`, `newton-phone/teachers/README.md` - Fixed references
- `interface-builder/README.md`, `newton-phone/builder/README.md` - Fixed references
- `interface-builder/deploy.sh`, `newton-phone/builder/deploy.sh` - Updated output URLs
- `newton-phone/README.md` - Fixed API references
- `frontend/index.html`, `newton-phone/index.html` - Updated hardcoded links
- `.github/workflows/cloudflare-pages.yml` - Added note about primary deployment
- `newton-phone/render.yaml` - Updated comments

## Deployment Architecture

### Current (Primary)
**All-in-one Render Deployment:** `https://newton-api-1.onrender.com`
- Backend: FastAPI server at root
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
- Single deployment to manage
- Simplified routing
- Consistent URLs

### Legacy (Backup)
**Cloudflare Pages:** Static frontends can still be deployed separately
- Frontends automatically detect Cloudflare Pages domain
- Point to `newton-api-1.onrender.com` for API calls
- CORS is configured on server to allow this
- Useful for testing or CDN distribution

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

if (hostname.endsWith('.onrender.com')) {
    return window.location.origin;  // Same origin
}

if (hostname.endsWith('.pages.dev')) {
    return 'https://newton-api-1.onrender.com';  // Cross-origin
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

## Remaining References

These references are acceptable and should remain:
- `.pages.dev` domain detection in API base URL logic (needed for Cloudflare Pages support)
- `pages.dev` in comments explaining legacy deployment model
- Documentation explaining the migration from Cloudflare Pages to Render

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
- ✅ Clear documentation of primary deployment model
- ✅ All legacy domains updated to newton-api-1.onrender.com
- ✅ Consistent API base URL detection across all frontends
- ✅ Backward compatible with existing deployments

## Files Changed

**Phase 1 - Core Infrastructure:**
- `shared-config.js` (new)
- `newton_supercomputer.py`

**Phase 2 - Frontend Apps:**
- 10 app.js/HTML files updated

**Phase 3 - Documentation:**
- 16 documentation/config files updated

**Total:** 28 files modified, 1 file created

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
   curl https://newton-api-1.onrender.com/health
   curl https://newton-api-1.onrender.com/shared-config.js
   curl https://newton-api-1.onrender.com/mission-control/
   ```

3. **Frontend Testing:**
   - Open `https://newton-api-1.onrender.com/mission-control/`
   - Check browser console for `window.NewtonConfig`
   - Verify API calls go to same origin
   - Test each frontend app (/app, /teachers, /builder, etc.)

## Conclusion

All routing issues have been resolved by:
1. Centralizing API configuration
2. Adding proper static file mounts
3. Updating all legacy domain references
4. Improving documentation clarity

The codebase now has a single source of truth for API endpoints, proper mission-control routing, and consistent documentation.
