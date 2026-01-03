# Newton PDA

**January 3, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Newton PDA is a Progressive Web App for personal data management, built on Newton's verification principles.

## Overview

Newton PDA provides a unified data store (the "Soup") for Notes, Names, and Dates. All data is encrypted locally using identity-derived keys and follows an append-only versioning model.

**Key Principles:**
- **Append-only** — Nothing deleted, only superseded. Full audit trail.
- **Z-score verification** — Items crystallize from DRAFT → PENDING → VERIFIED over 3 commits
- **Identity-derived encryption** — AES-256-GCM from your name/passphrase (like Tahoe-LAFS)
- **Local-first** — IndexedDB storage, works offline

---

## Quick Start

### Access

**Hosted:** `https://your-domain/newton-pda/`

**Local:**
```bash
cd newton-pda
python3 -m http.server 8000
# Open http://localhost:8000
```

### Login

Enter your name and passphrase. This derives your encryption key locally — no accounts, no server.

The same credentials on any device unlock your soup.

---

## The Soup

The Soup is Newton PDA's unified data layer. Everything — notes, contacts, events — lives in the same encrypted store.

### Data Types

| Type | Tab | Purpose |
|------|-----|---------|
| `note` | Notes | Free-form text, ideas, documentation |
| `name` | Names | Contacts, people, organizations |
| `date` | Dates | Events, tasks, reminders |

### Item Lifecycle

```
CREATE (Z: 10.0)
   │
   ▼  Commit #1
PENDING (Z: 6.67)
   │
   ▼  Commit #2
PENDING (Z: 3.33)
   │
   ▼  Commit #3
VERIFIED (Z: 0.0)
```

Each commit lowers the Z-score by 3.33. At Z = 0.0, the item is crystallized and can be beamed.

---

## Encryption

Newton PDA uses identity-derived encryption:

1. **Key Derivation**: PBKDF2 with 100,000 iterations, SHA-256
2. **Encryption**: AES-256-GCM with random 12-byte IV
3. **Storage**: Encrypted blobs in IndexedDB

```javascript
// Key derivation (simplified)
const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encode(`${name}:${passphrase}`),
    'PBKDF2',
    false,
    ['deriveKey']
);

const key = await crypto.subtle.deriveKey(
    {
        name: 'PBKDF2',
        salt: encode(`newton-soup-${name}`),
        iterations: 100000,
        hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
);
```

**Sovereignty**: Your data never leaves your device unencrypted. The same credentials work on any device because the key derivation is deterministic.

---

## Versioning

Newton PDA uses append-only versioning. Every edit creates a new version; nothing is ever deleted.

### Version Structure

```javascript
{
    versionId: "abc123",          // Unique version ID
    itemId: "def456",             // Parent item ID
    encrypted: { ... },           // AES-256-GCM encrypted content
    timestamp: 1735654320000,     // When created
    previousVersion: "xyz789",    // Link to previous version
    commitNumber: 2               // Which commit this belongs to
}
```

### Retrieving History

```javascript
const history = await Soup.getItemHistory(itemId);
// Returns all versions in chronological order
```

---

## Relationships

Newton PDA tracks two types of relationships:

### Explicit References

Hard links created when you explicitly connect items:

```javascript
await Soup.createItem('note', 'Meeting Notes',
    'Discussed project with @john',
    [{ targetId: 'contact-123', type: 'mentions' }]
);
```

### Inferred Relationships

Soft connections extracted automatically:

| Pattern | Type | Example |
|---------|------|---------|
| `@mention` | mentions | `@john` → links to Name "John" |
| `#tag` | tagged | `#urgent` → creates tag relationship |
| Dates | temporal | `2025-01-15` → extracted for indexing |

```javascript
// Get all relationships for an item
const rels = await Soup.getRelationships(itemId);

// Get items that reference this item
const backlinks = await Soup.getBacklinks(itemId);
```

---

## Beaming

Verified items can be "beamed" — exported as signed payloads for sharing.

### Export

```javascript
const beam = await Soup.beam(itemId);
// Returns { payload: "base64...", checksum: "sha256..." }
```

### Import

```javascript
const newItem = await Soup.receiveBeam(beamData);
// Creates new item with BEAMED status
```

### Payload Structure

