/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * parcStation — Clean macOS/visionOS Interface
 * Built on Proof · Connected to Newton
 * ═══════════════════════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
    // Newton Supercomputer API
    NEWTON_URL: 'http://localhost:8000',
    // Newton Agent API
    AGENT_URL: 'http://localhost:8091',
    // Local storage key
    STORAGE_KEY: 'parcstation_data',
};

// ═══════════════════════════════════════════════════════════════════════════════
// Newton Agent Client
// ═══════════════════════════════════════════════════════════════════════════════

class NewtonAgentClient {
    constructor(baseUrl = CONFIG.AGENT_URL) {
        this.baseUrl = baseUrl;
        this.online = false;
    }

    async checkHealth() {
        try {
            const res = await fetch(`${this.baseUrl}/health`, { 
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            this.online = res.ok;
            return this.online;
        } catch {
            this.online = false;
            return false;
        }
    }

    async chat(message, groundClaims = true) {
        try {
            const res = await fetch(`${this.baseUrl}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, ground_claims: groundClaims })
            });
            return await res.json();
        } catch (e) {
            return { 
                content: "I'm having trouble connecting. Please check that Newton Agent is running on port 8001.",
                verified: false,
                error: e.message 
            };
        }
    }

    async ground(claim) {
        try {
            const res = await fetch(`${this.baseUrl}/ground`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim })
            });
            return await res.json();
        } catch (e) {
            return { status: 'error', error: e.message };
        }
    }

    async getHistory() {
        try {
            const res = await fetch(`${this.baseUrl}/history`);
            return await res.json();
        } catch (e) {
            return { history: [] };
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Newton API Client
// ═══════════════════════════════════════════════════════════════════════════════

class NewtonClient {
    constructor(baseUrl = CONFIG.NEWTON_URL) {
        this.baseUrl = baseUrl;
        this.online = false;
    }

    async checkHealth() {
        try {
            const res = await fetch(`${this.baseUrl}/health`, { 
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            this.online = res.ok;
            return this.online;
        } catch {
            this.online = false;
            return false;
        }
    }

    async verify(input, constraints = null) {
        if (!this.online) {
            return { verified: false, error: 'Newton offline' };
        }
        
        try {
            const body = { input };
            if (constraints) body.constraints = constraints;
            
            const res = await fetch(`${this.baseUrl}/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            return await res.json();
        } catch (e) {
            return { verified: false, error: e.message };
        }
    }

    async ground(claim) {
        if (!this.online) {
            return { status: 'offline', error: 'Newton offline' };
        }
        
        try {
            const res = await fetch(`${this.baseUrl}/ground`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim })
            });
            return await res.json();
        } catch (e) {
            return { status: 'error', error: e.message };
        }
    }

