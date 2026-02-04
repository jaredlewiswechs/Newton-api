/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * NINA DESKTOP — JavaScript Controller
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * Unified desktop shell with:
 * - Window manager (drag, resize, focus, z-order)
 * - Command palette (⌘K / Ctrl+K)
 * - Inspector panel (live object inspection)
 * - Services menu (NeXT-style select → run service)
 * - Dock with app launchers
 *
 * All backed by the Foghorn kernel object system.
 *
 * © 2026 Jared Lewis · Ada Computing Company · Houston, Texas
 * ═══════════════════════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════════════════════
// API CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const API_BASE = 'http://localhost:8000/foghorn';

// ═══════════════════════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════════════════════

const state = {
    objects: [],
    selectedObject: null,
    windows: [],
    activeWindow: null,
    windowZIndex: 100,
    commandPaletteOpen: false,
    servicesMenuOpen: false,
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMMANDS REGISTRY
// ═══════════════════════════════════════════════════════════════════════════════

const commands = [
    { id: 'new-card', title: 'New Card', icon: '📝', shortcut: '⌘N', action: () => createNewCard() },
    { id: 'new-query', title: 'New Query', icon: '🔍', shortcut: '⌘⇧F', action: () => createNewQuery() },
    { id: 'open-workspace', title: 'Open Workspace', icon: '📁', action: () => toggleSidebar() },
    { id: 'toggle-inspector', title: 'Toggle Inspector', icon: '🔬', shortcut: '⌘I', action: () => toggleInspector() },
    { id: 'run-service', title: 'Run Service...', icon: '⚙️', shortcut: '⌘⇧S', action: () => openServicesMenu() },
    { id: 'undo', title: 'Undo', icon: '↩️', shortcut: '⌘Z', action: () => undo() },
    { id: 'redo', title: 'Redo', icon: '↪️', shortcut: '⌘⇧Z', action: () => redo() },
    { id: 'search', title: 'Search Objects', icon: '🔎', shortcut: '⌘F', action: () => focusSearch() },
    { id: 'refresh', title: 'Refresh Workspace', icon: '🔄', shortcut: '⌘R', action: () => refreshWorkspace() },
];

// ═══════════════════════════════════════════════════════════════════════════════
// SERVICES REGISTRY  
// ═══════════════════════════════════════════════════════════════════════════════

const services = [
    { id: 'compute', name: 'Compute', icon: '🧮', accepts: ['card', 'query'], produces: ['card'] },
    { id: 'verify', name: 'Verify Claim', icon: '✓', accepts: ['card'], produces: ['receipt'] },
    { id: 'extract', name: 'Extract', icon: '📄', accepts: ['file_asset'], produces: ['card'] },
    { id: 'summarize', name: 'Summarize', icon: '📋', accepts: ['card', 'result_set'], produces: ['card'] },
    { id: 'link', name: 'Create Link', icon: '🔗', accepts: ['card', 'query'], produces: ['link_curve'] },
    { id: 'export-json', name: 'Export as JSON', icon: '📤', accepts: ['card', 'query', 'result_set'], produces: [] },
];

// ═══════════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initKeyboardShortcuts();
    initMenuBar();
    initDock();
    initCommandPalette();
    initObjectList();
    initWindowManager();
    refreshWorkspace();
    
    console.log('🖥️ Nina Desktop initialized');
});

// ═══════════════════════════════════════════════════════════════════════════════
// MENU BAR — NeXTSTEP Style Dropdown Menus
// ═══════════════════════════════════════════════════════════════════════════════

