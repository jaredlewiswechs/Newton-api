/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NEWTON MISSION CONTROL - APPLICATION LOGIC
 * Real-time health monitoring and diagnostics for Newton API
 * 
 * © 2026 Jared Lewis · Ada Computing Company
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { ENDPOINTS, API_ENVIRONMENTS, DEFAULT_CONFIG } from './config.js';

// ═══════════════════════════════════════════════════════════════════════════
// State Management
// ═══════════════════════════════════════════════════════════════════════════

const state = {
    config: { ...DEFAULT_CONFIG },
    services: [],
    testResults: new Map(),
    logs: [],
    currentCategory: 'all',
    currentFilter: '',
    autoRefreshTimer: null,
    testingInProgress: false
};

// ═══════════════════════════════════════════════════════════════════════════
// Initialization
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    loadConfiguration();
    initializeUI();
    buildServicesList();
    renderServices();
    setupEventListeners();
    startAutoRefresh();
    
    addLog('info', 'Mission Control initialized');
    addLog('info', `Environment: ${state.config.environment}`);
});

// ═══════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════

function loadConfiguration() {
    const saved = localStorage.getItem('newton-mission-control-config');
    if (saved) {
        try {
            state.config = { ...DEFAULT_CONFIG, ...JSON.parse(saved) };
        } catch (e) {
            addLog('error', 'Failed to load configuration: ' + e.message);
        }
    }
}

function saveConfiguration() {
    try {
        localStorage.setItem('newton-mission-control-config', JSON.stringify(state.config));
        addLog('success', 'Configuration saved');
    } catch (e) {
        addLog('error', 'Failed to save configuration: ' + e.message);
    }
}

function getApiBaseUrl() {
    if (state.config.environment === 'custom') {
        return state.config.customUrl || API_ENVIRONMENTS.localhost;
    }
    return API_ENVIRONMENTS[state.config.environment] || API_ENVIRONMENTS.localhost;
}

// ═══════════════════════════════════════════════════════════════════════════
// UI Initialization
// ═══════════════════════════════════════════════════════════════════════════

function initializeUI() {
    // Set theme
    document.body.setAttribute('data-theme', state.config.theme);
    updateThemeIcon();
    
    // Set environment selector
    const envSelect = document.getElementById('env-select');
    envSelect.value = state.config.environment;
    
    if (state.config.environment === 'custom') {
        const customInput = document.getElementById('custom-url');
        customInput.style.display = 'block';
        customInput.value = state.config.customUrl;
    }
    
    // Set config values
    document.getElementById('config-timeout').value = state.config.timeout;
    document.getElementById('config-autorefresh').checked = state.config.autoRefresh;
    document.getElementById('config-interval').value = state.config.refreshInterval;
}

function updateThemeIcon() {
    const icon = document.querySelector('.theme-icon');
    icon.textContent = state.config.theme === 'dark' ? '🌙' : '☀️';
}

// ═══════════════════════════════════════════════════════════════════════════
// Services Management
// ═══════════════════════════════════════════════════════════════════════════

function buildServicesList() {
    state.services = [];
    
    Object.entries(ENDPOINTS).forEach(([category, categoryData]) => {
        categoryData.endpoints.forEach(endpoint => {
            state.services.push({
                id: `${category}-${endpoint.path}`,
                category,
                categoryName: categoryData.name,
                ...endpoint,
                status: 'untested',
                lastTested: null,
                responseTime: null,
                error: null
            });
        });
    });
    
    updateCategoryCounts();
}

function updateCategoryCounts() {
    const counts = {};
    counts.all = state.services.length;
    
    Object.keys(ENDPOINTS).forEach(category => {
        counts[category] = state.services.filter(s => s.category === category).length;
    });
    
    Object.entries(counts).forEach(([category, count]) => {
        const el = document.getElementById(`count-${category}`);
        if (el) el.textContent = count;
    });
}

