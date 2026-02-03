/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * NINA PDA - Consumer Application Controller
 * A contemporary Apple Newton for verified computation
 * 
 * © 2026 parcRI Research / Ada Computing Company
 * ═══════════════════════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════════════════════
// APP STATE
// ═══════════════════════════════════════════════════════════════════════════════

const NinaState = {
    currentApp: 'home',
    notes: [],
    names: [],
    events: [],
    verifyHistory: [],
    calcExpression: '',
    calcResult: '0',
    currentMonth: new Date(),
    regime: 'factual'
};

// ═══════════════════════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════════════════════

function navigateTo(appId) {
    // Hide all apps
    document.querySelectorAll('.nina-app, .nina-home').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show target app
    const targetId = appId === 'home' ? 'home-screen' : `app-${appId}`;
    const target = document.getElementById(targetId);
    if (target) {
        target.style.display = 'flex';
    }
    
    // Update title
    const titles = {
        'home': 'Nina',
        'notes': 'Notes',
        'names': 'Names',
        'dates': 'Dates',
        'calc': 'Calculator',
        'verify': 'Verify',
        'assist': 'Assist'
    };
    document.getElementById('app-title').textContent = titles[appId] || 'Nina';
    
    // Show/hide back button
    document.getElementById('btn-back').style.visibility = 
        appId === 'home' ? 'hidden' : 'visible';
    
    NinaState.currentApp = appId;
}

// ═══════════════════════════════════════════════════════════════════════════════
// TIME UPDATE
// ═══════════════════════════════════════════════════════════════════════════════

function updateTime() {
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    });
    document.getElementById('status-time').textContent = time;
}

// ═══════════════════════════════════════════════════════════════════════════════
// NOTES APP
// ═══════════════════════════════════════════════════════════════════════════════

function initNotes() {
    // Sample notes
    NinaState.notes = [
        { id: 1, title: 'Welcome to Nina', content: 'Your personal digital assistant with verified computation.', verified: true },
        { id: 2, title: 'Shopping List', content: '- Milk\n- Bread\n- Coffee', verified: true },
        { id: 3, title: 'Meeting Notes', content: 'Discuss project timeline with team.', verified: false }
    ];
    renderNotes();
}

function renderNotes() {
    const list = document.getElementById('notes-list');
    list.innerHTML = NinaState.notes.map(note => `
        <div class="note-item" data-id="${note.id}">
            <h4>${note.title} ${note.verified ? '✓' : ''}</h4>
            <p>${note.content.substring(0, 50)}...</p>
        </div>
    `).join('');
}

// ═══════════════════════════════════════════════════════════════════════════════
// NAMES APP
// ═══════════════════════════════════════════════════════════════════════════════

function initNames() {
    NinaState.names = [
        { id: 1, name: 'Ada Lovelace', role: 'First Programmer', initials: 'AL' },
        { id: 2, name: 'Isaac Newton', role: 'Physicist', initials: 'IN' },
        { id: 3, name: 'John Sculley', role: 'Apple CEO (Newton era)', initials: 'JS' },
        { id: 4, name: 'Steve Sakoman', role: 'Newton Creator', initials: 'SS' }
    ];
    renderNames();
}

function renderNames() {
    const list = document.getElementById('names-list');
    const search = document.getElementById('names-search').value.toLowerCase();
    const filtered = NinaState.names.filter(n => 
        n.name.toLowerCase().includes(search) || 
        n.role.toLowerCase().includes(search)
    );
    
    list.innerHTML = filtered.map(name => `
        <div class="name-item" data-id="${name.id}">
            <div class="name-avatar">${name.initials}</div>
            <div class="name-info">
                <h4>${name.name}</h4>
                <p>${name.role}</p>
            </div>
        </div>
    `).join('');
}

// ═══════════════════════════════════════════════════════════════════════════════
// DATES APP
// ═══════════════════════════════════════════════════════════════════════════════

function initDates() {
    NinaState.events = [
        { date: '2026-02-03', title: 'Nina Launch Day' },
        { date: '2026-02-14', title: 'Valentine\'s Day' }
    ];
    renderCalendar();
}

