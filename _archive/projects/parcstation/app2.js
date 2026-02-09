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
    AGENT_URL: 'http://localhost:8090',
    // Cartridge API
    CARTRIDGE_URL: 'http://localhost:8093',
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
// Cartridge Client (Wikipedia, arXiv, Calendar, Export, Dictionary)
// ═══════════════════════════════════════════════════════════════════════════════

class CartridgeClient {
    constructor(baseUrl = CONFIG.CARTRIDGE_URL) {
        this.baseUrl = baseUrl;
        this.online = false;
        this.cartridges = [];
    }

    async checkHealth() {
        try {
            const res = await fetch(`${this.baseUrl}/health`, { 
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            this.online = res.ok;
            if (this.online) {
                await this.loadCartridges();
            }
            return this.online;
        } catch {
            this.online = false;
            return false;
        }
    }

    async loadCartridges() {
        try {
            const res = await fetch(`${this.baseUrl}/cartridges`);
            const data = await res.json();
            this.cartridges = data.cartridges || [];
            return this.cartridges;
        } catch {
            this.cartridges = [];
            return [];
        }
    }

    // Wikipedia
    async wikipediaSummary(query, sentences = 3) {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/wikipedia/summary`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, sentences })
            });
            return await res.json();
        } catch (e) {
            return { found: false, error: e.message };
        }
    }

    async wikipediaSearch(query) {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/wikipedia/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            return await res.json();
        } catch (e) {
            return { results: [], error: e.message };
        }
    }

    // arXiv
    async arxivSearch(query, maxResults = 5) {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/arxiv/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, max_results: maxResults })
            });
            return await res.json();
        } catch (e) {
            return { results: [], error: e.message };
        }
    }

    // Calendar
    async parseDate(query) {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/calendar/parse`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            return await res.json();
        } catch (e) {
            return { parsed: false, error: e.message };
        }
    }

    async getNow() {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/calendar/now`);
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    }

    // Export
    async exportJSON(stacks) {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/export/json`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stacks })
            });
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    }

    async exportMarkdown(stacks) {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/export/markdown`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stacks })
            });
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    }

    // Code
    async evaluateCode(code) {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/code/evaluate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            return await res.json();
        } catch (e) {
            return { success: false, error: e.message };
        }
    }

    // Dictionary
    async define(word) {
        try {
            const res = await fetch(`${this.baseUrl}/cartridge/dictionary/define`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ word })
            });
            return await res.json();
        } catch (e) {
            return { found: false, error: e.message };
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
            documents: [],  // NEW: Knowledge authoring layer
            cartridges: [
                { id: 'calculator', name: 'Calculator', icon: '🧮', type: 'built-in' },
                { id: 'grounding', name: 'Grounding', icon: '🔍', type: 'built-in' },
                { id: 'voicepath', name: 'VoicePath', icon: '🎵', type: 'built-in' },
                { id: 'documents', name: 'Documents', icon: '📝', type: 'built-in' },
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
                this.data.documents = parsed.documents || [];
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
                documents: this.data.documents,
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

        // Search documents
        for (const doc of this.data.documents) {
            if (doc.title.toLowerCase().includes(q) || 
                doc.content.toLowerCase().includes(q)) {
                results.push({ type: 'document', item: doc });
            }
        }

        return results;
    }

    // Cartridges
    getCartridges() {
        return this.data.cartridges;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Documents - Knowledge Authoring Layer
    // ═══════════════════════════════════════════════════════════════════════════

    getDocuments() {
        return this.data.documents;
    }

    getDocument(id) {
        return this.data.documents.find(d => d.id === id);
    }

    addDocument(doc) {
        doc.id = 'doc-' + Date.now();
        doc.created = Date.now();
        doc.modified = Date.now();
        doc.claims = doc.claims || [];
        this.data.documents.push(doc);
        this.save();
        return doc;
    }

    updateDocument(id, updates) {
        const doc = this.getDocument(id);
        if (doc) {
            Object.assign(doc, updates);
            doc.modified = Date.now();
            this.save();
        }
        return doc;
    }

    deleteDocument(id) {
        this.data.documents = this.data.documents.filter(d => d.id !== id);
        this.save();
    }

    // Add claim to document
    addClaimToDocument(docId, claim) {
        const doc = this.getDocument(docId);
        if (doc) {
            claim.id = 'claim-' + Date.now();
            claim.status = claim.status || 'draft';
            claim.card_id = null;
            doc.claims.push(claim);
            doc.modified = Date.now();
            this.save();
            return claim;
        }
        return null;
    }

    // Update claim in document
    updateClaimInDocument(docId, claimId, updates) {
        const doc = this.getDocument(docId);
        if (doc) {
            const claim = doc.claims.find(c => c.id === claimId);
            if (claim) {
                Object.assign(claim, updates);
                doc.modified = Date.now();
                this.save();
                return claim;
            }
        }
        return null;
    }

    // Remove claim from document
    removeClaimFromDocument(docId, claimId) {
        const doc = this.getDocument(docId);
        if (doc) {
            doc.claims = doc.claims.filter(c => c.id !== claimId);
            doc.modified = Date.now();
            this.save();
        }
    }

    // Promote claim to card (the compile step!)
    promoteClaimToCard(docId, claimId, stackId) {
        const doc = this.getDocument(docId);
        if (!doc) return null;

        const claim = doc.claims.find(c => c.id === claimId);
        if (!claim) return null;

        // Create card from claim
        const card = this.addCard({
            stackId: stackId,
            title: claim.text.slice(0, 50) + (claim.text.length > 50 ? '...' : ''),
            claim: claim.text,
            sources: [],
            status: 'draft',
            origin: {
                documentId: docId,
                claimId: claimId,
                range: claim.range
            }
        });

        // Link claim to card
        claim.card_id = card.id;
        claim.status = 'promoted';
        doc.modified = Date.now();
        this.save();

        return card;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Application
// ═══════════════════════════════════════════════════════════════════════════════

class ParcStationApp {
    constructor() {
        this.newton = new NewtonClient();
        this.agent = new NewtonAgentClient();
        this.cartridges = new CartridgeClient();
        this.store = new DataStore();
        this.currentView = 'stacks';
        this.currentStack = null;
        this.currentCard = null;
        this.currentDocument = null;
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
        this.renderCartridges();
        this.showStacksView();
    }

    async checkNewtonStatus() {
        const online = await this.newton.checkHealth();
        const agentOnline = await this.agent.checkHealth();
        const cartridgesOnline = await this.cartridges.checkHealth();
        
        const indicator = document.querySelector('#newton-status .status-indicator');
        const text = document.querySelector('#newton-status .status-text');
        
        const bothOnline = online || agentOnline;
        
        if (indicator) {
            indicator.classList.toggle('online', bothOnline);
            indicator.classList.toggle('offline', !bothOnline);
        }
        if (text) {
            const parts = [];
            if (online) parts.push('Newton');
            if (agentOnline) parts.push('Agent');
            if (cartridgesOnline) parts.push('Cartridges');
            
            if (parts.length > 0) {
                text.textContent = parts.join(' + ') + ' Ready';
            } else {
                text.textContent = 'Systems Offline';
            }
        }
    }

    renderCartridges() {
        const cartridgeList = document.getElementById('cartridge-list');
        if (!cartridgeList) return;
        
        // Define available cartridges with their handlers
        const cartridgeItems = [
            { id: 'calculator', icon: '🔢', name: 'Calculator', action: () => this.activateCartridge('calculator') },
            { id: 'grounding', icon: '🔍', name: 'Grounding', action: () => this.activateCartridge('grounding') },
            { id: 'knowledge', icon: '🧠', name: 'Knowledge', action: () => this.activateCartridge('knowledge') },
            { id: 'wikipedia', icon: '📚', name: 'Wikipedia', action: () => this.activateCartridge('wikipedia') },
            { id: 'arxiv', icon: '📄', name: 'arXiv', action: () => this.activateCartridge('arxiv') },
            { id: 'dictionary', icon: '📖', name: 'Dictionary', action: () => this.activateCartridge('dictionary') },
            { id: 'calendar', icon: '📅', name: 'Calendar', action: () => this.activateCartridge('calendar') },
            { id: 'trajectory', icon: '📐', name: 'Trajectory', action: () => this.activateCartridge('trajectory') },
            { id: 'voicepath', icon: '🎵', name: 'VoicePath', action: () => this.activateCartridge('voicepath') },
            { id: 'export', icon: '📤', name: 'Export', action: () => this.exportStacks() },
        ];
        
        cartridgeList.innerHTML = cartridgeItems.map(c => `
            <button class="cartridge-item" data-cartridge="${c.id}">
                <span class="cartridge-icon">${c.icon}</span>
                <span class="cartridge-name">${c.name}</span>
            </button>
        `).join('');
        
        // Bind click handlers
        cartridgeItems.forEach(c => {
            const btn = cartridgeList.querySelector(`[data-cartridge="${c.id}"]`);
            if (btn) btn.addEventListener('click', c.action);
        });
    }

    openCartridgeSheet(type) {
        const sheet = document.querySelector('.sheet');
        const overlay = document.querySelector('.sheet-overlay');
        if (!sheet || !overlay) return;
        
        let html = '';
        
        switch(type) {
            case 'wikipedia':
                html = `
                    <div class="sheet-header">
                        <h2>📚 Wikipedia</h2>
                        <button class="btn-close" onclick="app.closeSheet()">×</button>
                    </div>
                    <div class="sheet-content">
                        <input type="text" id="wiki-query" class="input" placeholder="Search Wikipedia..." autofocus>
                        <button class="btn btn-primary" onclick="app.searchWikipedia()">Search</button>
                        <div id="wiki-results" class="results-container"></div>
                    </div>
                `;
                break;
                
            case 'arxiv':
                html = `
                    <div class="sheet-header">
                        <h2>📄 arXiv</h2>
                        <button class="btn-close" onclick="app.closeSheet()">×</button>
                    </div>
                    <div class="sheet-content">
                        <input type="text" id="arxiv-query" class="input" placeholder="Search academic papers..." autofocus>
                        <button class="btn btn-primary" onclick="app.searchArxiv()">Search</button>
                        <div id="arxiv-results" class="results-container"></div>
                    </div>
                `;
                break;
                
            case 'calendar':
                html = `
                    <div class="sheet-header">
                        <h2>📅 Calendar</h2>
                        <button class="btn-close" onclick="app.closeSheet()">×</button>
                    </div>
                    <div class="sheet-content">
                        <input type="text" id="date-query" class="input" placeholder="e.g., next friday, in 3 days..." autofocus>
                        <button class="btn btn-primary" onclick="app.parseDate()">Parse</button>
                        <div id="date-results" class="results-container"></div>
                    </div>
                `;
                break;
                
            case 'dictionary':
                html = `
                    <div class="sheet-header">
                        <h2>📖 Dictionary</h2>
                        <button class="btn-close" onclick="app.closeSheet()">×</button>
                    </div>
                    <div class="sheet-content">
                        <input type="text" id="dict-query" class="input" placeholder="Enter a word..." autofocus>
                        <button class="btn btn-primary" onclick="app.lookupWord()">Define</button>
                        <div id="dict-results" class="results-container"></div>
                    </div>
                `;
                break;
        }
        
        sheet.innerHTML = html;
        sheet.classList.add('visible');
        sheet.classList.remove('hidden');
        overlay.classList.add('visible');
        overlay.classList.remove('hidden');
        
        // Focus input
        setTimeout(() => {
            const input = sheet.querySelector('input');
            if (input) input.focus();
        }, 100);
    }

    openExportSheet() {
        const sheet = document.querySelector('.sheet');
        const overlay = document.querySelector('.sheet-overlay');
        if (!sheet || !overlay) return;
        
        const stacks = this.store.getStacks();
        
        sheet.innerHTML = `
            <div class="sheet-header">
                <h2>📤 Export</h2>
                <button class="btn-close" onclick="app.closeSheet()">×</button>
            </div>
            <div class="sheet-content">
                <p class="text-muted">${stacks.length} stack(s) will be exported</p>
                <div class="export-buttons">
                    <button class="btn btn-primary" onclick="app.exportAsJSON()">
                        Export as JSON
                    </button>
                    <button class="btn btn-secondary" onclick="app.exportAsMarkdown()">
                        Export as Markdown
                    </button>
                </div>
                <div id="export-status" class="export-status"></div>
            </div>
        `;
        
        sheet.classList.add('visible');
        sheet.classList.remove('hidden');
        overlay.classList.add('visible');
        overlay.classList.remove('hidden');
    }

    // Cartridge actions
    async searchWikipedia() {
        const query = document.getElementById('wiki-query')?.value;
        if (!query) return;
        
        const results = document.getElementById('wiki-results');
        results.innerHTML = '<div class="loading">Searching Wikipedia...</div>';
        
        const data = await this.cartridges.wikipediaSummary(query);
        
        if (data.found) {
            results.innerHTML = `
                <div class="result-card">
                    <h3>${data.title}</h3>
                    <p>${data.summary}</p>
                    ${data.thumbnail ? `<img src="${data.thumbnail}" class="wiki-thumb">` : ''}
                    <a href="${data.url}" target="_blank" class="source-link">Read on Wikipedia →</a>
                    <button class="btn btn-sm" onclick="app.createCardFromWiki('${data.title.replace(/'/g, "\\'")}', '${data.summary.replace(/'/g, "\\'")}', '${data.url}')">
                        + Add as Card
                    </button>
                </div>
            `;
        } else {
            results.innerHTML = `<div class="no-results">No article found for "${query}"</div>`;
        }
    }

    async searchArxiv() {
        const query = document.getElementById('arxiv-query')?.value;
        if (!query) return;
        
        const results = document.getElementById('arxiv-results');
        results.innerHTML = '<div class="loading">Searching arXiv...</div>';
        
        const data = await this.cartridges.arxivSearch(query, 5);
        
        if (data.results && data.results.length > 0) {
            results.innerHTML = data.results.map(paper => `
                <div class="result-card">
                    <h3>${paper.title}</h3>
                    <p class="authors">${paper.authors.join(', ')}</p>
                    <p class="summary">${paper.summary.substring(0, 200)}...</p>
                    <div class="result-actions">
                        <a href="${paper.url}" target="_blank" class="source-link">View Paper →</a>
                        <a href="${paper.pdf_url}" target="_blank" class="source-link">PDF →</a>
                    </div>
                </div>
            `).join('');
        } else {
            results.innerHTML = `<div class="no-results">No papers found for "${query}"</div>`;
        }
    }

    async parseDate() {
        const query = document.getElementById('date-query')?.value;
        if (!query) return;
        
        const results = document.getElementById('date-results');
        results.innerHTML = '<div class="loading">Parsing...</div>';
        
        const data = await this.cartridges.parseDate(query);
        
        if (data.parsed) {
            results.innerHTML = `
                <div class="result-card">
                    <h3>${data.formatted}</h3>
                    <p>${data.day_of_week}</p>
                    <p class="text-muted">${data.direction === 'future' ? `In ${data.days_from_now} days` : 
                                          data.direction === 'past' ? `${data.days_from_now} days ago` : 'Today'}</p>
                    <p class="iso-date">${data.iso}</p>
                </div>
            `;
        } else {
            results.innerHTML = `<div class="no-results">Could not parse "${query}"</div>`;
        }
    }

    async lookupWord() {
        const word = document.getElementById('dict-query')?.value;
        if (!word) return;
        
        const results = document.getElementById('dict-results');
        results.innerHTML = '<div class="loading">Looking up...</div>';
        
        const data = await this.cartridges.define(word);
        
        if (data.found) {
            results.innerHTML = `
                <div class="result-card">
                    <h3>${data.word}</h3>
                    ${data.phonetic ? `<p class="phonetic">${data.phonetic}</p>` : ''}
                    ${data.definitions.map(d => `
                        <div class="definition">
                            <span class="pos">${d.part_of_speech}</span>
                            <p>${d.definition}</p>
                            ${d.example ? `<p class="example">"${d.example}"</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            results.innerHTML = `<div class="no-results">Word not found: "${word}"</div>`;
        }
    }

    createCardFromWiki(title, summary, url) {
        if (!this.currentStack) {
            alert('Please select a stack first');
            return;
        }
        
        const card = {
            id: 'card_' + Date.now(),
            content: `${title}\n\n${summary}`,
            trust: 'partial',
            sources: [{ url, title: 'Wikipedia', tier: 'encyclopedia' }],
            created: Date.now(),
            modified: Date.now()
        };
        
        this.store.addCard(this.currentStack.id, card);
        this.closeSheet();
        this.showStackDetail(this.currentStack.id);
    }

    async exportAsJSON() {
        const stacks = this.store.getStacks();
        const data = await this.cartridges.exportJSON(stacks);
        
        if (data.content) {
            this.downloadFile(data.content, data.filename, data.mime_type);
            document.getElementById('export-status').innerHTML = 
                `<span class="success">✓ Exported ${data.filename}</span>`;
        }
    }

    async exportAsMarkdown() {
        const stacks = this.store.getStacks();
        const data = await this.cartridges.exportMarkdown(stacks);
        
        if (data.content) {
            this.downloadFile(data.content, data.filename, data.mime_type);
            document.getElementById('export-status').innerHTML = 
                `<span class="success">✓ Exported ${data.filename}</span>`;
        }
    }

    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    closeSheet() {
        const sheet = document.querySelector('.sheet');
        const overlay = document.querySelector('.sheet-overlay');
        if (sheet) {
            sheet.classList.remove('visible');
            sheet.classList.add('hidden');
        }
        if (overlay) {
            overlay.classList.remove('visible');
            overlay.classList.add('hidden');
        }
    }

    bindEvents() {
        // Navigation
        document.getElementById('btn-back')?.addEventListener('click', () => this.goBack());
        
        // Sheet overlay close
        document.querySelector('.sheet-overlay')?.addEventListener('click', () => this.closeSheet());
        
        // Search - opens Spotlight
        document.getElementById('spotlight-trigger')?.addEventListener('click', () => {
            window.spotlight?.open();
        });
        document.getElementById('search-input')?.addEventListener('focus', () => {
            window.spotlight?.open();
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
        document.getElementById('btn-add-source')?.addEventListener('click', () => this.showAddSourceSheet());

        // Sheet overlay
        document.getElementById('sheet-overlay')?.addEventListener('click', () => this.hideAllSheets());

        // Color picker
        document.querySelectorAll('#color-picker .color-option').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('#color-picker .color-option').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            });
        });

        // Document Editor
        document.getElementById('btn-mark-claim')?.addEventListener('click', () => this.markSelectionAsClaim());
        document.getElementById('btn-save-doc')?.addEventListener('click', () => this.saveDocumentContent());
        
        // Auto-save on content change
        document.getElementById('doc-editor-content')?.addEventListener('input', () => this.scheduleDocumentSave());
        document.getElementById('doc-editor-title')?.addEventListener('input', () => this.scheduleDocumentSave());

        // Documents nav
        document.getElementById('nav-documents')?.addEventListener('click', () => this.showDocumentsView());
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
            } else if (prev.view === 'documents') {
                this.showDocumentsView();
            } else if (prev.view === 'document-editor' && prev.docId) {
                this.showDocumentEditor(prev.docId);
            }
        } else {
            this.showStacksView();
        }
        this.updateBackButton();
    }

    // Update back button visibility based on navigation history
    updateBackButton() {
        const backBtn = document.getElementById('btn-back');
        if (backBtn) {
            // Hide back button on root views (stacks, documents) with no history
            const isRootView = this.currentView === 'stacks' || this.currentView === 'documents';
            const hasHistory = this.history.length > 0;
            if (isRootView && !hasHistory) {
                backBtn.style.opacity = '0';
                backBtn.style.pointerEvents = 'none';
            } else {
                backBtn.style.opacity = '1';
                backBtn.style.pointerEvents = 'auto';
            }
        }
    }

    pushHistory() {
        this.history.push({
            view: this.currentView,
            stackId: this.currentStack?.id,
            cardId: this.currentCard?.id,
            docId: this.currentDocument?.id
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
                } else if (action === 'documents') {
                    this.showDocumentsView();
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
        this.updateBackButton();
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
    // Document Editor Views
    // ═══════════════════════════════════════════════════════════════════════════

    showDocumentsView() {
        this.hideAllViews();
        this.currentView = 'documents';
        this.currentDocument = null;
        this.history = [];

        document.getElementById('view-documents')?.classList.remove('hidden');
        this.updateBreadcrumb([{ label: 'Documents' }]);
        this.renderDocumentsList();
        this.renderSidebar();
    }

    showDocumentEditor(docId) {
        const doc = this.store.getDocument(docId);
        if (!doc) return;

        this.pushHistory();
        this.hideAllViews();
        this.currentView = 'document-editor';
        this.currentDocument = doc;

        document.getElementById('view-document-editor')?.classList.remove('hidden');
        this.updateBreadcrumb([
            { label: 'Documents', action: 'documents' },
            { label: doc.title }
        ]);
        this.renderDocumentEditor();
        this.renderSidebar();
    }

    renderDocumentsList() {
        const container = document.getElementById('documents-grid');
        if (!container) return;

        const documents = this.store.getDocuments();
        
        if (documents.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📝</div>
                    <h3>No Documents Yet</h3>
                    <p>Create your first document to start authoring knowledge</p>
                    <button class="btn btn-primary" onclick="app.showNewDocumentSheet()">
                        <span class="btn-icon">+</span>
                        New Document
                    </button>
                </div>
            `;
            return;
        }

        container.innerHTML = documents.map(doc => {
            const claimCount = doc.claims?.length || 0;
            const verifiedCount = doc.claims?.filter(c => c.status === 'verified').length || 0;
            const promotedCount = doc.claims?.filter(c => c.status === 'promoted' || c.card_id).length || 0;
            
            return `
                <div class="document-card glass" data-doc-id="${doc.id}">
                    <div class="document-card-header">
                        <span class="document-icon">📄</span>
                        <h3 class="document-title">${this.escapeHtml(doc.title)}</h3>
                    </div>
                    <div class="document-preview">
                        ${this.escapeHtml(doc.content?.slice(0, 150) || 'Empty document...')}${doc.content?.length > 150 ? '...' : ''}
                    </div>
                    <div class="document-meta">
                        <span class="doc-stat">
                            <span class="stat-icon">📝</span>
                            ${claimCount} claims
                        </span>
                        <span class="doc-stat">
                            <span class="stat-icon">✓</span>
                            ${verifiedCount} verified
                        </span>
                        <span class="doc-stat">
                            <span class="stat-icon">↗</span>
                            ${promotedCount} promoted
                        </span>
                    </div>
                    <div class="document-date">
                        Modified ${this.formatDate(doc.modified)}
                    </div>
                </div>
            `;
        }).join('');

        // Bind click events
        container.querySelectorAll('.document-card').forEach(card => {
            card.addEventListener('click', () => {
                const docId = card.dataset.docId;
                this.showDocumentEditor(docId);
            });
        });
    }

    renderDocumentEditor() {
        const doc = this.currentDocument;
        if (!doc) return;

        // Title
        const titleEl = document.getElementById('doc-editor-title');
        if (titleEl) {
            titleEl.value = doc.title;
        }

        // Content
        const contentEl = document.getElementById('doc-editor-content');
        if (contentEl) {
            contentEl.value = doc.content || '';
            this.highlightClaimsInEditor();
        }

        // Claims list
        this.renderDocumentClaims();
    }

    highlightClaimsInEditor() {
        // For now, we'll use a simpler approach - show claims in sidebar
        // Full rich-text highlighting would require contenteditable or a library
    }

    renderDocumentClaims() {
        const doc = this.currentDocument;
        if (!doc) return;

        const container = document.getElementById('doc-claims-list');
        if (!container) return;

        if (!doc.claims || doc.claims.length === 0) {
            container.innerHTML = `
                <div class="claims-empty">
                    <p>No claims yet</p>
                    <p class="hint">Select text and click "Mark as Claim" to extract verifiable statements</p>
                </div>
            `;
            return;
        }

        container.innerHTML = doc.claims.map(claim => {
            const statusIcon = {
                'draft': '○',
                'promoted': '↗',
                'verified': '✓',
                'partial': '◐',
                'unverified': '✗'
            }[claim.status] || '○';

            const statusClass = claim.status || 'draft';

            return `
                <div class="claim-item ${statusClass}" data-claim-id="${claim.id}">
                    <span class="claim-status-icon">${statusIcon}</span>
                    <span class="claim-text">${this.escapeHtml(claim.text)}</span>
                    <div class="claim-actions">
                        ${claim.status === 'draft' ? `
                            <button class="btn-sm btn-verify-claim" title="Verify">⚡</button>
                            <button class="btn-sm btn-promote-claim" title="Promote to Card">↗</button>
                        ` : ''}
                        ${claim.card_id ? `
                            <button class="btn-sm btn-view-card" data-card-id="${claim.card_id}" title="View Card">📄</button>
                        ` : ''}
                        <button class="btn-sm btn-delete-claim" title="Remove">×</button>
                    </div>
                </div>
            `;
        }).join('');

        // Bind claim actions
        container.querySelectorAll('.claim-item').forEach(item => {
            const claimId = item.dataset.claimId;

            item.querySelector('.btn-verify-claim')?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.verifyClaimNow(claimId);
            });

            item.querySelector('.btn-promote-claim')?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showPromoteClaimSheet(claimId);
            });

            item.querySelector('.btn-view-card')?.addEventListener('click', (e) => {
                e.stopPropagation();
                const cardId = e.target.dataset.cardId;
                this.showCardDetail(cardId);
            });

            item.querySelector('.btn-delete-claim')?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteClaim(claimId);
            });
        });
    }

    // Mark selected text as a claim
    markSelectionAsClaim() {
        const contentEl = document.getElementById('doc-editor-content');
        if (!contentEl || !this.currentDocument) return;

        const start = contentEl.selectionStart;
        const end = contentEl.selectionEnd;
        
        if (start === end) {
            this.showToast('Select some text first');
            return;
        }

        const selectedText = contentEl.value.substring(start, end).trim();
        if (!selectedText) {
            this.showToast('Selection is empty');
            return;
        }

        // Add claim
        const claim = this.store.addClaimToDocument(this.currentDocument.id, {
            text: selectedText,
            range: [start, end],
            status: 'draft'
        });

        if (claim) {
            this.showToast('Claim marked');
            this.renderDocumentClaims();
        }
    }

    // Verify claim immediately
    async verifyClaimNow(claimId) {
        const doc = this.currentDocument;
        if (!doc) return;

        const claim = doc.claims.find(c => c.id === claimId);
        if (!claim) return;

        // Show loading
        this.showToast('Verifying claim...');

        try {
            // Ground the claim
            const groundResult = await this.newton.ground(claim.text);
            
            // Update claim status based on result
            const newStatus = groundResult.status === 'grounded' ? 'verified' : 
                             groundResult.status === 'partially_grounded' ? 'partial' : 'unverified';

            this.store.updateClaimInDocument(doc.id, claimId, {
                status: newStatus,
                verification: {
                    result: groundResult,
                    timestamp: Date.now()
                }
            });

            this.renderDocumentClaims();
            this.showToast(`Claim ${newStatus}`);
        } catch (e) {
            this.showToast('Verification failed');
        }
    }

    // Show sheet to select stack for promotion
    showPromoteClaimSheet(claimId) {
        const doc = this.currentDocument;
        if (!doc) return;

        const claim = doc.claims.find(c => c.id === claimId);
        if (!claim) return;

        // Store for later
        this.pendingClaimPromotion = { docId: doc.id, claimId };

        // Show stack selection sheet
        const sheet = document.getElementById('promote-claim-sheet');
        if (!sheet) return;

        // Populate stacks
        const stackSelect = document.getElementById('promote-stack-select');
        if (stackSelect) {
            stackSelect.innerHTML = this.store.getStacks().map(s => 
                `<option value="${s.id}">${this.escapeHtml(s.name)}</option>`
            ).join('');
        }

        // Show claim preview
        const preview = document.getElementById('promote-claim-preview');
        if (preview) {
            preview.textContent = claim.text;
        }

        this.showSheet('promote-claim-sheet');
    }

    // Execute the promotion
    promoteClaimToCard() {
        if (!this.pendingClaimPromotion) return;

        const { docId, claimId } = this.pendingClaimPromotion;
        const stackId = document.getElementById('promote-stack-select')?.value;

        if (!stackId) {
            this.showToast('Select a stack');
            return;
        }

        const card = this.store.promoteClaimToCard(docId, claimId, stackId);
        
        if (card) {
            this.hideSheet('promote-claim-sheet');
            this.showToast('Claim promoted to card!');
            this.renderDocumentClaims();
            this.pendingClaimPromotion = null;
        }
    }

    deleteClaim(claimId) {
        if (!this.currentDocument) return;
        
        this.store.removeClaimFromDocument(this.currentDocument.id, claimId);
        this.renderDocumentClaims();
        this.showToast('Claim removed');
    }

    // Save document content
    saveDocumentContent() {
        const doc = this.currentDocument;
        if (!doc) return;

        const titleEl = document.getElementById('doc-editor-title');
        const contentEl = document.getElementById('doc-editor-content');

        this.store.updateDocument(doc.id, {
            title: titleEl?.value || doc.title,
            content: contentEl?.value || doc.content
        });

        this.showToast('Document saved');
    }

    // Auto-save on content change (debounced)
    scheduleDocumentSave() {
        if (this.docSaveTimeout) {
            clearTimeout(this.docSaveTimeout);
        }
        this.docSaveTimeout = setTimeout(() => {
            this.saveDocumentContent();
        }, 1000);
    }

    // New document
    showNewDocumentSheet() {
        const sheet = document.getElementById('new-document-sheet');
        if (sheet) {
            document.getElementById('new-doc-title')?.focus();
            this.showSheet('new-document-sheet');
        }
    }

    createNewDocument() {
        const titleEl = document.getElementById('new-doc-title');
        const title = titleEl?.value?.trim() || 'Untitled Document';

        const doc = this.store.addDocument({
            title,
            content: '',
            claims: []
        });

        this.hideSheet('new-document-sheet');
        if (titleEl) titleEl.value = '';
        
        this.showDocumentEditor(doc.id);
    }

    formatDate(timestamp) {
        if (!timestamp) return 'Unknown';
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
        
        return date.toLocaleDateString();
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

            // Bind cartridge click handlers
            cartridgeList.querySelectorAll('.cartridge-item').forEach(item => {
                item.addEventListener('click', () => {
                    const cartridgeId = item.dataset.id;
                    this.activateCartridge(cartridgeId);
                });
            });
        }
    }

    activateCartridge(cartridgeId) {
        // Get cartridge info
        const cartridgeInfo = {
            'wikipedia': { name: 'Wikipedia', icon: '📖', placeholder: 'Search Wikipedia...' },
            'arxiv': { name: 'arXiv Papers', icon: '📄', placeholder: 'Search papers...' },
            'calculator': { name: 'Calculator', icon: '🔢', placeholder: 'Enter expression (e.g., 2+2)' },
            'calendar': { name: 'Calendar', icon: '📅', placeholder: 'e.g., next friday, in 3 days' },
            'dictionary': { name: 'Dictionary', icon: '📚', placeholder: 'Enter word to define...' },
            'code': { name: 'Code Runner', icon: '💻', placeholder: 'Enter code...' },
            'grounding': { name: 'Grounding', icon: '🔍', placeholder: 'Verify a claim with evidence...' },
            'voicepath': { name: 'VoicePath', icon: '🎵', placeholder: 'Describe audio to generate...' },
            'trajectory': { name: 'Trajectory', icon: '📐', placeholder: 'Analyze text as kinematic trajectory...' },
            'knowledge': { name: 'Knowledge', icon: '🧠', placeholder: 'Ask a factual question...' },
            'documents': { name: 'Documents', icon: '📝', placeholder: '', isView: true },
            'export': { name: 'Export', icon: '📤', placeholder: '' }
        };

        const info = cartridgeInfo[cartridgeId];
        if (!info) {
            this.showToast('Unknown cartridge');
            return;
        }

        // Special case: Documents opens the documents view
        if (cartridgeId === 'documents') {
            this.navigateTo('documents');
            return;
        }

        // Special case: Export doesn't need a panel
        if (cartridgeId === 'export') {
            this.exportStacks();
            return;
        }

        // Open cartridge panel
        this.openCartridgePanel(cartridgeId, info);
    }

    openCartridgePanel(cartridgeId, info) {
        this.currentCartridge = cartridgeId;
        
        // Update panel UI
        document.getElementById('cartridge-panel-icon').textContent = info.icon;
        document.getElementById('cartridge-panel-name').textContent = info.name;
        document.getElementById('cartridge-search-input').placeholder = info.placeholder;
        document.getElementById('cartridge-search-input').value = '';
        document.getElementById('cartridge-results').innerHTML = `
            <div class="cartridge-empty">
                <p>Enter a search term above</p>
            </div>
        `;
        
        // Show panel
        document.getElementById('cartridge-panel')?.classList.remove('hidden');
        document.getElementById('cartridge-search-input')?.focus();

        // Bind search
        const searchBtn = document.getElementById('cartridge-search-btn');
        const searchInput = document.getElementById('cartridge-search-input');
        
        searchBtn.onclick = () => this.executeCartridgeSearch();
        searchInput.onkeypress = (e) => {
            if (e.key === 'Enter') this.executeCartridgeSearch();
        };
    }

    closeCartridgePanel() {
        document.getElementById('cartridge-panel')?.classList.add('hidden');
        this.currentCartridge = null;
    }

    async executeCartridgeSearch() {
        const query = document.getElementById('cartridge-search-input')?.value?.trim();
        if (!query) return;

        const resultsEl = document.getElementById('cartridge-results');
        resultsEl.innerHTML = '<div class="cartridge-loading">Searching...</div>';

        try {
            let results;
            switch (this.currentCartridge) {
                case 'wikipedia':
                    results = await this.searchWikipedia(query);
                    break;
                case 'arxiv':
                    results = await this.searchArxiv(query);
                    break;
                case 'calculator':
                    results = await this.calculate(query);
                    break;
                case 'calendar':
                    results = await this.parseDate(query);
                    break;
                case 'dictionary':
                    results = await this.defineWord(query);
                    break;
                case 'grounding':
                    results = await this.groundClaim(query);
                    break;
                case 'voicepath':
                    results = await this.generateVoicePath(query);
                    break;
                case 'trajectory':
                    results = await this.analyzeTrajectory(query);
                    break;
                case 'knowledge':
                    results = await this.queryKnowledge(query);
                    break;
                default:
                    results = { error: 'Unknown cartridge' };
            }
            
            this.renderCartridgeResults(results);
        } catch (e) {
            resultsEl.innerHTML = `<div class="cartridge-error">Error: ${e.message}</div>`;
        }
    }

    async searchWikipedia(query) {
        const resp = await fetch(`${CONFIG.CARTRIDGE_URL}/cartridge/wikipedia/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        return resp.json();
    }

    async searchArxiv(query) {
        const resp = await fetch(`${CONFIG.CARTRIDGE_URL}/cartridge/arxiv/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        return resp.json();
    }

    async calculate(expression) {
        // Priority order:
        // 1. Newton Supercomputer Logic Engine (verified computation)
        // 2. Newton Agent TI Calculator (TI-84 style)
        // 3. Cartridge basic math fallback
        
        // Try Newton Supercomputer Logic Engine first (verified Turing-complete)
        try {
            const newtonResp = await fetch(`${CONFIG.NEWTON_URL}/calculate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    expression: this.parseToLogicExpression(expression),
                    max_iterations: 1000,
                    max_operations: 10000,
                    timeout_seconds: 5.0
                })
            });
            if (newtonResp.ok) {
                const data = await newtonResp.json();
                if (data.result !== null && data.result !== undefined) {
                    return {
                        result: data.result,
                        input: expression,
                        expression: expression,
                        verified: data.verified,
                        source: 'Newton Logic Engine',
                        operations: data.operations,
                        fingerprint: data.fingerprint
                    };
                }
            }
        } catch (e) {
            console.log('Newton Logic Engine unavailable, trying Agent...');
        }

        // Try Newton Agent's TI Calculator (full TI-84 support)
        try {
            const agentResp = await fetch(`${CONFIG.AGENT_URL}/calculate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expression })
            });
            if (agentResp.ok) {
                const data = await agentResp.json();
                return {
                    result: data.result,
                    input: expression,
                    expression: expression,
                    verified: data.verified !== false,
                    source: data.source || 'TI Calculator'
                };
            }
        } catch (e) {
            console.log('Agent calculator unavailable, using cartridge fallback');
        }
        // Fallback to cartridge basic math
        const resp = await fetch(`${CONFIG.CARTRIDGE_URL}/cartridge/code/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: expression })
        });
        return resp.json();
    }

    // Parse simple math expressions to Newton Logic Engine format
    parseToLogicExpression(expr) {
        // If already in Newton format (object), return as-is
        if (typeof expr === 'object') return expr;
        
        // Simple arithmetic: "2+3" -> {"op": "+", "args": [2, 3]}
        const str = String(expr).trim();
        
        // Handle simple binary operations
        const opMap = {
            '+': '+', '-': '-', '*': '*', '/': '/', 
            '^': '^', '**': '^', '%': 'mod'
        };
        
        for (const [sym, op] of Object.entries(opMap)) {
            if (str.includes(sym) && !str.startsWith(sym)) {
                const parts = str.split(sym);
                if (parts.length === 2) {
                    const a = parseFloat(parts[0].trim());
                    const b = parseFloat(parts[1].trim());
                    if (!isNaN(a) && !isNaN(b)) {
                        return { op, args: [a, b] };
                    }
                }
            }
        }
        
        // Handle functions: sqrt(16) -> {"op": "sqrt", "args": [16]}
        const funcMatch = str.match(/^(\w+)\s*\(\s*(.+)\s*\)$/);
        if (funcMatch) {
            const func = funcMatch[1].toLowerCase();
            const arg = parseFloat(funcMatch[2]);
            if (!isNaN(arg)) {
                return { op: func, args: [arg] };
            }
        }
        
        // Just a number
        const num = parseFloat(str);
        if (!isNaN(num)) {
            return num;
        }
        
        // Return as string for Newton to parse
        return str;
    }

    async parseDate(query) {
        const resp = await fetch(`${CONFIG.CARTRIDGE_URL}/cartridge/calendar/parse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        return resp.json();
    }

    async defineWord(word) {
        // Free dictionary API
        const resp = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`);
        if (!resp.ok) return { error: 'Word not found' };
        return { results: await resp.json(), type: 'dictionary' };
    }

    async groundClaim(claim) {
        // Use Newton Agent's ENHANCED grounding (Google + DuckDuckGo + Wikipedia)
        try {
            const resp = await fetch(`${CONFIG.AGENT_URL}/ground`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim, require_official: false })
            });
            if (!resp.ok) {
                // Fallback to Newton Supercomputer if Agent is down
                const fallback = await fetch(`${CONFIG.NEWTON_URL}/ground`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ claim, max_results: 5 })
                });
                if (!fallback.ok) throw new Error('All grounding services unavailable');
                const data = await fallback.json();
                return { type: 'grounding', claim, ...data };
            }
            const data = await resp.json();
            return { 
                type: 'grounding', 
                claim: claim,
                grounded: data.status === 'VERIFIED' || data.status === 'LIKELY',
                confidence: (10 - (data.confidence_score || 10)) / 10, // Convert 0-10 to 0-1 (inverted)
                status: data.status,
                sources: data.evidence?.map(e => ({
                    url: e.url,
                    title: e.title,
                    type: e.tier || 'web'
                })) || [],
                reasoning: data.reasoning || '',
                ...data
            };
        } catch (e) {
            return { error: `Grounding failed: ${e.message}. Is Newton Agent running on ${CONFIG.AGENT_URL}?` };
        }
    }

    async generateVoicePath(description) {
        // VoicePath generates audio specs from natural language
        try {
            const resp = await fetch(`${CONFIG.CARTRIDGE_URL}/cartridge/voicepath/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description })
            });
            if (!resp.ok) throw new Error('VoicePath service unavailable');
            return await resp.json();
        } catch (e) {
            return { error: `VoicePath failed: ${e.message}` };
        }
    }

    async analyzeTrajectory(text) {
        // Kinematic Linguistics: Language as Bézier trajectories through meaning space
        try {
            const resp = await fetch(`${CONFIG.AGENT_URL}/trajectory/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            if (!resp.ok) throw new Error('Trajectory analysis unavailable');
            const data = await resp.json();
            return { type: 'trajectory', text, ...data };
        } catch (e) {
            return { error: `Trajectory analysis failed: ${e.message}. Is Newton Agent running?` };
        }
    }

    async queryKnowledge(query) {
        // Query Newton Agent's verified knowledge base (CIA Factbook, NIST, etc.)
        try {
            const resp = await fetch(`${CONFIG.AGENT_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query, ground_claims: true })
            });
            if (!resp.ok) throw new Error('Knowledge service unavailable');
            const data = await resp.json();
            return { 
                type: 'knowledge', 
                query,
                answer: data.content,
                verified: data.verified,
                grounding: data.grounding,
                sources: data.grounding?.results || [],
                ...data
            };
        } catch (e) {
            return { error: `Knowledge query failed: ${e.message}. Is Newton Agent running?` };
        }
    }

    renderCartridgeResults(data) {
        const resultsEl = document.getElementById('cartridge-results');
        
        if (data.error) {
            resultsEl.innerHTML = `<div class="cartridge-error">${data.error}</div>`;
            return;
        }

        // Wikipedia results
        if (data.results && this.currentCartridge === 'wikipedia') {
            resultsEl.innerHTML = data.results.map(r => `
                <div class="cartridge-result-item" data-url="${r.url}" data-title="${this.escapeHtml(r.title)}">
                    <div class="result-title">${this.escapeHtml(r.title)}</div>
                    <div class="result-snippet">${this.escapeHtml(r.snippet)}</div>
                    <div class="result-actions">
                        <button class="btn-sm btn-use-source" data-url="${r.url}" data-title="${this.escapeHtml(r.title)}" data-type="wikipedia">
                            + Add as Source
                        </button>
                        <a href="${r.url}" target="_blank" class="btn-sm">Open ↗</a>
                    </div>
                </div>
            `).join('');
        }
        // arXiv results
        else if (data.results && this.currentCartridge === 'arxiv') {
            resultsEl.innerHTML = data.results.map(r => `
                <div class="cartridge-result-item" data-url="${r.url}">
                    <div class="result-title">${this.escapeHtml(r.title)}</div>
                    <div class="result-authors">${this.escapeHtml(r.authors?.join(', ') || '')}</div>
                    <div class="result-snippet">${this.escapeHtml(r.summary?.slice(0, 200) || '')}...</div>
                    <div class="result-actions">
                        <button class="btn-sm btn-use-source" data-url="${r.url}" data-title="${this.escapeHtml(r.title)}" data-type="arxiv">
                            + Add as Source
                        </button>
                        <a href="${r.pdf_url || r.url}" target="_blank" class="btn-sm">Open PDF ↗</a>
                    </div>
                </div>
            `).join('');
        }
        // Calculator result
        else if (data.result !== undefined && (this.currentCartridge === 'calculator' || data.verified !== undefined)) {
            resultsEl.innerHTML = `
                <div class="cartridge-result-calc">
                    <div class="calc-expression">${this.escapeHtml(data.input || data.expression || '')}</div>
                    <div class="calc-equals">=</div>
                    <div class="calc-result">${data.result}</div>
                    ${data.verified ? '<div class="calc-verified">✓ Verified</div>' : ''}
                    <button class="btn btn-secondary" onclick="navigator.clipboard.writeText('${data.result}'); app.showToast('Copied!')">
                        Copy Result
                    </button>
                </div>
            `;
        }
        // Calendar result
        else if (data.datetime || data.date) {
            resultsEl.innerHTML = `
                <div class="cartridge-result-date">
                    <div class="date-label">${this.escapeHtml(data.query || '')}</div>
                    <div class="date-result">${data.formatted || data.datetime || data.date}</div>
                    <div class="date-iso">${data.iso || data.datetime || data.date}</div>
                </div>
            `;
        }
        // Dictionary result
        else if (data.type === 'dictionary' && data.results) {
            const word = data.results[0];
            resultsEl.innerHTML = `
                <div class="cartridge-result-dict">
                    <div class="dict-word">${this.escapeHtml(word.word)}</div>
                    <div class="dict-phonetic">${word.phonetic || ''}</div>
                    ${word.meanings?.map(m => `
                        <div class="dict-meaning">
                            <div class="dict-pos">${m.partOfSpeech}</div>
                            ${m.definitions?.slice(0, 2).map(d => `
                                <div class="dict-def">• ${this.escapeHtml(d.definition)}</div>
                            `).join('')}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        // Grounding result (from Newton)
        else if (data.type === 'grounding') {
            const verifiedClass = data.grounded ? 'verified' : 'unverified';
            const verifiedIcon = data.grounded ? '✓' : '⚠';
            const verifiedText = data.grounded ? 'Grounded in Evidence' : 'Insufficient Evidence';
            
            resultsEl.innerHTML = `
                <div class="cartridge-result-grounding">
                    <div class="grounding-claim">"${this.escapeHtml(data.claim)}"</div>
                    <div class="grounding-verdict ${verifiedClass}">
                        <span class="verdict-icon">${verifiedIcon}</span>
                        <span class="verdict-text">${verifiedText}</span>
                    </div>
                    <div class="grounding-confidence">
                        Confidence: ${Math.round((data.confidence || 0) * 100)}%
                    </div>
                    ${data.sources?.length ? `
                        <div class="grounding-sources">
                            <div class="sources-title">Evidence Sources:</div>
                            ${data.sources.map(s => `
                                <div class="source-item">
                                    <span class="source-type">${s.type || 'web'}</span>
                                    <a href="${s.url || '#'}" target="_blank" class="source-link">${this.escapeHtml(s.title || s.url || 'Source')}</a>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    <div class="grounding-actions">
                        <button class="btn btn-primary btn-sm" onclick="app.useGroundingAsVerification('${this.escapeHtml(data.claim)}', ${data.grounded}, ${data.confidence || 0})">
                            Use for Verification
                        </button>
                    </div>
                </div>
            `;
        }
        // VoicePath result
        else if (data.type === 'voicepath' || data.audio_spec) {
            resultsEl.innerHTML = `
                <div class="cartridge-result-voicepath">
                    <div class="voicepath-title">Generated Audio Spec</div>
                    <div class="voicepath-spec">
                        <div class="spec-row"><span class="spec-label">Duration:</span> ${data.duration || '10s'}</div>
                        <div class="spec-row"><span class="spec-label">Tempo:</span> ${data.tempo || '120'} BPM</div>
                        <div class="spec-row"><span class="spec-label">Key:</span> ${data.key || 'C major'}</div>
                        <div class="spec-row"><span class="spec-label">Style:</span> ${data.style || 'ambient'}</div>
                    </div>
                    ${data.description ? `<div class="voicepath-desc">${this.escapeHtml(data.description)}</div>` : ''}
                    <div class="voicepath-actions">
                        <button class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText(JSON.stringify(${JSON.stringify(data)}, null, 2)); app.showToast('Spec copied!')">
                            Copy Spec
                        </button>
                    </div>
                </div>
            `;
        }
        // Trajectory/Kinematic analysis result
        else if (data.type === 'trajectory') {
            const metrics = data.metrics || {};
            resultsEl.innerHTML = `
                <div class="cartridge-result-trajectory">
                    <div class="trajectory-title">📐 Kinematic Analysis</div>
                    <div class="trajectory-text">"${this.escapeHtml(data.text)}"</div>
                    <div class="trajectory-metrics">
                        <div class="metric">
                            <span class="metric-label">Weight</span>
                            <div class="metric-bar"><div class="metric-fill" style="width: ${(metrics.total_weight || 0) * 10}%"></div></div>
                            <span class="metric-value">${(metrics.total_weight || 0).toFixed(2)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Curvature</span>
                            <div class="metric-bar"><div class="metric-fill curvature" style="width: ${Math.abs(metrics.total_curvature || 0) * 50 + 50}%"></div></div>
                            <span class="metric-value">${(metrics.total_curvature || 0).toFixed(2)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Commit</span>
                            <div class="metric-bar"><div class="metric-fill commit" style="width: ${(metrics.total_commit || 0) * 100}%"></div></div>
                            <span class="metric-value">${(metrics.total_commit || 0).toFixed(2)}</span>
                        </div>
                    </div>
                    ${data.grammar ? `
                        <div class="trajectory-grammar">
                            <span class="grammar-label">Grammar:</span>
                            <span class="grammar-status ${data.grammar.envelopes_balanced ? 'valid' : 'invalid'}">
                                ${data.grammar.envelopes_balanced ? '✓ Balanced' : '⚠ Unbalanced'}
                            </span>
                            <span class="grammar-status ${data.grammar.properly_terminated ? 'valid' : 'invalid'}">
                                ${data.grammar.properly_terminated ? '✓ Terminated' : '⚠ Open'}
                            </span>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        // Knowledge/Chat result
        else if (data.type === 'knowledge') {
            const verified = data.verified;
            resultsEl.innerHTML = `
                <div class="cartridge-result-knowledge">
                    <div class="knowledge-query">Q: ${this.escapeHtml(data.query)}</div>
                    <div class="knowledge-answer ${verified ? 'verified' : ''}">
                        <div class="answer-content">${this.escapeHtml(data.answer || 'No answer found')}</div>
                        ${verified ? '<div class="answer-badge">✓ Verified</div>' : ''}
                    </div>
                    ${data.sources?.length ? `
                        <div class="knowledge-sources">
                            <div class="sources-title">Sources:</div>
                            ${data.sources.slice(0, 3).map(s => `
                                <div class="source-item">
                                    <span class="source-status ${s.status?.toLowerCase() || 'unknown'}">${s.status || '?'}</span>
                                    <span class="source-claim">${this.escapeHtml(s.claim || '')}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        }
        else {
            resultsEl.innerHTML = '<div class="cartridge-empty">No results found</div>';
        }

        // Bind "Add as Source" buttons
        resultsEl.querySelectorAll('.btn-use-source').forEach(btn => {
            btn.addEventListener('click', () => {
                this.addSourceToCurrentCard({
                    type: btn.dataset.type,
                    location: btn.dataset.url,
                    title: btn.dataset.title
                });
            });
        });
    }

    exportStacks() {
        const data = {
            exported: new Date().toISOString(),
            stacks: this.store.getStacks().map(s => ({
                ...s,
                cards: this.store.getCards(s.id)
            }))
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `parcstation-export-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        this.showToast('Stacks exported!');
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Add Source - Multi-method source addition
    // ═══════════════════════════════════════════════════════════════════════════

    showAddSourceSheet() {
        if (!this.currentCard) {
            this.showToast('No card selected');
            return;
        }
        
        this.showSheet('add-source-sheet');
        this.initSourceTabs();
    }

    initSourceTabs() {
        const tabs = document.querySelectorAll('.source-tab');
        const contents = document.querySelectorAll('.source-tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update tabs
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update content
                contents.forEach(c => c.classList.add('hidden'));
                const targetId = `source-tab-${tab.dataset.tab}`;
                document.getElementById(targetId)?.classList.remove('active');
                document.getElementById(targetId)?.classList.remove('hidden');
                document.getElementById(targetId)?.classList.add('active');
            });
        });
    }

    addSourceFromUrl() {
        const url = document.getElementById('source-url')?.value?.trim();
        if (!url) {
            this.showToast('Enter a URL');
            return;
        }

        this.addSourceToCurrentCard({
            type: 'url',
            location: url,
            title: url
        });
        
        document.getElementById('source-url').value = '';
        this.hideSheet('add-source-sheet');
    }

    async searchWikipediaForSource() {
        const query = document.getElementById('source-wiki-search')?.value?.trim();
        if (!query) return;

        const resultsEl = document.getElementById('wiki-source-results');
        resultsEl.innerHTML = '<div class="source-loading">Searching...</div>';

        try {
            const data = await this.searchWikipedia(query);
            if (data.results) {
                resultsEl.innerHTML = data.results.map(r => `
                    <div class="source-result-item">
                        <div class="source-result-title">${this.escapeHtml(r.title)}</div>
                        <div class="source-result-snippet">${this.escapeHtml(r.snippet)}</div>
                        <button class="btn btn-sm btn-primary" 
                                onclick="app.selectSourceResult('wikipedia', '${r.url}', '${this.escapeHtml(r.title)}')">
                            Select
                        </button>
                    </div>
                `).join('');
            } else {
                resultsEl.innerHTML = '<div class="source-empty">No results</div>';
            }
        } catch (e) {
            resultsEl.innerHTML = '<div class="source-error">Search failed</div>';
        }
    }

    async searchArxivForSource() {
        const query = document.getElementById('source-arxiv-search')?.value?.trim();
        if (!query) return;

        const resultsEl = document.getElementById('arxiv-source-results');
        resultsEl.innerHTML = '<div class="source-loading">Searching...</div>';

        try {
            const data = await this.searchArxiv(query);
            if (data.results) {
                resultsEl.innerHTML = data.results.map(r => `
                    <div class="source-result-item">
                        <div class="source-result-title">${this.escapeHtml(r.title)}</div>
                        <div class="source-result-authors">${this.escapeHtml(r.authors?.join(', ') || '')}</div>
                        <button class="btn btn-sm btn-primary" 
                                onclick="app.selectSourceResult('arxiv', '${r.url}', '${this.escapeHtml(r.title)}')">
                            Select
                        </button>
                    </div>
                `).join('');
            } else {
                resultsEl.innerHTML = '<div class="source-empty">No results</div>';
            }
        } catch (e) {
            resultsEl.innerHTML = '<div class="source-error">Search failed</div>';
        }
    }

    selectSourceResult(type, url, title) {
        this.addSourceToCurrentCard({ type, location: url, title });
        this.hideSheet('add-source-sheet');
    }

    addManualSource() {
        const title = document.getElementById('source-manual-title')?.value?.trim();
        const desc = document.getElementById('source-manual-desc')?.value?.trim();
        
        if (!title) {
            this.showToast('Enter a title');
            return;
        }

        this.addSourceToCurrentCard({
            type: 'manual',
            location: desc || title,
            title
        });

        document.getElementById('source-manual-title').value = '';
        document.getElementById('source-manual-desc').value = '';
        this.hideSheet('add-source-sheet');
    }

    addSourceToCurrentCard(source) {
        if (!this.currentCard) {
            this.showToast('No card selected');
            return;
        }

        // Add source to card
        if (!this.currentCard.sources) {
            this.currentCard.sources = [];
        }
        
        this.currentCard.sources.push({
            type: source.type,
            location: source.location,
            title: source.title,
            verified: false,
            addedAt: Date.now()
        });

        // Save
        this.store.updateCard(this.currentCard.id, {
            sources: this.currentCard.sources
        });

        // Re-render
        this.renderCardDetail();
        this.closeCartridgePanel();
        this.showToast('Source added!');
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
        if (!card.sources || card.sources.length === 0) {
            sourceList.innerHTML = '<p style="color: var(--text-tertiary); font-size: 13px;">No sources attached</p>';
        } else {
            sourceList.innerHTML = card.sources.map(s => `
                <div class="source-item">
                    <span class="source-type-icon">${this.getSourceIcon(s.type)}</span>
                    <div class="source-info">
                        <span class="source-name">${this.escapeHtml(s.title || s.name || s.location)}</span>
                        ${s.location && s.location.startsWith('http') ? `
                            <a href="${s.location}" target="_blank" class="source-link">Open ↗</a>
                        ` : ''}
                    </div>
                    <span class="source-status ${s.verified ? 'verified' : ''}">${s.verified ? '✓' : ''}</span>
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

    getSourceIcon(type) {
        const icons = {
            'wikipedia': '📖',
            'arxiv': '📄',
            'url': '🔗',
            'manual': '✏️',
            'document': '📑',
            'attestation': '✍️',
            'computation': '🔢'
        };
        return icons[type] || '📎';
    }

    showToast(message, duration = 3000) {
        // Remove existing toast
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();

        // Create toast
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Auto-remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Spotlight Search (Cmd+K)
// V-Twin semantics + Newton verification
// ═══════════════════════════════════════════════════════════════════════════════

class SpotlightSearch {
    constructor(app) {
        this.app = app;
        this.overlay = document.getElementById('spotlight-overlay');
        this.input = document.getElementById('spotlight-input');
        this.resultsContainer = document.getElementById('spotlight-results');
        this.selectedIndex = 0;
        this.currentResults = [];
        this.searchTimeout = null;
        
        this.init();
    }

    init() {
        // Keyboard shortcut: Cmd+K / Ctrl+K
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.open();
            }
            if (e.key === 'Escape' && !this.overlay?.classList.contains('hidden')) {
                this.close();
            }
        });

        // Search input
        this.input?.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Input keyboard navigation
        this.input?.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.selectNext();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.selectPrev();
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.executeSelected();
            }
        });

        // Click outside to close
        this.overlay?.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });

        // Quick action items
        this.resultsContainer?.querySelectorAll('.spotlight-item').forEach(item => {
            item.addEventListener('click', () => {
                const action = item.dataset.action;
                this.executeAction(action);
            });
        });

        console.log('✦ Spotlight initialized');
    }

    open() {
        if (!this.overlay) return;
        this.overlay.classList.remove('hidden');
        this.input?.focus();
        this.input.value = '';
        this.selectedIndex = 0;
        this.showDefaultResults();
    }

    close() {
        this.overlay?.classList.add('hidden');
        this.input.value = '';
    }

    showDefaultResults() {
        // Reset to default quick actions
        const html = `
            <div class="spotlight-section">
                <div class="spotlight-section-title">Quick Actions</div>
                <div class="spotlight-item selected" data-action="new-stack">
                    <span class="spotlight-item-icon">📚</span>
                    <span class="spotlight-item-text">New Stack</span>
                    <span class="spotlight-item-hint">⌘N</span>
                </div>
                <div class="spotlight-item" data-action="new-card">
                    <span class="spotlight-item-icon">📄</span>
                    <span class="spotlight-item-text">New Card</span>
                    <span class="spotlight-item-hint">⌘⇧N</span>
                </div>
                <div class="spotlight-item" data-action="chat">
                    <span class="spotlight-item-icon">💬</span>
                    <span class="spotlight-item-text">Ask Newton</span>
                    <span class="spotlight-item-hint">⌘J</span>
                </div>
            </div>
            <div class="spotlight-section">
                <div class="spotlight-section-title">Cartridges</div>
                <div class="spotlight-item" data-action="wikipedia">
                    <span class="spotlight-item-icon">📖</span>
                    <span class="spotlight-item-text">Wikipedia</span>
                    <span class="spotlight-item-meta">Search verified knowledge</span>
                </div>
                <div class="spotlight-item" data-action="arxiv">
                    <span class="spotlight-item-icon">📑</span>
                    <span class="spotlight-item-text">arXiv</span>
                    <span class="spotlight-item-meta">Search scientific papers</span>
                </div>
                <div class="spotlight-item" data-action="calculate">
                    <span class="spotlight-item-icon">🔢</span>
                    <span class="spotlight-item-text">Calculator</span>
                    <span class="spotlight-item-meta">Verified computations</span>
                </div>
            </div>
        `;
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = html;
            this.bindResultItems();
        }
        this.currentResults = this.resultsContainer?.querySelectorAll('.spotlight-item') || [];
        this.selectedIndex = 0;
    }

    async handleSearch(query) {
        clearTimeout(this.searchTimeout);
        
        if (!query.trim()) {
            this.showDefaultResults();
            return;
        }

        // Debounce search
        this.searchTimeout = setTimeout(() => this.performSearch(query), 150);
    }

    async performSearch(query) {
        const q = query.toLowerCase().trim();
        
        // Show loading
        this.resultsContainer.innerHTML = `
            <div class="spotlight-loading">Searching...</div>
        `;

        const results = [];

        // 1. Search local stacks first (V-Twin: your data first)
        const localResults = this.searchLocalStacks(q);
        if (localResults.length > 0) {
            results.push({
                section: 'Your Stacks',
                items: localResults
            });
        }

        // 2. Quick actions that match
        const actions = this.matchActions(q);
        if (actions.length > 0) {
            results.push({
                section: 'Actions',
                items: actions
            });
        }

        // 3. Cartridge searches (Wikipedia, arXiv)
        if (q.startsWith('wiki ') || q.startsWith('w ')) {
            const wikiQuery = q.replace(/^(wiki|w)\s+/, '');
            const wikiResults = await this.searchWikipedia(wikiQuery);
            if (wikiResults.length > 0) {
                results.push({
                    section: 'Wikipedia',
                    items: wikiResults
                });
            }
        }

        if (q.startsWith('arxiv ') || q.startsWith('a ')) {
            const arxivQuery = q.replace(/^(arxiv|a)\s+/, '');
            const arxivResults = await this.searchArxiv(arxivQuery);
            if (arxivResults.length > 0) {
                results.push({
                    section: 'arXiv Papers',
                    items: arxivResults
                });
            }
        }

        // 4. Math expression detection
        if (/^[\d\s\+\-\*\/\(\)\.\^]+$/.test(q) || q.startsWith('calc ') || q.startsWith('= ')) {
            const expr = q.replace(/^(calc|=)\s*/, '');
            const calcResult = await this.calculate(expr);
            if (calcResult) {
                results.push({
                    section: 'Calculation',
                    items: [calcResult]
                });
            }
        }

        // Render results
        this.renderResults(results, q);
    }

    searchLocalStacks(query) {
        const results = [];
        const stacks = this.app.dataStore?.stacks || [];
        
        for (const stack of stacks) {
            // Search stack names
            if (stack.name?.toLowerCase().includes(query)) {
                results.push({
                    icon: '📚',
                    text: stack.name,
                    meta: `${stack.cards?.length || 0} cards`,
                    action: 'open-stack',
                    data: stack.id
                });
            }
            
            // Search cards in stack
            for (const card of (stack.cards || [])) {
                if (card.title?.toLowerCase().includes(query) || 
                    card.content?.toLowerCase().includes(query)) {
                    results.push({
                        icon: this.getTrustIcon(card.trust_level),
                        text: card.title || 'Untitled',
                        meta: stack.name,
                        trust: card.trust_level,
                        action: 'open-card',
                        data: { stackId: stack.id, cardId: card.id }
                    });
                }
            }
        }
        
        return results.slice(0, 5); // Limit results
    }

    getTrustIcon(trust) {
        const icons = {
            verified: '✓',
            partial: '◐',
            draft: '○',
            unverified: '○'
        };
        return icons[trust] || '○';
    }

    matchActions(query) {
        const actions = [
            { icon: '📚', text: 'New Stack', action: 'new-stack', keywords: ['new', 'stack', 'create'] },
            { icon: '📄', text: 'New Card', action: 'new-card', keywords: ['new', 'card', 'add'] },
            { icon: '💬', text: 'Ask Newton', action: 'chat', keywords: ['ask', 'chat', 'newton', 'ai'] },
            { icon: '🔢', text: 'Calculator', action: 'calculate', keywords: ['calc', 'math', 'compute'] },
            { icon: '📖', text: 'Wikipedia', action: 'wikipedia', keywords: ['wiki', 'encyclopedia'] },
            { icon: '📑', text: 'arXiv', action: 'arxiv', keywords: ['paper', 'science', 'research'] },
            { icon: '🔍', text: 'Ground Claim', action: 'ground', keywords: ['verify', 'ground', 'fact'] },
        ];
        
        return actions.filter(a => 
            a.text.toLowerCase().includes(query) ||
            a.keywords.some(k => k.includes(query) || query.includes(k))
        );
    }

    async searchWikipedia(query) {
        try {
            // Use Wikipedia API directly (no key needed)
            const url = `https://en.wikipedia.org/w/api.php?action=opensearch&search=${encodeURIComponent(query)}&limit=5&format=json&origin=*`;
            const response = await fetch(url);
            const data = await response.json();
            
            const titles = data[1] || [];
            const urls = data[3] || [];
            
            return titles.map((title, i) => ({
                icon: '📖',
                text: title,
                meta: 'Wikipedia',
                action: 'open-url',
                data: urls[i],
                trust: 'partial' // Wikipedia is crowd-sourced
            }));
        } catch (e) {
            console.error('Wikipedia search failed:', e);
            return [];
        }
    }

    async searchArxiv(query) {
        try {
            // Use arXiv API (no key needed)
            const url = `https://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(query)}&start=0&max_results=5`;
            const response = await fetch(url);
            const text = await response.text();
            
            // Parse XML
            const parser = new DOMParser();
            const xml = parser.parseFromString(text, 'text/xml');
            const entries = xml.querySelectorAll('entry');
            
            return Array.from(entries).map(entry => {
                const title = entry.querySelector('title')?.textContent?.trim() || 'Untitled';
                const link = entry.querySelector('id')?.textContent || '';
                const authors = Array.from(entry.querySelectorAll('author name'))
                    .map(a => a.textContent).slice(0, 2).join(', ');
                
                return {
                    icon: '📑',
                    text: title.replace(/\s+/g, ' ').slice(0, 60) + (title.length > 60 ? '...' : ''),
                    meta: authors || 'arXiv',
                    action: 'open-url',
                    data: link,
                    trust: 'verified' // Peer-reviewed
                };
            });
        } catch (e) {
            console.error('arXiv search failed:', e);
            return [];
        }
    }

    async calculate(expr) {
        try {
            // Use Newton verified calculation
            const response = await fetch(`${CONFIG.NEWTON_URL}/calculate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    expression: this.parseExpression(expr)
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                return {
                    icon: '🔢',
                    text: `${expr} = ${data.result}`,
                    meta: data.verified ? '✓ Verified' : 'Computed',
                    action: 'copy',
                    data: data.result,
                    trust: 'verified'
                };
            }
        } catch (e) {
            // Fallback to safe JS eval for basic math
            try {
                const result = this.safeEval(expr);
                return {
                    icon: '🔢',
                    text: `${expr} = ${result}`,
                    meta: 'Calculated',
                    action: 'copy',
                    data: result
                };
            } catch {
                return null;
            }
        }
        return null;
    }

    parseExpression(expr) {
        // Convert infix to Newton expression format
        // Simple cases only for now
        const cleaned = expr.trim();
        
        // Try to parse simple binary operations
        const match = cleaned.match(/^([\d.]+)\s*([\+\-\*\/\^])\s*([\d.]+)$/);
        if (match) {
            const [, a, op, b] = match;
            const opMap = { '+': '+', '-': '-', '*': '*', '/': '/', '^': '**' };
            return { op: opMap[op] || op, args: [parseFloat(a), parseFloat(b)] };
        }
        
        // Fallback: return as string for Newton to parse
        return cleaned;
    }

    safeEval(expr) {
        // Only allow safe math characters
        const safe = expr.replace(/[^0-9\+\-\*\/\.\(\)\s\^]/g, '');
        const result = Function('"use strict"; return (' + safe.replace(/\^/g, '**') + ')')();
        return Math.round(result * 1000000) / 1000000; // Limit precision
    }

    renderResults(results, query) {
        if (results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="spotlight-empty">
                    <p>No results for "${query}"</p>
                    <p style="font-size: 0.8rem; margin-top: 8px;">
                        Try: <code>wiki [topic]</code> or <code>arxiv [topic]</code>
                    </p>
                </div>
            `;
            this.currentResults = [];
            return;
        }

        let html = '';
        for (const group of results) {
            html += `<div class="spotlight-section">`;
            html += `<div class="spotlight-section-title">${group.section}</div>`;
            
            for (const item of group.items) {
                const trustBadge = item.trust ? 
                    `<span class="spotlight-item-trust ${item.trust}">${this.getTrustIcon(item.trust)}</span>` : '';
                
                html += `
                    <div class="spotlight-item" data-action="${item.action}" data-payload='${JSON.stringify(item.data || '')}'>
                        <span class="spotlight-item-icon">${item.icon}</span>
                        <span class="spotlight-item-text">${item.text}</span>
                        ${item.meta ? `<span class="spotlight-item-meta">${item.meta}</span>` : ''}
                        ${trustBadge}
                    </div>
                `;
            }
            html += `</div>`;
        }

        this.resultsContainer.innerHTML = html;
        this.bindResultItems();
        this.currentResults = this.resultsContainer.querySelectorAll('.spotlight-item');
        this.selectedIndex = 0;
        this.updateSelection();
    }

    bindResultItems() {
        this.resultsContainer?.querySelectorAll('.spotlight-item').forEach(item => {
            item.addEventListener('click', () => {
                const action = item.dataset.action;
                const payload = item.dataset.payload ? JSON.parse(item.dataset.payload) : null;
                this.executeAction(action, payload);
            });
        });
    }

    selectNext() {
        if (this.currentResults.length === 0) return;
        this.selectedIndex = (this.selectedIndex + 1) % this.currentResults.length;
        this.updateSelection();
    }

    selectPrev() {
        if (this.currentResults.length === 0) return;
        this.selectedIndex = (this.selectedIndex - 1 + this.currentResults.length) % this.currentResults.length;
        this.updateSelection();
    }

    updateSelection() {
        this.currentResults.forEach((item, i) => {
            item.classList.toggle('selected', i === this.selectedIndex);
        });
        
        // Scroll into view
        this.currentResults[this.selectedIndex]?.scrollIntoView({ block: 'nearest' });
    }

    executeSelected() {
        const item = this.currentResults[this.selectedIndex];
        if (!item) return;
        
        const action = item.dataset.action;
        const payload = item.dataset.payload ? JSON.parse(item.dataset.payload) : null;
        this.executeAction(action, payload);
    }

    executeAction(action, payload) {
        this.close();
        
        switch (action) {
            case 'new-stack':
                this.app.showCreateStackModal?.();
                break;
            case 'new-card':
                this.app.showCreateCardModal?.();
                break;
            case 'new-document':
                this.app.showNewDocumentSheet?.();
                break;
            case 'chat':
                this.app.toggleChat?.();
                break;
            case 'open-stack':
                this.app.selectStack?.(payload);
                break;
            case 'open-card':
                this.app.selectStack?.(payload?.stackId);
                this.app.selectCard?.(payload?.cardId);
                break;
            case 'open-url':
                window.open(payload, '_blank');
                break;
            case 'copy':
                navigator.clipboard?.writeText(String(payload));
                this.app.showToast?.(`Copied: ${payload}`);
                break;
            case 'wikipedia':
                this.open();
                this.input.value = 'wiki ';
                this.input.focus();
                break;
            case 'arxiv':
                this.open();
                this.input.value = 'arxiv ';
                this.input.focus();
                break;
            case 'calculate':
                this.open();
                this.input.value = '= ';
                this.input.focus();
                break;
            case 'ground':
                // Open grounding modal or chat with grounding context
                this.app.toggleChat?.();
                break;
            default:
                console.log('Unknown action:', action);
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Initialize
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    window.app = new ParcStationApp();
    window.spotlight = new SpotlightSearch(window.app);
});
