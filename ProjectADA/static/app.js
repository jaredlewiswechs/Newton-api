// ═══════════════════════════════════════════════════════════
// ProjectADA - Frontend
// ═══════════════════════════════════════════════════════════

let currentChatId = null;
let chatCache = {};
let trajectoryDebounce = null;

// ── API helpers ──

async function api(path, opts = {}) {
    const res = await fetch(path, {
        headers: { 'Content-Type': 'application/json', ...opts.headers },
        ...opts,
    });
    return res.json();
}

// ── Navigation ──

function switchNav(section) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`[data-nav="${section}"]`).classList.add('active');

    const chatList = document.getElementById('chatListPanel');
    const convPanel = document.getElementById('conversationPanel');
    const knowledgePanel = document.getElementById('knowledgePanel');
    const settingsPanel = document.getElementById('settingsPanel');

    chatList.style.display = '';
    convPanel.style.display = '';
    knowledgePanel.classList.remove('active');
    settingsPanel.classList.remove('active');

    if (section === 'knowledge') {
        convPanel.style.display = 'none';
        knowledgePanel.classList.add('active');
        loadKnowledge();
    } else if (section === 'settings') {
        convPanel.style.display = 'none';
        settingsPanel.classList.add('active');
        loadHealth();
    }
}

// ── Chat List ──

async function loadChats() {
    const chats = await api('/api/chats');
    renderChatList(chats);
}

function renderChatList(chats) {
    const el = document.getElementById('chatList');
    if (!chats.length) {
        el.innerHTML = '<div class="chat-list-empty">No conversations yet. Start one!</div>';
        return;
    }
    el.innerHTML = chats.map(c => `
        <div class="chat-item ${c.id === currentChatId ? 'active' : ''}" onclick="openChat('${c.id}')">
            <div class="chat-item-title">${esc(c.title)}</div>
            <div class="chat-item-preview">${esc(c.preview)}</div>
            <div class="chat-item-meta">
                <span>${timeAgo(c.updated)}</span>
                <span>${c.message_count} messages</span>
            </div>
        </div>
    `).join('');
}

function filterChats(q) {
    const items = document.querySelectorAll('.chat-item');
    const lq = q.toLowerCase();
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(lq) ? '' : 'none';
    });
}

// ── Chat CRUD ──

async function createChat() {
    const chat = await api('/api/chats', { method: 'POST' });
    currentChatId = chat.id;
    await loadChats();
    openChat(chat.id);
}

async function openChat(cid) {
    currentChatId = cid;
    const chat = await api(`/api/chats/${cid}`);
    chatCache[cid] = chat;

    // Show conversation UI
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('convHeader').style.display = '';
    document.getElementById('messages').style.display = '';
    document.getElementById('inputArea').style.display = '';
    document.getElementById('convTitle').textContent = chat.title || 'Conversation';

    renderMessages(chat.messages);
    loadChats();

    // Focus input
    document.getElementById('messageInput').focus();
}

// ── Messages ──

function renderMessages(msgs) {
    const el = document.getElementById('messages');
    if (!msgs.length) {
        el.innerHTML = `
            <div class="message assistant">
                <div class="message-bubble">Hello! I'm Ada, your AI assistant. I have access to the Knowledge bank and can reference verified information. Every response passes through the full verification pipeline. How can I assist you today?</div>
                <div class="message-time">Just now</div>
            </div>`;
        return;
    }
    el.innerHTML = msgs.map(m => renderMessage(m)).join('');
    el.scrollTop = el.scrollHeight;
}

function renderMessage(m) {
    const isAssistant = m.role === 'assistant';
    const meta = m.meta || {};
    let verificationHtml = '';
    if (isAssistant && meta.verified !== undefined) {
        const cls = meta.verified ? 'verified' : 'unverified';
        const icon = meta.verified ? '&#10003;' : '&#9888;';
        const label = meta.verified ? 'Verified' : 'Unverified';
        verificationHtml = `<div class="message-verification ${cls}">${icon} ${label}`;
        if (meta.processing_time_ms) verificationHtml += ` &middot; ${meta.processing_time_ms}ms`;
        if (meta.meta_verification && meta.meta_verification.verified !== undefined) {
            verificationHtml += ` &middot; Meta: ${meta.meta_verification.verified ? 'OK' : 'FAIL'}`;
        }
        if (meta.ada_whisper) {
            verificationHtml += ` &middot; Ada: ${meta.ada_whisper.level || 'quiet'}`;
        }
        verificationHtml += '</div>';
    }

    return `
        <div class="message ${m.role}">
            <div class="message-bubble">${formatContent(m.content)}</div>
            ${verificationHtml}
            <div class="message-time">${m.timestamp ? formatTime(m.timestamp) : 'Just now'}</div>
        </div>`;
}

