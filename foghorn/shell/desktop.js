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
const STORAGE_KEY = 'nina-desktop-state';

// ═══════════════════════════════════════════════════════════════════════════════
// STATE (with persistence)
// ═══════════════════════════════════════════════════════════════════════════════

const state = {
    objects: [],
    selectedObject: null,
    windows: [],
    activeWindow: null,
    windowZIndex: 100,
    commandPaletteOpen: false,
    servicesMenuOpen: false,
    sidebarVisible: true,
    inspectorVisible: true,
};

// ═══════════════════════════════════════════════════════════════════════════════
// PERSISTENCE — localStorage backed
// ═══════════════════════════════════════════════════════════════════════════════

function loadState() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            const parsed = JSON.parse(saved);
            // Restore only serializable state
            state.objects = parsed.objects || [];
            state.sidebarVisible = parsed.sidebarVisible !== false;
            state.inspectorVisible = parsed.inspectorVisible !== false;
            console.log('📂 Restored state from localStorage');
        }
    } catch (e) {
        console.log('Could not restore state:', e);
    }
}

function saveState() {
    try {
        const toSave = {
            objects: state.objects,
            sidebarVisible: state.sidebarVisible,
            inspectorVisible: state.inspectorVisible,
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
    } catch (e) {
        console.log('Could not save state:', e);
    }
}

// Auto-save on changes
function persistState() {
    saveState();
}

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
    loadState();
    initClock();
    initKeyboardShortcuts();
    initMenuBar();
    initDock();
    initCommandPalette();
    initObjectList();
    initWindowManager();
    initPanelState();
    initContextMenu();
    initCanvasDragDrop();
    initBezierCanvas();
    refreshWorkspace();
    
    console.log('🖥️ Nina Desktop initialized');
});

// Apply saved panel visibility state
function initPanelState() {
    const sidebar = document.getElementById('sidebar');
    const inspector = document.getElementById('inspector');
    
    sidebar.style.display = state.sidebarVisible ? 'flex' : 'none';
    inspector.style.display = state.inspectorVisible ? 'flex' : 'none';
}

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
        // File menu
        case 'new-card':
            createNewCard();
            break;
        case 'new-query':
            createNewQuery();
            break;
        case 'new-file':
            createNewFileAsset();
            break;
        case 'open':
            openFileDialog();
            break;
        case 'save':
            saveCurrentObject();
            break;
        case 'save-as':
            saveAsDialog();
            break;
        case 'export':
            exportWorkspace();
            break;
        
        // Edit menu
        case 'undo':
            undo();
            break;
        case 'redo':
            redo();
            break;
        case 'cut':
            document.execCommand('cut');
            break;
        case 'copy':
            document.execCommand('copy');
            break;
        case 'paste':
            document.execCommand('paste');
            break;
        case 'delete':
            deleteSelectedObject();
            break;
        case 'select-all':
            document.execCommand('selectAll');
            break;
        
        // View menu
        case 'toggle-sidebar':
            toggleSidebar();
            break;
        case 'toggle-inspector':
            toggleInspector();
            break;
        case 'zoom-in':
            zoomIn();
            break;
        case 'zoom-out':
            zoomOut();
            break;
        case 'zoom-reset':
            zoomReset();
            break;
        
        // Objects menu
        case 'inspect':
            toggleInspector();
            break;
        case 'duplicate':
            duplicateSelectedObject();
            break;
        
        // Services menu
        case 'all-services':
            openServicesMenu();
            break;
        case 'verify':
        case 'compute':
        case 'extract':
        case 'summarize':
            runServiceByName(action);
            break;
        
        // Window menu
        case 'minimize':
            if (state.activeWindow) minimizeWindow(state.activeWindow);
            break;
        case 'zoom':
            if (state.activeWindow) maximizeWindow(state.activeWindow);
            break;
        case 'bring-all':
            bringAllWindowsToFront();
            break;
        
        // Help menu
        case 'search-help':
            openHelpSearch();
            break;
        case 'nina-help':
            openHelp();
            break;
        case 'keyboard':
            showKeyboardShortcuts();
            break;
        
        default:
            console.log('Unhandled action:', action);
            showNotification(`Action "${action}" not yet implemented`);
    }
}

// Notifications
function showNotification(message, type = 'info') {
    console.log(`[${type}] ${message}`);
    // Could add a toast notification UI here
}

function runServiceByName(serviceName) {
    if (!state.selectedObject) {
        showNotification('Select an object first');
        return;
    }
    const service = services.find(s => s.id === serviceName);
    if (service) {
        runService(serviceName);
    }
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
            // Merge server objects with local objects
            const serverObjects = data.cards || [];
            const localObjects = state.objects.filter(o => o.id?.startsWith('local-'));
            state.objects = [...serverObjects, ...localObjects];
        } else {
            // Use local state if server unavailable
            if (state.objects.length === 0) {
                state.objects = [
                    { id: 'demo1', hash: 'abc123', type: 'card', title: 'Welcome to Nina', content: 'Your first card' },
                    { id: 'demo2', hash: 'def456', type: 'card', title: 'Getting Started', content: 'Try creating a new card with ⌘N' },
                    { id: 'demo3', hash: 'ghi789', type: 'query', text: 'What is the capital of France?' },
                ];
            }
        }
    } catch (e) {
        console.log('API not available, using local/demo objects');
        if (state.objects.length === 0) {
            state.objects = [
                { id: 'demo1', hash: 'abc123', type: 'card', title: 'Welcome to Nina', content: 'Your first card' },
                { id: 'demo2', hash: 'def456', type: 'card', title: 'Getting Started', content: 'Try creating a new card with ⌘N' },
                { id: 'demo3', hash: 'ghi789', type: 'query', text: 'What is the capital of France?' },
            ];
        }
    }
    
    persistState();
    renderObjectList('all');
    updateWindowMenu();
}