function updateStatistics() {
    const success = state.services.filter(s => s.status === 'success').length;
    const error = state.services.filter(s => s.status === 'error').length;
    const untested = state.services.filter(s => s.status === 'untested').length;
    
    document.getElementById('stat-success').textContent = success;
    document.getElementById('stat-error').textContent = error;
    document.getElementById('stat-untested').textContent = untested;
    
    // Update global status
    const statusBadge = document.getElementById('global-status');
    const statusIndicator = statusBadge.querySelector('.status-indicator');
    const statusText = statusBadge.querySelector('.status-text');
    
    if (error > 0) {
        statusIndicator.className = 'status-indicator error';
        statusText.textContent = `${error} service${error !== 1 ? 's' : ''} failing`;
    } else if (untested > 0) {
        statusIndicator.className = 'status-indicator';
        statusText.textContent = `${untested} service${untested !== 1 ? 's' : ''} untested`;
    } else {
        statusIndicator.className = 'status-indicator success';
        statusText.textContent = 'All services operational';
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Service Testing
// ═══════════════════════════════════════════════════════════════════════════

async function testService(service) {
    const startTime = performance.now();
    const baseUrl = getApiBaseUrl();
    const url = `${baseUrl}${service.path}`;
    
    addLog('info', `Testing ${service.method} ${service.path}`);
    
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), state.config.timeout);
        
        const options = {
            method: service.method,
            headers: {
                'Content-Type': 'application/json',
            },
            signal: controller.signal
        };
        
        if (service.method !== 'GET' && service.sampleData) {
            options.body = JSON.stringify(service.sampleData);
        }
        
        const response = await fetch(url, options);
        clearTimeout(timeout);
        
        const endTime = performance.now();
        const responseTime = Math.round(endTime - startTime);
        
        let data;
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }
        
        const result = {
            status: response.ok ? 'success' : 'error',
            statusCode: response.status,
            responseTime,
            data,
            headers: Object.fromEntries(response.headers.entries()),
            timestamp: new Date().toISOString()
        };
        
        service.status = result.status;
        service.lastTested = result.timestamp;
        service.responseTime = responseTime;
        service.error = response.ok ? null : `HTTP ${response.status}`;
        
        state.testResults.set(service.id, result);
        
        addLog(
            response.ok ? 'success' : 'error',
            `${service.method} ${service.path} → ${response.status} (${responseTime}ms)`
        );
        
        return result;
        
    } catch (error) {
        const endTime = performance.now();
        const responseTime = Math.round(endTime - startTime);
        
        const errorType = diagnoseError(error);
        const result = {
            status: 'error',
            statusCode: null,
            responseTime,
            error: error.message,
            errorType,
            timestamp: new Date().toISOString()
        };
        
        service.status = 'error';
        service.lastTested = result.timestamp;
        service.responseTime = responseTime;
        service.error = errorType;
        
        state.testResults.set(service.id, result);
        
        addLog('error', `${service.method} ${service.path} → ${errorType}`);
        
        return result;
    }
}

function diagnoseError(error) {
    if (error.name === 'AbortError') {
        return 'Timeout - Request took too long to complete';
    }
    
    if (error.message.includes('Failed to fetch')) {
        return 'Network Error - Check if API is running and CORS is configured';
    }
    
    if (error.message.includes('CORS')) {
        return 'CORS Error - API needs to allow requests from this origin';
    }
    
    if (error.message.includes('NetworkError')) {
        return 'Network Error - Cannot reach API server';
    }
    
    return error.message || 'Unknown Error';
}