function initMenuBar() {
    const menuItems = document.querySelectorAll('.menu-item[data-menu]');
    let activeMenu = null;
    
    // Toggle menu on click
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const menuId = item.getAttribute('data-menu');
            const dropdown = item.querySelector('.dropdown-menu');
            
            if (activeMenu === item) {
                // Close current menu
                closeAllMenus();
            } else {
                // Close others and open this one
                closeAllMenus();
                item.classList.add('open');
                if (dropdown) dropdown.classList.add('open');
                activeMenu = item;
            }
        });
        
        // Open on hover if a menu is already open
        item.addEventListener('mouseenter', () => {
            if (activeMenu && activeMenu !== item) {
                const dropdown = item.querySelector('.dropdown-menu');
                closeAllMenus();
                item.classList.add('open');
                if (dropdown) dropdown.classList.add('open');
                activeMenu = item;
            }
        });
    });
    
    // Handle dropdown item clicks
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            if (item.classList.contains('disabled')) return;
            
            const action = item.getAttribute('data-action');
            if (action) {
                executeMenuAction(action);
            }
            closeAllMenus();
        });
    });
    
    // Close menus when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.menu-item')) {
            closeAllMenus();
        }
    });
    
    // Close menus on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && activeMenu) {
            closeAllMenus();
        }
    });
    
    function closeAllMenus() {
        menuItems.forEach(item => {
            item.classList.remove('open');
            const dropdown = item.querySelector('.dropdown-menu');
            if (dropdown) dropdown.classList.remove('open');
        });
        activeMenu = null;
    }
}

function executeMenuAction(action) {
    console.log('Menu action:', action);
    
    switch (action) {
        case 'new-card':
            createNewCard();
            break;
        case 'new-query':
            createNewQuery();
            break;
        case 'toggle-sidebar':
            toggleSidebar();
            break;
        case 'toggle-inspector':
            toggleInspector();
            break;
        case 'undo':
            undo();
            break;
        case 'redo':
            redo();
            break;
        case 'all-services':
            openServicesMenu();
            break;
        case 'verify':
        case 'compute':
        case 'extract':
        case 'summarize':
            runService(action);
            break;
        default:
            console.log('Unhandled action:', action);
    }
}

function runService(serviceName) {
    if (!state.selectedObject) {
        console.log('No object selected for service');
        return;
    }
    console.log(`Running service ${serviceName} on`, state.selectedObject);
    // TODO: Implement service execution
}

// ═══════════════════════════════════════════════════════════════════════════════
// CLOCK
// ═══════════════════════════════════════════════════════════════════════════════

function initClock() {
    const clock = document.getElementById('clock');
    
    function updateClock() {
        const now = new Date();
        clock.textContent = now.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
    
    updateClock();
    setInterval(updateClock, 1000);
}

// ═══════════════════════════════════════════════════════════════════════════════
// KEYBOARD SHORTCUTS
// ═══════════════════════════════════════════════════════════════════════════════

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        const cmdKey = isMac ? e.metaKey : e.ctrlKey;
        
        // ⌘K / Ctrl+K - Command Palette
        if (cmdKey && e.key === 'k') {
            e.preventDefault();
            toggleCommandPalette();
            return;
        }
        
        // ⌘I / Ctrl+I - Toggle Inspector
        if (cmdKey && e.key === 'i') {
            e.preventDefault();
            toggleInspector();
            return;
        }
        
        // ⌘N / Ctrl+N - New Card
        if (cmdKey && e.key === 'n') {
            e.preventDefault();
            createNewCard();
            return;
        }
        
        // ⌘Z / Ctrl+Z - Undo
        if (cmdKey && !e.shiftKey && e.key === 'z') {
            e.preventDefault();
            undo();
            return;
        }
        
        // ⌘⇧Z / Ctrl+Shift+Z - Redo
        if (cmdKey && e.shiftKey && e.key === 'z') {
            e.preventDefault();
            redo();
            return;
        }
        
        // Escape - Close modals
        if (e.key === 'Escape') {
            closeAllModals();
            return;
        }
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMMAND PALETTE
// ═══════════════════════════════════════════════════════════════════════════════

function initCommandPalette() {
    const palette = document.getElementById('command-palette');
    const input = document.getElementById('palette-input');
    const results = document.getElementById('palette-results');
    
    let selectedIndex = 0;
    let filteredCommands = [...commands];
    
    input.addEventListener('input', () => {
        const query = input.value.toLowerCase();
        filteredCommands = commands.filter(cmd => 
            cmd.title.toLowerCase().includes(query) ||
            cmd.id.toLowerCase().includes(query)
        );
        selectedIndex = 0;
        renderPaletteResults();
    });
    
    input.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, filteredCommands.length - 1);
            renderPaletteResults();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, 0);
            renderPaletteResults();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (filteredCommands[selectedIndex]) {
                filteredCommands[selectedIndex].action();
                closeCommandPalette();
            }
        }
    });
    
    palette.addEventListener('click', (e) => {
        if (e.target === palette) {
            closeCommandPalette();
        }
    });
    
    function renderPaletteResults() {
        results.innerHTML = filteredCommands.map((cmd, i) => `
            <li class="palette-result ${i === selectedIndex ? 'selected' : ''}" data-index="${i}">
                <span class="palette-result-icon">${cmd.icon}</span>
                <div class="palette-result-info">
                    <div class="palette-result-title">${cmd.title}</div>
                </div>
                ${cmd.shortcut ? `<span class="palette-result-shortcut">${cmd.shortcut}</span>` : ''}
            </li>
        `).join('');
        
        // Click handler for results
        results.querySelectorAll('.palette-result').forEach(el => {
            el.addEventListener('click', () => {
                const index = parseInt(el.dataset.index);
                filteredCommands[index].action();
                closeCommandPalette();
            });
        });
    }
    
    // Initial render
    renderPaletteResults();
}

