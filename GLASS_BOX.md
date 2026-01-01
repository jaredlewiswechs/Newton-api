# Glass Box Activation - Implementation Guide

## Overview

The Glass Box activation adds full transparency and human oversight to Newton's verification system. It enables:

1. **Policy-as-Code**: Declarative policy enforcement before and after operations
2. **Human-in-the-Loop (HITL)**: Approval workflows for critical operations
3. **Provenance Tracking**: Full logging of all verification operations to encrypted Vault
4. **Merkle Anchoring**: Periodic checkpoints with cryptographic proof export
5. **CLI Verification**: Standalone tool for external proof verification

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GLASS BOX ACTIVATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   POLICY    │  │  NEGOTIATOR │  │    VAULT    │            │
│  │   ENGINE    │  │   (HITL)    │  │   CLIENT    │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                         │                                       │
│                   ┌─────┴─────┐                                 │
│                   │   FORGE   │                                 │
│                   │ (Enhanced)│                                 │
│                   └─────┬─────┘                                 │
│                         │                                       │
│  ┌──────────────────────┴──────────────────────┐               │
│  │              MERKLE ANCHOR                   │               │
│  │              SCHEDULER                        │               │
│  └──────────────────┬──────────────────────────┘               │
│                     │                                           │
│              ┌──────┴──────┐                                    │
│              │   LEDGER    │                                    │
│              └─────────────┘                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. VaultClient (`core/vault_client.py`)

Simplified interface for logging verification operations to encrypted storage.

**Features:**
- Provenance record creation with full metadata
- Automatic encryption using identity-derived keys
- Retrieval of historical verification records

**Usage:**
```python
from core import get_vault_client

client = get_vault_client()
entry_id = client.log_verification(
    operation="verify",
    input_data="test data",
    result="pass",
    metadata={"elapsed_us": 42}
)
```

### 2. PolicyEngine (`core/policy_engine.py`)

Policy-as-Code middleware for enforcing organizational rules.

**Policy Types:**
- `INPUT_VALIDATION`: Required fields, data structure validation
- `OUTPUT_VALIDATION`: Type checking, format validation
- `RATE_LIMIT`: Request throttling (framework for future implementation)
- `CONTENT_FILTER`: Blacklist/whitelist, regex patterns
- `SIZE_LIMIT`: Maximum data size enforcement

**Policy Actions:**
- `ALLOW`: Pass through
- `DENY`: Block operation
- `WARN`: Log warning but allow
- `REQUIRE_APPROVAL`: Trigger HITL workflow

**Usage:**
```python
from core import get_policy_engine, Policy, PolicyType, PolicyAction

engine = get_policy_engine()

# Add a size limit policy
policy = Policy(
    id="size_limit_1mb",
    name="1MB Size Limit",
    type=PolicyType.SIZE_LIMIT,
    action=PolicyAction.DENY,
    condition={"max_size": 1000000}
)
engine.add_policy(policy)

# Evaluate input
results = engine.evaluate_input(data, "operation_name")
if engine.check_enforcement_needed(results):
    # Block operation
    pass
```

### 3. Negotiator (`core/negotiator.py`)

Human-in-the-Loop approval system for operations requiring judgment.

**Request Priorities:**
- `CRITICAL`: Highest priority, immediate attention
- `HIGH`: Important, review soon
- `MEDIUM`: Standard review
- `LOW`: Review when convenient

**Usage:**
```python
from core import get_negotiator, RequestPriority

negotiator = get_negotiator()

# Request approval
request = negotiator.request_approval(
    operation="sensitive_verify",
    input_data="critical data",
    reason="Requires human oversight",
    priority=RequestPriority.HIGH,
    ttl_seconds=3600
)

# Later: approve/reject
negotiator.approve(request.id, "admin_user", "Looks good")
# or
negotiator.reject(request.id, "admin_user", "Invalid request")
```

### 4. MerkleAnchorScheduler (`core/merkle_anchor.py`)

Periodic Merkle tree anchoring and cryptographic proof generation.

**Features:**
- Automatic scheduled anchoring (default: every 5 minutes)
- Manual anchor creation on demand
- Merkle proof generation for any ledger entry
- Proof verification (internal and external)
- Certificate export for external verification

**Usage:**
```python
from core import MerkleAnchorScheduler

scheduler = MerkleAnchorScheduler(ledger, interval_seconds=300)
scheduler.start()

# Create manual anchor
anchor = scheduler.create_anchor()

# Generate proof for entry
proof = scheduler.generate_proof(entry_index=5)

# Verify proof
valid = scheduler.verify_proof(proof)

# Export certificate
certificate = proof.export_certificate()
```

## API Endpoints

### Policy Management

- `GET /policy` - List all policies and stats
- `POST /policy` - Add new policy
- `DELETE /policy/{id}` - Remove policy

### Negotiator (HITL)

- `GET /negotiator/pending` - Get pending approval requests
- `POST /negotiator/request` - Create approval request
- `GET /negotiator/request/{id}` - Get specific request
- `POST /negotiator/approve/{id}` - Approve request
- `POST /negotiator/reject/{id}` - Reject request