function renderObjectList(filter = 'all') {
    const list = document.getElementById('object-list');
    const filtered = filter === 'all' 
        ? state.objects 
        : state.objects.filter(obj => obj.type === filter);
    
    list.innerHTML = filtered.map(obj => `
        <li class="object-item ${state.selectedObject?.id === obj.id ? 'selected' : ''}" 
            data-id="${obj.id}" data-hash="${obj.hash}" draggable="true">
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
        
        // Right-click context menu
        el.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const obj = state.objects.find(o => o.id === el.dataset.id);
            if (obj) {
                selectObject(obj);
                showContextMenu(e.clientX, e.clientY, obj);
            }
        });
        
        // Drag to canvas
        el.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', el.dataset.id);
            el.classList.add('dragging');
        });
        
        el.addEventListener('dragend', () => {
            el.classList.remove('dragging');
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
    state.inspectorVisible = inspector.style.display === 'none';
    inspector.style.display = state.inspectorVisible ? 'flex' : 'none';
    persistState();
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
    updateWindowMenu();
    
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
        updateWindowMenu();
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
            openCardsApp();
            break;
        case 'search':
            openSearchApp();
            break;
        case 'maps':
            openMapsApp();
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
    state.sidebarVisible = sidebar.style.display === 'none';
    sidebar.style.display = state.sidebarVisible ? 'flex' : 'none';
    persistState();
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
    
    // Show progress window
    const progressWin = createWindow(`${service.name}`, `
        <div style="padding: 16px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">${service.icon}</div>
            <h3>Processing...</h3>
            <p style="color: var(--text-secondary); margin-top: 8px;">
                ${getObjectTitle(state.selectedObject)}
            </p>
        </div>
    `, { width: 300, height: 220 });
    
    try {
        const response = await fetch(`${API_BASE}/services/${serviceId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ object_id: state.selectedObject.id })
        });
        
        let result;
        if (response.ok) {
            result = await response.json();
        } else {
            // Simulate result for demo
            result = { success: true, simulated: true };
        }
        
        // Update window with result
        progressWin.querySelector('.window-content').innerHTML = `
            <div style="padding: 16px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 16px;">${service.icon}</div>
                <h3>Service: ${service.name}</h3>
                <p style="color: var(--text-secondary); margin-top: 8px;">
                    ${getObjectTitle(state.selectedObject)}
                </p>
                <p style="margin-top: 16px; color: var(--success);">✓ Complete</p>
                ${result.receipt ? `<p style="font-size: 11px; color: var(--text-tertiary); margin-top: 8px;">Receipt: ${result.receipt.id?.slice(0,8) || 'generated'}</p>` : ''}
            </div>
        `;
        
        // Create receipt object
        if (result.receipt) {
            state.objects.push({
                id: result.receipt.id || `receipt-${Date.now()}`,
                type: 'receipt',
                ...result.receipt
            });
            persistState();
            renderObjectList('all');
        }
        
    } catch (e) {
        console.log('Service API not available, showing demo result');
        progressWin.querySelector('.window-content').innerHTML = `
            <div style="padding: 16px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 16px;">${service.icon}</div>
                <h3>Service: ${service.name}</h3>
                <p style="color: var(--text-secondary); margin-top: 8px;">
                    ${getObjectTitle(state.selectedObject)}
                </p>
                <p style="margin-top: 16px; color: var(--success);">✓ Complete (Demo)</p>
            </div>
        `;
    }
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
            await refreshWorkspace();
            showNotification('Card created');
        } else {
            throw new Error('API error');
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
        persistState();
        renderObjectList('all');
        showNotification('Card saved locally');
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
    persistState();
    renderObjectList('all');
    showNotification('Query created');
    
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

// ═══════════════════════════════════════════════════════════════════════════════
// ADDITIONAL ACTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function createNewFileAsset() {
    const content = `
        <div style="display: flex; flex-direction: column; gap: 12px; padding: 8px;">
            <div style="padding: 24px; border: 2px dashed var(--border-medium); text-align: center;">
                <p style="font-size: 32px; margin-bottom: 8px;">📁</p>
                <p>Drag & drop a file here</p>
                <p style="font-size: 12px; color: var(--text-tertiary); margin-top: 8px;">or</p>
                <input type="file" id="file-input" style="margin-top: 12px;">
            </div>
            <button onclick="handleFileUpload()" 
                    style="padding: 12px 24px; background: var(--accent); color: white; 
                           border: none; font-weight: 500; cursor: pointer;">
                Upload File
            </button>
        </div>
    `;
    createWindow('New File Asset', content, { width: 400, height: 300 });
}

window.handleFileUpload = function() {
    const input = document.getElementById('file-input');
    if (input.files.length > 0) {
        const file = input.files[0];
        const asset = {
            id: `local-${Date.now()}`,
            hash: Math.random().toString(36).slice(2),
            type: 'file_asset',
            name: file.name,
            size: file.size,
            mime_type: file.type,
            created_at: Date.now()
        };
        state.objects.push(asset);
        persistState();
        renderObjectList('all');
        if (state.activeWindow) closeWindow(state.activeWindow);
        showNotification(`File "${file.name}" added`);
    }
};

function openFileDialog() {
    createWindow('Open', `
        <div style="padding: 16px;">
            <p style="margin-bottom: 16px;">Open a workspace file:</p>
            <input type="file" accept=".json" onchange="handleWorkspaceOpen(this)">
        </div>
    `, { width: 350, height: 180 });
}

window.handleWorkspaceOpen = async function(input) {
    if (input.files.length > 0) {
        const file = input.files[0];
        const text = await file.text();
        try {
            const data = JSON.parse(text);
            if (data.objects) {
                state.objects = [...state.objects, ...data.objects];
                persistState();
                renderObjectList('all');
                showNotification(`Imported ${data.objects.length} objects`);
            }
        } catch (e) {
            showNotification('Invalid file format', 'error');
        }
        if (state.activeWindow) closeWindow(state.activeWindow);
    }
};

function saveCurrentObject() {
    if (!state.selectedObject) {
        showNotification('No object selected');
        return;
    }
    // Objects are auto-saved via persistence
    showNotification('Saved');
}