function renderCalendar() {
    const grid = document.getElementById('calendar-grid');
    const date = NinaState.currentMonth;
    const year = date.getFullYear();
    const month = date.getMonth();
    
    // Update header
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'];
    document.getElementById('current-month').textContent = `${monthNames[month]} ${year}`;
    
    // Day headers
    const dayHeaders = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
    let html = dayHeaders.map(d => `<div class="calendar-day header">${d}</div>`).join('');
    
    // Get first day and total days
    const firstDay = new Date(year, month, 1).getDay();
    const totalDays = new Date(year, month + 1, 0).getDate();
    const prevMonthDays = new Date(year, month, 0).getDate();
    
    // Previous month days
    for (let i = firstDay - 1; i >= 0; i--) {
        html += `<div class="calendar-day other-month">${prevMonthDays - i}</div>`;
    }
    
    // Current month days
    const today = new Date();
    for (let i = 1; i <= totalDays; i++) {
        const isToday = today.getDate() === i && 
                        today.getMonth() === month && 
                        today.getFullYear() === year;
        html += `<div class="calendar-day ${isToday ? 'today' : ''}">${i}</div>`;
    }
    
    // Next month days
    const remaining = 42 - (firstDay + totalDays);
    for (let i = 1; i <= remaining; i++) {
        html += `<div class="calendar-day other-month">${i}</div>`;
    }
    
    grid.innerHTML = html;
    
    // Render today's events
    renderEvents();
}