function toggleCommandPalette() {
    const palette = document.getElementById('command-palette');
    const input = document.getElementById('palette-input');
    
    if (palette.classList.contains('hidden')) {
        palette.classList.remove('hidden');
        input.value = '';
        input.focus();
        state.commandPaletteOpen = true;
    } else {
        closeCommandPalette();
    }
}

function closeCommandPalette() {
    const palette = document.getElementById('command-palette');
    palette.classList.add('hidden');
    state.commandPaletteOpen = false;
}

// ═══════════════════════════════════════════════════════════════════════════════
// OBJECT LIST (Sidebar)
// ═══════════════════════════════════════════════════════════════════════════════

function initObjectList() {
    const filters = document.querySelectorAll('.filter-btn');
    
    filters.forEach(btn => {
        btn.addEventListener('click', () => {
            filters.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderObjectList(btn.dataset.type);
        });
    });
}

async function refreshWorkspace() {
    try {
        const response = await fetch(`${API_BASE}/cards`);
        if (response.ok) {
            const data = await response.json();
            state.objects = data.cards || [];
        } else {
            // Fallback: demo objects
            state.objects = [
                { id: 'demo1', hash: 'abc123', type: 'card', title: 'Welcome to Nina', content: 'Your first card' },
                { id: 'demo2', hash: 'def456', type: 'card', title: 'Getting Started', content: 'Try creating a new card with ⌘N' },
                { id: 'demo3', hash: 'ghi789', type: 'query', text: 'What is the capital of France?' },
            ];
        }
    } catch (e) {
        console.log('API not available, using demo objects');
        state.objects = [
            { id: 'demo1', hash: 'abc123', type: 'card', title: 'Welcome to Nina', content: 'Your first card' },
            { id: 'demo2', hash: 'def456', type: 'card', title: 'Getting Started', content: 'Try creating a new card with ⌘N' },
            { id: 'demo3', hash: 'ghi789', type: 'query', text: 'What is the capital of France?' },
        ];
    }
    
    renderObjectList('all');
}

