/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * NEWTON INTERFACE BUILDER - Application
 * Build verified interfaces from templates
 * ═══════════════════════════════════════════════════════════════════════════════
 */

// ─────────────────────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────────────────────

const CONFIG = {
    API_BASE: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://newton-api.onrender.com',
    TIMEOUT: 60000
};

// ─────────────────────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────────────────────

const state = {
    connected: false,
    loading: false,
    currentView: 'templates',
    templates: [],
    selectedTemplate: null,
    variables: {},
    builtInterface: null,
    outputFormat: 'all'
};

// ─────────────────────────────────────────────────────────────────────────────
// API Client
// ─────────────────────────────────────────────────────────────────────────────

const api = {
    async request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);

        try {
            const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            throw error;
        }
    },

    async getTemplates(query = '', type = null, tags = null) {
        let url = '/interface/templates';
        const params = new URLSearchParams();
        if (query) params.set('query', query);
        if (type) params.set('type', type);
        if (tags) params.set('tags', tags);
        const queryString = params.toString();
        if (queryString) url += '?' + queryString;
        return this.request(url);
    },

    async getTemplate(templateId) {
        return this.request(`/interface/templates/${templateId}`);
    },

    async buildInterface(templateId, variables, outputFormat = 'all') {
        return this.request('/interface/build', {
            method: 'POST',
            body: JSON.stringify({
                template_id: templateId,
                variables: variables,
                output_format: outputFormat
            })
        });
    },

    async buildFromSpec(spec, outputFormat = 'all') {
        return this.request('/interface/build', {
            method: 'POST',
            body: JSON.stringify({
                spec: spec,
                output_format: outputFormat
            })
        });
    },

    async getComponents() {
        return this.request('/interface/components');
    },

    async getInfo() {
        return this.request('/interface/info');
    },

    async checkHealth() {
        return this.request('/health');
    }
};

// ─────────────────────────────────────────────────────────────────────────────
// Toast Notifications
// ─────────────────────────────────────────────────────────────────────────────

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${getToastIcon(type)}</span>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return '✓';
        case 'error': return '✗';
        case 'info': return 'ℹ';
        default: return '•';
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// View Management
// ─────────────────────────────────────────────────────────────────────────────

