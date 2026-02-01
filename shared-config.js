/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON SHARED CONFIGURATION
 * Single source of truth for API endpoint configuration
 * 
 * This module is used by all Newton frontend applications to determine
 * the correct API base URL based on the deployment environment.
 * 
 * © 2026 Jared Lewis · Ada Computing Company
 * ═══════════════════════════════════════════════════════════════════════════
 */

/**
 * Determine API base URL based on deployment environment.
 * 
 * Deployment model:
 * - Local: API at http://localhost:8000
 * - Render: All-in-one deployment at newton-api-1.onrender.com (API + static frontends)
 * - Legacy Cloudflare Pages: Static frontends point to Render API
 * 
 * @returns {string} The API base URL
 */
function getApiBase() {
    const hostname = window.location.hostname;
    
    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // Render deployment - API is on same origin
    // Use endsWith to prevent subdomain spoofing attacks
    if (hostname.endsWith('.onrender.com') || hostname === 'onrender.com') {
        return window.location.origin;
    }
    
    // Legacy Cloudflare Pages or other static hosting - point to Render API
    // Note: Primary deployment model is now Render (all-in-one)
    if (hostname.endsWith('.pages.dev') || hostname === 'pages.dev' ||
        hostname.endsWith('.cloudflare.com') || hostname === 'cloudflare.com') {
        return 'https://newton-api-1.onrender.com';
    }
    
    // Default: assume API is on same origin
    return window.location.origin;
}

/**
 * Get Mission Control URL based on current deployment
 * @returns {string} The Mission Control dashboard URL
 */
function getMissionControlUrl() {
    return `${getApiBase()}/mission-control/`;
}

// Export for use in applications
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = { getApiBase, getMissionControlUrl };
} else {
    // Browser environment - make available globally
    window.NewtonConfig = {
        getApiBase,
        getMissionControlUrl,
        API_BASE: getApiBase(),
        MISSION_CONTROL_URL: getMissionControlUrl()
    };
}