function renderObjectList(filter = 'all') {
    const list = document.getElementById('object-list');
    const filtered = filter === 'all' 
        ? state.objects 
        : state.objects.filter(obj => obj.type === filter);
    
    list.innerHTML = filtered.map(obj => `
        <li class="object-item ${state.selectedObject?.id === obj.id ? 'selected' : ''}" 
            data-id="${obj.id}" data-hash="${obj.hash}">
            <span class="object-icon">${getObjectIcon(obj.type)}</span>
            <div class="object-info">
                <div class="object-title">${getObjectTitle(obj)}</div>
                <div class="object-meta">${obj.type} · ${obj.id?.slice(0, 8) || '...'}</div>
            </div>
        </li>
    `).join('');
    
    // Click handlers
    list.querySelectorAll('.object-item').forEach(el => {
        el.addEventListener('click', () => {
            const obj = state.objects.find(o => o.id === el.dataset.id);
            selectObject(obj);
        });
        
        el.addEventListener('dblclick', () => {
            const obj = state.objects.find(o => o.id === el.dataset.id);
            openObjectWindow(obj);
        });
    });
}

function getObjectIcon(type) {
    const icons = {
        card: '📝',
        query: '🔍',
        result_set: '📊',
        file_asset: '📁',
        task: '✅',
        receipt: '🧾',
        link_curve: '🔗',
        rule: '📏',
        map_place: '📍',
        route: '🗺️',
        automation: '⚡',
    };
    return icons[type] || '📄';
}

function getObjectTitle(obj) {
    return obj.title || obj.text || obj.name || `${obj.object_type} ${obj.id?.slice(0, 6) || ''}`;
}

// ═══════════════════════════════════════════════════════════════════════════════
// INSPECTOR
// ═══════════════════════════════════════════════════════════════════════════════

function selectObject(obj) {
    state.selectedObject = obj;
    
    // Update list selection
    document.querySelectorAll('.object-item').forEach(el => {
        el.classList.toggle('selected', el.dataset.id === obj?.id);
    });
    
    // Update inspector
    updateInspector(obj);
}

function updateInspector(obj) {
    const content = document.getElementById('inspector-content');
    
    if (!obj) {
        content.innerHTML = `
            <div class="inspector-empty">
                <p>Select an object to inspect</p>
                <p class="hint">Click any card, query, or file in the workspace</p>
            </div>
        `;
        return;
    }
    
    content.innerHTML = `
        <div class="inspector-section">
            <div class="inspector-section-title">Identity</div>
            <div class="inspector-row">
                <span class="inspector-label">Type</span>
                <span class="inspector-value">${obj.type}</span>
            </div>
            <div class="inspector-row">
                <span class="inspector-label">ID</span>
                <span class="inspector-value">${obj.id || '—'}</span>
            </div>
            <div class="inspector-row">
                <span class="inspector-label">Hash</span>
                <span class="inspector-value">${obj.hash?.slice(0, 12) || '—'}...</span>
            </div>
        </div>
        
        <div class="inspector-section">
            <div class="inspector-section-title">Content</div>
            ${renderObjectFields(obj)}
        </div>
        
        <div class="inspector-section">
            <div class="inspector-section-title">Metadata</div>
            <div class="inspector-row">
                <span class="inspector-label">Created</span>
                <span class="inspector-value">${formatTimestamp(obj.created_at)}</span>
            </div>
            <div class="inspector-row">
                <span class="inspector-label">Verified</span>
                <span class="inspector-value">${obj.verified ? '✓ Yes' : '✗ No'}</span>
            </div>
        </div>
    `;
}

function renderObjectFields(obj) {
    const fields = [];
    
    if (obj.title) fields.push(['Title', obj.title]);
    if (obj.content) fields.push(['Content', obj.content.slice(0, 100) + (obj.content.length > 100 ? '...' : '')]);
    if (obj.text) fields.push(['Text', obj.text]);
    if (obj.tags) fields.push(['Tags', obj.tags.join(', ')]);
    if (obj.source) fields.push(['Source', obj.source]);
    
    return fields.map(([label, value]) => `
        <div class="inspector-row">
            <span class="inspector-label">${label}</span>
            <span class="inspector-value">${value}</span>
        </div>
    `).join('');
}

