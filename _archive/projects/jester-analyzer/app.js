/**
 * JESTER - Code Constraint Analyzer
 * Newton-style deterministic code analysis
 * Updated: February 1, 2026
 */

// =============================================================================
// Configuration
// =============================================================================

const CONFIG = {
    // API URL detection - use shared config if available
    apiUrl: detectApiUrl(),
    // Storage keys
    storageKey: 'jester_history',
    maxHistory: 50,
};

function detectApiUrl() {
    // Try to use shared config first
    if (typeof window.NewtonConfig !== 'undefined') {
        return window.NewtonConfig.API_BASE;
    }
    
    // Fallback: detect from hostname
    const hostname = window.location.hostname;
    
    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // Vercel deployment - API is on same origin (PRIMARY)
    if (hostname.endsWith('.vercel.app') || hostname === 'vercel.app') {
        return window.location.origin;
    }
    
    // Legacy Render deployment - API is on same origin
    if (hostname.endsWith('.onrender.com') || hostname === 'onrender.com') {
        return window.location.origin;
    }
    
    // Legacy Cloudflare Pages - same origin
    if (hostname.endsWith('.pages.dev') || hostname === 'pages.dev' ||
        hostname.endsWith('.cloudflare.com') || hostname === 'cloudflare.com') {
        return window.location.origin;
    }
    
    // Default: assume API is on same origin
    return window.location.origin;
}

// =============================================================================
// State
// =============================================================================

const state = {
    currentView: 'analyzer',
    lastAnalysis: null,
    history: [],
    isConnected: false,
};

// =============================================================================
// DOM Elements
// =============================================================================

const elements = {
    // Views
    views: document.querySelectorAll('.view'),
    navItems: document.querySelectorAll('.nav-item'),
    contentTitle: document.getElementById('content-title'),

    // Analyzer
    codeInput: document.getElementById('code-input'),
    lineNumbers: document.getElementById('line-numbers'),
    languageSelect: document.getElementById('language-select'),
    analyzeBtn: document.getElementById('analyze-btn'),
    resultsContent: document.getElementById('results-content'),
    constraintCount: document.getElementById('constraint-count'),

    // Buttons
    clearCodeBtn: document.getElementById('clear-code-btn'),
    pasteCodeBtn: document.getElementById('paste-code-btn'),
    loadExampleBtn: document.getElementById('load-example-btn'),
    copyJsonBtn: document.getElementById('copy-json-btn'),
    downloadJsonBtn: document.getElementById('download-json-btn'),
    copyCdlBtn: document.getElementById('copy-cdl-btn'),
    downloadCdlBtn: document.getElementById('download-cdl-btn'),

    // Output
    cartridgeJson: document.getElementById('cartridge-json'),
    cdlCode: document.getElementById('cdl-code'),
    historyList: document.getElementById('history-list'),
    examplesGrid: document.getElementById('examples-grid'),

    // Status
    statusDot: document.getElementById('status-dot'),
    statusText: document.getElementById('status-text'),

    // Overlays
    loadingOverlay: document.getElementById('loading-overlay'),
    toastContainer: document.getElementById('toast-container'),
};

// =============================================================================
// Examples
// =============================================================================