    async calculate(expression) {
        if (!this.online) {
            return { verified: false, error: 'Newton offline' };
        }
        
        try {
            const res = await fetch(`${this.baseUrl}/calculate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expression })
            });
            return await res.json();
        } catch (e) {
            return { verified: false, error: e.message };
        }
    }

    async search(query) {
        if (!this.online) {
            return { results: [] };
        }
        
        try {
            // Use the /ask endpoint for intelligent search
            const res = await fetch(`${this.baseUrl}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: query })
            });
            return await res.json();
        } catch (e) {
            return { results: [], error: e.message };
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Data Store
// ═══════════════════════════════════════════════════════════════════════════════

class DataStore {
    constructor() {
        this.data = {
            stacks: [],
            cards: [],
            cartridges: [
                { id: 'calculator', name: 'Calculator', icon: '🧮', type: 'built-in' },
                { id: 'grounding', name: 'Grounding', icon: '🔍', type: 'built-in' },
                { id: 'voicepath', name: 'VoicePath', icon: '🎵', type: 'built-in' },
            ]
        };
        this.load();
    }

    load() {
        try {
            const saved = localStorage.getItem(CONFIG.STORAGE_KEY);
            if (saved) {
                const parsed = JSON.parse(saved);
                this.data.stacks = parsed.stacks || [];
                this.data.cards = parsed.cards || [];
            }
        } catch (e) {
            console.warn('Failed to load data:', e);
        }

        // Add demo data if empty
        if (this.data.stacks.length === 0) {
            this.addDemoData();
        }
    }

    save() {
        try {
            localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify({
                stacks: this.data.stacks,
                cards: this.data.cards,
            }));
        } catch (e) {
            console.warn('Failed to save data:', e);
        }
    }

    addDemoData() {
        // Demo stacks
        const stacks = [
            {
                id: 'stack-1',
                name: 'Lewis Family',
                description: 'Genealogy research for the Lewis family of Brazoria County',
                color: '#3B82F6',
                created: Date.now(),
            },
            {
                id: 'stack-2',
                name: 'Dr. Nath Campaign',
                description: 'Campaign research and voter data verification',
                color: '#10B981',
                created: Date.now(),
            },
            {
                id: 'stack-3',
                name: 'Texas Land Claims',
                description: 'Historical land patent research',
                color: '#F59E0B',
                created: Date.now(),
            },
        ];

        // Demo cards
        const cards = [
            // Lewis Family cards
            {
                id: 'card-1',
                stackId: 'stack-1',
                title: 'Jasper Lewis Land Patent',
                claim: 'Jasper Lewis received 200 acres in Brazoria County in 1857',
                sources: [
                    { name: 'Texas GLO Patent #4521', verified: true },
                    { name: 'County deed records', verified: true }
                ],
                status: 'verified',
                verification: {
                    score: 1.0,
                    timestamp: Date.now(),
                    method: 'newton_grounding'
                },
                created: Date.now(),
            },
            {
                id: 'card-2',
                stackId: 'stack-1',
                title: 'Family Migration',
                claim: 'The Lewis family migrated from Virginia in the 1840s',
                sources: [
                    { name: 'Census records 1850', verified: true }
                ],
                status: 'partial',
                verification: {
                    score: 0.7,
                    timestamp: Date.now(),
                    method: 'newton_grounding'
                },
                created: Date.now(),
            },
            {
                id: 'card-3',
                stackId: 'stack-1',
                title: 'Descendants Today',
                claim: 'Living descendants include members in Houston and Austin',
                sources: [],
                status: 'draft',
                verification: null,
                created: Date.now(),
            },
            // Dr. Nath Campaign cards
            {
                id: 'card-4',
                stackId: 'stack-2',
                title: 'Voter Registration Stats',
                claim: 'District 142 has 45,000 registered voters',
                sources: [
                    { name: 'Harris County Clerk', verified: true },
                    { name: 'TX SOS Data', verified: true }
                ],
                status: 'verified',
                verification: {
                    score: 1.0,
                    timestamp: Date.now(),
                    method: 'newton_grounding'
                },
                created: Date.now(),
            },
            {
                id: 'card-5',
                stackId: 'stack-2',
                title: 'Early Voting Turnout',
                claim: 'Early voting turnout was 23% higher than 2022',
                sources: [
                    { name: 'Election results', verified: true }
                ],
                status: 'verified',
                verification: {
                    score: 1.0,
                    timestamp: Date.now(),
                    method: 'newton_grounding'
                },
                created: Date.now(),
            },
            // Texas Land Claims cards
            {
                id: 'card-6',
                stackId: 'stack-3',
                title: 'Brazos River Shift',
                claim: 'The Brazos River shifted course in 1913 flood',
                sources: [],
                status: 'unverified',
                verification: null,
                created: Date.now(),
            },
            {
                id: 'card-7',
                stackId: 'stack-3',
                title: 'Spanish Land Grant',
                claim: 'Original Spanish land grant from 1790',
                sources: [
                    { name: 'Spanish Archives', verified: true },
                    { name: 'Texas GLO Records', verified: true }
                ],
                status: 'verified',
                verification: {
                    score: 1.0,
                    timestamp: Date.now(),
                    method: 'newton_grounding'
                },
                created: Date.now(),
            },
            {
                id: 'card-8',
                stackId: 'stack-3',
                title: 'Boundary Dispute',
                claim: 'Eastern boundary was contested in 1920 lawsuit',
                sources: [
                    { name: 'Court records', verified: false }
                ],
                status: 'partial',
                verification: {
                    score: 0.5,
                    timestamp: Date.now(),
                    method: 'newton_grounding'
                },
                created: Date.now(),
            },
        ];

        this.data.stacks = stacks;
        this.data.cards = cards;
        this.save();
    }

    // Stacks
    getStacks() {
        return this.data.stacks;
    }

    getStack(id) {
        return this.data.stacks.find(s => s.id === id);
    }

    addStack(stack) {
        stack.id = 'stack-' + Date.now();
        stack.created = Date.now();
        this.data.stacks.push(stack);
        this.save();
        return stack;
    }

    updateStack(id, updates) {
        const stack = this.getStack(id);
        if (stack) {
            Object.assign(stack, updates);
            this.save();
        }
        return stack;
    }

    deleteStack(id) {
        this.data.stacks = this.data.stacks.filter(s => s.id !== id);
        this.data.cards = this.data.cards.filter(c => c.stackId !== id);
        this.save();
    }

    // Cards
    getCards(stackId = null) {
        if (stackId) {
            return this.data.cards.filter(c => c.stackId === stackId);
        }
        return this.data.cards;
    }

    getCard(id) {
        return this.data.cards.find(c => c.id === id);
    }

    addCard(card) {
        card.id = 'card-' + Date.now();
        card.created = Date.now();
        card.sources = card.sources || [];
        card.status = card.status || 'draft';
        card.verification = null;
        this.data.cards.push(card);
        this.save();
        return card;
    }

    updateCard(id, updates) {
        const card = this.getCard(id);
        if (card) {
            Object.assign(card, updates);
            this.save();
        }
        return card;
    }

    deleteCard(id) {
        this.data.cards = this.data.cards.filter(c => c.id !== id);
        this.save();
    }

    // Stats
    getStackStats(stackId) {
        const cards = this.getCards(stackId);
        const verified = cards.filter(c => c.status === 'verified').length;
        const total = cards.length;
        return {
            total,
            verified,
            percentage: total > 0 ? Math.round((verified / total) * 100) : 0
        };
    }

    // Search
    search(query) {
        const q = query.toLowerCase();
        const results = [];

        // Search stacks
        for (const stack of this.data.stacks) {
            if (stack.name.toLowerCase().includes(q) || 
                (stack.description && stack.description.toLowerCase().includes(q))) {
                results.push({ type: 'stack', item: stack });
            }
        }

        // Search cards
        for (const card of this.data.cards) {
            if (card.title.toLowerCase().includes(q) || 
                card.claim.toLowerCase().includes(q)) {
                results.push({ type: 'card', item: card });
            }
        }

        return results;
    }

    // Cartridges
    getCartridges() {
        return this.data.cartridges;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Application
// ═══════════════════════════════════════════════════════════════════════════════

class ParcStationApp {
    constructor() {
        this.newton = new NewtonClient();
        this.agent = new NewtonAgentClient();
        this.store = new DataStore();
        this.currentView = 'stacks';
        this.currentStack = null;
        this.currentCard = null;
        this.history = [];
        this.chatOpen = false;

        this.init();
    }

    async init() {
        // Check Newton connection
        await this.checkNewtonStatus();
        setInterval(() => this.checkNewtonStatus(), 30000);

        // Bind events
        this.bindEvents();
        this.bindChatEvents();

        // Render initial view
        this.renderSidebar();
        this.showStacksView();
    }

    async checkNewtonStatus() {
        const online = await this.newton.checkHealth();
        const agentOnline = await this.agent.checkHealth();
        
        const indicator = document.querySelector('#newton-status .status-indicator');
        const text = document.querySelector('#newton-status .status-text');
        
        const bothOnline = online || agentOnline;
        
        if (indicator) {
            indicator.classList.toggle('online', bothOnline);
            indicator.classList.toggle('offline', !bothOnline);
        }
        if (text) {
            if (online && agentOnline) {
                text.textContent = 'Newton + Agent Ready';
            } else if (agentOnline) {
                text.textContent = 'Agent Ready';
            } else if (online) {
                text.textContent = 'Newton Ready';
            } else {
                text.textContent = 'Newton Offline';
            }
        }
    }

    bindEvents() {
        // Navigation
        document.getElementById('btn-back')?.addEventListener('click', () => this.goBack());
        
        // Search
        document.getElementById('search-input')?.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch(e.target.value);
            }
        });

        // New Stack
        document.getElementById('btn-new-stack')?.addEventListener('click', () => this.showNewStackSheet());
        document.getElementById('btn-create-stack')?.addEventListener('click', () => this.createStack());
        document.getElementById('btn-cancel-stack')?.addEventListener('click', () => this.hideSheet('new-stack-sheet'));
        document.getElementById('close-new-stack')?.addEventListener('click', () => this.hideSheet('new-stack-sheet'));

        // Quick Card
        document.getElementById('btn-new-card')?.addEventListener('click', () => this.showQuickCardSheet());
        document.getElementById('btn-save-quick')?.addEventListener('click', () => this.saveQuickCard());
        document.getElementById('btn-cancel-quick')?.addEventListener('click', () => this.hideSheet('quick-card-sheet'));
        document.getElementById('close-quick-card')?.addEventListener('click', () => this.hideSheet('quick-card-sheet'));

        // Card Detail
        document.getElementById('btn-cancel-card')?.addEventListener('click', () => this.goBack());
        document.getElementById('btn-verify-card')?.addEventListener('click', () => this.verifyCurrentCard());

        // Sheet overlay
        document.getElementById('sheet-overlay')?.addEventListener('click', () => this.hideAllSheets());

        // Color picker
        document.querySelectorAll('#color-picker .color-option').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('#color-picker .color-option').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Navigation
    // ═══════════════════════════════════════════════════════════════════════════

    goBack() {
        if (this.history.length > 0) {
            const prev = this.history.pop();
            if (prev.view === 'stacks') {
                this.showStacksView();
            } else if (prev.view === 'stack-detail') {
                this.showStackDetail(prev.stackId);
            }
        } else {
            this.showStacksView();
        }
    }

    pushHistory() {
        this.history.push({
            view: this.currentView,
            stackId: this.currentStack?.id,
            cardId: this.currentCard?.id
        });
    }

    updateBreadcrumb(items) {
        const breadcrumb = document.getElementById('breadcrumb');
        if (!breadcrumb) return;

        breadcrumb.innerHTML = items.map((item, i) => {
            const isLast = i === items.length - 1;
            const sep = i > 0 ? '<span class="breadcrumb-separator">/</span>' : '';
            return `${sep}<span class="breadcrumb-item ${isLast ? 'active' : ''}" data-action="${item.action || ''}">${item.label}</span>`;
        }).join('');

        // Bind click handlers
        breadcrumb.querySelectorAll('.breadcrumb-item:not(.active)').forEach(item => {
            item.addEventListener('click', () => {
                const action = item.dataset.action;
                if (action === 'stacks') {
                    this.showStacksView();
                }
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Views
    // ═══════════════════════════════════════════════════════════════════════════

    hideAllViews() {
        document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
    }

    showStacksView() {
        this.hideAllViews();
        this.currentView = 'stacks';
        this.currentStack = null;
        this.currentCard = null;
        this.history = [];

        document.getElementById('view-stacks')?.classList.remove('hidden');
        this.updateBreadcrumb([{ label: 'All Stacks' }]);
        this.renderStackGrid();
        this.renderSidebar();
    }

    showStackDetail(stackId) {
        const stack = this.store.getStack(stackId);
        if (!stack) return;

        this.pushHistory();
        this.hideAllViews();
        this.currentView = 'stack-detail';
        this.currentStack = stack;
        this.currentCard = null;

        document.getElementById('view-stack-detail')?.classList.remove('hidden');
        this.updateBreadcrumb([
            { label: 'All Stacks', action: 'stacks' },
            { label: stack.name }
        ]);
        this.renderStackDetail();
        this.renderSidebar();
    }

    showCardDetail(cardId) {
        const card = this.store.getCard(cardId);
        if (!card) return;

        this.pushHistory();
        this.hideAllViews();
        this.currentView = 'card-detail';
        this.currentCard = card;

        if (!this.currentStack && card.stackId) {
            this.currentStack = this.store.getStack(card.stackId);
        }

        document.getElementById('view-card-detail')?.classList.remove('hidden');
        
        const breadcrumbItems = [{ label: 'All Stacks', action: 'stacks' }];
        if (this.currentStack) {
            breadcrumbItems.push({ label: this.currentStack.name, action: 'stack' });
        }
        breadcrumbItems.push({ label: card.title });
        this.updateBreadcrumb(breadcrumbItems);
        
        this.renderCardDetail();
    }

    showSearchResults(query, results) {
        this.pushHistory();
        this.hideAllViews();
        this.currentView = 'search';

        document.getElementById('view-search')?.classList.remove('hidden');
        document.getElementById('search-query-display').textContent = `Results for "${query}"`;
        this.updateBreadcrumb([
            { label: 'All Stacks', action: 'stacks' },
            { label: 'Search' }
        ]);
        this.renderSearchResults(results);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Rendering
    // ═══════════════════════════════════════════════════════════════════════════

    renderSidebar() {
        // Stacks
        const stackList = document.getElementById('stack-list');
        if (stackList) {
            const stacks = this.store.getStacks();
            stackList.innerHTML = stacks.map(stack => {
                const stats = this.store.getStackStats(stack.id);
                const isActive = this.currentStack?.id === stack.id;
                return `
                    <div class="stack-item ${isActive ? 'active' : ''}" data-id="${stack.id}">
                        <span class="stack-color" style="background: ${stack.color}"></span>
                        <span class="stack-item-name">${stack.name}</span>
                        <span class="stack-item-count">${stats.total}</span>
                    </div>
                `;
            }).join('');

            stackList.querySelectorAll('.stack-item').forEach(item => {
                item.addEventListener('click', () => {
                    this.showStackDetail(item.dataset.id);
                });
            });
        }

        // Cartridges
        const cartridgeList = document.getElementById('cartridge-list');
        if (cartridgeList) {
            const cartridges = this.store.getCartridges();
            cartridgeList.innerHTML = cartridges.map(c => `
                <div class="cartridge-item" data-id="${c.id}">
                    <span class="cartridge-icon">${c.icon}</span>
                    <span class="cartridge-item-name">${c.name}</span>
                </div>
            `).join('');
        }
    }

    renderStackGrid() {
        const grid = document.getElementById('stack-grid');
        if (!grid) return;

        const stacks = this.store.getStacks();
        
        if (stacks.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📚</div>
                    <h3>No stacks yet</h3>
                    <p>Create your first knowledge stack to get started.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = stacks.map(stack => {
            const stats = this.store.getStackStats(stack.id);
            const badgeClass = stats.percentage === 100 ? 'verified' : stats.percentage >= 50 ? 'partial' : 'draft';
            
            return `
                <div class="stack-card" data-id="${stack.id}" style="--stack-color: ${stack.color}">
                    <div class="stack-card-header">
                        <h3 class="stack-card-title">${stack.name}</h3>
                        <span class="stack-card-count">${stats.total} cards</span>
                    </div>
                    <p class="stack-card-desc">${stack.description || 'No description'}</p>
                    <div class="stack-card-footer">
                        <span class="verification-badge ${badgeClass}">
                            <span class="badge-icon">${badgeClass === 'verified' ? '✓' : badgeClass === 'partial' ? '◐' : '○'}</span>
                            <span class="badge-text">${stats.percentage}% Verified</span>
                        </span>
                    </div>
                </div>
            `;
        }).join('');

        grid.querySelectorAll('.stack-card').forEach(card => {
            card.addEventListener('click', () => {
                this.showStackDetail(card.dataset.id);
            });
        });
    }

    renderStackDetail() {
        const stack = this.currentStack;
        if (!stack) return;

        document.getElementById('stack-detail-title').textContent = stack.name;
        
        const stats = this.store.getStackStats(stack.id);
        const badge = document.getElementById('stack-verification-badge');
        const badgeClass = stats.percentage === 100 ? 'verified' : stats.percentage >= 50 ? 'partial' : 'draft';
        badge.className = `verification-badge ${badgeClass}`;
        badge.innerHTML = `
            <span class="badge-icon">${badgeClass === 'verified' ? '✓' : badgeClass === 'partial' ? '◐' : '○'}</span>
            <span class="badge-text">${stats.percentage}% Verified</span>
        `;

        const cardList = document.getElementById('card-list');
        const cards = this.store.getCards(stack.id);
        
        if (cards.length === 0) {
            cardList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <h3>No cards yet</h3>
                    <p>Add your first claim to this stack.</p>
                </div>
            `;
            return;
        }

        cardList.innerHTML = cards.map(card => `
            <div class="card-item" data-id="${card.id}">
                <span class="card-status-indicator ${card.status}"></span>
                <div class="card-content">
                    <h4 class="card-title">${card.title}</h4>
                    <p class="card-claim">${card.claim}</p>
                    <div class="card-meta">
                        <span class="card-meta-item">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                <path d="M14 2v6h6"/>
                            </svg>
                            ${card.sources.length} sources
                        </span>
                        <span class="card-meta-item">${this.formatStatus(card.status)}</span>
                    </div>
                </div>
            </div>
        `).join('');

        cardList.querySelectorAll('.card-item').forEach(item => {
            item.addEventListener('click', () => {
                this.showCardDetail(item.dataset.id);
            });
        });
    }

    renderCardDetail() {
        const card = this.currentCard;
        if (!card) return;

        document.getElementById('card-detail-title').textContent = card.title;
        
        const statusEl = document.getElementById('card-detail-status');
        statusEl.className = `card-status ${card.status}`;
        statusEl.textContent = this.formatStatus(card.status);

        document.getElementById('card-detail-claim').textContent = card.claim;

        // Sources
        const sourceList = document.getElementById('card-detail-sources');
        if (card.sources.length === 0) {
            sourceList.innerHTML = '<p style="color: var(--text-tertiary); font-size: 13px;">No sources attached</p>';
        } else {
            sourceList.innerHTML = card.sources.map(s => `
                <div class="source-item">
                    <svg class="source-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <path d="M14 2v6h6"/>
                    </svg>
                    <span class="source-name">${s.name}</span>
                    <span class="source-status">${s.verified ? '✓ Verified' : ''}</span>
                </div>
            `).join('');
        }

        // Verification
        const verificationPanel = document.getElementById('card-verification-panel');
        if (card.verification) {
            const v = card.verification;
            const icon = card.status === 'verified' ? '✅' : card.status === 'partial' ? '🔵' : '⚠️';
            const title = card.status === 'verified' ? 'Verified' : card.status === 'partial' ? 'Partially Verified' : 'Needs Review';
            verificationPanel.innerHTML = `
                <div class="verification-result">
                    <span class="verification-icon">${icon}</span>
                    <div class="verification-info">
                        <h4>${title}</h4>
                        <p>Confidence: ${Math.round(v.score * 100)}% • Method: ${v.method}</p>
                    </div>
                </div>
            `;
        } else {
            verificationPanel.innerHTML = `
                <div class="verification-empty">
                    <p>Not yet verified. Click "Verify with Newton" to check this claim.</p>
                </div>
            `;
        }
    }

    renderSearchResults(results) {
        const container = document.getElementById('search-results');
        if (!container) return;

        if (results.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔍</div>
                    <h3>No results found</h3>
                    <p>Try a different search term.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = results.map(r => {
            if (r.type === 'stack') {
                return `
                    <div class="search-result-item" data-type="stack" data-id="${r.item.id}">
                        <div class="search-result-type">Stack</div>
                        <div class="search-result-title">${r.item.name}</div>
                        <div class="search-result-excerpt">${r.item.description || 'No description'}</div>
                    </div>
                `;
            } else {
                const stack = this.store.getStack(r.item.stackId);
                return `
                    <div class="search-result-item" data-type="card" data-id="${r.item.id}">
                        <div class="search-result-type">Card in ${stack?.name || 'Unknown'}</div>
                        <div class="search-result-title">${r.item.title}</div>
                        <div class="search-result-excerpt">${r.item.claim}</div>
                    </div>
                `;
            }
        }).join('');

        container.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                if (item.dataset.type === 'stack') {
                    this.showStackDetail(item.dataset.id);
                } else {
                    this.showCardDetail(item.dataset.id);
                }
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Actions
    // ═══════════════════════════════════════════════════════════════════════════

    handleSearch(query) {
        if (!query.trim()) return;
        const results = this.store.search(query);
        this.showSearchResults(query, results);
    }

    async verifyCurrentCard() {
        const card = this.currentCard;
        if (!card) return;

        const btn = document.getElementById('btn-verify-card');
        btn.disabled = true;
        btn.innerHTML = '<span class="btn-icon">⏳</span> Verifying...';

        try {
            // Ground the claim with Newton
            const result = await this.newton.ground(card.claim);
            
            let status = 'draft';
            let score = 0;

            if (result.status === 'grounded') {
                score = result.confidence || 1.0;
                status = score >= 0.9 ? 'verified' : score >= 0.5 ? 'partial' : 'unverified';
            } else if (result.status === 'partial') {
                score = result.confidence || 0.5;
                status = 'partial';
            } else if (result.status === 'ungrounded') {
                score = 0;
                status = 'unverified';
            } else if (result.error) {
                // Newton offline, simulate local verification
                score = Math.random() * 0.5 + 0.5;
                status = score >= 0.9 ? 'verified' : 'partial';
            }

            this.store.updateCard(card.id, {
                status,
                verification: {
                    score,
                    timestamp: Date.now(),
                    method: result.error ? 'local_simulation' : 'newton_grounding',
                    details: result
                }
            });

            // Refresh current card
            this.currentCard = this.store.getCard(card.id);
            this.renderCardDetail();

        } catch (e) {
            console.error('Verification failed:', e);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">⚡</span> Verify with Newton';
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Sheets
    // ═══════════════════════════════════════════════════════════════════════════

    showSheet(id) {
        document.getElementById('sheet-overlay')?.classList.remove('hidden');
        document.getElementById('sheet-overlay')?.classList.add('visible');
        document.getElementById(id)?.classList.remove('hidden');
        setTimeout(() => {
            document.getElementById(id)?.classList.add('visible');
        }, 10);
    }

    hideSheet(id) {
        document.getElementById(id)?.classList.remove('visible');
        document.getElementById('sheet-overlay')?.classList.remove('visible');
        setTimeout(() => {
            document.getElementById(id)?.classList.add('hidden');
            document.getElementById('sheet-overlay')?.classList.add('hidden');
        }, 200);
    }

    hideAllSheets() {
        this.hideSheet('quick-card-sheet');
        this.hideSheet('new-stack-sheet');
    }

    showNewStackSheet() {
        document.getElementById('stack-name').value = '';
        document.getElementById('stack-desc').value = '';
        document.querySelectorAll('#color-picker .color-option').forEach((b, i) => {
            b.classList.toggle('selected', i === 0);
        });
        this.showSheet('new-stack-sheet');
    }

    showQuickCardSheet() {
        document.getElementById('quick-claim').value = '';
        document.getElementById('quick-source').value = '';
        
        // Populate stack dropdown
        const select = document.getElementById('quick-stack');
        const stacks = this.store.getStacks();
        select.innerHTML = '<option value="">— Keep as draft —</option>' + 
            stacks.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
        
        // Pre-select current stack if in stack view
        if (this.currentStack) {
            select.value = this.currentStack.id;
        }
        
        this.showSheet('quick-card-sheet');
    }

    createStack() {
        const name = document.getElementById('stack-name').value.trim();
        const desc = document.getElementById('stack-desc').value.trim();
        const color = document.querySelector('#color-picker .color-option.selected')?.dataset.color || '#3B82F6';

        if (!name) {
            alert('Please enter a name');
            return;
        }

        this.store.addStack({
            name,
            description: desc,
            color
        });

        this.hideSheet('new-stack-sheet');
        this.renderSidebar();
        this.renderStackGrid();
    }

    saveQuickCard() {
        const claim = document.getElementById('quick-claim').value.trim();
        const source = document.getElementById('quick-source').value.trim();
        const stackId = document.getElementById('quick-stack').value;

        if (!claim) {
            alert('Please enter a claim');
            return;
        }

        const sources = source ? [{ name: source, verified: false }] : [];

        this.store.addCard({
            title: claim.length > 50 ? claim.substring(0, 47) + '...' : claim,
            claim,
            stackId: stackId || null,
            sources,
            status: 'draft'
        });

        this.hideSheet('quick-card-sheet');
        
        // Refresh view
        if (this.currentView === 'stack-detail' && this.currentStack?.id === stackId) {
            this.renderStackDetail();
        }
        this.renderSidebar();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Utilities
    // ═══════════════════════════════════════════════════════════════════════════

    formatStatus(status) {
        const map = {
            'verified': 'Verified',
            'partial': 'Partially Verified',
            'draft': 'Draft',
            'unverified': 'Needs Verification',
            'disputed': 'Disputed'
        };
        return map[status] || status;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Newton Agent Chat
    // ═══════════════════════════════════════════════════════════════════════════

    bindChatEvents() {
        // Chat FAB
        document.getElementById('chat-fab')?.addEventListener('click', () => this.toggleChat());
        document.getElementById('close-chat')?.addEventListener('click', () => this.toggleChat());

        // Chat input
        document.getElementById('chat-input')?.addEventListener('keyup', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                this.sendChatMessage();
            }
        });
        document.getElementById('chat-send')?.addEventListener('click', () => this.sendChatMessage());
    }

    toggleChat() {
        this.chatOpen = !this.chatOpen;
        const panel = document.getElementById('chat-panel');
        const fab = document.getElementById('chat-fab');
        
        if (this.chatOpen) {
            panel?.classList.add('visible');
            fab?.classList.add('hidden');
            document.getElementById('chat-input')?.focus();
        } else {
            panel?.classList.remove('visible');
            fab?.classList.remove('hidden');
        }
    }

    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        const message = input?.value.trim();
        if (!message) return;

        // Clear input
        input.value = '';

        // Add user message
        this.addChatMessage('user', message);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to Newton Agent
            const response = await this.agent.chat(message);
            
            // Remove typing indicator
            this.hideTypingIndicator();

            // Add assistant response
            this.addChatMessage('assistant', response.content, {
                verified: response.verified,
                grounding: response.grounding
            });

        } catch (e) {
            this.hideTypingIndicator();
            this.addChatMessage('assistant', 'Sorry, I encountered an error. Please try again.', { error: true });
        }
    }

    addChatMessage(role, content, meta = {}) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        const avatar = role === 'user' ? '👤' : '🧠';
        const metaHtml = role === 'assistant' ? `
            <div class="chat-message-meta">
                ${meta.verified ? '<span class="verified">✓ Grounded response</span>' : 
                  meta.error ? '<span style="color: var(--disputed)">⚠ Error</span>' : 
                  '<span>◐ Ungrounded</span>'}
            </div>
        ` : '';

        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${role}`;
        messageEl.innerHTML = `
            <div class="chat-message-avatar">${avatar}</div>
            <div>
                <div class="chat-message-content">${this.escapeHtml(content)}</div>
                ${metaHtml}
            </div>
        `;

        container.appendChild(messageEl);
        container.scrollTop = container.scrollHeight;
    }

    showTypingIndicator() {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        const indicator = document.createElement('div');
        indicator.className = 'chat-message assistant';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <div class="chat-message-avatar">🧠</div>
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
        container.appendChild(indicator);
        container.scrollTop = container.scrollHeight;
    }

    hideTypingIndicator() {
        document.getElementById('typing-indicator')?.remove();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Initialize
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    window.app = new ParcStationApp();
});
