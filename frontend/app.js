/**
 * Newton Supercomputer - Frontend Application
 * Verified Computation at Scale
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

        const verified = result.verified;
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