const EXAMPLES = [
    {
        id: 'python-withdraw',
        title: 'Bank Withdrawal',
        language: 'python',
        description: 'Classic financial constraint example with guards',
        code: `def withdraw(amount, balance):
    """Withdraw money from account."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if amount > balance:
        return None  # Insufficient funds
    if balance < 100:
        print("Warning: Low balance")
    return balance - amount`
    },
    {
        id: 'swift-guard',
        title: 'Swift Guard Pattern',
        language: 'swift',
        description: 'Swift early exit with guard statements',
        code: `func processUser(_ user: User?) -> String {
    guard let user = user else {
        return "No user provided"
    }
    guard user.age >= 18 else {
        return "User must be adult"
    }
    guard user.isVerified else {
        return "User not verified"
    }
    precondition(user.id > 0, "Invalid user ID")
    return "Processing \\(user.name)"
}`
    },
    {
        id: 'javascript-validation',
        title: 'Input Validation',
        language: 'javascript',
        description: 'Form validation with multiple checks',
        code: `function validateForm(data) {
    if (!data) {
        throw new Error('No data provided');
    }
    if (data.email === null) {
        return { valid: false, error: 'Email required' };
    }
    if (data.password.length < 8) {
        return { valid: false, error: 'Password too short' };
    }
    if (data.age < 13) {
        throw new Error('Must be 13 or older');
    }
    return { valid: true };
}`
    },
    {
        id: 'c-bounds',
        title: 'Array Bounds Check',
        language: 'c',
        description: 'C array access with bounds validation',
        code: `int get_element(int* arr, int size, int index) {
    assert(arr != NULL);
    assert(size > 0);

    if (index < 0) {
        return -1;  // Invalid index
    }
    if (index >= size) {
        return -1;  // Out of bounds
    }

    return arr[index];
}`
    },
    {
        id: 'java-null',
        title: 'Java Null Safety',
        language: 'java',
        description: 'Defensive null checking pattern',
        code: `public String processOrder(Order order) {
    if (order == null) {
        throw new IllegalArgumentException("Order cannot be null");
    }
    if (order.getItems() == null) {
        return "Empty order";
    }
    if (order.getItems().size() == 0) {
        return "No items in order";
    }
    assert order.getTotal() >= 0 : "Total cannot be negative";
    return "Order processed: " + order.getId();
}`
    },
    {
        id: 'go-error',
        title: 'Go Error Handling',
        language: 'go',
        description: 'Idiomatic Go error checking',
        code: `func fetchData(url string) ([]byte, error) {
    if url == "" {
        return nil, errors.New("URL cannot be empty")
    }
    if !strings.HasPrefix(url, "https://") {
        panic("URL must use HTTPS")
    }

    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    if resp.StatusCode != 200 {
        return nil, fmt.Errorf("bad status: %d", resp.StatusCode)
    }

    return io.ReadAll(resp.Body)
}`
    },
    {
        id: 'rust-option',
        title: 'Rust Option Handling',
        language: 'rust',
        description: 'Rust unwrap and expect patterns',
        code: `fn process_value(input: Option<i32>) -> i32 {
    let value = input.expect("Input must be provided");

    assert!(value >= 0, "Value must be non-negative");

    if value > 1000 {
        panic!("Value too large");
    }

    let result = value.checked_mul(2).unwrap();
    result
}`
    },
    {
        id: 'objc-nsassert',
        title: 'Objective-C Assertions',
        language: 'objc',
        description: 'NSAssert and parameter validation',
        code: `- (NSString *)formatUser:(User *)user {
    NSParameterAssert(user != nil);
    NSAssert(user.name.length > 0, @"Name required");

    if (user.age < 0) {
        return @"Invalid age";
    }
    if (user.email == nil) {
        return @"Email required";
    }

    return [NSString stringWithFormat:@"%@ (%ld)",
            user.name, (long)user.age];
}`
    }
];

// =============================================================================
// API Functions
// =============================================================================

async function checkConnection() {
    try {
        const response = await fetch(`${CONFIG.apiUrl}/jester/info`);
        if (response.ok) {
            state.isConnected = true;
            elements.statusDot.classList.add('connected');
            elements.statusDot.classList.remove('disconnected');
            elements.statusText.textContent = 'Connected';
        } else {
            throw new Error('Not OK');
        }
    } catch (e) {
        state.isConnected = false;
        elements.statusDot.classList.remove('connected');
        elements.statusDot.classList.add('disconnected');
        elements.statusText.textContent = 'Offline';
    }
}

