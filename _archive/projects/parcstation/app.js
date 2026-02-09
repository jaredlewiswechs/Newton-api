/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * PARCSTATION APP
 * Main Application Entry Point
 * 
 * © 2026 Jared Lewis · Ada Computing Company · Houston, Texas
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { ParcStation, Stack, Card, Cartridge, TrustLevel } from './notebook.js';

// ═══════════════════════════════════════════════════════════════════════════════
// DEMO DATA
// ═══════════════════════════════════════════════════════════════════════════════

const DEMO_NOTEBOOK = {
    stacks: [
        {
            id: 'lewis-family',
            name: 'Lewis Family',
            description: 'Genealogy and land records',
            position: { x: -20, y: 0, z: -10 },
            color: 0x4a9eff,
            cards: [
                {
                    id: 'card-1',
                    claim: 'Jasper Lewis owned 200 acres in Brazoria County in 1857',
                    sources: [{ type: 'document', location: 'Texas GLO Patent #4521', verified: true }],
                    verification: { status: 'verified', confidence: 1.0 }
                },
                {
                    id: 'card-2',
                    claim: 'The creek boundary moved 47 feet between 1857 and 1923',
                    sources: [
                        { type: 'document', location: 'GLO Survey 1857', verified: true },
                        { type: 'document', location: 'County Survey 1923', verified: true }
                    ],
                    verification: { status: 'verified', confidence: 1.0 }
                },
                {
                    id: 'card-3',
                    claim: 'Jasper Lewis was born in 1820 in Alabama',
                    sources: [],
                    verification: { status: 'draft', confidence: 0.3 }
                }
            ]
        },
        {
            id: 'dr-nath-campaign',
            name: 'Dr. Nath Campaign',
            description: 'Political strategy and voter data',
            position: { x: 15, y: 0, z: 5 },
            color: 0xa855f7,
            cards: [
                {
                    id: 'card-4',
                    claim: 'District J turnout in 2023 was 12.3%',
                    sources: [{ type: 'url', location: 'Texas SOS Official Results', verified: true }],
                    verification: { status: 'verified', confidence: 1.0 }
                },
                {
                    id: 'card-5',
                    claim: 'Target margin for victory is 2,500 votes',
                    sources: [{ type: 'computation', location: 'Newton calculation', verified: true }],
                    verification: { status: 'verified', confidence: 0.95 }
                }
            ]
        },
        {
            id: 'texas-land',
            name: 'Texas Land Claims',
            description: 'Historical land patents and surveys',
            position: { x: -5, y: 0, z: 20 },
            color: 0x22c55e,
            cards: [
                {
                    id: 'card-6',
                    claim: 'Stephen F. Austin\'s colony granted in 1823',
                    sources: [{ type: 'document', location: 'Mexican Land Grant Records', verified: true }],
                    verification: { status: 'verified', confidence: 1.0 }
                },
                {
                    id: 'card-7',
                    claim: 'Gradient boundary law applies to navigable streams',
                    sources: [{ type: 'document', location: 'Texas Water Code §11.021', verified: true }],
                    verification: { status: 'verified', confidence: 1.0 }
                },
                {
                    id: 'card-8',
                    claim: 'The Brazos River shifted course in 1913 flood',
                    sources: [],
                    verification: { status: 'draft', confidence: 0.4 }
                }
            ]
        },
        {
            id: 'damian-nil',
            name: 'Damian NIL',
            description: 'Name, Image, Likeness tracking',
            position: { x: 25, y: 0, z: -15 },
            color: 0xf59e0b,
            cards: [
                {
                    id: 'card-9',
                    claim: 'Damian\'s 40-yard dash time: 4.52 seconds',
                    sources: [{ type: 'attestation', location: 'Official combine results', verified: true }],
                    verification: { status: 'verified', confidence: 1.0 }
                },
                {
                    id: 'card-10',
                    claim: 'Social media following: 45,000 combined',
                    sources: [],
                    verification: { status: 'unverified', confidence: 0.0 }
                }
            ]
        }
    ],
    cartridges: [
        {
            id: 'cartridge-voicepath',
            type: 'voicepath',
            name: 'VoicePath Player',
            position: { x: 35, y: 0, z: 10 },
            verified: true
        },
        {
            id: 'cartridge-data',
            type: 'data',
            name: 'Campaign Analytics',
            position: { x: 30, y: 0, z: -5 },
            verified: true
        }
    ],
    quickCards: [
        {
            id: 'quick-1',
            claim: 'Need to verify: Great-grandfather\'s military service records',
            position: { x: -30, y: 0, z: 25 }
        }
    ]
};