```javascript
{
    version: 1,
    beamedAt: 1735654320000,
    beamedBy: "alice",
    item: {
        id: "original-id",
        type: "note",
        title: "My Note",
        content: "...",
        zScore: 0,
        status: "VERIFIED"
    },
    history: [...],           // Full version history
    relationships: [...],     // Explicit refs only
    audit: [...]              // Audit trail
}
```

---

## Audit Ledger

Every action is logged:

```javascript
{
    id: "audit-123",
    itemId: "item-456",
    action: "CREATE" | "UPDATE" | "COMMIT" | "BEAM" | "RECEIVE_BEAM",
    timestamp: 1735654320000,
    identity: "alice",
    signature: "sha256..."    // Cryptographic signature
}
```

### Retrieve Audit Log

```javascript
// All actions for an item
const log = await Soup.getAuditLog(itemId);

// All actions by current user
const fullLog = await Soup.getAuditLog();
```

---

## API Reference

### Authentication

```javascript
await Soup.authenticate(name, passphrase);
// Returns { identity: "name", authenticated: true }

Soup.logout();

Soup.isAuthenticated();  // boolean
Soup.getIdentity();      // string | null
```

### Items

```javascript
// Create
const item = await Soup.createItem(type, title, content, explicitRefs);

// Read
const item = await Soup.getItem(itemId);
const items = await Soup.listItems(type);  // type optional

// Update
const updated = await Soup.updateItem(itemId, newContent, explicitRefs);

// Commit (advance Z-score)
const committed = await Soup.commit(itemId);
```

### History

```javascript
const versions = await Soup.getItemHistory(itemId);
```

### Relationships

```javascript
const rels = await Soup.getRelationships(itemId);
const backlinks = await Soup.getBacklinks(itemId);
```

### Search

```javascript
const results = await Soup.search(query);
const tagged = await Soup.findByTag('urgent');
```

### Beaming

```javascript
const beam = await Soup.beam(itemId);  // Only works for VERIFIED items
const imported = await Soup.receiveBeam(beamData);
```

---

## Storage

Newton PDA uses IndexedDB with four object stores:

| Store | Purpose | Key |
|-------|---------|-----|
| `items` | Item metadata | `id` |
| `versions` | Encrypted content versions | `versionId` |
| `relationships` | Item connections | `id` |
| `audit` | Action log | `id` |

### Indexes

- `items.type` — Filter by note/name/date
- `items.status` — Filter by DRAFT/PENDING/VERIFIED
- `versions.itemId` — Get all versions for item
- `relationships.fromId` — Get outgoing relationships
- `relationships.toId` — Get incoming relationships (backlinks)
- `audit.itemId` — Get audit trail for item

---

## PWA Features

### Manifest

```json
{
    "name": "Newton PDA",
    "short_name": "Newton",
    "display": "standalone",
    "background_color": "#1a1a1a",
    "theme_color": "#1a1a1a"
}
```

### Shortcuts

- **New Note** — Quick-create a note
- **New Name** — Quick-add a contact
- **New Date** — Quick-create an event

### Installation

On supported browsers, the PWA can be installed to the home screen for app-like experience.

---

## Design

Newton PDA follows a NeXTSTEP-inspired aesthetic:

- **Dark mode default** — `#1a1a1a` background
- **Grooved dividers** — Subtle 3D effect borders
- **Panel headers** — Gradient headers with uppercase labels
- **SF Pro typography** — System font stack
- **Status colors**:
  - DRAFT: Gray (`#666666`)
  - PENDING: Orange (`#ff9f0a`)
  - VERIFIED: Green (`#30d158`)
  - BEAMED: Blue (`#0a84ff`)

---

## Files

| File | Purpose |
|------|---------|
| `newton-pda/index.html` | Main application UI |
| `newton-pda/soup.js` | Data layer (ES module) |
| `newton-pda/manifest.json` | PWA manifest |

---

## Security Considerations

1. **Key strength depends on passphrase** — Use a strong, unique passphrase
2. **No recovery** — Lost passphrase = lost data (by design)
3. **Browser storage** — Data persists in IndexedDB; clearing browser data deletes soup
4. **Same-origin** — Soup is scoped to origin (protocol + domain + port)
5. **No sync** — Each device has its own soup; use beaming to transfer

---

© 2025 Ada Computing Company · Houston, Texas