async function analyzeCode(code, language = null) {
    const payload = { code };
    if (language) {
        payload.language = language;
    }

    const response = await fetch(`${CONFIG.apiUrl}/jester/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error(`Analysis failed: ${response.status}`);
    }

    return await response.json();
}

async function getCdlOutput(code, language = null) {
    const payload = { code };
    if (language) {
        payload.language = language;
    }

    const response = await fetch(`${CONFIG.apiUrl}/jester/cdl`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error(`CDL generation failed: ${response.status}`);
    }

    return await response.json();
}

// =============================================================================
// UI Functions
// =============================================================================

function showView(viewName) {
    state.currentView = viewName;

    // Update nav
    elements.navItems.forEach(item => {
        if (item.dataset.view === viewName) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Update views
    elements.views.forEach(view => {
        if (view.id === `view-${viewName}`) {
            view.classList.add('active');
        } else {
            view.classList.remove('active');
        }
    });

    // Update title
    const titles = {
        analyzer: 'Code Analyzer',
        history: 'Analysis History',
        cartridge: 'Newton Cartridge',
        cdl: 'CDL Output',
        docs: 'Documentation',
        examples: 'Code Examples',
    };
    elements.contentTitle.textContent = titles[viewName] || viewName;
}

function updateLineNumbers() {
    const lines = elements.codeInput.value.split('\n');
    const numbers = lines.map((_, i) => i + 1).join('\n');
    elements.lineNumbers.textContent = numbers;
}

function showLoading(show = true) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function renderResults(data) {
    if (!data || !data.constraints || data.constraints.length === 0) {
        elements.resultsContent.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">&#x1F50D;</div>
                <div class="empty-title">No Constraints Found</div>
                <div class="empty-description">
                    No guards, assertions, or constraints were detected in this code.
                    Try code with if statements, assertions, or guard clauses.
                </div>
            </div>
        `;
        elements.constraintCount.textContent = '0 constraints';
        return;
    }

    const summary = data.summary || {};
    const constraints = data.constraints;
    const forbidden = data.forbidden_states || [];
    const invariants = data.required_invariants || [];

    let html = `
        <div class="results-summary">
            <div class="summary-title">Analysis Summary - ${data.source_language}</div>
            <div class="summary-stats">
                <div class="stat-item">
                    <div class="stat-value">${constraints.length}</div>
                    <div class="stat-label">Constraints</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${forbidden.length}</div>
                    <div class="stat-label">Forbidden</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${invariants.length}</div>
                    <div class="stat-label">Invariants</div>
                </div>
            </div>
        </div>
    `;

    // Constraints list
    html += '<div class="constraint-list">';
    for (const c of constraints) {
        html += `
            <div class="constraint-card">
                <div class="constraint-header">
                    <span class="constraint-kind ${c.kind}">${formatKind(c.kind)}</span>
                    ${c.line_number ? `<span class="constraint-line">Line ${c.line_number}</span>` : ''}
                </div>
                <div class="constraint-raw">${escapeHtml(c.raw_condition)}</div>
                <div class="constraint-newton">${escapeHtml(c.newton_constraint)}</div>
                ${c.context ? `<div class="constraint-context">${escapeHtml(c.context)}</div>` : ''}
            </div>
        `;
    }
    html += '</div>';

    // Forbidden states
    if (forbidden.length > 0) {
        html += `
            <div class="forbidden-states">
                <h4>Forbidden States</h4>
                <ul>
                    ${forbidden.map(f => `<li>${escapeHtml(f)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Invariants
    if (invariants.length > 0) {
        html += `
            <div class="invariants">
                <h4>Required Invariants</h4>
                <ul>
                    ${invariants.map(i => `<li>${escapeHtml(i)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    elements.resultsContent.innerHTML = html;
    elements.constraintCount.textContent = `${constraints.length} constraint${constraints.length !== 1 ? 's' : ''}`;
}

function renderHistory() {
    if (state.history.length === 0) {
        elements.historyList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">&#x1F4CB;</div>
                <div class="empty-title">No History Yet</div>
                <div class="empty-description">
                    Your analysis history will appear here.
                </div>
            </div>
        `;
        return;
    }

    let html = '';
    for (const item of state.history.slice().reverse()) {
        const date = new Date(item.timestamp);
        const timeStr = date.toLocaleString();
        const snippet = item.code.substring(0, 60).replace(/\n/g, ' ');

        html += `
            <div class="history-item" data-index="${state.history.indexOf(item)}">
                <div class="history-meta">
                    <span class="history-lang">${item.language}</span>
                    <span class="history-time">${timeStr}</span>
                </div>
                <div class="history-snippet">${escapeHtml(snippet)}...</div>
                <div class="history-stats">
                    <span>${item.constraintCount} constraints</span>
                </div>
            </div>
        `;
    }

    elements.historyList.innerHTML = html;

    // Add click handlers
    elements.historyList.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const index = parseInt(item.dataset.index);
            loadFromHistory(index);
        });
    });
}

function renderExamples() {
    let html = '';
    for (const example of EXAMPLES) {
        const preview = example.code.substring(0, 150);
        html += `
            <div class="example-card" data-id="${example.id}">
                <div class="example-header">
                    <span class="example-title">${example.title}</span>
                    <span class="example-lang">${example.language}</span>
                </div>
                <div class="example-description">${example.description}</div>
                <div class="example-preview">${escapeHtml(preview)}...</div>
            </div>
        `;
    }

    elements.examplesGrid.innerHTML = html;

    // Add click handlers
    elements.examplesGrid.querySelectorAll('.example-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = card.dataset.id;
            loadExample(id);
        });
    });
}

function loadExample(id) {
    const example = EXAMPLES.find(e => e.id === id);
    if (example) {
        elements.codeInput.value = example.code;
        elements.languageSelect.value = example.language;
        updateLineNumbers();
        showView('analyzer');
        showToast(`Loaded: ${example.title}`, 'success');
    }
}

function loadFromHistory(index) {
    const item = state.history[index];
    if (item) {
        elements.codeInput.value = item.code;
        elements.languageSelect.value = item.language || '';
        updateLineNumbers();

        if (item.result) {
            state.lastAnalysis = item.result;
            renderResults(item.result);
            updateCartridgeView(item.result);
            if (item.cdl) {
                elements.cdlCode.textContent = item.cdl;
            }
        }

        showView('analyzer');
        showToast('Loaded from history', 'success');
    }
}

function updateCartridgeView(data) {
    elements.cartridgeJson.textContent = JSON.stringify(data, null, 2);
}

// =============================================================================
// Helpers
// =============================================================================

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatKind(kind) {
    const map = {
        guard: 'Guard',
        assertion: 'Assertion',
        early_exit: 'Early Exit',
        null_check: 'Null Check',
        range_check: 'Range Check',
        exception: 'Exception',
        precondition: 'Precondition',
        postcondition: 'Postcondition',
        invariant: 'Invariant',
        type_check: 'Type Check',
        forbidden_state: 'Forbidden',
    };
    return map[kind] || kind;
}

function saveHistory() {
    try {
        localStorage.setItem(CONFIG.storageKey, JSON.stringify(state.history));
    } catch (e) {
        console.warn('Failed to save history:', e);
    }
}

function loadHistory() {
    try {
        const saved = localStorage.getItem(CONFIG.storageKey);
        if (saved) {
            state.history = JSON.parse(saved);
        }
    } catch (e) {
        console.warn('Failed to load history:', e);
        state.history = [];
    }
}

function addToHistory(code, language, result, cdl) {
    const entry = {
        code,
        language,
        result,
        cdl,
        constraintCount: result.constraints?.length || 0,
        timestamp: Date.now(),
    };

    state.history.push(entry);

    // Keep only last N entries
    if (state.history.length > CONFIG.maxHistory) {
        state.history = state.history.slice(-CONFIG.maxHistory);
    }

    saveHistory();
    renderHistory();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

function downloadFile(content, filename, type = 'application/json') {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${filename}`, 'success');
}

// =============================================================================
// Event Handlers
// =============================================================================

async function handleAnalyze() {
    const code = elements.codeInput.value.trim();
    if (!code) {
        showToast('Please enter some code to analyze', 'error');
        return;
    }

    const language = elements.languageSelect.value || null;

    showLoading(true);

    try {
        // Analyze code
        const result = await analyzeCode(code, language);
        state.lastAnalysis = result;

        // Get CDL output
        let cdl = '';
        try {
            const cdlResult = await getCdlOutput(code, language);
            cdl = cdlResult.cdl || '';
            elements.cdlCode.textContent = cdl;
        } catch (e) {
            console.warn('CDL generation failed:', e);
            elements.cdlCode.textContent = '// CDL generation failed';
        }

        // Update UI
        renderResults(result);
        updateCartridgeView(result);

        // Add to history
        addToHistory(code, language || result.source_language, result, cdl);

        showToast(`Found ${result.constraints?.length || 0} constraints`, 'success');

    } catch (error) {
        console.error('Analysis error:', error);
        showToast(`Analysis failed: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// =============================================================================
// Initialization
// =============================================================================

function init() {
    // Load saved history
    loadHistory();

    // Check API connection
    checkConnection();
    setInterval(checkConnection, 30000);

    // Navigation
    elements.navItems.forEach(item => {
        item.addEventListener('click', () => {
            showView(item.dataset.view);
        });
    });

    // Code input
    elements.codeInput.addEventListener('input', updateLineNumbers);
    elements.codeInput.addEventListener('scroll', () => {
        elements.lineNumbers.scrollTop = elements.codeInput.scrollTop;
    });

    // Analyze button
    elements.analyzeBtn.addEventListener('click', handleAnalyze);

    // Keyboard shortcut
    elements.codeInput.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            handleAnalyze();
        }
    });

    // Clear button
    elements.clearCodeBtn.addEventListener('click', () => {
        elements.codeInput.value = '';
        updateLineNumbers();
    });

    // Paste button
    elements.pasteCodeBtn.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            elements.codeInput.value = text;
            updateLineNumbers();
            showToast('Pasted from clipboard', 'success');
        } catch (e) {
            showToast('Failed to paste', 'error');
        }
    });

    // Load example button
    elements.loadExampleBtn.addEventListener('click', () => {
        showView('examples');
    });

    // Copy/download buttons
    elements.copyJsonBtn.addEventListener('click', () => {
        copyToClipboard(elements.cartridgeJson.textContent);
    });

    elements.downloadJsonBtn.addEventListener('click', () => {
        downloadFile(elements.cartridgeJson.textContent, 'cartridge.json');
    });

    elements.copyCdlBtn.addEventListener('click', () => {
        copyToClipboard(elements.cdlCode.textContent);
    });

    elements.downloadCdlBtn.addEventListener('click', () => {
        downloadFile(elements.cdlCode.textContent, 'constraints.cdl', 'text/plain');
    });

    // Initial renders
    updateLineNumbers();
    renderHistory();
    renderExamples();
}

// Make showView global for inline onclick
window.showView = showView;

// Start app
document.addEventListener('DOMContentLoaded', init);
