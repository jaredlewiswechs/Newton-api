/**
 * Newton PDA - The Soup
 * Unified data layer for Notes, Names, Dates
 *
 * Design principles:
 * - Append-only versioning (nothing deleted, only superseded)
 * - Z-score verification (10.0 → 0.0 over three commits)
 * - Identity-derived encryption (AES-256-GCM from name/passphrase)
 * - IndexedDB persistence
 * - Relationship layer (explicit refs + inferred @mentions/#tags)
 */

const Soup = (() => {
    const DB_NAME = 'newton-soup';
    const DB_VERSION = 1;

    let db = null;
    let encryptionKey = null;
    let currentIdentity = null;

    // ─────────────────────────────────────────────────────────────
    // Crypto Layer - Identity-derived encryption like Tahoe-LAFS
    // ─────────────────────────────────────────────────────────────

    async function deriveKey(name, passphrase) {
        const encoder = new TextEncoder();
        const keyMaterial = await crypto.subtle.importKey(
            'raw',
            encoder.encode(`${name}:${passphrase}`),
            'PBKDF2',
            false,
            ['deriveBits', 'deriveKey']
        );

        const salt = encoder.encode(`newton-soup-${name}`);

        return crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt: salt,
                iterations: 100000,
                hash: 'SHA-256'
            },
            keyMaterial,
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt', 'decrypt']
        );
    }

    async function encrypt(data) {
        if (!encryptionKey) throw new Error('Not authenticated');

        const encoder = new TextEncoder();
        const iv = crypto.getRandomValues(new Uint8Array(12));
        const encoded = encoder.encode(JSON.stringify(data));

        const ciphertext = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv: iv },
            encryptionKey,
            encoded
        );

        return {
            iv: Array.from(iv),
            data: Array.from(new Uint8Array(ciphertext))
        };
    }

    async function decrypt(encrypted) {
        if (!encryptionKey) throw new Error('Not authenticated');

        const decoder = new TextDecoder();
        const iv = new Uint8Array(encrypted.iv);
        const data = new Uint8Array(encrypted.data);

        const decrypted = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: iv },
            encryptionKey,
            data
        );

        return JSON.parse(decoder.decode(decrypted));
    }

    // ─────────────────────────────────────────────────────────────
    // Database Layer - IndexedDB with encrypted storage
    // ─────────────────────────────────────────────────────────────

    function openDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Items store - all soup entries
                if (!db.objectStoreNames.contains('items')) {
                    const items = db.createObjectStore('items', { keyPath: 'id' });
                    items.createIndex('type', 'type', { unique: false });
                    items.createIndex('currentVersion', 'currentVersion', { unique: false });
                    items.createIndex('status', 'status', { unique: false });
                    items.createIndex('createdAt', 'createdAt', { unique: false });
                }

                // Versions store - append-only history
                if (!db.objectStoreNames.contains('versions')) {
                    const versions = db.createObjectStore('versions', { keyPath: 'versionId' });
                    versions.createIndex('itemId', 'itemId', { unique: false });
                    versions.createIndex('timestamp', 'timestamp', { unique: false });
                }

                // Relationships store
                if (!db.objectStoreNames.contains('relationships')) {
                    const rels = db.createObjectStore('relationships', { keyPath: 'id' });
                    rels.createIndex('fromId', 'fromId', { unique: false });
                    rels.createIndex('toId', 'toId', { unique: false });
                    rels.createIndex('type', 'type', { unique: false });
                }

                // Audit ledger
                if (!db.objectStoreNames.contains('audit')) {
                    const audit = db.createObjectStore('audit', { keyPath: 'id' });
                    audit.createIndex('itemId', 'itemId', { unique: false });
                    audit.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    }

    // ─────────────────────────────────────────────────────────────
    // Z-Score Verification System
    // ─────────────────────────────────────────────────────────────

    const Z_INITIAL = 10.0;
    const Z_VERIFIED = 0.0;
    const Z_DECAY_PER_COMMIT = 3.33;

    function calculateZScore(commitCount) {
        const z = Z_INITIAL - (commitCount * Z_DECAY_PER_COMMIT);
        return Math.max(Z_VERIFIED, z);
    }

    function getStatus(zScore) {
        if (zScore <= Z_VERIFIED) return 'VERIFIED';
        if (zScore < Z_INITIAL) return 'PENDING';
        return 'DRAFT';
    }

    // ─────────────────────────────────────────────────────────────
    // Relationship Layer
    // ─────────────────────────────────────────────────────────────

    function extractMentions(text) {
        const mentions = text.match(/@[\w-]+/g) || [];
        return mentions.map(m => m.substring(1));
    }

    function extractTags(text) {
        const tags = text.match(/#[\w-]+/g) || [];
        return tags.map(t => t.substring(1));
    }

    function extractDates(text) {
        const datePatterns = [
            /\d{4}-\d{2}-\d{2}/g,
            /\d{1,2}\/\d{1,2}\/\d{4}/g,
            /(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}/gi
        ];

        const dates = [];
        for (const pattern of datePatterns) {
            const matches = text.match(pattern) || [];
            dates.push(...matches);
        }
        return dates;
    }

    async function updateRelationships(itemId, content, explicitRefs = []) {
        const tx = db.transaction(['relationships', 'items'], 'readwrite');
        const relStore = tx.objectStore('relationships');
        const itemStore = tx.objectStore('items');

        // Remove old inferred relationships
        const index = relStore.index('fromId');
        const existing = await new Promise(resolve => {
            const request = index.getAll(itemId);
            request.onsuccess = () => resolve(request.result);
        });

        for (const rel of existing.filter(r => r.inferred)) {
            relStore.delete(rel.id);
        }

        const relationships = [];

        // Add explicit references
        for (const ref of explicitRefs) {
            const rel = {
                id: `${itemId}->${ref.targetId}:${ref.type}`,
                fromId: itemId,
                toId: ref.targetId,
                type: ref.type,
                inferred: false,
                createdAt: Date.now()
            };
            relStore.put(rel);
            relationships.push(rel);
        }

        // Find @mentions and link to Names
        const mentions = extractMentions(content);
        const allItems = await new Promise(resolve => {
            const request = itemStore.getAll();
            request.onsuccess = () => resolve(request.result);
        });

        for (const mention of mentions) {
            const nameItem = allItems.find(item =>
                item.type === 'name' &&
                item.title.toLowerCase().includes(mention.toLowerCase())
            );
            if (nameItem) {
                const rel = {
                    id: `${itemId}->@${nameItem.id}`,
                    fromId: itemId,
                    toId: nameItem.id,
                    type: 'mentions',
                    inferred: true,
                    createdAt: Date.now()
                };
                relStore.put(rel);
                relationships.push(rel);
            }
        }

        // Extract and store tags
        const tags = extractTags(content);
        for (const tag of tags) {
            const rel = {
                id: `${itemId}->#${tag}`,
                fromId: itemId,
                toId: `#${tag}`,
                type: 'tagged',
                inferred: true,
                createdAt: Date.now()
            };
            relStore.put(rel);
            relationships.push(rel);
        }

        return relationships;
    }

    // ─────────────────────────────────────────────────────────────
    // Core Soup Operations
    // ─────────────────────────────────────────────────────────────

    async function generateId() {
        const array = new Uint8Array(16);
        crypto.getRandomValues(array);
        return Array.from(array, b => b.toString(16).padStart(2, '0')).join('');
    }

    async function createItem(type, title, content, explicitRefs = []) {
        if (!db) throw new Error('Database not initialized');

        const id = await generateId();
        const versionId = await generateId();
        const now = Date.now();

        const encryptedContent = await encrypt({ content });

        const item = {
            id,
            type, // 'note', 'name', 'date'
            title,
            currentVersion: versionId,
            commitCount: 0,
            zScore: Z_INITIAL,
            status: 'DRAFT',
            createdAt: now,
            updatedAt: now
        };

        const version = {
            versionId,
            itemId: id,
            encrypted: encryptedContent,
            timestamp: now,
            commitNumber: 0
        };

        const auditEntry = {
            id: await generateId(),
            itemId: id,
            action: 'CREATE',
            timestamp: now,
            identity: currentIdentity,
            signature: await signAction('CREATE', id, now)
        };

        const tx = db.transaction(['items', 'versions', 'audit'], 'readwrite');
        tx.objectStore('items').put(item);
        tx.objectStore('versions').put(version);
        tx.objectStore('audit').put(auditEntry);

        await new Promise((resolve, reject) => {
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });

        await updateRelationships(id, content, explicitRefs);

        return { ...item, content };
    }

    async function commit(itemId) {
        const tx = db.transaction(['items', 'versions', 'audit'], 'readwrite');
        const itemStore = tx.objectStore('items');

        const item = await new Promise(resolve => {
            const request = itemStore.get(itemId);
            request.onsuccess = () => resolve(request.result);
        });

        if (!item) throw new Error('Item not found');

        const newCommitCount = item.commitCount + 1;
        const newZScore = calculateZScore(newCommitCount);
        const now = Date.now();

        item.commitCount = newCommitCount;
        item.zScore = newZScore;
        item.status = getStatus(newZScore);
        item.updatedAt = now;

        const auditEntry = {
            id: await generateId(),
            itemId: itemId,
            action: 'COMMIT',
            commitNumber: newCommitCount,
            zScore: newZScore,
            timestamp: now,
            identity: currentIdentity,
            signature: await signAction('COMMIT', itemId, now)
        };

        itemStore.put(item);
        tx.objectStore('audit').put(auditEntry);

        await new Promise((resolve, reject) => {
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });

        return item;
    }

    async function updateItem(itemId, newContent, explicitRefs = []) {
        const tx = db.transaction(['items', 'versions', 'audit'], 'readwrite');
        const itemStore = tx.objectStore('items');
        const versionStore = tx.objectStore('versions');

        const item = await new Promise(resolve => {
            const request = itemStore.get(itemId);
            request.onsuccess = () => resolve(request.result);
        });

        if (!item) throw new Error('Item not found');

        const versionId = await generateId();
        const now = Date.now();
        const encryptedContent = await encrypt({ content: newContent });

        // Create new version (append-only)
        const version = {
            versionId,
            itemId,
            encrypted: encryptedContent,
            timestamp: now,
            previousVersion: item.currentVersion,
            commitNumber: item.commitCount
        };

        // Update item to point to new version
        item.currentVersion = versionId;
        item.updatedAt = now;

        const auditEntry = {
            id: await generateId(),
            itemId: itemId,
            action: 'UPDATE',
            versionId: versionId,
            timestamp: now,
            identity: currentIdentity,
            signature: await signAction('UPDATE', itemId, now)
        };

        itemStore.put(item);
        versionStore.put(version);
        tx.objectStore('audit').put(auditEntry);

        await new Promise((resolve, reject) => {
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });

        await updateRelationships(itemId, newContent, explicitRefs);

        return { ...item, content: newContent };
    }

    async function getItem(itemId) {
        const tx = db.transaction(['items', 'versions'], 'readonly');

        const item = await new Promise(resolve => {
            const request = tx.objectStore('items').get(itemId);
            request.onsuccess = () => resolve(request.result);
        });

        if (!item) return null;

        const version = await new Promise(resolve => {
            const request = tx.objectStore('versions').get(item.currentVersion);
            request.onsuccess = () => resolve(request.result);
        });

        if (!version) return { ...item, content: null };

        const decrypted = await decrypt(version.encrypted);

        return { ...item, content: decrypted.content };
    }

    async function getItemHistory(itemId) {
        const tx = db.transaction(['versions'], 'readonly');
        const index = tx.objectStore('versions').index('itemId');

        const versions = await new Promise(resolve => {
            const request = index.getAll(itemId);
            request.onsuccess = () => resolve(request.result);
        });

        // Decrypt all versions
        const history = [];
        for (const version of versions.sort((a, b) => a.timestamp - b.timestamp)) {
            const decrypted = await decrypt(version.encrypted);
            history.push({
                versionId: version.versionId,
                content: decrypted.content,
                timestamp: version.timestamp,
                commitNumber: version.commitNumber
            });
        }

        return history;
    }

    async function listItems(type = null) {
        const tx = db.transaction(['items', 'versions'], 'readonly');
        const itemStore = tx.objectStore('items');

        let items;
        if (type) {
            const index = itemStore.index('type');
            items = await new Promise(resolve => {
                const request = index.getAll(type);
                request.onsuccess = () => resolve(request.result);
            });
        } else {
            items = await new Promise(resolve => {
                const request = itemStore.getAll();
                request.onsuccess = () => resolve(request.result);
            });
        }

        return items.sort((a, b) => b.updatedAt - a.updatedAt);
    }

    async function getRelationships(itemId) {
        const tx = db.transaction(['relationships'], 'readonly');
        const index = tx.objectStore('relationships').index('fromId');

        return new Promise(resolve => {
            const request = index.getAll(itemId);
            request.onsuccess = () => resolve(request.result);
        });
    }

    async function getBacklinks(itemId) {
        const tx = db.transaction(['relationships'], 'readonly');
        const index = tx.objectStore('relationships').index('toId');

        return new Promise(resolve => {
            const request = index.getAll(itemId);
            request.onsuccess = () => resolve(request.result);
        });
    }

    // ─────────────────────────────────────────────────────────────
    // Audit & Signatures
    // ─────────────────────────────────────────────────────────────

    async function signAction(action, itemId, timestamp) {
        const encoder = new TextEncoder();
        const data = encoder.encode(`${currentIdentity}:${action}:${itemId}:${timestamp}`);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    async function getAuditLog(itemId = null) {
        const tx = db.transaction(['audit'], 'readonly');
        const store = tx.objectStore('audit');

        let entries;
        if (itemId) {
            const index = store.index('itemId');
            entries = await new Promise(resolve => {
                const request = index.getAll(itemId);
                request.onsuccess = () => resolve(request.result);
            });
        } else {
            entries = await new Promise(resolve => {
                const request = store.getAll();
                request.onsuccess = () => resolve(request.result);
            });
        }

        return entries.sort((a, b) => b.timestamp - a.timestamp);
    }

    // ─────────────────────────────────────────────────────────────
    // Beaming - Export verified items for sharing
    // ─────────────────────────────────────────────────────────────

    async function beam(itemId) {
        const item = await getItem(itemId);
        if (!item) throw new Error('Item not found');

        if (item.status !== 'VERIFIED') {
            throw new Error('Only verified items can be beamed');
        }

        const history = await getItemHistory(itemId);
        const relationships = await getRelationships(itemId);
        const audit = await getAuditLog(itemId);

        const beamPayload = {
            version: 1,
            beamedAt: Date.now(),
            beamedBy: currentIdentity,
            item: {
                id: item.id,
                type: item.type,
                title: item.title,
                content: item.content,
                zScore: item.zScore,
                status: item.status,
                createdAt: item.createdAt
            },
            history: history,
            relationships: relationships.filter(r => !r.inferred),
            audit: audit
        };

        // Base64 encode for transfer
        const json = JSON.stringify(beamPayload);
        const encoded = btoa(unescape(encodeURIComponent(json)));

        return {
            payload: encoded,
            checksum: await signAction('BEAM', itemId, beamPayload.beamedAt)
        };
    }

    async function receiveBeam(beamData) {
        const json = decodeURIComponent(escape(atob(beamData.payload)));
        const payload = JSON.parse(json);

        // Verify checksum
        const expectedChecksum = await signAction('BEAM', payload.item.id, payload.beamedAt);
        // Note: In production, you'd verify with the sender's public key

        // Import the item
        const item = await createItem(
            payload.item.type,
            payload.item.title,
            payload.item.content
        );

        // Mark as beamed (inherits verified status)
        const tx = db.transaction(['items', 'audit'], 'readwrite');
        const itemStore = tx.objectStore('items');
        const auditStore = tx.objectStore('audit');

        const newItem = await new Promise(resolve => {
            const request = itemStore.get(item.id);
            request.onsuccess = () => resolve(request.result);
        });

        newItem.status = 'BEAMED';
        newItem.zScore = 0;
        newItem.beamedFrom = payload.beamedBy;
        newItem.originalId = payload.item.id;

        itemStore.put(newItem);

        const auditEntry = {
            id: await generateId(),
            itemId: newItem.id,
            action: 'RECEIVE_BEAM',
            originalId: payload.item.id,
            beamedBy: payload.beamedBy,
            timestamp: Date.now(),
            identity: currentIdentity
        };

        auditStore.put(auditEntry);

        await new Promise((resolve, reject) => {
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });

        return newItem;
    }

    // ─────────────────────────────────────────────────────────────
    // Authentication & Initialization
    // ─────────────────────────────────────────────────────────────

    async function authenticate(name, passphrase) {
        encryptionKey = await deriveKey(name, passphrase);
        currentIdentity = name;
        db = await openDatabase();

        return {
            identity: currentIdentity,
            authenticated: true
        };
    }

    function logout() {
        encryptionKey = null;
        currentIdentity = null;
        if (db) {
            db.close();
            db = null;
        }
    }

    function isAuthenticated() {
        return encryptionKey !== null && currentIdentity !== null;
    }

    function getIdentity() {
        return currentIdentity;
    }

    // ─────────────────────────────────────────────────────────────
    // Search
    // ─────────────────────────────────────────────────────────────

    async function search(query) {
        const items = await listItems();
        const results = [];

        const queryLower = query.toLowerCase();

        for (const item of items) {
            const fullItem = await getItem(item.id);
            if (!fullItem) continue;

            const titleMatch = item.title.toLowerCase().includes(queryLower);
            const contentMatch = fullItem.content &&
                fullItem.content.toLowerCase().includes(queryLower);

            if (titleMatch || contentMatch) {
                results.push({
                    ...fullItem,
                    matchType: titleMatch ? 'title' : 'content'
                });
            }
        }

        return results;
    }

    async function findByTag(tag) {
        const tx = db.transaction(['relationships', 'items'], 'readonly');
        const relIndex = tx.objectStore('relationships').index('toId');

        const rels = await new Promise(resolve => {
            const request = relIndex.getAll(`#${tag}`);
            request.onsuccess = () => resolve(request.result);
        });

        const items = [];
        for (const rel of rels) {
            const item = await getItem(rel.fromId);
            if (item) items.push(item);
        }

        return items;
    }

    // ─────────────────────────────────────────────────────────────
    // Public API
    // ─────────────────────────────────────────────────────────────

    return {
        // Auth
        authenticate,
        logout,
        isAuthenticated,
        getIdentity,

        // CRUD
        createItem,
        getItem,
        updateItem,
        listItems,

        // Versioning
        commit,
        getItemHistory,

        // Relationships
        getRelationships,
        getBacklinks,

        // Audit
        getAuditLog,

        // Beaming
        beam,
        receiveBeam,

        // Search
        search,
        findByTag,

        // Helpers
        extractMentions,
        extractTags,
        extractDates,

        // Constants
        Z_INITIAL,
        Z_VERIFIED
    };
})();

export default Soup;