function renderEvents() {
    const list = document.getElementById('events-list');
    const today = new Date().toISOString().split('T')[0];
    const todayEvents = NinaState.events.filter(e => e.date === today);
    
    if (todayEvents.length === 0) {
        list.innerHTML = '<div class="event-item">No events today</div>';
    } else {
        list.innerHTML = todayEvents.map(e => 
            `<div class="event-item">${e.title}</div>`
        ).join('');
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// CALCULATOR APP (Newton Verified)
// ═══════════════════════════════════════════════════════════════════════════════

function initCalc() {
    NinaState.calcExpression = '';
    NinaState.calcResult = '0';
    updateCalcDisplay();
}

function updateCalcDisplay() {
    document.getElementById('calc-expression').textContent = NinaState.calcExpression;
    document.getElementById('calc-result').textContent = NinaState.calcResult;
}

function calcInput(value) {
    if (NinaState.calcResult === 'Error') {
        NinaState.calcExpression = '';
        NinaState.calcResult = '0';
    }
    NinaState.calcExpression += value;
    updateCalcDisplay();
}

function calcAction(action) {
    switch (action) {
        case 'clear':
            NinaState.calcExpression = '';
            NinaState.calcResult = '0';
            break;
        case 'backspace':
            NinaState.calcExpression = NinaState.calcExpression.slice(0, -1);
            break;
        case 'add':
            NinaState.calcExpression += '+';
            break;
        case 'subtract':
            NinaState.calcExpression += '-';
            break;
        case 'multiply':
            NinaState.calcExpression += '×';
            break;
        case 'divide':
            NinaState.calcExpression += '÷';
            break;
        case 'percent':
            NinaState.calcExpression += '%';
            break;
        case 'equals':
            calculateResult();
            break;
    }
    updateCalcDisplay();
}

function calculateResult() {
    try {
        // Convert display operators to JS operators
        let expr = NinaState.calcExpression
            .replace(/×/g, '*')
            .replace(/÷/g, '/')
            .replace(/%/g, '/100');
        
        // NEWTON VERIFICATION: Bounded evaluation
        // In production, this would call the Newton logic engine
        const result = Function('"use strict"; return (' + expr + ')')();
        
        if (!isFinite(result)) {
            NinaState.calcResult = 'Error';
        } else {
            // Round to avoid floating point weirdness
            NinaState.calcResult = Math.round(result * 1000000000) / 1000000000;
        }
        
        // Log verified calculation
        console.log(`[NINA] Verified: ${NinaState.calcExpression} = ${NinaState.calcResult}`);
        
    } catch (e) {
        NinaState.calcResult = 'Error';
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// VERIFY APP (Newton's Killer Feature)
// ═══════════════════════════════════════════════════════════════════════════════

async function verifyStatement() {
    const statement = document.getElementById('verify-statement').value.trim();
    if (!statement) return;
    
    const resultDiv = document.getElementById('verify-result');
    const statusDiv = document.getElementById('result-status');
    const traceDiv = document.getElementById('result-trace');
    const trustLabel = document.getElementById('trust-label');
    const boundsReport = document.getElementById('bounds-report');
    
    // Show loading
    resultDiv.style.display = 'block';
    statusDiv.textContent = '⏳ Verifying...';
    statusDiv.className = 'result-status';
    traceDiv.textContent = '';
    
    // Simulate verification (in production, calls Newton backend)
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Mock verification result
    const mockVerification = verifyLocally(statement);
    
    // Display result
    if (mockVerification.verified) {
        statusDiv.textContent = '✓ VERIFIED';
        statusDiv.className = 'result-status verified';
        trustLabel.textContent = 'TRUSTED';
        trustLabel.className = 'trust-label';
    } else {
        statusDiv.textContent = '✗ UNVERIFIED';
        statusDiv.className = 'result-status unverified';
        trustLabel.textContent = 'UNTRUSTED';
        trustLabel.className = 'trust-label untrusted';
    }
    
    traceDiv.textContent = mockVerification.trace.join('\n');
    boundsReport.textContent = `${mockVerification.ops} ops | ${mockVerification.time_ms}ms`;
    
    // Add to history
    NinaState.verifyHistory.unshift({
        statement: statement.substring(0, 30) + '...',
        verified: mockVerification.verified,
        time: new Date().toLocaleTimeString()
    });
    renderVerifyHistory();
}

function verifyLocally(statement) {
    // Local verification heuristics
    const lower = statement.toLowerCase();
    
    // Simple fact patterns
    const factPatterns = [
        { pattern: /capital of france.*paris|paris.*capital of france/i, verified: true },
        { pattern: /2\s*\+\s*2\s*=\s*4|4\s*=\s*2\s*\+\s*2/i, verified: true },
        { pattern: /earth.*round|earth.*sphere/i, verified: true },
        { pattern: /1\s*==\s*1/i, verified: true },
        { pattern: /newton.*verified/i, verified: true }
    ];
    
    for (const fp of factPatterns) {
        if (fp.pattern.test(statement)) {
            return {
                verified: fp.verified,
                trace: [
                    `> Parse: "${statement}"`,
                    `> Shape: VERIFY_FACT`,
                    `> Match: Pattern ${fp.pattern}`,
                    `> Result: ${fp.verified ? 'TRUE' : 'FALSE'}`
                ],
                ops: Math.floor(Math.random() * 50) + 10,
                time_ms: Math.floor(Math.random() * 20) + 5
            };
        }
    }
    
    // Unknown - return unverified
    return {
        verified: false,
        trace: [
            `> Parse: "${statement}"`,
            `> Shape: UNKNOWN`,
            `> No verified source found`,
            `> Requires external verification`
        ],
        ops: Math.floor(Math.random() * 30) + 5,
        time_ms: Math.floor(Math.random() * 10) + 2
    };
}

function renderVerifyHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = NinaState.verifyHistory.slice(0, 5).map(h => `
        <div class="history-item">
            ${h.verified ? '✓' : '✗'} ${h.statement} <span style="float:right">${h.time}</span>
        </div>
    `).join('');
}

// ═══════════════════════════════════════════════════════════════════════════════
// ASSIST APP (AI Assistant)
// ═══════════════════════════════════════════════════════════════════════════════

async function sendAssistMessage() {
    const input = document.getElementById('assist-query');
    const query = input.value.trim();
    if (!query) return;
    
    const chat = document.getElementById('assist-chat');
    
    // Add user message
    chat.innerHTML += `
        <div class="chat-message user">
            <p>${escapeHtml(query)}</p>
        </div>
    `;
    
    input.value = '';
    
    // Get regime
    const regime = document.getElementById('regime-select').value;
    
    // Simulate response (in production, calls Newton backend)
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const response = generateAssistResponse(query, regime);
    
    chat.innerHTML += `
        <div class="chat-message nina">
            <p>${response.message}</p>
            <div class="verified-badge">${response.verified ? '✓ Verified' : '⚠ Unverified'} | Regime: ${regime}</div>
        </div>
    `;
    
    // Scroll to bottom
    chat.scrollTop = chat.scrollHeight;
}

function generateAssistResponse(query, regime) {
    const lower = query.toLowerCase();
    
    // Simple response patterns
    if (lower.includes('capital') && lower.includes('france')) {
        return { message: 'The capital of France is Paris.', verified: true };
    }
    if (lower.match(/what is \d+\s*[\+\-\*\/]\s*\d+/)) {
        try {
            const expr = lower.match(/what is (.+)/)[1].replace(/x/g, '*');
            const result = eval(expr);
            return { message: `${expr} = ${result}`, verified: true };
        } catch {
            return { message: 'I couldn\'t compute that expression.', verified: false };
        }
    }
    if (lower.includes('hello') || lower.includes('hi')) {
        return { message: 'Hello! I\'m Nina, your verified assistant. How can I help you?', verified: true };
    }
    if (lower.includes('newton')) {
        return { message: 'Newton is a verified computation substrate. The constraint is the instruction.', verified: true };
    }
    if (lower.includes('time') || lower.includes('date')) {
        return { message: `The current time is ${new Date().toLocaleString()}.`, verified: true };
    }
    
    return { 
        message: 'I don\'t have a verified answer for that. In a full Newton deployment, I would check the knowledge base and provide a sourced response.',
        verified: false 
    };
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    // Update time
    updateTime();
    setInterval(updateTime, 1000);
    
    // Initialize apps
    initNotes();
    initNames();
    initDates();
    initCalc();
    
    // Navigation: App icons
    document.querySelectorAll('.app-icon').forEach(icon => {
        icon.addEventListener('click', () => {
            const app = icon.dataset.app;
            navigateTo(app);
        });
    });
    
    // Navigation: Home button
    document.getElementById('home-button').addEventListener('click', () => {
        navigateTo('home');
    });
    
    // Navigation: Back button
    document.getElementById('btn-back').addEventListener('click', () => {
        navigateTo('home');
    });
    
    // Names search
    document.getElementById('names-search').addEventListener('input', renderNames);
    
    // Calendar navigation
    document.getElementById('prev-month').addEventListener('click', () => {
        NinaState.currentMonth.setMonth(NinaState.currentMonth.getMonth() - 1);
        renderCalendar();
    });
    document.getElementById('next-month').addEventListener('click', () => {
        NinaState.currentMonth.setMonth(NinaState.currentMonth.getMonth() + 1);
        renderCalendar();
    });
    
    // Calculator keys
    document.querySelectorAll('.calc-key').forEach(key => {
        key.addEventListener('click', () => {
            if (key.dataset.value) {
                calcInput(key.dataset.value);
            } else if (key.dataset.action) {
                calcAction(key.dataset.action);
            }
        });
    });
    
    // Verify button
    document.getElementById('verify-btn').addEventListener('click', verifyStatement);
    document.getElementById('verify-statement').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            verifyStatement();
        }
    });
    
    // Assist send
    document.getElementById('assist-send').addEventListener('click', sendAssistMessage);
    document.getElementById('assist-query').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendAssistMessage();
        }
    });
    
    // Regime change
    document.getElementById('regime-select').addEventListener('change', (e) => {
        NinaState.regime = e.target.value;
    });
    
    // Developer mode toggle (Ctrl+Shift+D)
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'D') {
            const devIndicator = document.getElementById('dev-indicator');
            devIndicator.style.display = devIndicator.style.display === 'none' ? 'flex' : 'none';
        }
    });
    
    console.log('[NINA] Personal Digital Assistant initialized');
    console.log('[NINA] Press Ctrl+Shift+D for developer mode');
});
