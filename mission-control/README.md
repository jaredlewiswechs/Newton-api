# Newton Mission Control

**Real-time health monitoring and diagnostics for Newton API**

Mission Control is the unified dashboard for testing, monitoring, and diagnosing all Newton Supercomputer services. Think of it as your system administrator console for the Newton ecosystem.

## Features

### 🎯 Unified Dashboard
- Single page showing status of ALL Newton services
- Visual indicators (green/red/yellow/gray) for each endpoint
- Real-time health checks every 30 seconds (configurable)
- Response time tracking for performance monitoring

### 🧪 Interactive Testing
- Click any service to open test panel
- Execute tests with sample data
- View request/response with syntax highlighting
- Copy responses, generate cURL commands
- Download responses as JSON files

### ⚙️ API Configuration
- Toggle between localhost and production environments
- Custom API URL support
- Persistent configuration (localStorage)
- Configurable timeout and refresh intervals
- Export/import configuration

### 🔍 Error Diagnostics
- Automatic CORS detection and reporting
- Network timeout detection with suggestions
- Response time tracking
- Detailed error messages with troubleshooting tips

### 📊 Service Categories

Mission Control monitors these Newton service categories:

- **Core Verification**: `/ask`, `/verify`, `/calculate`, `/constraint`
- **Education**: TEKS standards, lesson planning, assessment analysis
- **Teacher's Aide**: Student tracking, classroom management
- **Grounding**: External evidence verification
- **Statistics**: Adversarial-resistant statistics
- **Jester**: Code constraint analyzer
- **Interface Builder**: UI generation from descriptions
- **Glass Box**: Merkle anchors, negotiator, policies
- **Ledger**: Immutable audit trail
- **Vault**: Encrypted storage
- **Chatbot Compiler**: Governed chatbot requests
- **Voice Interface**: MOAD voice commands
- **Constraint Extractor**: Fuzzy to formal constraints
- **Cartridges**: Specialized computation modules
- **Gumroad**: License management
- **parcCloud**: Authentication gateway
- **System**: Health checks and metrics

## Quick Start

### Option 1: Direct File Access

1. Navigate to the `mission-control` directory
2. Open `index.html` in your browser
3. Select your environment (localhost/production/custom)
4. Click "Test All" to verify all endpoints

### Option 2: Local Web Server

```bash
# Using Python
cd mission-control
python -m http.server 8080

# Using Node.js
npx http-server -p 8080

# Then open http://localhost:8080
```

### Option 3: Integrate with Newton API

If serving through the Newton API itself, add to `newton_supercomputer.py`:

```python
# Serve Mission Control
app.mount("/mission-control", StaticFiles(directory="mission-control", html=True), name="mission-control")
```

Then access at: `http://localhost:8000/mission-control/`

## Usage

### Testing Services

**Test Individual Service:**
1. Click on any service card
2. Review request details
3. Click "Execute Test"
4. View response or error diagnostics

**Test All Services:**
1. Click "Test All" in header
2. Watch as each service is tested sequentially
3. Review results in the grid view

**Auto-Refresh:**
- Enable in Configuration panel
- Set interval (default: 30 seconds)
- Mission Control will automatically test all services

### Configuration

Access via the ⚙️ button in the header:

- **Request Timeout**: Max time for API calls (default: 30000ms)
- **Auto-Refresh**: Enable/disable automatic testing
- **Refresh Interval**: Seconds between auto-tests (default: 30s)

### Diagnostics

**CORS Errors:**
```
💡 CORS Issue: The API server needs to include this origin in its CORS policy.
💡 For local development, ensure the API is running and configured to accept 
   requests from http://localhost:8080
```

**Timeout Errors:**
```
💡 Timeout: Request exceeded 30000ms limit.
💡 Try increasing the timeout in Configuration or check if the endpoint is slow.
```

**Network Errors:**
```
💡 Network Error: Cannot reach the API server.
💡 Check if the API is running at: http://localhost:8000
```

### Logs

The Activity Log (bottom panel) shows:
- All test executions
- Success/error status
- Response times
- Configuration changes

**Log Filters:**
- **All**: Show everything
- **Success**: Only successful tests
- **Errors**: Only failures
- **Warnings**: Only warnings

**Log Actions:**
- Clear logs
- Export logs as JSON
- Toggle panel collapse

## Design Philosophy

Mission Control follows the **NeXTWorkstation** aesthetic:

- **Clean grayscale/monochrome** base colors
- **Status colors** for feedback (green/red/yellow)
- **Grid-based layout** with clear hierarchy
- **System fonts** (SF Pro, SF Mono)
- **Subtle shadows** for depth
- **Professional, technical** appearance
- **Dark mode by default** with light mode toggle

## Integration with Other Apps

Other Newton apps can reference Mission Control for diagnostics:

### In Your App's Error Handler:

```javascript
function handleApiError(error) {
    console.error('API Error:', error);
    
    // Show helpful message
    showError(`
        API request failed. 
        Check Mission Control for diagnostics:
        http://localhost:8000/mission-control/
    `);
}
```

### Shared Configuration:

Apps can reference Mission Control's saved configuration:

```javascript
const config = JSON.parse(
    localStorage.getItem('newton-mission-control-config')
);
const API_BASE = config?.environment === 'production' 
    ? 'https://newton-api-1.onrender.com'
    : 'http://localhost:8000';
```

Note: For best results, use the shared-config.js module instead:
```html
<script src="/shared-config.js"></script>
<script>
  const API_BASE = window.NewtonConfig.API_BASE;
</script>
```

## File Structure

```
mission-control/
├── index.html      # Main dashboard UI
├── app.js          # Application logic
├── styles.css      # NeXT-inspired styling
├── config.js       # API endpoint definitions
└── README.md       # This file
```

## API Endpoint Configuration

All endpoints are defined in `config.js`. To add a new endpoint:

```javascript
export const ENDPOINTS = {
    myCategory: {
        name: 'My Category',
        description: 'Category description',
        endpoints: [
            {
                path: '/my/endpoint',
                method: 'POST',
                name: 'My Endpoint',
                description: 'What this endpoint does',
                sampleData: { /* sample request */ }
            }
        ]
    }
};
```

## Troubleshooting

### "Failed to fetch" errors

1. Check if Newton API is running: `http://localhost:8000/health`
2. Verify CORS is enabled in Newton API
3. Check browser console for detailed errors
4. Try testing from Mission Control's test panel

### Auto-refresh not working

1. Check Configuration → Auto-Refresh is enabled
2. Verify refresh interval is reasonable (5-300 seconds)
3. Check browser console for errors

### Services showing as "Untested"

1. Click "Test All" to test all services
2. Or click individual service cards to test them
3. Check if API base URL is correct in environment selector

### Custom URL not working

1. Ensure URL includes protocol (http:// or https://)
2. Don't include trailing slash
3. Example: `http://192.168.1.100:8000`

## Performance

- **Lightweight**: Vanilla JavaScript, no frameworks
- **Fast**: Grid-based rendering with minimal DOM updates
- **Efficient**: Throttled API calls to avoid overwhelming server
- **Responsive**: Works on desktop and tablet (768px+)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

Requires:
- ES6 Modules
- Fetch API
- LocalStorage
- CSS Grid

## Contributing

When adding new Newton endpoints:

1. Update `config.js` with endpoint definition
2. Include sample data for POST/PUT requests
3. Add to appropriate category
4. Test thoroughly with Mission Control

## License

© 2026 Jared Lewis · Ada Computing Company · Houston, Texas

Part of the Newton Supercomputer project.

---

**"1 == 1. The cloud is weather. We're building shelter."**