function formatContent(text) {
    if (!text) return '';
    return esc(text).replace(/\n/g, '<br>');
}

// ── Send Message ──

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const text = input.value.trim();
    if (!text || !currentChatId) return;

    // Add user message immediately
    const msgEl = document.getElementById('messages');
    msgEl.innerHTML += renderMessage({ role: 'user', content: text, timestamp: new Date().toISOString() });

    // Clear input
    input.value = '';
    input.style.height = 'auto';
    document.getElementById('btnSend').classList.remove('active');
    hideTrajectory();

    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    msgEl.innerHTML += `<div class="message assistant" id="${typingId}">
        <div class="message-bubble" style="opacity:0.6;">Thinking...</div>
    </div>`;
    msgEl.scrollTop = msgEl.scrollHeight;

    // Update status
    setStatus('thinking', 'accent');

    try {
        const resp = await api(`/api/chats/${currentChatId}/message`, {
            method: 'POST',
            body: JSON.stringify({ message: text }),
        });

        // Remove typing indicator
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        // Add real response
        msgEl.innerHTML += renderMessage(resp);
        msgEl.scrollTop = msgEl.scrollHeight;

        // Update status based on verification
        if (resp.meta && resp.meta.verified) {
            setStatus('verified', 'green');
        } else {
            setStatus('responded', 'accent');
        }

        // Reload chat list to update preview
        loadChats();
    } catch (e) {
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();
        msgEl.innerHTML += renderMessage({
            role: 'assistant',
            content: 'Connection error. Please check that the server is running.',
            meta: { verified: false },
        });
        setStatus('error', 'red');
    }
}

function setStatus(text, color) {
    document.getElementById('statusText').textContent = text.charAt(0).toUpperCase() + text.slice(1);
    const dot = document.getElementById('statusDot');
    dot.className = 'status-dot';
    if (color === 'green') dot.classList.add('green');
    else if (color === 'red') dot.classList.add('red');
    // Default is accent (orange)
}

// ── Input handling ──

function onInputChange(el) {
    // Auto-resize
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';

    // Toggle send button
    const hasText = el.value.trim().length > 0;
    document.getElementById('btnSend').classList.toggle('active', hasText);

    // Trajectory feedback (debounced)
    if (hasText) {
        clearTimeout(trajectoryDebounce);
        trajectoryDebounce = setTimeout(() => updateTrajectory(el.value), 200);
    } else {
        hideTrajectory();
    }
}

function onInputKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// ── Trajectory real-time feedback ──

async function updateTrajectory(text) {
    try {
        const data = await api('/api/trajectory/compose', {
            method: 'POST',
            body: JSON.stringify({ text }),
        });
        showTrajectory(data);
    } catch (e) {
        // Silent fail - trajectory is optional feedback
    }
}

function showTrajectory(data) {
    const bar = document.getElementById('trajectoryBar');
    bar.classList.remove('hidden');

    const w = Math.min(Math.abs(data.weight || 0), 1);
    const c = Math.min(Math.abs(data.commit || 0), 1);

    document.getElementById('trajWeight').style.width = (w * 100) + '%';
    document.getElementById('trajWeightVal').textContent = (data.weight || 0).toFixed(2);
    document.getElementById('trajCurveVal').textContent = (data.curvature || 0).toFixed(2);
    document.getElementById('trajCommit').style.width = (c * 100) + '%';
    document.getElementById('trajCommitVal').textContent = (data.commit || 0).toFixed(2);
    document.getElementById('trajDepthVal').textContent = data.envelope_depth || 0;

    const warning = document.getElementById('trajWarning');
    if (data.needs_closure) {
        warning.textContent = 'Needs closure';
    } else if (data.approaching_commit) {
        warning.textContent = 'Ready to commit';
    } else {
        warning.textContent = '';
    }
}

