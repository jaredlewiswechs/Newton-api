/**
 * Newton Supercomputer - Frontend Application
 * Verified Computation at Scale
 * 
 * © 2026 Jared Lewis Conglomerate
 * Last Updated: January 3, 2026
 */

// ═══════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════

const CONFIG = {
    // API endpoint - change for production
    API_BASE: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://newton-api.onrender.com',

    // Request timeout
    TIMEOUT: 60000
};

// ═══════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════

const state = {
    currentView: 'ask',
    constraints: [],
    ledgerEntries: []
};

// ═══════════════════════════════════════════════════════════════════════════
// DOM Elements
// ═══════════════════════════════════════════════════════════════════════════

const elements = {
    // Navigation
    navTabs: document.querySelectorAll('.nav-tab'),
    views: document.querySelectorAll('.view'),

    // Loading
    loading: document.getElementById('loading'),

    // Ask View
    askInput: document.getElementById('ask-input'),
    askSubmit: document.getElementById('ask-submit'),
    askResult: document.getElementById('ask-result'),
    askStatus: document.getElementById('ask-status'),
    askOutput: document.getElementById('ask-output'),
    askElapsed: document.getElementById('ask-elapsed'),

    // Calculate View
    calcInput: document.getElementById('calc-input'),
    calcSubmit: document.getElementById('calc-submit'),
    calcResult: document.getElementById('calc-result'),
    calcStatus: document.getElementById('calc-status'),
    calcOutput: document.getElementById('calc-output'),
    calcElapsed: document.getElementById('calc-elapsed'),
    calcOps: document.getElementById('calc-ops'),
    maxIterations: document.getElementById('max-iterations'),
    maxOperations: document.getElementById('max-operations'),
    timeout: document.getElementById('timeout'),
    loadExample: document.getElementById('load-example'),

    // Orchestrate View
    constraintDomain: document.getElementById('constraint-domain'),
    constraintField: document.getElementById('constraint-field'),
    constraintOperator: document.getElementById('constraint-operator'),
    constraintValue: document.getElementById('constraint-value'),
    addConstraint: document.getElementById('add-constraint'),
    constraintList: document.getElementById('constraint-list'),
    testObject: document.getElementById('test-object'),
    verifyConstraint: document.getElementById('verify-constraint'),
    constraintResult: document.getElementById('constraint-result'),
    constraintStatus: document.getElementById('constraint-status'),
    constraintOutput: document.getElementById('constraint-output'),

    // Ledger View
    ledgerCount: document.getElementById('ledger-count'),
    ledgerRoot: document.getElementById('ledger-root'),
    refreshLedger: document.getElementById('refresh-ledger'),
    verifyChain: document.getElementById('verify-chain'),
    ledgerEntries: document.getElementById('ledger-entries')
};

// ═══════════════════════════════════════════════════════════════════════════
// API Client
// ═══════════════════════════════════════════════════════════════════════════

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

    async ask(query) {
        return this.request('/ask', {
            method: 'POST',
            body: JSON.stringify({ query })
        });
    },

    async verify(input) {
        return this.request('/verify', {
            method: 'POST',
            body: JSON.stringify({ input })
        });
    },

    async calculate(expression, bounds = {}) {
        return this.request('/calculate', {
            method: 'POST',
            body: JSON.stringify({
                expression,
                max_iterations: bounds.maxIterations || 10000,
                max_operations: bounds.maxOperations || 1000000,
                timeout_seconds: bounds.timeoutSeconds || 30.0
            })
        });
    },

    async evaluateConstraint(constraint, object) {
        return this.request('/constraint', {
            method: 'POST',
            body: JSON.stringify({ constraint, object })
        });
    },

    async getLedger(limit = 100, offset = 0) {
        return this.request(`/ledger?limit=${limit}&offset=${offset}`);
    },

    async verifyLedger() {
        return this.request('/ledger/verify');
    },

    async health() {
        return this.request('/health');
    }
};

// ═══════════════════════════════════════════════════════════════════════════
// UI Helpers
// ═══════════════════════════════════════════════════════════════════════════

function showLoading() {
    elements.loading.style.display = 'flex';
}

function hideLoading() {
    elements.loading.style.display = 'none';
}

function showView(viewName) {
    state.currentView = viewName;

    // Update tabs
    elements.navTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.view === viewName);
    });

    // Update views
    elements.views.forEach(view => {
        view.classList.toggle('active', view.id === `view-${viewName}`);
    });
}