function showView(viewName) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.view === viewName);
    });

    // Update views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.toggle('active', view.id === `view-${viewName}`);
    });

    // Update title
    const titles = {
        'templates': 'Templates',
        'builder': 'Builder',
        'docs': 'Documentation',
        'components': 'Components'
    };
    document.getElementById('content-title').textContent = titles[viewName] || viewName;

    state.currentView = viewName;

    // Load view-specific data
    if (viewName === 'templates') {
        loadTemplates();
    } else if (viewName === 'docs') {
        loadDocs();
    } else if (viewName === 'components') {
        loadComponents();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Templates View
// ─────────────────────────────────────────────────────────────────────────────

async function loadTemplates(query = '', type = null) {
    const grid = document.getElementById('templates-grid');
    grid.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const result = await api.getTemplates(query, type);
        state.templates = result.templates;
        renderTemplates();
    } catch (error) {
        showToast(`Failed to load templates: ${error.message}`, 'error');
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠</div>
                <div class="empty-title">Failed to load templates</div>
                <div class="empty-description">${error.message}</div>
                <button class="btn btn-primary" onclick="loadTemplates()">Retry</button>
            </div>
        `;
    }
}

function renderTemplates() {
    const grid = document.getElementById('templates-grid');

    if (state.templates.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <div class="empty-title">No templates found</div>
                <div class="empty-description">Try a different search query</div>
            </div>
        `;
        return;
    }

    const icons = {
        'dashboard': '📊',
        'form': '📝',
        'settings': '⚙️',
        'empty_state': '📭',
        'data_table': '📋',
        'wizard': '🧙',
        'landing': '🚀'
    };

    grid.innerHTML = state.templates.map(template => `
        <div class="template-card" onclick="selectTemplate('${template.id}')">
            <div class="template-preview">${icons[template.type] || '📦'}</div>
            <div class="template-info">
                <div class="template-name">${template.name}</div>
                <div class="template-description">${template.description}</div>
                <div class="template-tags">
                    ${template.tags.map(tag => `<span class="template-tag">${tag}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

async function selectTemplate(templateId) {
    try {
        const result = await api.getTemplate(templateId);
        state.selectedTemplate = result.template;
        state.variables = {};

        // Initialize variables with defaults
        if (result.template.variables) {
            result.template.variables.forEach(varName => {
                state.variables[varName] = '';
            });
        }

        showView('builder');
        renderBuilder();
    } catch (error) {
        showToast(`Failed to load template: ${error.message}`, 'error');
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Builder View
// ─────────────────────────────────────────────────────────────────────────────

function renderBuilder() {
    const panel = document.getElementById('builder-panel');
    const template = state.selectedTemplate;

    if (!template) {
        panel.innerHTML = `
            <div class="panel-header">
                <div class="panel-title">No Template Selected</div>
            </div>
            <div class="panel-content">
                <p style="color: var(--text-secondary);">Select a template from the Templates view to get started.</p>
                <button class="btn btn-primary" style="margin-top: var(--space-4)" onclick="showView('templates')">
                    Browse Templates
                </button>
            </div>
        `;
        return;
    }

    panel.innerHTML = `
        <div class="panel-header">
            <div class="panel-title">${template.name}</div>
        </div>
        <div class="panel-content">
            <div class="variables-form" id="variables-form">
                ${template.variables.map(varName => `
                    <div class="variable-field">
                        <label class="variable-label">${formatVariableName(varName)}</label>
                        <input
                            type="text"
                            class="input"
                            id="var-${varName}"
                            placeholder="${varName}"
                            onchange="updateVariable('${varName}', this.value)"
                        >
                    </div>
                `).join('')}
            </div>
            <div style="margin-top: var(--space-6)">
                <div class="input-group">
                    <label class="input-label">Output Format</label>
                    <select class="select" id="output-format" onchange="state.outputFormat = this.value">
                        <option value="all">All Formats</option>
                        <option value="json">JSON Only</option>
                        <option value="jsx">React JSX Only</option>
                        <option value="html">HTML Only</option>
                    </select>
                </div>
                <button class="btn btn-newton btn-lg" style="width: 100%; margin-top: var(--space-4)" onclick="buildInterface()">
                    ✓ Build Interface
                </button>
            </div>
        </div>
    `;
}

function formatVariableName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function updateVariable(name, value) {
    state.variables[name] = value;
}

async function buildInterface() {
    if (!state.selectedTemplate) {
        showToast('Please select a template first', 'error');
        return;
    }

    setLoading(true);
    const startTime = performance.now();

    try {
        const result = await api.buildInterface(
            state.selectedTemplate.id,
            state.variables,
            state.outputFormat
        );

        const elapsed = (performance.now() - startTime).toFixed(2);
        state.builtInterface = result;

        renderPreview();

        if (result.verified) {
            showToast(`Interface built successfully in ${elapsed}ms`, 'success');
        } else {
            showToast(`Build failed: ${result.error}`, 'error');
        }
    } catch (error) {
        showToast(`Build failed: ${error.message}`, 'error');
    } finally {
        setLoading(false);
    }
}

function renderPreview() {
    const result = state.builtInterface;
    if (!result) return;

    const previewTab = document.getElementById('tab-preview');
    const jsxTab = document.getElementById('tab-jsx');
    const htmlTab = document.getElementById('tab-html');

    // Preview tab - render the result details
    previewTab.innerHTML = `
        <div class="verification-result">
            <div class="verification-header">
                <span class="badge ${result.verified ? 'badge-success' : 'badge-error'}">
                    ${result.verified ? '✓ VERIFIED' : '✗ FAILED'}
                </span>
                <span class="verification-time">${result.elapsed_us?.toFixed(2)}μs</span>
            </div>
            ${result.verified ? `
                <div class="verification-details">
                    <div><strong>Interface:</strong> ${result.interface?.name || 'Untitled'}</div>
                    <div><strong>Type:</strong> ${result.interface?.type || 'N/A'}</div>
                    <div><strong>Layout:</strong> ${result.interface?.layout || 'N/A'}</div>
                    <div><strong>Components:</strong> ${result.interface?.components?.length || 0}</div>
                    <div><strong>Fingerprint:</strong> ${result.fingerprint || 'N/A'}</div>
                </div>
            ` : `
                <div class="verification-details">
                    <div><strong>Error:</strong> ${result.error || 'Unknown error'}</div>
                    ${result.law ? `<div><strong>Law:</strong> ${result.law}</div>` : ''}
                </div>
            `}
        </div>
        ${result.interface ? `
            <div style="margin-top: var(--space-4)">
                <h3 style="font-size: 14px; margin-bottom: var(--space-3)">Component Tree</h3>
                <div class="code-block">
                    <pre>${syntaxHighlightJSON(JSON.stringify(result.interface, null, 2))}</pre>
                </div>
            </div>
        ` : ''}
    `;

    // JSX tab
    if (result.jsx) {
        jsxTab.innerHTML = `
            <div class="code-block">
                <pre>${syntaxHighlightJSX(result.jsx)}</pre>
            </div>
            <button class="btn btn-secondary" style="margin-top: var(--space-3)" onclick="copyToClipboard('jsx')">
                Copy JSX
            </button>
        `;
    } else {
        jsxTab.innerHTML = '<p style="color: var(--text-tertiary)">JSX not generated. Select "All Formats" or "React JSX Only" output format.</p>';
    }

    // HTML tab
    if (result.html) {
        htmlTab.innerHTML = `
            <div class="code-block">
                <pre>${escapeHtml(result.html)}</pre>
            </div>
            <button class="btn btn-secondary" style="margin-top: var(--space-3)" onclick="copyToClipboard('html')">
                Copy HTML
            </button>
        `;
    } else {
        htmlTab.innerHTML = '<p style="color: var(--text-tertiary)">HTML not generated. Select "All Formats" or "HTML Only" output format.</p>';
    }
}

function syntaxHighlightJSON(json) {
    return json
        .replace(/("[\w_]+")\s*:/g, '<span class="code-attr">$1</span>:')
        .replace(/:\s*(".*?")/g, ': <span class="code-string">$1</span>')
        .replace(/:\s*(\d+)/g, ': <span class="code-number">$1</span>')
        .replace(/:\s*(true|false|null)/g, ': <span class="code-keyword">$1</span>');
}

function syntaxHighlightJSX(jsx) {
    return escapeHtml(jsx)
        .replace(/(&lt;\/?[\w]+)/g, '<span class="code-tag">$1</span>')
        .replace(/([\w-]+)=/g, '<span class="code-attr">$1</span>=')
        .replace(/(".*?")/g, '<span class="code-string">$1</span>')
        .replace(/(import|from|export|const|return)/g, '<span class="code-keyword">$1</span>');
}

function escapeHtml(html) {
    return html
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function copyToClipboard(type) {
    const content = type === 'jsx' ? state.builtInterface?.jsx : state.builtInterface?.html;
    if (content) {
        navigator.clipboard.writeText(content);
        showToast(`${type.toUpperCase()} copied to clipboard`, 'success');
    }
}

function switchCanvasTab(tabName) {
    document.querySelectorAll('.canvas-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    document.querySelectorAll('.canvas-content').forEach(content => {
        content.style.display = content.id === `tab-${tabName}` ? 'block' : 'none';
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// Components View
// ─────────────────────────────────────────────────────────────────────────────

async function loadComponents() {
    const container = document.getElementById('components-list');
    container.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const result = await api.getComponents();

        // Group by category
        const categories = {};
        result.components.forEach(comp => {
            if (!categories[comp.category]) {
                categories[comp.category] = [];
            }
            categories[comp.category].push(comp);
        });

        container.innerHTML = Object.entries(categories).map(([category, components]) => `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title" style="text-transform: capitalize">${category} Components</h3>
                    <span class="badge badge-newton">${components.length}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: var(--space-3)">
                    ${components.map(comp => `
                        <div style="padding: var(--space-3); background: var(--surface-tertiary); border-radius: var(--radius-sm); text-align: center">
                            <div style="font-size: 24px; margin-bottom: var(--space-2)">${getComponentIcon(comp.value)}</div>
                            <div style="font-size: 12px; text-transform: capitalize">${comp.value.replace(/_/g, ' ')}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    } catch (error) {
        showToast(`Failed to load components: ${error.message}`, 'error');
    }
}

function getComponentIcon(type) {
    const icons = {
        'container': '📦',
        'grid': '⊞',
        'flex': '↔',
        'sidebar': '◧',
        'header': '▔',
        'footer': '▁',
        'card': '🃏',
        'modal': '⬜',
        'button': '🔘',
        'input': '⬜',
        'textarea': '📝',
        'select': '▼',
        'checkbox': '☑',
        'radio': '◉',
        'toggle': '⚙',
        'slider': '─○─',
        'text': 'T',
        'heading': 'H',
        'badge': '🏷',
        'metric': '📊',
        'code': '{ }',
        'table': '⊞',
        'list': '☰',
        'image': '🖼',
        'icon': '✦',
        'alert': '⚠',
        'toast': '💬',
        'progress': '▓',
        'spinner': '⟳',
        'skeleton': '░'
    };
    return icons[type] || '●';
}

// ─────────────────────────────────────────────────────────────────────────────
// Docs View
// ─────────────────────────────────────────────────────────────────────────────

async function loadDocs() {
    const container = document.getElementById('docs-content');
    container.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const info = await api.getInfo();

        container.innerHTML = `
            <div class="docs-section">
                <h2 class="docs-heading">Overview</h2>
                <p class="docs-text">${info.description}</p>
                <p class="docs-text" style="font-style: italic; color: var(--accent-primary)">"${info.philosophy}"</p>
            </div>

            <div class="docs-section">
                <h2 class="docs-heading">Capabilities</h2>
                <ul class="docs-list">
                    ${info.capabilities.map(cap => `<li>${cap}</li>`).join('')}
                </ul>
            </div>

            <div class="docs-section">
                <h2 class="docs-heading">API Endpoints</h2>
                ${info.endpoints.map(ep => `
                    <div class="endpoint-card">
                        <span class="endpoint-method ${ep.method.toLowerCase()}">${ep.method}</span>
                        <span class="endpoint-path">${ep.path}</span>
                        <div class="endpoint-desc">${ep.description}</div>
                    </div>
                `).join('')}
            </div>

            <div class="docs-section">
                <h2 class="docs-heading">Interface Types</h2>
                <div style="display: flex; flex-wrap: wrap; gap: var(--space-2)">
                    ${info.interface_types.map(type => `
                        <span class="badge badge-info" style="text-transform: capitalize">${type.replace(/_/g, ' ')}</span>
                    `).join('')}
                </div>
            </div>

            <div class="docs-section">
                <h2 class="docs-heading">Layout Patterns</h2>
                <div style="display: flex; flex-wrap: wrap; gap: var(--space-2)">
                    ${info.layout_patterns.map(pattern => `
                        <span class="badge badge-newton" style="text-transform: capitalize">${pattern.replace(/_/g, ' ')}</span>
                    `).join('')}
                </div>
            </div>

            <div class="docs-section">
                <h2 class="docs-heading">Output Formats</h2>
                <ul class="docs-list">
                    ${info.output_formats.map(format => `
                        <li><strong>${format}</strong> - ${getFormatDescription(format)}</li>
                    `).join('')}
                </ul>
            </div>

            <div class="docs-section">
                <h2 class="docs-heading">Quick Start</h2>
                <h3 class="docs-subheading">1. Build from Template</h3>
                <div class="code-block">
                    <pre>POST /interface/build
{
    "template_id": "dashboard-basic",
    "variables": {
        "title": "My Dashboard",
        "metric1_value": "98.4%",
        "metric1_label": "Success Rate"
    },
    "output_format": "all"
}</pre>
                </div>

                <h3 class="docs-subheading">2. Build from Spec</h3>
                <div class="code-block">
                    <pre>POST /interface/build
{
    "spec": {
        "name": "Custom Form",
        "type": "form",
        "layout": "single_column",
        "components": [
            {
                "id": "title",
                "type": "heading",
                "props": {"content": "Contact Us"}
            },
            {
                "id": "email",
                "type": "input",
                "props": {"placeholder": "Email"}
            },
            {
                "id": "submit",
                "type": "button",
                "variant": "primary",
                "props": {"label": "Submit"}
            }
        ]
    }
}</pre>
                </div>
            </div>
        `;
    } catch (error) {
        showToast(`Failed to load docs: ${error.message}`, 'error');
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📚</div>
                <div class="empty-title">Failed to load documentation</div>
                <button class="btn btn-primary" onclick="loadDocs()">Retry</button>
            </div>
        `;
    }
}

function getFormatDescription(format) {
    const descriptions = {
        'json': 'Component tree as JSON object',
        'jsx': 'React JSX component code',
        'html': 'Production-ready HTML',
        'all': 'All formats in a single response'
    };
    return descriptions[format] || format;
}

// ─────────────────────────────────────────────────────────────────────────────
// Loading State
// ─────────────────────────────────────────────────────────────────────────────

function setLoading(loading) {
    state.loading = loading;
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = loading ? 'flex' : 'none';
}

// ─────────────────────────────────────────────────────────────────────────────
// Connection Status
// ─────────────────────────────────────────────────────────────────────────────

async function checkConnection() {
    try {
        await api.checkHealth();
        state.connected = true;
        updateConnectionStatus(true);
    } catch (error) {
        state.connected = false;
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');

    dot.classList.toggle('disconnected', !connected);
    text.textContent = connected ? 'Connected' : 'Disconnected';
}

// ─────────────────────────────────────────────────────────────────────────────
// Search & Filter
// ─────────────────────────────────────────────────────────────────────────────

function handleSearch(query) {
    if (state.currentView === 'templates') {
        loadTemplates(query);
    }
}

function filterByType(type) {
    if (state.currentView === 'templates') {
        loadTemplates('', type || null);
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Initialization
// ─────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // Check connection
    checkConnection();
    setInterval(checkConnection, 30000);

    // Initial view
    showView('templates');

    // Setup nav handlers
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const view = item.dataset.view;
            if (view) showView(view);
        });
    });

    // Setup search
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => handleSearch(e.target.value), 300);
        });
    }

    // Setup filter
    const typeFilter = document.getElementById('type-filter');
    if (typeFilter) {
        typeFilter.addEventListener('change', (e) => filterByType(e.target.value));
    }

    // Setup canvas tabs
    document.querySelectorAll('.canvas-tab').forEach(tab => {
        tab.addEventListener('click', () => switchCanvasTab(tab.dataset.tab));
    });
});

// Export for debugging
window.state = state;
window.api = api;