function formatTimestamp(ts) {
    if (!ts) return '—';
    const date = new Date(typeof ts === 'number' ? ts : parseInt(ts));
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function toggleInspector() {
    const inspector = document.getElementById('inspector');
    inspector.style.display = inspector.style.display === 'none' ? 'flex' : 'none';
}

// ═══════════════════════════════════════════════════════════════════════════════
// WINDOW MANAGER
// ═══════════════════════════════════════════════════════════════════════════════

function initWindowManager() {
    // Global mouse move/up for dragging
    document.addEventListener('mousemove', handleWindowDrag);
    document.addEventListener('mouseup', handleWindowDragEnd);
}

let dragState = null;

function handleWindowDrag(e) {
    if (!dragState) return;
    
    const { window, startX, startY, startLeft, startTop, type } = dragState;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    
    if (type === 'move') {
        window.style.left = `${startLeft + dx}px`;
        window.style.top = `${startTop + dy}px`;
    } else if (type === 'resize') {
        window.style.width = `${Math.max(300, startLeft + dx)}px`;
        window.style.height = `${Math.max(200, startTop + dy)}px`;
    }
}

function handleWindowDragEnd() {
    if (dragState) {
        document.body.classList.remove('dragging');
        dragState = null;
    }
}

function createWindow(title, content, options = {}) {
    const container = document.getElementById('windows-container');
    const id = `window-${Date.now()}`;
    
    const x = options.x ?? 100 + (state.windows.length * 30);
    const y = options.y ?? 50 + (state.windows.length * 30);
    const width = options.width ?? 500;
    const height = options.height ?? 400;
    
    const win = document.createElement('div');
    win.className = 'window';
    win.id = id;
    win.style.left = `${x}px`;
    win.style.top = `${y}px`;
    win.style.width = `${width}px`;
    win.style.height = `${height}px`;
    win.style.zIndex = ++state.windowZIndex;
    
    win.innerHTML = `
        <div class="window-titlebar">
            <div class="window-controls">
                <button class="window-btn window-btn-close" data-action="close"></button>
                <button class="window-btn window-btn-minimize" data-action="minimize"></button>
                <button class="window-btn window-btn-maximize" data-action="maximize"></button>
            </div>
            <div class="window-title">${title}</div>
            <div class="window-toolbar"></div>
        </div>
        <div class="window-content">${content}</div>
        <div class="window-resize"></div>
    `;
    
    container.appendChild(win);
    state.windows.push({ id, title });
    
    // Focus handling
    win.addEventListener('mousedown', () => focusWindow(id));
    
    // Titlebar drag
    const titlebar = win.querySelector('.window-titlebar');
    titlebar.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('window-btn')) return;
        
        document.body.classList.add('dragging');
        dragState = {
            window: win,
            startX: e.clientX,
            startY: e.clientY,
            startLeft: win.offsetLeft,
            startTop: win.offsetTop,
            type: 'move'
        };
    });
    
    // Resize handle
    const resizeHandle = win.querySelector('.window-resize');
    resizeHandle.addEventListener('mousedown', (e) => {
        e.stopPropagation();
        document.body.classList.add('dragging');
        dragState = {
            window: win,
            startX: e.clientX,
            startY: e.clientY,
            startLeft: win.offsetWidth,
            startTop: win.offsetHeight,
            type: 'resize'
        };
    });
    
    // Window controls
    win.querySelectorAll('.window-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = btn.dataset.action;
            if (action === 'close') closeWindow(id);
            else if (action === 'minimize') minimizeWindow(id);
            else if (action === 'maximize') maximizeWindow(id);
        });
    });
    
    focusWindow(id);
    return win;
}

function focusWindow(id) {
    document.querySelectorAll('.window').forEach(w => {
        w.classList.toggle('inactive', w.id !== id);
        if (w.id === id) {
            w.style.zIndex = ++state.windowZIndex;
        }
    });
    state.activeWindow = id;
}

function closeWindow(id) {
    const win = document.getElementById(id);
    if (!win) return;
    
    win.classList.add('closing');
    setTimeout(() => {
        win.remove();
        state.windows = state.windows.filter(w => w.id !== id);
    }, 150);
}