function formatElapsed(microseconds) {
    if (microseconds < 1000) {
        return `${microseconds}μs`;
    } else if (microseconds < 1000000) {
        return `${(microseconds / 1000).toFixed(2)}ms`;
    } else {
        return `${(microseconds / 1000000).toFixed(2)}s`;
    }
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════════════════
// Ask View
// ═══════════════════════════════════════════════════════════════════════════

async function handleAsk() {
    const query = elements.askInput.value.trim();
    if (!query) return;

    showLoading();
    elements.askResult.style.display = 'none';

    try {
        const result = await api.ask(query);

        // Update UI
        elements.askResult.style.display = 'block';

        const verified = result.answer?.verified ?? result.verified;
        elements.askStatus.innerHTML = `
            <div class="status-badge ${verified ? 'verified' : 'failed'}">
                ${verified ? 'VERIFIED' : 'FAILED'}
            </div>
        `;

        elements.askElapsed.textContent = result.elapsed_us
            ? formatElapsed(result.elapsed_us)
            : '';

        elements.askOutput.textContent = JSON.stringify(result, null, 2);

    } catch (error) {
        elements.askResult.style.display = 'block';
        elements.askStatus.innerHTML = `
            <div class="status-badge failed">ERROR</div>
        `;
        elements.askOutput.textContent = error.message;
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Calculate View
// ═══════════════════════════════════════════════════════════════════════════

const EXAMPLES = [
    {
        name: 'Arithmetic',
        expression: { op: '+', args: [2, 3] }
    },
    {
        name: 'Nested',
        expression: { op: '*', args: [{ op: '+', args: [2, 3] }, 4] }
    },
    {
        name: 'Conditional',
        expression: { op: 'if', args: [{ op: '>', args: [10, 5] }, 'yes', 'no'] }
    },
    {
        name: 'Bounded Loop',
        expression: { op: 'for', args: ['i', 0, 5, { op: '*', args: [{ op: 'var', args: ['i'] }, 2] }] }
    },
    {
        name: 'Factorial',
        expression: {
            op: 'block',
            args: [
                { op: 'def', args: ['factorial', ['n'],
                    { op: 'if', args: [
                        { op: '<=', args: [{ op: 'var', args: ['n'] }, 1] },
                        1,
                        { op: '*', args: [
                            { op: 'var', args: ['n'] },
                            { op: 'call', args: ['factorial', { op: '-', args: [{ op: 'var', args: ['n'] }, 1] }] }
                        ] }
                    ] }
                ] },
                { op: 'call', args: ['factorial', 10] }
            ]
        }
    },
    {
        name: 'Map Double',
        expression: {
            op: 'map',
            args: [
                { op: 'lambda', args: [['x'], { op: '*', args: [{ op: 'var', args: ['x'] }, 2] }] },
                { op: 'list', args: [1, 2, 3, 4, 5] }
            ]
        }
    },
    {
        name: 'Reduce Sum',
        expression: {
            op: 'reduce',
            args: [
                { op: 'lambda', args: [['acc', 'x'], { op: '+', args: [{ op: 'var', args: ['acc'] }, { op: 'var', args: ['x'] }] }] },
                0,
                { op: 'list', args: [1, 2, 3, 4, 5] }
            ]
        }
    }
];

let exampleIndex = 0;

function loadNextExample() {
    const example = EXAMPLES[exampleIndex];
    elements.calcInput.value = JSON.stringify(example.expression, null, 2);
    exampleIndex = (exampleIndex + 1) % EXAMPLES.length;
}

async function handleCalculate() {
    let expression;
    try {
        expression = JSON.parse(elements.calcInput.value);
    } catch (e) {
        alert('Invalid JSON expression');
        return;
    }

    const bounds = {
        maxIterations: parseInt(elements.maxIterations.value) || 10000,
        maxOperations: parseInt(elements.maxOperations.value) || 1000000,
        timeoutSeconds: parseFloat(elements.timeout.value) || 30.0
    };

    showLoading();
    elements.calcResult.style.display = 'none';

    try {
        const result = await api.calculate(expression, bounds);

        elements.calcResult.style.display = 'block';

        const verified = result.verified;
        elements.calcStatus.innerHTML = `
            <div class="status-badge ${verified ? 'verified' : 'failed'}">
                ${verified ? 'VERIFIED' : 'ERROR'}
            </div>
        `;

        elements.calcElapsed.textContent = result.elapsed_us
            ? formatElapsed(result.elapsed_us)
            : '';

        elements.calcOps.textContent = result.operations
            ? `${result.operations.toLocaleString()} ops`
            : '';

        // Format result
        let displayValue = result.result;
        if (typeof displayValue === 'object') {
            displayValue = JSON.stringify(displayValue, null, 2);
        }
        elements.calcOutput.textContent = displayValue;

    } catch (error) {
        elements.calcResult.style.display = 'block';
        elements.calcStatus.innerHTML = `
            <div class="status-badge failed">ERROR</div>
        `;
        elements.calcOutput.textContent = error.message;
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Orchestrate View
// ═══════════════════════════════════════════════════════════════════════════

function addConstraint() {
    const domain = elements.constraintDomain.value;
    const field = elements.constraintField.value.trim();
    const operator = elements.constraintOperator.value;
    let value = elements.constraintValue.value.trim();

    if (!field || !value) {
        alert('Please fill in all fields');
        return;
    }

    // Parse value (try as number, then as JSON, then as string)
    if (!isNaN(value)) {
        value = parseFloat(value);
    } else {
        try {
            value = JSON.parse(value);
        } catch (e) {
            // Keep as string
        }
    }

    const constraint = {
        domain,
        field,
        operator,
        value
    };

    state.constraints.push(constraint);
    renderConstraints();

    // Clear inputs
    elements.constraintField.value = '';
    elements.constraintValue.value = '';
}

function removeConstraint(index) {
    state.constraints.splice(index, 1);
    renderConstraints();
}

function renderConstraints() {
    if (state.constraints.length === 0) {
        elements.constraintList.innerHTML = `
            <h4>Active Constraints</h4>
            <div class="constraints-empty">No constraints defined. Add one above.</div>
        `;
        return;
    }

    elements.constraintList.innerHTML = `
        <h4>Active Constraints</h4>
        ${state.constraints.map((c, i) => `
            <div class="constraint-item">
                <span>${c.field} ${c.operator} ${JSON.stringify(c.value)}</span>
                <button class="remove-btn" onclick="removeConstraint(${i})">×</button>
            </div>
        `).join('')}
    `;
}

async function handleVerifyConstraint() {
    if (state.constraints.length === 0) {
        alert('Please add at least one constraint');
        return;
    }

    let testObject;
    try {
        testObject = JSON.parse(elements.testObject.value || '{}');
    } catch (e) {
        alert('Invalid JSON test object');
        return;
    }

    // Build composite constraint if multiple
    let constraint;
    if (state.constraints.length === 1) {
        constraint = state.constraints[0];
    } else {
        constraint = {
            logic: 'and',
            constraints: state.constraints
        };
    }

    showLoading();
    elements.constraintResult.style.display = 'none';

    try {
        const result = await api.evaluateConstraint(constraint, testObject);

        elements.constraintResult.style.display = 'block';

        const passed = result.passed;
        elements.constraintStatus.innerHTML = `
            <div class="status-badge ${passed ? 'passed' : 'failed'}">
                ${passed ? 'PASSED' : 'FAILED'}
            </div>
        `;

        elements.constraintOutput.textContent = JSON.stringify(result, null, 2);

    } catch (error) {
        elements.constraintResult.style.display = 'block';
        elements.constraintStatus.innerHTML = `
            <div class="status-badge failed">ERROR</div>
        `;
        elements.constraintOutput.textContent = error.message;
    } finally {
        hideLoading();
    }
}

// Make removeConstraint available globally
window.removeConstraint = removeConstraint;

// ═══════════════════════════════════════════════════════════════════════════
// Ledger View
// ═══════════════════════════════════════════════════════════════════════════

async function loadLedger() {
    showLoading();

    try {
        const result = await api.getLedger();

        state.ledgerEntries = result.entries || [];
        elements.ledgerCount.textContent = result.total || state.ledgerEntries.length;
        elements.ledgerRoot.textContent = result.merkle_root
            ? result.merkle_root.substring(0, 16) + '...'
            : '-';

        renderLedger();

    } catch (error) {
        console.error('Failed to load ledger:', error);
        elements.ledgerEntries.innerHTML = `
            <div class="ledger-empty">
                <div class="empty-icon">!</div>
                <p>Failed to load ledger</p>
                <p class="empty-hint">${escapeHtml(error.message)}</p>
            </div>
        `;
    } finally {
        hideLoading();
    }
}

function renderLedger() {
    if (state.ledgerEntries.length === 0) {
        elements.ledgerEntries.innerHTML = `
            <div class="ledger-empty">
                <div class="empty-icon">L</div>
                <p>No ledger entries yet</p>
                <p class="empty-hint">Verified operations appear here</p>
            </div>
        `;
        return;
    }

    elements.ledgerEntries.innerHTML = state.ledgerEntries.map(entry => `
        <div class="ledger-entry">
            <span class="entry-index">#${entry.index}</span>
            <span class="entry-type">${entry.type || 'verification'}</span>
            <span class="entry-hash">${entry.hash || '-'}</span>
            <span class="entry-time">${entry.timestamp ? formatTimestamp(entry.timestamp) : '-'}</span>
        </div>
    `).join('');
}

async function handleVerifyChain() {
    showLoading();

    try {
        const result = await api.verifyLedger();

        if (result.valid) {
            alert(`Chain verified! ${result.entries} entries, all intact.`);
        } else {
            alert(`Chain verification failed: ${result.message}`);
        }

    } catch (error) {
        alert(`Verification failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Check API Status
// ═══════════════════════════════════════════════════════════════════════════

async function checkApiStatus() {
    const indicator = document.querySelector('.status-indicator');

    try {
        await api.health();
        indicator.classList.add('online');
        indicator.classList.remove('offline');
    } catch (error) {
        indicator.classList.remove('online');
        indicator.classList.add('offline');
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Beginner Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Set an example query in the Ask input field and optionally submit it
 * Used by the "Try these" example buttons
 */
function setAskExample(exampleText) {
    if (elements.askInput) {
        elements.askInput.value = exampleText;
        elements.askInput.focus();

        // Add a subtle highlight animation
        elements.askInput.style.transition = 'box-shadow 0.3s ease';
        elements.askInput.style.boxShadow = '0 0 0 3px rgba(78, 205, 196, 0.3)';
        setTimeout(() => {
            elements.askInput.style.boxShadow = '';
        }, 500);
    }
}

// Make function globally available for onclick handlers
window.setAskExample = setAskExample;

// ═══════════════════════════════════════════════════════════════════════════
// Event Listeners
// ═══════════════════════════════════════════════════════════════════════════

// Navigation
elements.navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        showView(tab.dataset.view);

        // Load ledger when switching to that view
        if (tab.dataset.view === 'ledger') {
            loadLedger();
        }
    });
});

// Ask View
elements.askSubmit.addEventListener('click', handleAsk);
elements.askInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleAsk();
    }
});

// Calculate View
elements.calcSubmit.addEventListener('click', handleCalculate);
elements.loadExample.addEventListener('click', loadNextExample);

// Orchestrate View
elements.addConstraint.addEventListener('click', addConstraint);
elements.verifyConstraint.addEventListener('click', handleVerifyConstraint);

// Ledger View
elements.refreshLedger.addEventListener('click', loadLedger);
elements.verifyChain.addEventListener('click', handleVerifyChain);

// ═══════════════════════════════════════════════════════════════════════════
// Initialize
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    // Check API status
    checkApiStatus();
    setInterval(checkApiStatus, 30000);

    // Load initial example
    loadNextExample();

    // Initialize constraint list
    renderConstraints();
});

// ═══════════════════════════════════════════════════════════════════════════
// Mobile Navigation (add dynamically if needed)
// ═══════════════════════════════════════════════════════════════════════════

function setupMobileNav() {
    if (window.innerWidth <= 768 && !document.querySelector('.nav-tabs-mobile')) {
        const mobileNav = document.createElement('nav');
        mobileNav.className = 'nav-tabs-mobile';
        mobileNav.innerHTML = `
            <button class="nav-tab active" data-view="ask">Ask</button>
            <button class="nav-tab" data-view="calculate">Calc</button>
            <button class="nav-tab" data-view="orchestrate">Orch</button>
            <button class="nav-tab" data-view="ledger">Ledger</button>
        `;
        document.body.appendChild(mobileNav);

        mobileNav.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                mobileNav.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                showView(tab.dataset.view);

                if (tab.dataset.view === 'ledger') {
                    loadLedger();
                }
            });
        });
    }
}

window.addEventListener('resize', setupMobileNav);
setupMobileNav();

// ═══════════════════════════════════════════════════════════════════════════
// GLASS BOX FEATURES
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Initialize Glass Box components
 */
function initGlassBox() {
    // Get Glass Box stats
    loadGlassBoxStats();
    
    // Set up event listeners
    const createAnchorBtn = document.getElementById('create-anchor');
    const viewApprovalsBtn = document.getElementById('view-approvals');
    const managePoliciesBtn = document.getElementById('manage-policies');
    
    if (createAnchorBtn) {
        createAnchorBtn.addEventListener('click', createMerkleAnchor);
    }
    
    if (viewApprovalsBtn) {
        viewApprovalsBtn.addEventListener('click', showApprovalRequests);
    }
    
    if (managePoliciesBtn) {
        managePoliciesBtn.addEventListener('click', showPolicyManager);
    }
}

/**
 * Load Glass Box statistics
 */
async function loadGlassBoxStats() {
    try {
        const [anchorsResp, approvalsResp, policiesResp] = await Promise.all([
            fetch(`${CONFIG.API_BASE}/merkle/anchors`),
            fetch(`${CONFIG.API_BASE}/negotiator/pending`),
            fetch(`${CONFIG.API_BASE}/policy`)
        ]);
        
        const anchorsData = await anchorsResp.json();
        const approvalsData = await approvalsResp.json();
        const policiesData = await policiesResp.json();
        
        // Update UI
        document.getElementById('anchor-count').textContent = anchorsData.count || 0;
        document.getElementById('pending-approvals').textContent = approvalsData.count || 0;
        document.getElementById('policy-count').textContent = policiesData.stats?.enabled_policies || 0;
        
    } catch (error) {
        console.error('Error loading Glass Box stats:', error);
    }
}

/**
 * Create a new Merkle anchor
 */
async function createMerkleAnchor() {
    try {
        showLoading();
        const response = await fetch(`${CONFIG.API_BASE}/merkle/anchor`, {
            method: 'POST'
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            showNotification('Merkle anchor created successfully', 'success');
            loadGlassBoxStats();
        } else {
            showNotification(data.message || 'No new entries to anchor', 'info');
        }
    } catch (error) {
        hideLoading();
        showNotification('Error creating anchor', 'error');
        console.error(error);
    }
}

/**
 * Export Merkle proof for a ledger entry
 */
async function exportMerkleProof(entryIndex) {
    try {
        showLoading();
        const response = await fetch(`${CONFIG.API_BASE}/merkle/proof/${entryIndex}`);
        const data = await response.json();
        hideLoading();
        
        if (data.proof) {
            // Download certificate as JSON
            const certificate = data.certificate;
            const blob = new Blob([JSON.stringify(certificate, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `newton-proof-${entryIndex}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Proof exported successfully', 'success');
        }
    } catch (error) {
        hideLoading();
        showNotification('Error exporting proof', 'error');
        console.error(error);
    }
}

/**
 * Show approval requests (HITL)
 */
async function showApprovalRequests() {
    try {
        showLoading();
        const response = await fetch(`${CONFIG.API_BASE}/negotiator/pending`);
        const data = await response.json();
        hideLoading();
        
        showApprovalModal(data.pending || []);
    } catch (error) {
        hideLoading();
        showNotification('Error loading approval requests', 'error');
        console.error(error);
    }
}

/**
 * Show policy manager
 */
async function showPolicyManager() {
    try {
        showLoading();
        const response = await fetch(`${CONFIG.API_BASE}/policy`);
        const data = await response.json();
        hideLoading();
        
        showPolicyModal(data.policies || []);
    } catch (error) {
        hideLoading();
        showNotification('Error loading policies', 'error');
        console.error(error);
    }
}

/**
 * Show approval modal
 */
function showApprovalModal(requests) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Pending Approval Requests</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            <div class="approval-list">
                ${requests.length === 0 ? '<p>No pending approvals</p>' : requests.map(req => `
                    <div class="approval-request">
                        <div class="approval-request-header">
                            <strong>${req.operation}</strong>
                            <span class="approval-priority ${req.priority}">${req.priority}</span>
                        </div>
                        <p>${req.reason}</p>
                        <code>${req.input_hash}</code>
                        <div class="approval-actions">
                            <button class="btn success" onclick="approveRequest('${req.id}')">Approve</button>
                            <button class="btn danger" onclick="rejectRequest('${req.id}')">Reject</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

/**
 * Show policy modal
 */
function showPolicyModal(policies) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Policy Management</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            <div class="policy-list">
                ${policies.map(policy => `
                    <div class="approval-request">
                        <div class="approval-request-header">
                            <strong>${policy.name}</strong>
                            <span class="approval-priority ${policy.action}">${policy.type}</span>
                        </div>
                        <p>${policy.metadata?.description || 'No description'}</p>
                        <p><strong>Action:</strong> ${policy.action}</p>
                        <p><strong>Enabled:</strong> ${policy.enabled ? 'Yes' : 'No'}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

/**
 * Approve a request
 */
async function approveRequest(requestId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/negotiator/approve/${requestId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                approver: 'user',
                comments: 'Approved via UI'
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showNotification('Request approved', 'success');
            document.querySelector('.modal-overlay').remove();
            loadGlassBoxStats();
        }
    } catch (error) {
        showNotification('Error approving request', 'error');
        console.error(error);
    }
}

/**
 * Reject a request
 */
async function rejectRequest(requestId) {
    try {
        const reason = prompt('Enter rejection reason:');
        if (!reason) return;
        
        const response = await fetch(`${CONFIG.API_BASE}/negotiator/reject/${requestId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                approver: 'user',
                reason: reason
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showNotification('Request rejected', 'success');
            document.querySelector('.modal-overlay').remove();
            loadGlassBoxStats();
        }
    } catch (error) {
        showNotification('Error rejecting request', 'error');
        console.error(error);
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#30d158' : type === 'error' ? '#ff453a' : '#0a84ff'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: fadeIn 0.3s ease-out;
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initialize Glass Box on page load
document.addEventListener('DOMContentLoaded', initGlassBox);

// Add export proof buttons to ledger entries when they're loaded
const originalLoadLedger = window.loadLedger;
if (originalLoadLedger) {
    window.loadLedger = async function() {
        await originalLoadLedger();
        
        // Add export buttons to entries
        document.querySelectorAll('.ledger-entry').forEach((entry, index) => {
            if (!entry.querySelector('.export-proof-btn')) {
                const exportBtn = document.createElement('button');
                exportBtn.className = 'export-proof-btn';
                exportBtn.textContent = 'Export Proof';
                exportBtn.onclick = () => exportMerkleProof(index);
                entry.appendChild(exportBtn);
            }
        });
    };
}

// ═══════════════════════════════════════════════════════════════════════════
// VOICE INTERFACE (MOAD - Mother Of All Demos)
// ═══════════════════════════════════════════════════════════════════════════

let voiceRecording = false;
let mediaRecorder = null;
let audioChunks = [];

/**
 * Initialize voice interface
 */
function initVoiceInterface() {
    const voiceRecordBtn = document.getElementById('voice-record');
    const voiceSubmitBtn = document.getElementById('voice-submit');
    const voiceStreamBtn = document.getElementById('voice-stream');

    if (voiceRecordBtn) {
        voiceRecordBtn.addEventListener('mousedown', startVoiceRecording);
        voiceRecordBtn.addEventListener('mouseup', stopVoiceRecording);
        voiceRecordBtn.addEventListener('touchstart', startVoiceRecording);
        voiceRecordBtn.addEventListener('touchend', stopVoiceRecording);
    }

    if (voiceSubmitBtn) {
        voiceSubmitBtn.addEventListener('click', handleVoiceSubmit);
    }

    if (voiceStreamBtn) {
        voiceStreamBtn.addEventListener('click', handleVoiceStream);
    }

    // Keyboard shortcut: Cmd+K or Ctrl+K
    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            showView('voice');
            document.getElementById('voice-input').focus();
        }
    });
}

/**
 * Start voice recording
 */
async function startVoiceRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.start();
        voiceRecording = true;

        const btn = document.getElementById('voice-record');
        const status = document.getElementById('voice-status');
        btn.classList.add('recording');
        btn.querySelector('.voice-text').textContent = 'Recording...';
        status.textContent = 'Listening...';
    } catch (error) {
        showNotification('Microphone access denied', 'error');
        console.error('Voice recording error:', error);
    }
}

/**
 * Stop voice recording
 */
function stopVoiceRecording() {
    if (mediaRecorder && voiceRecording) {
        mediaRecorder.stop();
        voiceRecording = false;

        const btn = document.getElementById('voice-record');
        const status = document.getElementById('voice-status');
        btn.classList.remove('recording');
        btn.querySelector('.voice-text').textContent = 'Hold to Speak';
        status.textContent = 'Processing...';

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            // In a real implementation, this would send to speech-to-text service
            // For now, prompt user to type instead
            showNotification('Speech-to-text coming soon! Please type your request.', 'info');
            status.textContent = 'Ready';
        };

        // Stop all tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

/**
 * Handle voice submit
 */
async function handleVoiceSubmit() {
    const input = document.getElementById('voice-input').value.trim();
    if (!input) {
        showNotification('Please enter a request', 'error');
        return;
    }

    showLoading();
    const resultPanel = document.getElementById('voice-result');
    resultPanel.style.display = 'none';

    try {
        const startTime = performance.now();
        const result = await api.request('/voice/ask', {
            method: 'POST',
            body: JSON.stringify({ query: input })
        });
        const elapsed = performance.now() - startTime;

        // Update performance metrics
        document.getElementById('voice-latency').textContent = `${elapsed.toFixed(2)}ms`;

        // Show result
        resultPanel.style.display = 'block';
        const verified = result.verified || result.success;
        document.getElementById('voice-result-status').innerHTML = `
            <div class="status-badge ${verified ? 'verified' : 'failed'}">
                ${verified ? 'VERIFIED' : 'FAILED'}
            </div>
        `;
        document.getElementById('voice-elapsed').textContent = formatElapsed(result.elapsed_us || elapsed * 1000);
        document.getElementById('voice-output').textContent = JSON.stringify(result, null, 2);

        // Store result for export
        window.lastVoiceResult = result;
    } catch (error) {
        resultPanel.style.display = 'block';
        document.getElementById('voice-result-status').innerHTML = `
            <div class="status-badge failed">ERROR</div>
        `;
        document.getElementById('voice-output').textContent = error.message;
    } finally {
        hideLoading();
    }
}

/**
 * Handle voice streaming
 */
async function handleVoiceStream() {
    const input = document.getElementById('voice-input').value.trim();
    if (!input) {
        showNotification('Please enter a request', 'error');
        return;
    }

    const resultPanel = document.getElementById('voice-result');
    const outputEl = document.getElementById('voice-output');
    resultPanel.style.display = 'block';
    outputEl.textContent = 'Streaming response...\n\n';

    try {
        // Simulate streaming for demo
        const response = await api.request('/voice/ask', {
            method: 'POST',
            body: JSON.stringify({ query: input, stream: true })
        });

        // In real implementation, this would be an SSE stream
        const text = JSON.stringify(response, null, 2);
        let currentText = '';
        for (let i = 0; i < text.length; i++) {
            currentText += text[i];
            outputEl.textContent = currentText;
            await new Promise(resolve => setTimeout(resolve, 10));
        }

        window.lastVoiceResult = response;
    } catch (error) {
        outputEl.textContent = `Error: ${error.message}`;
    }
}

/**
 * Load voice pattern
 */
function loadVoicePattern(patternType) {
    const patterns = {
        lesson: 'Create a lesson plan for 5th grade math on adding fractions with unlike denominators, aligned to TEKS 5.3K',
        assess: 'Analyze this assessment data and create student groupings for differentiation: Maria 85, James 72, Sofia 95, Alex 68',
        slides: 'Generate a presentation slide deck for my lesson on the water cycle with visual examples',
        constraint: 'Define a constraint that verifies bank account balance stays above $100 after any transaction'
    };

    document.getElementById('voice-input').value = patterns[patternType] || '';
    showNotification('Pattern loaded! Click "Process with Voice AI" to continue.', 'success');
}

/**
 * Export voice result
 */
function exportVoiceResult(format) {
    if (!window.lastVoiceResult) {
        showNotification('No result to export', 'error');
        return;
    }

    const result = window.lastVoiceResult;
    let content, mimeType, filename;

    if (format === 'json') {
        content = JSON.stringify(result, null, 2);
        mimeType = 'application/json';
        filename = 'newton-voice-result.json';
    } else if (format === 'csv') {
        // Simple CSV conversion
        const rows = [['Key', 'Value']];
        for (const [key, value] of Object.entries(result)) {
            rows.push([key, typeof value === 'object' ? JSON.stringify(value) : value]);
        }
        content = rows.map(row => row.join(',')).join('\n');
        mimeType = 'text/csv';
        filename = 'newton-voice-result.csv';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showNotification(`Exported as ${format.toUpperCase()}`, 'success');
}

/**
 * Copy voice result
 */
function copyVoiceResult() {
    if (!window.lastVoiceResult) {
        showNotification('No result to copy', 'error');
        return;
    }

    const text = JSON.stringify(window.lastVoiceResult, null, 2);
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard', 'success');
    }).catch(() => {
        showNotification('Failed to copy', 'error');
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// F/G RATIO CONSTRAINT DEMONSTRATIONS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check overdraft constraint
 */
function checkOverdraft() {
    const balance = parseFloat(document.getElementById('overdraft-balance').value) || 0;
    const withdrawal = parseFloat(document.getElementById('overdraft-withdrawal').value) || 0;
    
    const remaining = balance - withdrawal;
    const ratio = remaining;
    
    document.getElementById('overdraft-ratio').textContent = ratio.toFixed(2);
    
    const statusEl = document.getElementById('overdraft-status');
    if (ratio >= 0) {
        statusEl.innerHTML = '<div class="status-badge verified">ALLOWED</div>';
    } else {
        statusEl.innerHTML = '<div class="status-badge failed">OVERDRAFT</div>';
    }
}

/**
 * Check leverage constraint
 */
function checkLeverage() {
    const position = parseFloat(document.getElementById('leverage-position').value) || 0;
    const balance = parseFloat(document.getElementById('leverage-balance').value) || 1;
    
    const ratio = position / balance;
    
    document.getElementById('leverage-ratio').textContent = ratio.toFixed(2);
    
    const statusEl = document.getElementById('leverage-status');
    if (ratio <= 3.0) {
        statusEl.innerHTML = '<div class="status-badge verified">ALLOWED</div>';
    } else {
        statusEl.innerHTML = '<div class="status-badge failed">EXCESSIVE LEVERAGE</div>';
    }
}

/**
 * Check custom ratio constraint
 */
function checkCustomRatio() {
    const f = parseFloat(document.getElementById('custom-f').value) || 0;
    const g = parseFloat(document.getElementById('custom-g').value) || 1;
    const op = document.getElementById('custom-op').value;
    const threshold = parseFloat(document.getElementById('custom-threshold').value) || 0;
    
    if (g === 0) {
        document.getElementById('custom-ratio').textContent = '∞';
        document.getElementById('custom-status').innerHTML = '<div class="status-badge failed">finfr (g=0)</div>';
        return;
    }
    
    const ratio = f / g;
    document.getElementById('custom-ratio').textContent = ratio.toFixed(2);
    
    // Update constraint text
    const opSymbols = { ge: '≥', le: '≤', eq: '==', gt: '>', lt: '<' };
    document.getElementById('custom-constraint').textContent = `Must be ${opSymbols[op]} ${threshold}`;
    
    // Check constraint
    let passed = false;
    switch(op) {
        case 'ge': passed = ratio >= threshold; break;
        case 'le': passed = ratio <= threshold; break;
        case 'eq': passed = Math.abs(ratio - threshold) < 0.01; break;
        case 'gt': passed = ratio > threshold; break;
        case 'lt': passed = ratio < threshold; break;
    }
    
    const statusEl = document.getElementById('custom-status');
    if (passed) {
        statusEl.innerHTML = '<div class="status-badge verified">PASSED</div>';
    } else {
        statusEl.innerHTML = '<div class="status-badge failed">FAILED</div>';
    }
}

// Auto-update ratio displays when inputs change
document.addEventListener('DOMContentLoaded', () => {
    // Overdraft inputs
    ['overdraft-balance', 'overdraft-withdrawal'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', checkOverdraft);
    });
    
    // Leverage inputs
    ['leverage-position', 'leverage-balance'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', checkLeverage);
    });
    
    // Custom ratio inputs
    ['custom-f', 'custom-g', 'custom-op', 'custom-threshold'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', checkCustomRatio);
    });
    
    // Initialize voice interface
    initVoiceInterface();
    
    // Initialize ratio demonstrations
    checkOverdraft();
    checkLeverage();
    checkCustomRatio();
});

// Make functions globally available
window.loadVoicePattern = loadVoicePattern;
window.exportVoiceResult = exportVoiceResult;
window.copyVoiceResult = copyVoiceResult;
window.checkOverdraft = checkOverdraft;
window.checkLeverage = checkLeverage;
window.checkCustomRatio = checkCustomRatio;