function saveAsDialog() {
    if (!state.selectedObject) {
        showNotification('No object selected');
        return;
    }
    const data = JSON.stringify(state.selectedObject, null, 2);
    downloadFile(`${state.selectedObject.title || 'object'}.json`, data);
}

function exportWorkspace() {
    const data = JSON.stringify({ objects: state.objects, exported_at: Date.now() }, null, 2);
    downloadFile('nina-workspace.json', data);
    showNotification('Workspace exported');
}

function downloadFile(filename, content) {
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function deleteSelectedObject() {
    if (!state.selectedObject) {
        showNotification('No object selected');
        return;
    }
    const idx = state.objects.findIndex(o => o.id === state.selectedObject.id);
    if (idx >= 0) {
        state.objects.splice(idx, 1);
        state.selectedObject = null;
        persistState();
        renderObjectList('all');
        updateInspector(null);
        showNotification('Object deleted');
    }
}

function duplicateSelectedObject() {
    if (!state.selectedObject) {
        showNotification('No object selected');
        return;
    }
    const copy = { ...state.selectedObject };
    copy.id = `local-${Date.now()}`;
    copy.hash = Math.random().toString(36).slice(2);
    copy.title = (copy.title || 'Object') + ' (copy)';
    copy.created_at = Date.now();
    state.objects.push(copy);
    persistState();
    renderObjectList('all');
    selectObject(copy);
    showNotification('Object duplicated');
}

// Zoom functions
let currentZoom = 1;

function zoomIn() {
    currentZoom = Math.min(2, currentZoom + 0.1);
    document.getElementById('workspace-area').style.transform = `scale(${currentZoom})`;
    document.getElementById('workspace-area').style.transformOrigin = 'top left';
}

function zoomOut() {
    currentZoom = Math.max(0.5, currentZoom - 0.1);
    document.getElementById('workspace-area').style.transform = `scale(${currentZoom})`;
    document.getElementById('workspace-area').style.transformOrigin = 'top left';
}

function zoomReset() {
    currentZoom = 1;
    document.getElementById('workspace-area').style.transform = 'none';
}

function bringAllWindowsToFront() {
    document.querySelectorAll('.window').forEach(win => {
        win.style.display = 'flex';
    });
}

// Help functions
function openHelpSearch() {
    createWindow('Help Search', `
        <div style="padding: 16px;">
            <input type="text" placeholder="Search help topics..." 
                   style="width: 100%; padding: 12px; border: 1px solid var(--border-medium); font-size: 15px;">
            <div style="margin-top: 16px; color: var(--text-tertiary);">
                <p>Try searching for:</p>
                <ul style="margin-left: 20px; margin-top: 8px;">
                    <li>keyboard shortcuts</li>
                    <li>creating cards</li>
                    <li>services</li>
                </ul>
            </div>
        </div>
    `, { width: 400, height: 300 });
}

function openHelp() {
    createWindow('Nina Help', `
        <div style="padding: 16px;">
            <h2 style="margin-bottom: 16px;">Welcome to Nina Desktop</h2>
            <p style="margin-bottom: 12px;">Nina is your verified computation environment powered by Foghorn.</p>
            
            <h3 style="margin: 16px 0 8px;">Quick Start</h3>
            <ul style="margin-left: 20px;">
                <li><strong>⌘N</strong> — Create new card</li>
                <li><strong>⌘K</strong> — Command palette</li>
                <li><strong>⌘I</strong> — Toggle inspector</li>
                <li><strong>Double-click</strong> — Open object in window</li>
            </ul>
            
            <h3 style="margin: 16px 0 8px;">Services</h3>
            <p>Select an object and use Services menu to:</p>
            <ul style="margin-left: 20px;">
                <li>Verify claims</li>
                <li>Run computations</li>
                <li>Extract data</li>
                <li>Summarize content</li>
            </ul>
        </div>
    `, { width: 500, height: 450 });
}

function showKeyboardShortcuts() {
    createWindow('Keyboard Shortcuts', `
        <div style="padding: 16px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px; border-bottom: 1px solid var(--border-light);"><strong>⌘K</strong></td><td style="padding: 8px; border-bottom: 1px solid var(--border-light);">Command Palette</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid var(--border-light);"><strong>⌘N</strong></td><td style="padding: 8px; border-bottom: 1px solid var(--border-light);">New Card</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid var(--border-light);"><strong>⌘I</strong></td><td style="padding: 8px; border-bottom: 1px solid var(--border-light);">Toggle Inspector</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid var(--border-light);"><strong>⌘Z</strong></td><td style="padding: 8px; border-bottom: 1px solid var(--border-light);">Undo</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid var(--border-light);"><strong>⌘⇧Z</strong></td><td style="padding: 8px; border-bottom: 1px solid var(--border-light);">Redo</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid var(--border-light);"><strong>Escape</strong></td><td style="padding: 8px; border-bottom: 1px solid var(--border-light);">Close modals</td></tr>
            </table>
        </div>
    `, { width: 350, height: 320 });
}

// ═══════════════════════════════════════════════════════════════════════════════
// WINDOW MENU MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════

function updateWindowMenu() {
    const menuWindow = document.getElementById('menu-window');
    if (!menuWindow) return;
    
    // Find the "No Windows" placeholder
    const items = menuWindow.querySelectorAll('.dropdown-item');
    const noWindowsItem = Array.from(items).find(item => item.textContent.includes('No Windows'));
    
    // Remove existing window entries (after the last separator)
    const separators = menuWindow.querySelectorAll('.dropdown-separator');
    if (separators.length >= 2) {
        const lastSep = separators[separators.length - 1];
        let sibling = lastSep.nextElementSibling;
        while (sibling) {
            const next = sibling.nextElementSibling;
            sibling.remove();
            sibling = next;
        }
        
        // Add window list
        if (state.windows.length > 0) {
            state.windows.forEach(win => {
                const item = document.createElement('div');
                item.className = 'dropdown-item';
                item.textContent = win.title;
                item.addEventListener('click', () => {
                    focusWindow(win.id);
                    document.getElementById(win.id).style.display = 'flex';
                });
                menuWindow.appendChild(item);
            });
        } else {
            const item = document.createElement('div');
            item.className = 'dropdown-item disabled';
            item.textContent = 'No Windows';
            menuWindow.appendChild(item);
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONTEXT MENU (Right-Click)
// ═══════════════════════════════════════════════════════════════════════════════

let contextTarget = null;

function initContextMenu() {
    const menu = document.getElementById('context-menu');
    
    // Handle context menu items
    menu.querySelectorAll('.context-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const action = item.dataset.action;
            if (action && contextTarget) {
                handleContextAction(action, contextTarget);
            }
            hideContextMenu();
        });
    });
    
    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#context-menu')) {
            hideContextMenu();
        }
    });
    
    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideContextMenu();
        }
    });
}