function minimizeWindow(id) {
    const win = document.getElementById(id);
    if (win) win.style.display = 'none';
}

function maximizeWindow(id) {
    const win = document.getElementById(id);
    if (!win) return;
    
    // Toggle maximize
    if (win.dataset.maximized) {
        win.style.left = win.dataset.prevLeft;
        win.style.top = win.dataset.prevTop;
        win.style.width = win.dataset.prevWidth;
        win.style.height = win.dataset.prevHeight;
        delete win.dataset.maximized;
    } else {
        win.dataset.prevLeft = win.style.left;
        win.dataset.prevTop = win.style.top;
        win.dataset.prevWidth = win.style.width;
        win.dataset.prevHeight = win.style.height;
        win.style.left = '0';
        win.style.top = '0';
        win.style.width = '100%';
        win.style.height = '100%';
        win.dataset.maximized = 'true';
    }
}

function openObjectWindow(obj) {
    const title = getObjectTitle(obj);
    const content = `
        <div style="padding: 8px;">
            <h2 style="margin-bottom: 16px;">${title}</h2>
            <p style="color: var(--text-secondary); white-space: pre-wrap;">${obj.content || obj.text || 'No content'}</p>
            ${obj.tags ? `<div style="margin-top: 16px;"><strong>Tags:</strong> ${obj.tags.join(', ')}</div>` : ''}
        </div>
    `;
    createWindow(title, content);
}

// ═══════════════════════════════════════════════════════════════════════════════
// DOCK
// ═══════════════════════════════════════════════════════════════════════════════

function initDock() {
    document.querySelectorAll('.dock-item').forEach(item => {
        item.addEventListener('click', () => {
            const app = item.dataset.app;
            handleDockClick(app);
        });
    });
}

