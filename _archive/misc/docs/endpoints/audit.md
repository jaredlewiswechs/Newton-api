# Audit & Security Endpoints

**January 6, 2026** · **Jared Nashon Lewis** · **Jared Lewis Conglomerate** · **parcRI** · **Newton** · **tinyTalk** · **Ada Computing Company**

Newton provides cryptographic signing and an immutable audit trail for all operations.

## /sign

Generate cryptographic signatures for payloads.

### Use Cases

- Sign AI outputs for non-repudiation
- Create tamper-evident receipts
- Establish provenance for generated content

### Request

**POST** `/sign`

```json
{
  "payload": "The verified output content",
  "context": "user-session-123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `payload` | string | Yes | Content to sign |
| `context` | string | No | Additional context (e.g., session ID) |

### Response

```json
{
  "signature": "a7b3c8f2e1d4590f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4",
  "token": "F6A8B0C2D4E5F7A9B1C3",
  "timestamp": 1735689600,
  "payload_hash": "G7B9C1D3E5F7A9B1",
  "verified": true
}
```

| Field | Description |
|-------|-------------|
| `signature` | Full SHA-256 signature |
| `token` | Short verification token (24 chars) |
| `timestamp` | Unix timestamp of signing |
| `payload_hash` | Hash of the payload (16 chars) |
| `verified` | Always `true` on success |

### Example

```bash
curl -X POST https://api.parcri.net/sign \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "payload": "AI generated response: The answer is 42",
    "context": "session-abc-123"
  }'
```

---

## /ledger

Retrieve the append-only audit trail.

### How It Works

Every verification, analysis, and signature creates an entry in Newton's cryptographic ledger:

1. Each entry is hashed with SHA-256
2. Each entry includes the previous entry's hash (chain)
3. A nonce provides additional entropy
4. Merkle root enables bulk verification

### Request

**GET** `/ledger`

#### Query Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | int | 100 | 1000 | Entries to return |
| `offset` | int | 0 | - | Starting offset |

### Response

```json
{
  "entries": [
    {
      "id": 0,
      "type": "verification",
      "payload": {
        "input_hash": "A1B2C3D4...",
        "verified": true,
        "constraints": ["harm", "medical", "legal", "security"]
      },
      "timestamp": 1735600000,
      "prev_hash": "GENESIS",
      "nonce": "a1b2c3d4",
      "hash": "H8C0D2E4F6A8B0C2"
    },
    {
      "id": 1,
      "type": "signature",
      "payload": {
        "payload_hash": "B2C3D4E5...",
        "context": "session-123"
      },
      "timestamp": 1735600100,
      "prev_hash": "H8C0D2E4F6A8B0C2",
      "nonce": "e5f6g7h8",
      "hash": "I9D1E3F5A7B9C1D3"
    }
  ],
  "total": 1247,
  "merkle_root": "J0E2F4A6B8C0D2E4"
}
```

### Entry Types

| Type | Description |
|------|-------------|
| `verification` | `/verify` request |
| `analysis` | `/analyze` request |
| `signature` | `/sign` request |
| `compilation` | `/compile` request |
| `grounding` | `/ground` request |

### Example

```bash
# Get last 50 entries
curl "https://api.parcri.net/ledger?limit=50" \
  -H "X-API-Key: your-api-key"

# Get entries 100-150
curl "https://api.parcri.net/ledger?limit=50&offset=100" \
  -H "X-API-Key: your-api-key"
```

---

## /ledger/verify

Verify the integrity of the cryptographic ledger chain.

### What It Checks

1. **Genesis block** - First entry has `prev_hash: "GENESIS"`
2. **Chain linkage** - Each entry's `prev_hash` matches previous entry's `hash`
3. **Hash integrity** - Each entry's hash matches its computed hash
4. **Merkle root** - Computed from all entry hashes

### Request

**GET** `/ledger/verify`

### Response (Valid Chain)

```json
{
  "valid": true,
  "entries": 1247,
  "message": "Chain intact - all entries verified",
  "merkle_root": "J0E2F4A6B8C0D2E4",
  "first_entry": 1735600000,
  "last_entry": 1735689600
}
```

### Response (Invalid Chain)

```json
{
  "valid": false,
  "entries": 1247,
  "errors": [
    {
      "index": 523,
      "error": "Chain linkage broken"
    },
    {
      "index": 524,
      "error": "Entry hash mismatch (possible tampering)"
    }
  ],
  "message": "Chain integrity compromised: 2 error(s)",
  "merkle_root": "INVALID"
}
```

### Example

```bash
curl https://api.parcri.net/ledger/verify \
  -H "X-API-Key: your-api-key"
```

---

## Ledger Persistence

### Configuration

Set the ledger storage path:

```bash
export NEWTON_LEDGER_PATH=/var/newton/ledger.json
```

Default: `.newton_ledger.json` in the working directory.

### Storage Format

The ledger is stored as a JSON array:

```json
[
  {
    "id": 0,
    "type": "verification",
    "payload": {...},
    "timestamp": 1735600000,
    "prev_hash": "GENESIS",
    "nonce": "a1b2c3d4",
    "hash": "H8C0D2E4F6A8B0C2"
  }
]
```

### Maximum Size

The ledger is limited to 10,000 entries by default. When exceeded:
- Oldest entries are rotated out
- Chain is maintained from the new "genesis"

---

## Merkle Root Verification

The Merkle root provides efficient bulk verification:

```
              Root
            /      \
        H(0,1)    H(2,3)
        /    \    /    \
      H(0)  H(1) H(2)  H(3)
```

1. Combine pairs of hashes
2. Hash each combined pair
3. Repeat until one hash remains
4. That hash is the Merkle root

This allows verifying any single entry's inclusion in O(log n) time.