function showContextMenu(x, y, obj) {
    const menu = document.getElementById('context-menu');
    contextTarget = obj;
    
    // Populate services submenu
    const servicesContainer = document.getElementById('context-services');
    servicesContainer.innerHTML = '';
    
    const availableServices = services.filter(svc => 
        svc.accepts.includes(obj.type)
    );
    
    if (availableServices.length > 0) {
        availableServices.forEach(svc => {
            const item = document.createElement('div');
            item.className = 'context-item';
            item.textContent = `${svc.icon} ${svc.name}`;
            item.addEventListener('click', () => {
                selectObject(obj);
                runService(svc.id);
                hideContextMenu();
            });
            servicesContainer.appendChild(item);
        });
    } else {
        const item = document.createElement('div');
        item.className = 'context-item disabled';
        item.textContent = 'No services available';
        servicesContainer.appendChild(item);
    }
    
    // Position menu
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    menu.classList.remove('hidden');
    
    // Ensure menu stays within viewport
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
        menu.style.left = `${window.innerWidth - rect.width - 10}px`;
    }
    if (rect.bottom > window.innerHeight) {
        menu.style.top = `${window.innerHeight - rect.height - 10}px`;
    }
}

function hideContextMenu() {
    document.getElementById('context-menu').classList.add('hidden');
    contextTarget = null;
}

function handleContextAction(action, obj) {
    switch (action) {
        case 'open':
            openObjectWindow(obj);
            break;
        case 'inspect':
            selectObject(obj);
            if (!state.inspectorVisible) toggleInspector();
            break;
        case 'link':
            startLinkMode(obj);
            break;
        case 'duplicate':
            selectObject(obj);
            duplicateSelectedObject();
            break;
        case 'delete':
            selectObject(obj);
            deleteSelectedObject();
            break;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// CANVAS DRAG & DROP
// ═══════════════════════════════════════════════════════════════════════════════

// Canvas objects state
const canvasObjects = new Map(); // id -> { obj, x, y, element }

function initCanvasDragDrop() {
    const container = document.getElementById('windows-container');
    
    // Allow drop on canvas
    container.addEventListener('dragover', (e) => {
        e.preventDefault();
        container.classList.add('drag-over');
    });
    
    container.addEventListener('dragleave', () => {
        container.classList.remove('drag-over');
    });
    
    container.addEventListener('drop', (e) => {
        e.preventDefault();
        container.classList.remove('drag-over');
        
        const objId = e.dataTransfer.getData('text/plain');
        const obj = state.objects.find(o => o.id === objId);
        
        if (obj) {
            const rect = container.getBoundingClientRect();
            const x = e.clientX - rect.left - 60;
            const y = e.clientY - rect.top - 20;
            
            placeObjectOnCanvas(obj, x, y);
        }
    });
}

function placeObjectOnCanvas(obj, x, y) {
    // Check if already on canvas
    if (canvasObjects.has(obj.id)) {
        // Just move it
        const data = canvasObjects.get(obj.id);
        data.x = x;
        data.y = y;
        data.element.style.left = `${x}px`;
        data.element.style.top = `${y}px`;
        return;
    }
    
    const container = document.getElementById('canvas-objects');
    
    const el = document.createElement('div');
    el.className = 'canvas-object';
    el.dataset.id = obj.id;
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
    
    el.innerHTML = `
        <span class="obj-icon">${getObjectIcon(obj.type)}</span>
        <span class="obj-title">${getObjectTitle(obj)}</span>
        <div class="link-handle" title="Drag to link"></div>
    `;
    
    // Make draggable within canvas
    el.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('link-handle')) return;
        startCanvasObjectDrag(el, obj, e);
    });
    
    // Right-click context menu
    el.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showContextMenu(e.clientX, e.clientY, obj);
    });
    
    // Double-click to open
    el.addEventListener('dblclick', () => {
        openObjectWindow(obj);
    });
    
    // Link handle
    const linkHandle = el.querySelector('.link-handle');
    linkHandle.addEventListener('mousedown', (e) => {
        e.stopPropagation();
        startLinkDrag(obj, e);
    });
    
    container.appendChild(el);
    canvasObjects.set(obj.id, { obj, x, y, element: el });
    
    // Update curves
    renderBezierCurves();
}

let canvasDragState = null;

function startCanvasObjectDrag(el, obj, e) {
    canvasDragState = {
        element: el,
        obj,
        startX: e.clientX,
        startY: e.clientY,
        startLeft: parseInt(el.style.left) || 0,
        startTop: parseInt(el.style.top) || 0,
    };
    
    document.addEventListener('mousemove', handleCanvasObjectDrag);
    document.addEventListener('mouseup', endCanvasObjectDrag);
}

function handleCanvasObjectDrag(e) {
    if (!canvasDragState) return;
    
    const dx = e.clientX - canvasDragState.startX;
    const dy = e.clientY - canvasDragState.startY;
    
    const newX = canvasDragState.startLeft + dx;
    const newY = canvasDragState.startTop + dy;
    
    canvasDragState.element.style.left = `${newX}px`;
    canvasDragState.element.style.top = `${newY}px`;
    
    // Update stored position
    const data = canvasObjects.get(canvasDragState.obj.id);
    if (data) {
        data.x = newX;
        data.y = newY;
    }
    
    // Update curves live
    renderBezierCurves();
}