function handleDockClick(app) {
    switch (app) {
        case 'workspace':
            toggleSidebar();
            break;
        case 'cards':
            createWindow('Cards', '<p>Card browser coming soon...</p>');
            break;
        case 'search':
            createWindow('Search', `
                <div style="padding: 8px;">
                    <input type="text" placeholder="Search objects..." 
                           style="width: 100%; padding: 12px; border: 1px solid var(--border-medium); 
                                  border-radius: var(--radius-md); font-size: 15px;">
                </div>
            `);
            break;
        case 'maps':
            createWindow('Maps', '<p>Maps view coming soon...</p>');
            break;
        case 'inspector':
            toggleInspector();
            break;
        case 'services':
            openServicesMenu();
            break;
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.style.display = sidebar.style.display === 'none' ? 'flex' : 'none';
}

// ═══════════════════════════════════════════════════════════════════════════════
// SERVICES MENU
// ═══════════════════════════════════════════════════════════════════════════════

function openServicesMenu() {
    const menu = document.getElementById('services-menu');
    const selection = document.getElementById('services-selection');
    const list = document.getElementById('services-list');
    
    // Update selection label
    if (state.selectedObject) {
        selection.textContent = getObjectTitle(state.selectedObject);
    } else {
        selection.textContent = 'No selection';
    }
    
    // Render services
    list.innerHTML = services.map(svc => {
        const canRun = state.selectedObject && 
                       svc.accepts.includes(state.selectedObject.type);
        return `
            <li class="service-item ${canRun ? '' : 'disabled'}" data-id="${svc.id}">
                <span class="service-icon">${svc.icon}</span>
                <span class="service-name">${svc.name}</span>
            </li>
        `;
    }).join('');
    
    // Click handlers
    list.querySelectorAll('.service-item:not(.disabled)').forEach(el => {
        el.addEventListener('click', () => {
            runService(el.dataset.id);
            closeServicesMenu();
        });
    });
    
    menu.classList.remove('hidden');
    state.servicesMenuOpen = true;
}

function closeServicesMenu() {
    document.getElementById('services-menu').classList.add('hidden');
    state.servicesMenuOpen = false;
}

async function runService(serviceId) {
    if (!state.selectedObject) return;
    
    const service = services.find(s => s.id === serviceId);
    console.log(`Running service: ${service.name} on ${getObjectTitle(state.selectedObject)}`);
    
    // TODO: Call actual API
    // For now, show a result window
    createWindow(`${service.name} Result`, `
        <div style="padding: 16px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">${service.icon}</div>
            <h3>Service: ${service.name}</h3>
            <p style="color: var(--text-secondary); margin-top: 8px;">
                Running on: ${getObjectTitle(state.selectedObject)}
            </p>
            <p style="margin-top: 16px; color: var(--success);">✓ Complete</p>
        </div>
    `, { width: 300, height: 250 });
}

// ═══════════════════════════════════════════════════════════════════════════════
// ACTIONS
// ═══════════════════════════════════════════════════════════════════════════════

async function createNewCard() {
    const content = `
        <div style="display: flex; flex-direction: column; gap: 12px;">
            <input type="text" id="new-card-title" placeholder="Card title..." 
                   style="padding: 12px; border: 1px solid var(--border-medium); 
                          border-radius: var(--radius-md); font-size: 17px; font-weight: 500;">
            <textarea id="new-card-content" placeholder="Write your content here..." 
                      style="padding: 12px; border: 1px solid var(--border-medium); 
                             border-radius: var(--radius-md); font-size: 15px; min-height: 200px; resize: vertical;"></textarea>
            <button onclick="saveNewCard()" 
                    style="padding: 12px 24px; background: var(--accent); color: white; 
                           border-radius: var(--radius-md); font-weight: 500; cursor: pointer;">
                Save Card
            </button>
        </div>
    `;
    createWindow('New Card', content, { width: 450, height: 380 });
}

window.saveNewCard = async function() {
    const title = document.getElementById('new-card-title').value;
    const content = document.getElementById('new-card-content').value;
    
    if (!title && !content) return;
    
    try {
        const response = await fetch(`${API_BASE}/cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, tags: [] })
        });
        
        if (response.ok) {
            refreshWorkspace();
        }
    } catch (e) {
        console.log('API not available, adding to local state');
        state.objects.push({
            id: `local-${Date.now()}`,
            hash: Math.random().toString(36).slice(2),
            type: 'card',
            title,
            content,
            created_at: Date.now()
        });
        renderObjectList('all');
    }
    
    // Close the new card window
    if (state.activeWindow) {
        closeWindow(state.activeWindow);
    }
};

function createNewQuery() {
    const content = `
        <div style="display: flex; flex-direction: column; gap: 12px;">
            <input type="text" id="new-query-text" placeholder="Enter your query..." 
                   style="padding: 12px; border: 1px solid var(--border-medium); 
                          border-radius: var(--radius-md); font-size: 17px;">
            <button onclick="saveNewQuery()" 
                    style="padding: 12px 24px; background: var(--accent); color: white; 
                           border-radius: var(--radius-md); font-weight: 500; cursor: pointer;">
                Run Query
            </button>
        </div>
    `;
    createWindow('New Query', content, { width: 450, height: 180 });
}

window.saveNewQuery = function() {
    const text = document.getElementById('new-query-text').value;
    if (!text) return;
    
    state.objects.push({
        id: `query-${Date.now()}`,
        hash: Math.random().toString(36).slice(2),
        type: 'query',
        text,
        created_at: Date.now()
    });
    renderObjectList('all');
    
    if (state.activeWindow) {
        closeWindow(state.activeWindow);
    }
};

async function undo() {
    try {
        await fetch(`${API_BASE}/undo`, { method: 'POST' });
        refreshWorkspace();
    } catch (e) {
        console.log('Undo: API not available');
    }
}

async function redo() {
    try {
        await fetch(`${API_BASE}/redo`, { method: 'POST' });
        refreshWorkspace();
    } catch (e) {
        console.log('Redo: API not available');
    }
}

function focusSearch() {
    toggleCommandPalette();
}

function closeAllModals() {
    closeCommandPalette();
    closeServicesMenu();
}