// ═══════════════════════════════════════════════════════════════════════════════
// APPLICATION
// ═══════════════════════════════════════════════════════════════════════════════

class ParcStationApp {
    constructor() {
        this.station = null;
        this.init();
    }

    init() {
        // Initialize 3D viewport
        this.station = new ParcStation('viewport');
        
        // Load demo data
        this.station.loadNotebook(DEMO_NOTEBOOK);
        
        // Setup UI
        this.setupUI();
        this.setupEventListeners();
        this.updateStackList();
        
        console.log('parcStation initialized');
        console.log('Loaded:', DEMO_NOTEBOOK.stacks.length, 'stacks,', 
                    DEMO_NOTEBOOK.cartridges.length, 'cartridges');
    }

    setupUI() {
        // Hide detail panel initially
        document.getElementById('detail-panel').classList.remove('visible');
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('btn-home').addEventListener('click', () => {
            this.station.flyHome();
        });

        // Add Stack
        document.getElementById('btn-add-stack').addEventListener('click', () => {
            document.getElementById('modal-add-stack').showModal();
        });

        document.getElementById('cancel-add-stack').addEventListener('click', () => {
            document.getElementById('modal-add-stack').close();
        });

        document.getElementById('form-add-stack').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addNewStack();
        });

        // Add Cartridge
        document.getElementById('btn-add-cartridge').addEventListener('click', () => {
            document.getElementById('modal-add-cartridge').showModal();
        });

        document.getElementById('cancel-add-cartridge').addEventListener('click', () => {
            document.getElementById('modal-add-cartridge').close();
        });

        document.querySelectorAll('.cartridge-option').forEach(btn => {
            btn.addEventListener('click', () => {
                this.addNewCartridge(btn.dataset.type);
                document.getElementById('modal-add-cartridge').close();
            });
        });

        // Quick Card
        document.getElementById('btn-quick-card').addEventListener('click', () => {
            document.getElementById('modal-quick-card').showModal();
        });

        document.getElementById('cancel-quick-card').addEventListener('click', () => {
            document.getElementById('modal-quick-card').close();
        });

        document.getElementById('form-quick-card').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addQuickCard();
        });

        // Detail panel close
        document.getElementById('close-detail').addEventListener('click', () => {
            document.getElementById('detail-panel').classList.remove('visible');
        });

        // Search
        document.getElementById('search-btn').addEventListener('click', () => {
            this.search();
        });

        document.getElementById('search-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.search();
        });

        // Listen for parcStation events
        document.getElementById('viewport').addEventListener('parcstation:select', (e) => {
            this.showDetails(e.detail);
        });

        document.getElementById('viewport').addEventListener('parcstation:open', (e) => {
            this.openItem(e.detail);
        });
    }

    addNewStack() {
        const name = document.getElementById('stack-name').value;
        const description = document.getElementById('stack-description').value;
        const color = parseInt(document.getElementById('stack-color').value.replace('#', ''), 16);

        // Random position near center
        const angle = Math.random() * Math.PI * 2;
        const distance = 15 + Math.random() * 20;

        const stack = this.station.addStack({
            name,
            description,
            color,
            position: {
                x: Math.cos(angle) * distance,
                y: 0,
                z: Math.sin(angle) * distance
            },
            cards: []
        });

        // Reset form and close modal
        document.getElementById('form-add-stack').reset();
        document.getElementById('modal-add-stack').close();
        
        // Update sidebar
        this.updateStackList();

        // Fly to new stack
        this.station.flyToStack(stack);
    }

    addNewCartridge(type) {
        const angle = Math.random() * Math.PI * 2;
        const distance = 25 + Math.random() * 15;

        this.station.addCartridge({
            type,
            name: `${type.charAt(0).toUpperCase() + type.slice(1)} Cartridge`,
            position: {
                x: Math.cos(angle) * distance,
                y: 0,
                z: Math.sin(angle) * distance
            },
            verified: true
        });
    }

    addQuickCard() {
        const claim = document.getElementById('card-claim').value;
        const source = document.getElementById('card-source').value;

        const card = this.station.notebook.addQuickCard({
            claim,
            sources: source ? [{ type: 'document', location: source, verified: false }] : [],
            position: {
                x: -35 + Math.random() * 10,
                y: 0,
                z: 20 + Math.random() * 10
            }
        });

        // Create mesh for it
        this.station.createQuickCardMesh(card);

        // Reset form and close modal
        document.getElementById('form-quick-card').reset();
        document.getElementById('modal-quick-card').close();
    }

    showDetails(item) {
        const panel = document.getElementById('detail-panel');
        const title = document.getElementById('detail-title');
        const content = document.getElementById('detail-content');

        panel.classList.add('visible');

        if (item instanceof Stack || item.cards) {
            // Stack
            title.textContent = item.name;
            content.innerHTML = `
                <div class="detail-section">
                    <h4>Description</h4>
                    <p>${item.description || 'No description'}</p>
                </div>
                <div class="detail-section">
                    <h4>Verification</h4>
                    <div class="verification-bar">
                        <div class="verification-fill" style="width: ${item.verificationPercent}%"></div>
                    </div>
                    <p>${item.verificationPercent}% verified (${item.cards?.size || 0} cards)</p>
                </div>
                <div class="detail-section">
                    <h4>Cards</h4>
                    <ul class="card-list">
                        ${Array.from(item.cards?.values() || []).map(c => `
                            <li class="card-item ${c.verification.status}">
                                <span class="card-status">${c.verification.status === 'verified' ? '✓' : '○'}</span>
                                <span class="card-claim">${c.claim.substring(0, 50)}...</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="detail-actions">
                    <button class="btn btn-primary">Add Card</button>
                    <button class="btn btn-secondary">Edit Stack</button>
                </div>
            `;
        } else if (item.type && item.contract !== undefined) {
            // Cartridge
            title.textContent = item.name;
            content.innerHTML = `
                <div class="detail-section">
                    <h4>Type</h4>
                    <p class="cartridge-type-badge">${item.type}</p>
                </div>
                <div class="detail-section">
                    <h4>Status</h4>
                    <p>${item.verified ? '✓ Verified' : '⚠️ Unverified'}</p>
                </div>
                <div class="detail-section">
                    <h4>Contract</h4>
                    <p>Inputs: ${item.contract?.inputs?.length || 0}</p>
                    <p>Outputs: ${item.contract?.outputs?.length || 0}</p>
                    <p>Invariants: ${item.contract?.invariants?.length || 0}</p>
                </div>
                <div class="detail-actions">
                    <button class="btn btn-primary">Configure</button>
                    <button class="btn btn-secondary">View Contract</button>
                </div>
            `;
        } else {
            // Card (quick card or loose card)
            title.textContent = 'Quick Card';
            content.innerHTML = `
                <div class="detail-section">
                    <h4>Claim</h4>
                    <p>${item.claim}</p>
                </div>
                <div class="detail-section">
                    <h4>Status</h4>
                    <p class="status-draft">⚠️ Needs verification</p>
                </div>
                <div class="detail-section">
                    <h4>Sources</h4>
                    <p>${item.sources?.length || 0} attached</p>
                </div>
                <div class="detail-actions">
                    <button class="btn btn-primary">Verify with Newton</button>
                    <button class="btn btn-secondary">Move to Stack</button>
                </div>
            `;
        }
    }

    openItem(item) {
        console.log('Opening:', item);
        // Could open a full editor view here
    }

    search() {
        const query = document.getElementById('search-input').value;
        if (!query.trim()) return;

        console.log('Searching:', query);
        
        // Add to recent queries
        const recentList = document.getElementById('recent-queries');
        const li = document.createElement('li');
        li.className = 'query-item';
        li.innerHTML = `
            <span class="query-text">"${query}"</span>
            <span class="query-stack">→ Searching...</span>
        `;
        recentList.prepend(li);

        // TODO: Integrate with Newton search
        // For now, just clear the input
        document.getElementById('search-input').value = '';
    }

    updateStackList() {
        const list = document.getElementById('stack-list');
        list.innerHTML = '';

        this.station.notebook.stacks.forEach(stack => {
            const item = document.createElement('div');
            item.className = 'stack-list-item';
            item.innerHTML = `
                <div class="stack-icon" style="background-color: #${stack.color.toString(16).padStart(6, '0')}">
                    ${stack.cards.size}
                </div>
                <div class="stack-info">
                    <span class="stack-name">${stack.name}</span>
                    <span class="stack-verification">✓ ${stack.verificationPercent}%</span>
                </div>
            `;
            item.addEventListener('click', () => {
                this.station.flyToStack(stack);
            });
            list.appendChild(item);
        });
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// BOOT
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    window.app = new ParcStationApp();
});