function endCanvasObjectDrag() {
    canvasDragState = null;
    document.removeEventListener('mousemove', handleCanvasObjectDrag);
    document.removeEventListener('mouseup', endCanvasObjectDrag);
}

// ═══════════════════════════════════════════════════════════════════════════════
// BÉZIER CURVES CANVAS
// ═══════════════════════════════════════════════════════════════════════════════

// Links state
const links = []; // { sourceId, targetId, style }

function initBezierCanvas() {
    // Load saved links
    try {
        const savedLinks = localStorage.getItem('nina-desktop-links');
        if (savedLinks) {
            const parsed = JSON.parse(savedLinks);
            links.push(...parsed);
        }
    } catch (e) {
        console.log('Could not load links');
    }
}

function saveLinks() {
    try {
        localStorage.setItem('nina-desktop-links', JSON.stringify(links));
    } catch (e) {
        console.log('Could not save links');
    }
}

function renderBezierCurves() {
    const svg = document.getElementById('curves-canvas');
    
    // Clear existing paths (except defs)
    svg.querySelectorAll('path').forEach(p => p.remove());
    
    // Render each link
    links.forEach(link => {
        const sourceData = canvasObjects.get(link.sourceId);
        const targetData = canvasObjects.get(link.targetId);
        
        if (!sourceData || !targetData) return;
        
        const path = createBezierPath(
            sourceData.x + 120, sourceData.y + 20, // Right side of source
            targetData.x, targetData.y + 20,       // Left side of target
            link.style || 'solid'
        );
        
        svg.appendChild(path);
    });
    
    // Render temp link if active
    if (linkDragState && linkDragState.currentX !== undefined) {
        const sourceData = canvasObjects.get(linkDragState.sourceObj.id);
        if (sourceData) {
            const path = createBezierPath(
                sourceData.x + 120, sourceData.y + 20,
                linkDragState.currentX, linkDragState.currentY,
                'temp'
            );
            svg.appendChild(path);
        }
    }
}

function createBezierPath(x1, y1, x2, y2, style = 'solid') {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    
    // Calculate control points for smooth curve
    const dx = x2 - x1;
    const cp1x = x1 + dx * 0.4;
    const cp2x = x2 - dx * 0.4;
    
    const d = `M ${x1} ${y1} C ${cp1x} ${y1}, ${cp2x} ${y2}, ${x2} ${y2}`;
    path.setAttribute('d', d);
    path.classList.add('link-curve');
    
    if (style === 'temp') {
        path.classList.add('temp-link');
    } else if (style === 'dashed') {
        path.classList.add('dashed');
    } else if (style === 'dotted') {
        path.classList.add('dotted');
    }
    
    return path;
}

// ═══════════════════════════════════════════════════════════════════════════════
// LINK MODE (Drag to connect objects)
// ═══════════════════════════════════════════════════════════════════════════════

let linkDragState = null;

function startLinkMode(obj) {
    showNotification('Click another object to create link');
    state.linkModeSource = obj;
    document.body.style.cursor = 'crosshair';
    
    // Listen for click on canvas objects
    const handler = (e) => {
        const target = e.target.closest('.canvas-object');
        if (target && target.dataset.id !== obj.id) {
            const targetObj = state.objects.find(o => o.id === target.dataset.id);
            if (targetObj) {
                createLink(obj, targetObj);
            }
        }
        document.body.style.cursor = '';
        document.removeEventListener('click', handler);
        state.linkModeSource = null;
    };
    
    setTimeout(() => {
        document.addEventListener('click', handler);
    }, 100);
}

function startLinkDrag(obj, e) {
    const container = document.getElementById('windows-container');
    const rect = container.getBoundingClientRect();
    
    linkDragState = {
        sourceObj: obj,
        startX: e.clientX - rect.left,
        startY: e.clientY - rect.top,
    };
    
    document.addEventListener('mousemove', handleLinkDrag);
    document.addEventListener('mouseup', endLinkDrag);
}

function handleLinkDrag(e) {
    if (!linkDragState) return;
    
    const container = document.getElementById('windows-container');
    const rect = container.getBoundingClientRect();
    
    linkDragState.currentX = e.clientX - rect.left;
    linkDragState.currentY = e.clientY - rect.top;
    
    renderBezierCurves();
}

function endLinkDrag(e) {
    if (!linkDragState) return;
    
    // Check if dropped on another canvas object
    const target = document.elementFromPoint(e.clientX, e.clientY);
    const canvasObj = target?.closest('.canvas-object');
    
    if (canvasObj && canvasObj.dataset.id !== linkDragState.sourceObj.id) {
        const targetObj = state.objects.find(o => o.id === canvasObj.dataset.id);
        if (targetObj) {
            createLink(linkDragState.sourceObj, targetObj);
        }
    }
    
    linkDragState = null;
    document.removeEventListener('mousemove', handleLinkDrag);
    document.removeEventListener('mouseup', endLinkDrag);
    
    renderBezierCurves();
}