function hideTrajectory() {
    document.getElementById('trajectoryBar').classList.add('hidden');
}

// ── Knowledge Panel ──

async function loadKnowledge() {
    try {
        const data = await api('/api/knowledge');
        const el = document.getElementById('knowledgeContent');
        el.innerHTML = `
            <div class="system-card">
                <h3>Verified Facts <span class="system-status ok">${data.facts_count} facts</span></h3>
                <p>Pre-verified facts from CIA World Factbook, NIST, periodic table, and more. These are answered instantly without needing an LLM.</p>
            </div>
            <div class="system-card">
                <h3>Categories</h3>
                <p>${data.categories.length ? data.categories.join(', ') : 'No categories loaded'}</p>
            </div>
            <div class="system-card">
                <h3>5-Tier Query Pipeline</h3>
                <p>
                    <strong>Tier 0:</strong> Shared store (dynamic facts, ~0ms)<br>
                    <strong>Tier 1:</strong> Kinematic shape (question structure, ~0ms)<br>
                    <strong>Tier 2:</strong> Curated keywords (CIA, NIST, ~1ms)<br>
                    <strong>Tier 3:</strong> Semantic fields (Datamuse, ~200ms)<br>
                    <strong>Tier 4:</strong> Wikipedia facts (auto-scraped, ~1ms)
                </p>
            </div>`;
    } catch (e) {
        document.getElementById('knowledgeContent').innerHTML = `
            <div class="system-card">
                <h3>Error <span class="system-status error">failed</span></h3>
                <p>Could not connect to knowledge base.</p>
            </div>`;
    }
}

// ── Settings / Health ──

async function loadHealth() {
    try {
        const data = await api('/api/health');
        const el = document.getElementById('settingsContent');
        const systems = [
            { key: 'ada_sentinel', name: 'Ada Sentinel', desc: 'Drift detection and anomaly sensing. Monitors all inputs and outputs for off-rails behavior.' },
            { key: 'meta_newton', name: 'Meta Newton', desc: 'Self-verifying verifier. Recursively checks that the verification pipeline itself is within bounds.' },
            { key: 'analyzer', name: 'Kinematic Linguistics', desc: 'Language as Bezier curves. Every character has weight, curvature, and commit strength.' },
            { key: 'composer', name: 'Trajectory Composer', desc: 'Real-time writing feedback. Envelope depth, semantic coherence, and termination awareness.' },
            { key: 'verifier', name: 'Trajectory Verifier', desc: 'Grammar + Meaning envelope checking. Detects semantic incoherence before sending.' },
            { key: 'agent', name: 'Newton Agent', desc: 'Full 10-step verification pipeline: Identity, Math, KB, Mesh, LLM with safety constraints.' },
        ];
        el.innerHTML = systems.map(s => {
            const status = data.components[s.key] || 'unknown';
            const cls = status === 'ok' ? 'ok' : 'error';
            return `<div class="system-card">
                <h3>${s.name} <span class="system-status ${cls}">${status}</span></h3>
                <p>${s.desc}</p>
            </div>`;
        }).join('') + `
            <div class="system-card">
                <h3>Overall</h3>
                <p>Status: <strong>${data.status}</strong> | Active chats: ${data.chats}</p>
            </div>`;
    } catch (e) {
        document.getElementById('settingsContent').innerHTML = `
            <div class="system-card">
                <h3>Connection Error <span class="system-status error">offline</span></h3>
                <p>Cannot reach the ProjectADA server. Make sure it's running on port 5050.</p>
            </div>`;
    }
}

// ── Utilities ──

function esc(s) {
    if (!s) return '';
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

function timeAgo(iso) {
    if (!iso) return '';
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return mins + 'm ago';
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return hrs + 'h ago';
    const days = Math.floor(hrs / 24);
    if (days === 1) return 'Yesterday';
    return days + ' days ago';
}

function formatTime(iso) {
    if (!iso) return '';
    try {
        return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
        return '';
    }
}

// ── Init ──

loadChats();