### Merkle Anchoring

- `GET /merkle/anchors` - List all anchors
- `POST /merkle/anchor` - Create new anchor
- `GET /merkle/anchor/{id}` - Get specific anchor
- `GET /merkle/proof/{index}` - Generate and export proof
- `GET /merkle/latest` - Get latest anchor

## CLI Verifier

Standalone tool for verifying Merkle proofs without API access.

**Usage:**
```bash
# Verify a certificate file
python cli_verifier.py --certificate proof.json

# Verify inline proof
python cli_verifier.py \
  --entry-hash abc123... \
  --merkle-root def456... \
  --proof '[{"hash": "...", "direction": "left"}]'
```

**Export certificate from API:**
```bash
curl http://localhost:8000/merkle/proof/5 > proof.json
python cli_verifier.py --certificate proof.json
```

## Frontend

### Glass Box Panel

Located in the Ledger view, shows:
- Merkle anchor count with create button
- Pending approval count with view button
- Active policy count with manage button

### Proof Export

Each ledger entry has an "Export Proof" button that:
1. Generates Merkle proof for the entry
2. Creates verification certificate
3. Downloads as JSON file
4. Can be verified with CLI tool

### Negotiator Card

Modal showing pending HITL requests with:
- Operation type and priority
- Reason for approval requirement
- Approve/Reject buttons
- Real-time status updates

### Policy Manager

Modal displaying all policies with:
- Policy name and type
- Action (allow/deny/warn/require_approval)
- Enabled/disabled status
- Policy metadata

## Forge Integration

The Forge has been extended with Glass Box support:

```python
forge.enable_glass_box(
    vault_client=vault_client,
    policy_engine=policy_engine,
    negotiator=negotiator
)

# Use Glass Box verification
result = forge.verify_with_glass_box(
    constraint=constraint,
    obj=obj,
    operation="verify",
    require_approval=False  # Set to True to force HITL
)
```

**Glass Box verification flow:**
1. Evaluate input policies
2. Request human approval if needed
3. Perform verification
4. Evaluate output policies
5. Log to Vault for provenance
6. Return result

## Testing

Comprehensive test suite with 47 tests, all passing:

- **test_policy_engine.py**: 10 tests for policy evaluation
- **test_negotiator.py**: 12 tests for HITL workflows
- **test_merkle_proofs.py**: 13 tests for Merkle operations
- **test_glass_box.py**: 12 end-to-end integration tests

Run tests:
```bash
pytest tests/test_policy_engine.py -v
pytest tests/test_negotiator.py -v
pytest tests/test_merkle_proofs.py -v
pytest tests/test_glass_box.py -v
```

## Security Considerations

1. **Policy Enforcement**: Policies cannot be bypassed once enabled
2. **Approval Requirements**: HITL requests expire after TTL (default 1 hour)
3. **Provenance Logging**: All operations logged to encrypted Vault
4. **Merkle Anchoring**: Provides cryptographic proof of data integrity
5. **External Verification**: CLI tool enables third-party proof verification

## Example: Full Glass Box Pipeline

```python
from core import (
    get_forge, get_vault_client, get_policy_engine, 
    get_negotiator, MerkleAnchorScheduler,
    Policy, PolicyType, PolicyAction
)

# Initialize components
forge = get_forge()
vault_client = get_vault_client()
policy_engine = get_policy_engine()
negotiator = get_negotiator()
scheduler = MerkleAnchorScheduler(ledger)

# Add policy
policy = Policy(
    id="my_policy",
    name="My Policy",
    type=PolicyType.SIZE_LIMIT,
    action=PolicyAction.DENY,
    condition={"max_size": 1000}
)
policy_engine.add_policy(policy)

# Enable Glass Box
forge.enable_glass_box(
    vault_client=vault_client,
    policy_engine=policy_engine,
    negotiator=negotiator
)

# Start anchoring
scheduler.start()

# Perform verified operation
result = forge.verify_with_glass_box(
    constraint={"field": "value", "operator": "exists", "value": True},
    obj={"value": "test"},
    operation="my_operation"
)

# Create anchor
anchor = scheduler.create_anchor()

# Export proof
proof = scheduler.generate_proof(len(ledger) - 1)
certificate = proof.export_certificate()

# Save certificate
with open('proof.json', 'w') as f:
    json.dump(certificate, f, indent=2)

# Verify externally
# python cli_verifier.py --certificate proof.json
```

## Default Policies

Two default policies are automatically added:

1. **Size Limit** (1MB): Prevents processing oversized inputs
2. **Content Filter**: Warns on potential secrets (API keys, passwords)

These can be removed or modified as needed.

## Monitoring

Check Glass Box status:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

Both endpoints include Glass Box component status and statistics.

## Future Enhancements

Potential additions:
- Rate limiting implementation
- Policy versioning and rollback
- Approval delegation chains
- Anchor submission to external blockchains
- Multi-party approval workflows
- Policy templates library

---

**Glass Box Activation Status: ✅ COMPLETE**

All backend modules, API endpoints, CLI tools, frontend components, and tests implemented and passing.