function createLink(source, target) {
    // Check if link already exists
    const exists = links.some(l => 
        (l.sourceId === source.id && l.targetId === target.id) ||
        (l.sourceId === target.id && l.targetId === source.id)
    );
    
    if (!exists) {
        links.push({
            sourceId: source.id,
            targetId: target.id,
            style: 'solid',
            created_at: Date.now(),
        });
        saveLinks();
        renderBezierCurves();
        showNotification(`Linked: ${getObjectTitle(source)} → ${getObjectTitle(target)}`);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// PHASE C: CARDS APP — HyperCard-style Card Viewer/Editor
// ═══════════════════════════════════════════════════════════════════════════════

function openCardsApp() {
    const cards = state.objects.filter(o => o.type === 'card');
    
    const content = `
        <div class="cards-app">
            <div class="cards-toolbar">
                <button class="toolbar-btn" onclick="cardsNewCard()">+ New Card</button>
                <div class="toolbar-search">
                    <input type="text" id="cards-search" placeholder="Filter cards..." oninput="cardsFilter(this.value)">
                </div>
                <select id="cards-view" onchange="cardsChangeView(this.value)">
                    <option value="grid">Grid View</option>
                    <option value="list">List View</option>
                    <option value="stack">Stack View</option>
                </select>
            </div>
            <div class="cards-container" id="cards-container">
                ${renderCardGrid(cards)}
            </div>
        </div>
    `;
    
    createWindow('Cards', content, { width: 700, height: 500 });
}

function renderCardGrid(cards) {
    if (cards.length === 0) {
        return `
            <div class="cards-empty">
                <p style="font-size: 48px; margin-bottom: 16px;">📝</p>
                <p>No cards yet</p>
                <button onclick="cardsNewCard()" style="margin-top: 16px; padding: 8px 16px; cursor: pointer;">Create your first card</button>
            </div>
        `;
    }
    
    return `
        <div class="cards-grid">
            ${cards.map(card => `
                <div class="card-tile" data-id="${card.id}" ondblclick="openCardEditor('${card.id}')">
                    <div class="card-tile-header">
                        <span class="card-tile-icon">📝</span>
                        <span class="card-tile-title">${escapeHtml(card.title || 'Untitled')}</span>
                    </div>
                    <div class="card-tile-content">${escapeHtml((card.content || '').slice(0, 150))}${(card.content?.length > 150) ? '...' : ''}</div>
                    <div class="card-tile-meta">
                        ${card.tags?.length ? card.tags.map(t => `<span class="card-tag">${t}</span>`).join('') : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

window.cardsNewCard = function() {
    openCardEditor(null); // null = new card
};

window.cardsFilter = function(query) {
    const cards = state.objects.filter(o => 
        o.type === 'card' && 
        (o.title?.toLowerCase().includes(query.toLowerCase()) || 
         o.content?.toLowerCase().includes(query.toLowerCase()))
    );
    document.getElementById('cards-container').innerHTML = renderCardGrid(cards);
};

window.cardsChangeView = function(view) {
    const container = document.getElementById('cards-container');
    container.className = `cards-container cards-view-${view}`;
};

window.openCardEditor = function(cardId) {
    let card;
    let isNew = false;
    
    if (cardId) {
        card = state.objects.find(o => o.id === cardId);
    } else {
        isNew = true;
        card = {
            id: `card-${Date.now()}`,
            hash: Math.random().toString(36).slice(2),
            type: 'card',
            title: '',
            content: '',
            tags: [],
            blocks: [],
            created_at: Date.now(),
        };
    }
    
    const content = `
        <div class="card-editor">
            <div class="card-editor-header">
                <input type="text" class="card-title-input" id="card-title-${card.id}" 
                       value="${escapeHtml(card.title || '')}" placeholder="Card Title"
                       oninput="cardEditorDirty('${card.id}')">
                <div class="card-editor-actions">
                    <button onclick="cardAddBlock('${card.id}', 'text')">+ Text</button>
                    <button onclick="cardAddBlock('${card.id}', 'checklist')">+ Checklist</button>
                    <button onclick="cardAddBlock('${card.id}', 'code')">+ Code</button>
                    <button onclick="cardAddBlock('${card.id}', 'link')">+ Link</button>
                </div>
            </div>
            <div class="card-blocks" id="card-blocks-${card.id}">
                ${renderCardBlocks(card)}
            </div>
            <div class="card-editor-footer">
                <div class="card-tags-editor">
                    <span>Tags:</span>
                    <input type="text" id="card-tags-${card.id}" value="${(card.tags || []).join(', ')}" 
                           placeholder="tag1, tag2, tag3" oninput="cardEditorDirty('${card.id}')">
                </div>
                <div class="card-editor-buttons">
                    <button class="btn-secondary" onclick="closeWindow(state.activeWindow)">Cancel</button>
                    <button class="btn-primary" onclick="saveCard('${card.id}', ${isNew})">Save Card</button>
                </div>
            </div>
        </div>
    `;
    
    // Store temp card data for new cards
    if (isNew) {
        window._tempCard = card;
    }
    
    createWindow(isNew ? 'New Card' : `Edit: ${card.title || 'Untitled'}`, content, { width: 600, height: 500 });
};

function renderCardBlocks(card) {
    const blocks = card.blocks || [];
    
    if (blocks.length === 0) {
        // Default: single text block
        return `
            <div class="card-block" data-type="text" data-index="0">
                <textarea class="block-text" placeholder="Start writing..." 
                          oninput="updateBlock('${card.id}', 0, this.value)">${escapeHtml(card.content || '')}</textarea>
            </div>
        `;
    }
    
    return blocks.map((block, i) => renderBlock(card.id, block, i)).join('');
}

function renderBlock(cardId, block, index) {
    switch (block.type) {
        case 'text':
            return `
                <div class="card-block" data-type="text" data-index="${index}">
                    <textarea class="block-text" placeholder="Write something..." 
                              oninput="updateBlock('${cardId}', ${index}, this.value)">${escapeHtml(block.content || '')}</textarea>
                    <button class="block-delete" onclick="deleteBlock('${cardId}', ${index})">×</button>
                </div>
            `;
        case 'checklist':
            const items = block.items || [];
            return `
                <div class="card-block" data-type="checklist" data-index="${index}">
                    <div class="checklist-items">
                        ${items.map((item, j) => `
                            <label class="checklist-item">
                                <input type="checkbox" ${item.done ? 'checked' : ''} 
                                       onchange="toggleChecklistItem('${cardId}', ${index}, ${j})">
                                <span>${escapeHtml(item.text)}</span>
                            </label>
                        `).join('')}
                    </div>
                    <input type="text" class="checklist-add" placeholder="Add item..." 
                           onkeydown="if(event.key==='Enter'){addChecklistItem('${cardId}', ${index}, this.value);this.value='';}">
                    <button class="block-delete" onclick="deleteBlock('${cardId}', ${index})">×</button>
                </div>
            `;
        case 'code':
            return `
                <div class="card-block" data-type="code" data-index="${index}">
                    <select class="code-lang" onchange="updateBlockMeta('${cardId}', ${index}, 'lang', this.value)">
                        <option value="javascript" ${block.lang === 'javascript' ? 'selected' : ''}>JavaScript</option>
                        <option value="python" ${block.lang === 'python' ? 'selected' : ''}>Python</option>
                        <option value="json" ${block.lang === 'json' ? 'selected' : ''}>JSON</option>
                        <option value="text" ${block.lang === 'text' ? 'selected' : ''}>Plain</option>
                    </select>
                    <textarea class="block-code" placeholder="// Code here..." 
                              oninput="updateBlock('${cardId}', ${index}, this.value)">${escapeHtml(block.content || '')}</textarea>
                    <button class="block-delete" onclick="deleteBlock('${cardId}', ${index})">×</button>
                </div>
            `;
        case 'link':
            return `
                <div class="card-block" data-type="link" data-index="${index}">
                    <div class="link-block">
                        <span class="link-icon">🔗</span>
                        <input type="text" class="link-target" placeholder="Link to card ID or URL..." 
                               value="${escapeHtml(block.target || '')}"
                               oninput="updateBlock('${cardId}', ${index}, this.value)">
                    </div>
                    <button class="block-delete" onclick="deleteBlock('${cardId}', ${index})">×</button>
                </div>
            `;
        default:
            return '';
    }
}

window.cardAddBlock = function(cardId, type) {
    const card = getCardForEdit(cardId);
    if (!card.blocks) card.blocks = [];
    
    const newBlock = { type, content: '' };
    if (type === 'checklist') newBlock.items = [];
    if (type === 'code') newBlock.lang = 'javascript';
    
    card.blocks.push(newBlock);
    
    const container = document.getElementById(`card-blocks-${cardId}`);
    container.innerHTML = renderCardBlocks(card);
    cardEditorDirty(cardId);
};

window.deleteBlock = function(cardId, index) {
    const card = getCardForEdit(cardId);
    if (card.blocks) {
        card.blocks.splice(index, 1);
        const container = document.getElementById(`card-blocks-${cardId}`);
        container.innerHTML = renderCardBlocks(card);
        cardEditorDirty(cardId);
    }
};

window.updateBlock = function(cardId, index, value) {
    const card = getCardForEdit(cardId);
    if (card.blocks && card.blocks[index]) {
        card.blocks[index].content = value;
    } else {
        // Legacy: direct content
        card.content = value;
    }
    cardEditorDirty(cardId);
};

window.updateBlockMeta = function(cardId, index, key, value) {
    const card = getCardForEdit(cardId);
    if (card.blocks && card.blocks[index]) {
        card.blocks[index][key] = value;
    }
};

window.addChecklistItem = function(cardId, blockIndex, text) {
    if (!text.trim()) return;
    const card = getCardForEdit(cardId);
    if (card.blocks && card.blocks[blockIndex]) {
        if (!card.blocks[blockIndex].items) card.blocks[blockIndex].items = [];
        card.blocks[blockIndex].items.push({ text: text.trim(), done: false });
        const container = document.getElementById(`card-blocks-${cardId}`);
        container.innerHTML = renderCardBlocks(card);
        cardEditorDirty(cardId);
    }
};

window.toggleChecklistItem = function(cardId, blockIndex, itemIndex) {
    const card = getCardForEdit(cardId);
    if (card.blocks && card.blocks[blockIndex]?.items?.[itemIndex]) {
        card.blocks[blockIndex].items[itemIndex].done = !card.blocks[blockIndex].items[itemIndex].done;
    }
};

function getCardForEdit(cardId) {
    // Check if it's a temp new card
    if (window._tempCard && window._tempCard.id === cardId) {
        return window._tempCard;
    }
    return state.objects.find(o => o.id === cardId) || {};
}

window.cardEditorDirty = function(cardId) {
    // Mark as unsaved - could add visual indicator
};

window.saveCard = function(cardId, isNew) {
    const title = document.getElementById(`card-title-${cardId}`)?.value || 'Untitled';
    const tagsInput = document.getElementById(`card-tags-${cardId}`)?.value || '';
    const tags = tagsInput.split(',').map(t => t.trim()).filter(t => t);
    
    const card = getCardForEdit(cardId);
    card.title = title;
    card.tags = tags;
    card.updated_at = Date.now();
    
    // If blocks exist, compile content from first text block
    if (card.blocks?.length > 0) {
        const textBlock = card.blocks.find(b => b.type === 'text');
        if (textBlock) card.content = textBlock.content;
    }
    
    if (isNew) {
        state.objects.push(card);
        window._tempCard = null;
    } else {
        // Update in place
        const idx = state.objects.findIndex(o => o.id === cardId);
        if (idx >= 0) state.objects[idx] = card;
    }
    
    persistState();
    renderObjectList('all');
    
    // Close editor and refresh cards app if open
    if (state.activeWindow) {
        closeWindow(state.activeWindow);
    }
    
    showNotification(`Card "${title}" saved`);
};

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;')
               .replace(/"/g, '&quot;');
}

// ═══════════════════════════════════════════════════════════════════════════════
// PHASE C: SEARCH APP
// ═══════════════════════════════════════════════════════════════════════════════

function openSearchApp() {
    const content = `
        <div class="search-app">
            <div class="search-header">
                <input type="text" id="search-query" class="search-input" 
                       placeholder="Search all objects..." autofocus
                       oninput="performSearch(this.value)">
                <div class="search-filters">
                    <label><input type="checkbox" checked onchange="searchFilterChange()"> Cards</label>
                    <label><input type="checkbox" checked onchange="searchFilterChange()"> Queries</label>
                    <label><input type="checkbox" checked onchange="searchFilterChange()"> Files</label>
                </div>
            </div>
            <div class="search-results" id="search-results">
                <div class="search-empty">
                    <p style="font-size: 32px; margin-bottom: 8px;">🔍</p>
                    <p>Start typing to search</p>
                </div>
            </div>
            <div class="search-footer">
                <span id="search-count">0 results</span>
                <button onclick="saveSearchAsQuery()">Save as Query</button>
            </div>
        </div>
    `;
    
    createWindow('Search', content, { width: 500, height: 450 });
}

let lastSearchQuery = '';

window.performSearch = function(query) {
    lastSearchQuery = query;
    const results = document.getElementById('search-results');
    
    if (!query.trim()) {
        results.innerHTML = `
            <div class="search-empty">
                <p style="font-size: 32px; margin-bottom: 8px;">🔍</p>
                <p>Start typing to search</p>
            </div>
        `;
        document.getElementById('search-count').textContent = '0 results';
        return;
    }
    
    const q = query.toLowerCase();
    const matches = state.objects.filter(obj => {
        const title = (obj.title || obj.text || obj.name || '').toLowerCase();
        const content = (obj.content || '').toLowerCase();
        const tags = (obj.tags || []).join(' ').toLowerCase();
        return title.includes(q) || content.includes(q) || tags.includes(q);
    });
    
    document.getElementById('search-count').textContent = `${matches.length} result${matches.length !== 1 ? 's' : ''}`;
    
    if (matches.length === 0) {
        results.innerHTML = `
            <div class="search-empty">
                <p>No results for "${escapeHtml(query)}"</p>
            </div>
        `;
        return;
    }
    
    results.innerHTML = matches.map(obj => `
        <div class="search-result" onclick="openSearchResult('${obj.id}')">
            <span class="result-icon">${getObjectIcon(obj.type)}</span>
            <div class="result-info">
                <div class="result-title">${escapeHtml(getObjectTitle(obj))}</div>
                <div class="result-snippet">${escapeHtml((obj.content || obj.text || '').slice(0, 80))}...</div>
            </div>
            <span class="result-type">${obj.type}</span>
        </div>
    `).join('');
};

window.openSearchResult = function(objId) {
    const obj = state.objects.find(o => o.id === objId);
    if (obj) {
        selectObject(obj);
        openObjectWindow(obj);
    }
};

window.saveSearchAsQuery = function() {
    if (!lastSearchQuery.trim()) return;
    
    const query = {
        id: `query-${Date.now()}`,
        hash: Math.random().toString(36).slice(2),
        type: 'query',
        text: lastSearchQuery,
        created_at: Date.now(),
    };
    
    state.objects.push(query);
    persistState();
    renderObjectList('all');
    showNotification('Search saved as Query');
};

// ═══════════════════════════════════════════════════════════════════════════════
// PHASE C: MAPS APP (Stub for Places/Routes)
// ═══════════════════════════════════════════════════════════════════════════════

function openMapsApp() {
    const places = state.objects.filter(o => o.type === 'map_place');
    const routes = state.objects.filter(o => o.type === 'route');
    
    const content = `
        <div class="maps-app">
            <div class="maps-toolbar">
                <button onclick="mapsAddPlace()">+ Add Place</button>
                <button onclick="mapsCreateRoute()">+ Create Route</button>
            </div>
            <div class="maps-view" id="maps-view">
                <div class="maps-canvas" id="maps-canvas">
                    <!-- Simple coordinate-based view -->
                    <svg width="100%" height="100%" viewBox="0 0 400 300">
                        ${places.map(p => `
                            <g class="map-marker" onclick="selectMapPlace('${p.id}')">
                                <circle cx="${((p.longitude || 0) + 180) * 400 / 360}" 
                                        cy="${((90 - (p.latitude || 0)) * 300 / 180)}" 
                                        r="8" fill="#c00"/>
                                <text x="${((p.longitude || 0) + 180) * 400 / 360}" 
                                      y="${((90 - (p.latitude || 0)) * 300 / 180) - 12}" 
                                      text-anchor="middle" font-size="10">${escapeHtml(p.name || 'Place')}</text>
                            </g>
                        `).join('')}
                    </svg>
                </div>
            </div>
            <div class="maps-sidebar">
                <h4>Places (${places.length})</h4>
                <ul class="maps-list">
                    ${places.map(p => `
                        <li onclick="selectMapPlace('${p.id}')">${escapeHtml(p.name || 'Unnamed')}</li>
                    `).join('') || '<li class="empty">No places</li>'}
                </ul>
                <h4>Routes (${routes.length})</h4>
                <ul class="maps-list">
                    ${routes.map(r => `
                        <li onclick="selectRoute('${r.id}')">${escapeHtml(r.name || 'Unnamed Route')}</li>
                    `).join('') || '<li class="empty">No routes</li>'}
                </ul>
            </div>
        </div>
    `;
    
    createWindow('Maps', content, { width: 700, height: 450 });
}

window.mapsAddPlace = function() {
    const place = {
        id: `place-${Date.now()}`,
        hash: Math.random().toString(36).slice(2),
        type: 'map_place',
        name: 'New Place',
        latitude: 29.76 + (Math.random() - 0.5) * 0.1,  // Houston-ish
        longitude: -95.37 + (Math.random() - 0.5) * 0.1,
        created_at: Date.now(),
    };
    
    state.objects.push(place);
    persistState();
    renderObjectList('all');
    openMapsApp(); // Refresh
    showNotification('Place added');
};

window.mapsCreateRoute = function() {
    const places = state.objects.filter(o => o.type === 'map_place');
    if (places.length < 2) {
        showNotification('Need at least 2 places to create a route');
        return;
    }
    
    const route = {
        id: `route-${Date.now()}`,
        hash: Math.random().toString(36).slice(2),
        type: 'route',
        name: 'New Route',
        waypoints: places.slice(0, 2).map(p => p.id),
        created_at: Date.now(),
    };
    
    state.objects.push(route);
    persistState();
    renderObjectList('all');
    openMapsApp(); // Refresh
    showNotification('Route created');
};

window.selectMapPlace = function(placeId) {
    const place = state.objects.find(o => o.id === placeId);
    if (place) {
        selectObject(place);
    }
};