async function testAllServices() {
    if (state.testingInProgress) {
        addLog('warning', 'Test already in progress');
        return;
    }
    
    state.testingInProgress = true;
    const testButton = document.getElementById('test-all');
    testButton.disabled = true;
    testButton.textContent = 'Testing...';
    
    addLog('info', `Testing all ${state.services.length} services...`);
    
    const filtered = getFilteredServices();
    
    for (const service of filtered) {
        await testService(service);
        renderServices();
        updateStatistics();
        // Small delay to avoid overwhelming the API
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    state.testingInProgress = false;
    testButton.disabled = false;
    testButton.textContent = 'Test All';
    
    addLog('success', 'All tests completed');
}

// ═══════════════════════════════════════════════════════════════════════════
// Rendering
// ═══════════════════════════════════════════════════════════════════════════

function renderServices() {
    const grid = document.getElementById('services-grid');
    const emptyState = document.getElementById('empty-state');
    const filtered = getFilteredServices();
    
    if (filtered.length === 0) {
        grid.style.display = 'none';
        emptyState.style.display = 'flex';
        return;
    }
    
    grid.style.display = 'grid';
    emptyState.style.display = 'none';
    
    grid.innerHTML = filtered.map(service => createServiceCard(service)).join('');
    
    // Add click listeners
    grid.querySelectorAll('.service-card').forEach((card, index) => {
        card.addEventListener('click', () => openTestPanel(filtered[index]));
    });
    
    updateStatistics();
}

function createServiceCard(service) {
    return `
        <div class="service-card status-${service.status}" data-service-id="${service.id}">
            <div class="service-header">
                <div>
                    <div class="service-name">${service.name}</div>
                    <div class="service-path">
                        <span class="method-badge ${service.method}">${service.method}</span>
                        ${service.path}
                    </div>
                </div>
            </div>
            <div class="service-description">${service.description || 'No description'}</div>
            <div class="service-footer">
                <div class="service-timing">
                    ${service.responseTime ? `⏱ ${service.responseTime}ms` : '—'}
                </div>
                <div class="service-status">
                    <span class="status-dot ${service.status}"></span>
                    ${formatStatus(service)}
                </div>
            </div>
        </div>
    `;
}

function formatStatus(service) {
    if (service.status === 'untested') return 'Not tested';
    if (service.status === 'success') return 'OK';
    return service.error || 'Error';
}

function getFilteredServices() {
    let filtered = state.services;
    
    // Filter by category
    if (state.currentCategory !== 'all') {
        filtered = filtered.filter(s => s.category === state.currentCategory);
    }
    
    // Filter by search
    if (state.currentFilter) {
        const query = state.currentFilter.toLowerCase();
        filtered = filtered.filter(s => 
            s.name.toLowerCase().includes(query) ||
            s.path.toLowerCase().includes(query) ||
            s.description?.toLowerCase().includes(query)
        );
    }
    
    return filtered;
}

// ═══════════════════════════════════════════════════════════════════════════
// Test Panel
// ═══════════════════════════════════════════════════════════════════════════

function openTestPanel(service) {
    const panel = document.getElementById('test-panel');
    panel.style.display = 'flex';
    
    document.getElementById('test-title').textContent = service.name;
    document.getElementById('test-method').textContent = service.method;
    document.getElementById('test-method').className = `method-badge ${service.method}`;
    document.getElementById('test-path').textContent = service.path;
    document.getElementById('test-description').textContent = service.description || '';
    
    // Show/hide request editor based on method
    const editorContainer = document.getElementById('request-editor-container');
    const requestBody = document.getElementById('request-body');
    
    if (service.method !== 'GET' && service.sampleData) {
        editorContainer.style.display = 'block';
        requestBody.value = JSON.stringify(service.sampleData, null, 2);
    } else {
        editorContainer.style.display = 'none';
    }
    
    // Hide response sections initially
    document.getElementById('response-section').style.display = 'none';
    document.getElementById('error-section').style.display = 'none';
    
    // Execute test button
    const executeBtn = document.getElementById('execute-test');
    executeBtn.onclick = async () => {
        executeBtn.disabled = true;
        executeBtn.textContent = 'Testing...';
        
        // Update sample data if edited
        if (service.method !== 'GET') {
            try {
                service.sampleData = JSON.parse(requestBody.value);
            } catch (e) {
                addLog('warning', 'Invalid JSON in request body, using original');
            }
        }
        
        const result = await testService(service);
        renderServices();
        displayTestResult(service, result);
        
        executeBtn.disabled = false;
        executeBtn.textContent = 'Execute Test';
    };
}

function displayTestResult(service, result) {
    if (result.status === 'error' && !result.statusCode) {
        // Network/timeout error
        document.getElementById('response-section').style.display = 'none';
        document.getElementById('error-section').style.display = 'block';
        
        document.getElementById('error-type').textContent = result.errorType || 'Error';
        document.getElementById('error-message').textContent = result.error;
        
        const diagnostics = [];
        if (result.errorType?.includes('CORS')) {
            diagnostics.push('💡 CORS Issue: The API server needs to include this origin in its CORS policy.');
            diagnostics.push('💡 For local development, ensure the API is running and configured to accept requests from ' + window.location.origin);
        } else if (result.errorType?.includes('Timeout')) {
            diagnostics.push(`💡 Timeout: Request exceeded ${state.config.timeout}ms limit.`);
            diagnostics.push('💡 Try increasing the timeout in Configuration or check if the endpoint is slow.');
        } else if (result.errorType?.includes('Network')) {
            diagnostics.push('💡 Network Error: Cannot reach the API server.');
            diagnostics.push('💡 Check if the API is running at: ' + getApiBaseUrl());
        }
        
        document.getElementById('error-diagnostics').innerHTML = diagnostics.join('<br>');
        
    } else {
        // Successful response (or HTTP error)
        document.getElementById('error-section').style.display = 'none';
        document.getElementById('response-section').style.display = 'block';
        
        const statusEl = document.getElementById('response-status');
        statusEl.textContent = result.statusCode;
        statusEl.className = result.status === 'success' ? 'status-code' : 'status-code error';
        
        document.getElementById('response-time').textContent = `${result.responseTime}ms`;
        
        // Response body
        const bodyCode = document.getElementById('response-body-code');
        if (typeof result.data === 'object') {
            bodyCode.textContent = JSON.stringify(result.data, null, 2);
        } else {
            bodyCode.textContent = result.data;
        }
        
        // Response headers
        const headersCode = document.getElementById('response-headers-code');
        headersCode.textContent = JSON.stringify(result.headers, null, 2);
        
        // Setup action buttons
        setupResponseActions(service, result);
    }
}

function setupResponseActions(service, result) {
    document.getElementById('copy-response').onclick = () => {
        const text = typeof result.data === 'object' 
            ? JSON.stringify(result.data, null, 2) 
            : result.data;
        copyToClipboard(text);
        addLog('success', 'Response copied to clipboard');
    };
    
    document.getElementById('copy-curl').onclick = () => {
        const curl = generateCurlCommand(service);
        copyToClipboard(curl);
        addLog('success', 'cURL command copied to clipboard');
    };
    
    document.getElementById('download-response').onclick = () => {
        const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${service.name.replace(/\s/g, '_')}_response.json`;
        a.click();
        URL.revokeObjectURL(url);
        addLog('success', 'Response downloaded');
    };
}

function generateCurlCommand(service) {
    const baseUrl = getApiBaseUrl();
    const url = `${baseUrl}${service.path}`;
    
    let curl = `curl -X ${service.method} "${url}"`;
    curl += ` \\\n  -H "Content-Type: application/json"`;
    
    if (service.method !== 'GET' && service.sampleData) {
        curl += ` \\\n  -d '${JSON.stringify(service.sampleData)}'`;
    }
    
    return curl;
}

// ═══════════════════════════════════════════════════════════════════════════
// Logging
// ═══════════════════════════════════════════════════════════════════════════

function addLog(level, message) {
    const entry = {
        timestamp: new Date().toISOString(),
        level,
        message
    };
    
    state.logs.push(entry);
    
    // Keep only last 1000 logs
    if (state.logs.length > 1000) {
        state.logs.shift();
    }
    
    renderLogs();
}

function renderLogs() {
    const content = document.getElementById('log-content');
    const filter = document.querySelector('.log-filter.active').dataset.filter;
    
    let filtered = state.logs;
    if (filter !== 'all') {
        filtered = state.logs.filter(log => log.level === filter);
    }
    
    // Show last 50 logs
    const recent = filtered.slice(-50);
    
    content.innerHTML = recent.map(log => `
        <div class="log-entry">
            <span class="log-timestamp">${new Date(log.timestamp).toLocaleTimeString()}</span>
            <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
            <span class="log-message">${escapeHtml(log.message)}</span>
        </div>
    `).join('');
    
    // Auto-scroll to bottom
    content.scrollTop = content.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════════════════
// Auto-Refresh
// ═══════════════════════════════════════════════════════════════════════════

function startAutoRefresh() {
    if (state.autoRefreshTimer) {
        clearInterval(state.autoRefreshTimer);
    }
    
    if (state.config.autoRefresh) {
        state.autoRefreshTimer = setInterval(() => {
            if (!state.testingInProgress) {
                addLog('info', 'Auto-refresh triggered');
                testAllServices();
            }
        }, state.config.refreshInterval * 1000);
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Event Listeners
// ═══════════════════════════════════════════════════════════════════════════

function setupEventListeners() {
    // Environment selector
    document.getElementById('env-select').addEventListener('change', (e) => {
        state.config.environment = e.target.value;
        const customInput = document.getElementById('custom-url');
        
        if (e.target.value === 'custom') {
            customInput.style.display = 'block';
        } else {
            customInput.style.display = 'none';
        }
        
        saveConfiguration();
        addLog('info', `Environment changed to: ${e.target.value}`);
    });
    
    document.getElementById('custom-url').addEventListener('change', (e) => {
        state.config.customUrl = e.target.value;
        saveConfiguration();
    });
    
    // Test all button
    document.getElementById('test-all').addEventListener('click', testAllServices);
    
    // Refresh button
    document.getElementById('refresh-all').addEventListener('click', () => {
        renderServices();
        addLog('info', 'View refreshed');
    });
    
    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', () => {
        state.config.theme = state.config.theme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', state.config.theme);
        updateThemeIcon();
        saveConfiguration();
        addLog('info', `Theme: ${state.config.theme}`);
    });
    
    // Category navigation
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.category-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            state.currentCategory = item.dataset.category;
            renderServices();
        });
    });
    
    // Search
    document.getElementById('search-input').addEventListener('input', (e) => {
        state.currentFilter = e.target.value;
        renderServices();
    });
    
    // View controls
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            // Could implement list view here
        });
    });
    
    // Modal controls
    document.getElementById('modal-close').addEventListener('click', () => {
        document.getElementById('test-panel').style.display = 'none';
    });
    
    document.getElementById('modal-overlay').addEventListener('click', () => {
        document.getElementById('test-panel').style.display = 'none';
    });
    
    // Config modal
    document.getElementById('config-btn').addEventListener('click', () => {
        document.getElementById('config-panel').style.display = 'flex';
    });
    
    document.getElementById('config-close').addEventListener('click', () => {
        document.getElementById('config-panel').style.display = 'none';
    });
    
    document.getElementById('config-overlay').addEventListener('click', () => {
        document.getElementById('config-panel').style.display = 'none';
    });
    
    document.getElementById('save-config').addEventListener('click', () => {
        state.config.timeout = parseInt(document.getElementById('config-timeout').value);
        state.config.autoRefresh = document.getElementById('config-autorefresh').checked;
        state.config.refreshInterval = parseInt(document.getElementById('config-interval').value);
        
        saveConfiguration();
        startAutoRefresh();
        
        document.getElementById('config-panel').style.display = 'none';
        addLog('success', 'Configuration saved');
    });
    
    document.getElementById('reset-config').addEventListener('click', () => {
        state.config = { ...DEFAULT_CONFIG };
        saveConfiguration();
        initializeUI();
        startAutoRefresh();
        addLog('info', 'Configuration reset to defaults');
    });
    
    // Response tabs
    document.querySelectorAll('.response-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.response-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            document.querySelectorAll('.response-tab-content').forEach(c => c.style.display = 'none');
            document.getElementById(`response-${tab.dataset.tab}`).style.display = 'block';
        });
    });
    
    // Log controls
    document.getElementById('toggle-log').addEventListener('click', () => {
        const panel = document.getElementById('log-panel');
        panel.classList.toggle('collapsed');
    });
    
    document.querySelectorAll('.log-filter').forEach(filter => {
        filter.addEventListener('click', () => {
            document.querySelectorAll('.log-filter').forEach(f => f.classList.remove('active'));
            filter.classList.add('active');
            renderLogs();
        });
    });
    
    document.getElementById('clear-logs').addEventListener('click', () => {
        state.logs = [];
        renderLogs();
        addLog('info', 'Logs cleared');
    });
    
    document.getElementById('export-logs').addEventListener('click', () => {
        const blob = new Blob([JSON.stringify(state.logs, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `newton-logs-${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        addLog('success', 'Logs exported');
    });
    
    document.getElementById('export-config').addEventListener('click', () => {
        const exportData = {
            config: state.config,
            testResults: Array.from(state.testResults.entries())
        };
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `newton-config-${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        addLog('success', 'Configuration exported');
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// Utilities
// ═══════════════════════════════════════════════════════════════════════════

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
}
