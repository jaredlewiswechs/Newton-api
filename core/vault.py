#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON VAULT - ENCRYPTED CONSTRAINT STORAGE
The RAM of the Newton Supercomputer.

The Vault stores constraint sets encrypted with owner-derived keys.
Data sovereignty is non-negotiable.
Your constraints, your keys, your rules.

═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import hashlib
import hmac
import time
import json
import os
import base64
from pathlib import Path

# Use cryptography library if available, fallback to basic implementation
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VaultConfig:
    """Configuration for the Vault."""
    storage_path: str = ".newton_vault"
    key_derivation_iterations: int = 100000
    encryption_enabled: bool = True
    auto_save: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# ENCRYPTED ENTRY
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VaultEntry:
    """A single entry in the Vault."""
    id: str
    owner_id: str
    data: bytes  # Encrypted payload
    nonce: bytes
    created_at: int
    updated_at: int
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "data": base64.b64encode(self.data).decode(),
            "nonce": base64.b64encode(self.nonce).decode(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'VaultEntry':
        return cls(
            id=d["id"],
            owner_id=d["owner_id"],
            data=base64.b64decode(d["data"]),
            nonce=base64.b64decode(d["nonce"]),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            version=d.get("version", 1),
            metadata=d.get("metadata", {})
        )


# ═══════════════════════════════════════════════════════════════════════════════
# KEY DERIVATION
# ═══════════════════════════════════════════════════════════════════════════════

class KeyDerivation:
    """
    Derive encryption keys from identity.

    The key IS the identity. No separate authentication needed.
    If you have the key, you are the owner.
    """

    def __init__(self, iterations: int = 100000):
        self.iterations = iterations

    def derive_key(self, identity: str, passphrase: str, salt: Optional[bytes] = None) -> tuple:
        """
        Derive a 256-bit key from identity + passphrase.
        Returns (key, salt) tuple.
        """
        if salt is None:
            salt = os.urandom(16)

        material = f"{identity}:{passphrase}".encode()

        if CRYPTO_AVAILABLE:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self.iterations,
            )
            key = kdf.derive(material)
        else:
            # Fallback: simple PBKDF2-like derivation
            key = hashlib.pbkdf2_hmac(
                'sha256',
                material,
                salt,
                self.iterations,
                dklen=32
            )

        return key, salt

    def derive_fingerprint(self, identity: str) -> str:
        """Generate a public fingerprint for an identity."""
        return hashlib.sha256(identity.encode()).hexdigest()[:16].upper()


# ═══════════════════════════════════════════════════════════════════════════════
# ENCRYPTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class EncryptionEngine:
    """
    AES-256-GCM encryption.

    Authenticated encryption - tampering is detectable.
    """

    def encrypt(self, key: bytes, plaintext: bytes) -> tuple:
        """
        Encrypt data with AES-256-GCM.
        Returns (ciphertext, nonce) tuple.
        """
        nonce = os.urandom(12)

        if CRYPTO_AVAILABLE:
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        else:
            # Fallback: XOR with key-derived stream (NOT SECURE - demo only)
            # In production, require cryptography library
            stream = hashlib.sha256(key + nonce).digest()
            ciphertext = bytes(p ^ s for p, s in zip(plaintext, stream * (len(plaintext) // 32 + 1)))
            # Add simple MAC
            mac = hmac.new(key, ciphertext, hashlib.sha256).digest()[:16]
            ciphertext = ciphertext + mac

        return ciphertext, nonce

    def decrypt(self, key: bytes, ciphertext: bytes, nonce: bytes) -> bytes:
        """
        Decrypt data with AES-256-GCM.
        Raises exception if authentication fails.
        """
        if CRYPTO_AVAILABLE:
            aesgcm = AESGCM(key)
            return aesgcm.decrypt(nonce, ciphertext, None)
        else:
            # Fallback: verify MAC and XOR (NOT SECURE - demo only)
            mac = ciphertext[-16:]
            ciphertext = ciphertext[:-16]
            expected_mac = hmac.new(key, ciphertext, hashlib.sha256).digest()[:16]
            if not hmac.compare_digest(mac, expected_mac):
                raise ValueError("Authentication failed - data tampered")
            stream = hashlib.sha256(key + nonce).digest()
            return bytes(c ^ s for c, s in zip(ciphertext, stream * (len(ciphertext) // 32 + 1)))


# ═══════════════════════════════════════════════════════════════════════════════
# THE VAULT
# ═══════════════════════════════════════════════════════════════════════════════

class Vault:
    """
    The Newton Vault - Encrypted Constraint Storage.

    This is the RAM of the Newton Supercomputer.
    It stores constraint sets with owner-derived encryption.

    Data sovereignty is absolute:
    - Your constraints are encrypted with YOUR key
    - Only YOU can decrypt YOUR constraints
    - No master key, no backdoors, no exceptions
    """

    def __init__(self, config: Optional[VaultConfig] = None):
        self.config = config or VaultConfig()
        self.key_derivation = KeyDerivation(self.config.key_derivation_iterations)
        self.encryption = EncryptionEngine()
        self._entries: Dict[str, VaultEntry] = {}
        self._owner_index: Dict[str, List[str]] = {}  # owner_id -> [entry_ids]
        self._keys: Dict[str, tuple] = {}  # owner_id -> (key, salt)

        # Load existing vault
        self._load()

    # ─────────────────────────────────────────────────────────────────────────
    # KEY MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def register_identity(self, identity: str, passphrase: str) -> str:
        """
        Register a new identity and derive encryption key.
        Returns the identity fingerprint.
        """
        key, salt = self.key_derivation.derive_key(identity, passphrase)
        fingerprint = self.key_derivation.derive_fingerprint(identity)

        self._keys[fingerprint] = (key, salt)

        return fingerprint

    def unlock(self, identity: str, passphrase: str, salt: bytes) -> str:
        """
        Unlock an existing identity.
        Returns the identity fingerprint.
        """
        key, _ = self.key_derivation.derive_key(identity, passphrase, salt)
        fingerprint = self.key_derivation.derive_fingerprint(identity)

        self._keys[fingerprint] = (key, salt)

        return fingerprint

    def lock(self, owner_id: str):
        """Lock an identity (remove key from memory)."""
        if owner_id in self._keys:
            del self._keys[owner_id]

    def is_unlocked(self, owner_id: str) -> bool:
        """Check if an identity is unlocked."""
        return owner_id in self._keys

    # ─────────────────────────────────────────────────────────────────────────
    # STORAGE OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def store(
        self,
        owner_id: str,
        data: Union[Dict, List, str, bytes],
        entry_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store encrypted data in the Vault.
        Returns the entry ID.
        """
        if owner_id not in self._keys:
            raise PermissionError(f"Identity not unlocked: {owner_id}")

        key, _ = self._keys[owner_id]

        # Generate entry ID
        if entry_id is None:
            entry_id = f"V_{hashlib.sha256(os.urandom(16)).hexdigest()[:12].upper()}"

        # Serialize data
        if isinstance(data, (dict, list)):
            plaintext = json.dumps(data).encode()
        elif isinstance(data, str):
            plaintext = data.encode()
        else:
            plaintext = data

        # Encrypt
        now = int(time.time())
        if self.config.encryption_enabled:
            ciphertext, nonce = self.encryption.encrypt(key, plaintext)
        else:
            ciphertext = plaintext
            nonce = b''

        # Check for existing entry (update)
        version = 1
        created_at = now
        if entry_id in self._entries:
            version = self._entries[entry_id].version + 1
            created_at = self._entries[entry_id].created_at

        # Create entry
        entry = VaultEntry(
            id=entry_id,
            owner_id=owner_id,
            data=ciphertext,
            nonce=nonce,
            created_at=created_at,
            updated_at=now,
            version=version,
            metadata=metadata or {}
        )

        # Store
        self._entries[entry_id] = entry

        # Update owner index
        if owner_id not in self._owner_index:
            self._owner_index[owner_id] = []
        if entry_id not in self._owner_index[owner_id]:
            self._owner_index[owner_id].append(entry_id)

        # Auto-save
        if self.config.auto_save:
            self._save()

        return entry_id

    def retrieve(self, owner_id: str, entry_id: str) -> Any:
        """
        Retrieve and decrypt data from the Vault.
        """
        if owner_id not in self._keys:
            raise PermissionError(f"Identity not unlocked: {owner_id}")

        if entry_id not in self._entries:
            raise KeyError(f"Entry not found: {entry_id}")

        entry = self._entries[entry_id]

        if entry.owner_id != owner_id:
            raise PermissionError(f"Entry owned by different identity")

        key, _ = self._keys[owner_id]

        # Decrypt
        if self.config.encryption_enabled:
            plaintext = self.encryption.decrypt(key, entry.data, entry.nonce)
        else:
            plaintext = entry.data

        # Deserialize
        try:
            return json.loads(plaintext.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return plaintext

    def list_entries(self, owner_id: str) -> List[Dict[str, Any]]:
        """List all entries for an owner (metadata only, not decrypted content)."""
        if owner_id not in self._owner_index:
            return []

        return [
            {
                "id": self._entries[eid].id,
                "created_at": self._entries[eid].created_at,
                "updated_at": self._entries[eid].updated_at,
                "version": self._entries[eid].version,
                "metadata": self._entries[eid].metadata
            }
            for eid in self._owner_index[owner_id]
            if eid in self._entries
        ]

    def delete(self, owner_id: str, entry_id: str):
        """Delete an entry (if owner matches)."""
        if entry_id not in self._entries:
            return

        entry = self._entries[entry_id]
        if entry.owner_id != owner_id:
            raise PermissionError(f"Entry owned by different identity")

        del self._entries[entry_id]

        if owner_id in self._owner_index:
            self._owner_index[owner_id] = [
                eid for eid in self._owner_index[owner_id] if eid != entry_id
            ]

        if self.config.auto_save:
            self._save()

    # ─────────────────────────────────────────────────────────────────────────
    # CONSTRAINT-SPECIFIC OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def store_constraints(
        self,
        owner_id: str,
        constraints: List[Dict],
        name: Optional[str] = None
    ) -> str:
        """Store a constraint set."""
        return self.store(
            owner_id=owner_id,
            data={"constraints": constraints, "name": name or "unnamed"},
            metadata={"type": "constraint_set", "count": len(constraints)}
        )

    def retrieve_constraints(self, owner_id: str, entry_id: str) -> List[Dict]:
        """Retrieve a constraint set."""
        data = self.retrieve(owner_id, entry_id)
        if isinstance(data, dict) and "constraints" in data:
            return data["constraints"]
        return []

    # ─────────────────────────────────────────────────────────────────────────
    # PERSISTENCE
    # ─────────────────────────────────────────────────────────────────────────

    def _save(self):
        """Save vault to disk."""
        path = Path(self.config.storage_path)
        path.mkdir(parents=True, exist_ok=True)

        # Save entries
        entries_file = path / "entries.json"
        entries_data = {eid: entry.to_dict() for eid, entry in self._entries.items()}
        with open(entries_file, 'w') as f:
            json.dump(entries_data, f, indent=2)

        # Save index
        index_file = path / "index.json"
        with open(index_file, 'w') as f:
            json.dump(self._owner_index, f, indent=2)

    def _load(self):
        """Load vault from disk."""
        path = Path(self.config.storage_path)

        if not path.exists():
            return

        # Load entries
        entries_file = path / "entries.json"
        if entries_file.exists():
            try:
                with open(entries_file, 'r') as f:
                    entries_data = json.load(f)
                self._entries = {
                    eid: VaultEntry.from_dict(data)
                    for eid, data in entries_data.items()
                }
            except (json.JSONDecodeError, IOError):
                pass

        # Load index
        index_file = path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self._owner_index = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

    # ─────────────────────────────────────────────────────────────────────────
    # STATS
    # ─────────────────────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Get vault statistics."""
        return {
            "total_entries": len(self._entries),
            "total_owners": len(self._owner_index),
            "unlocked_identities": len(self._keys),
            "encryption_enabled": self.config.encryption_enabled,
            "crypto_library_available": CRYPTO_AVAILABLE
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_default_vault: Optional[Vault] = None

def get_vault(config: Optional[VaultConfig] = None) -> Vault:
    """Get the default Vault instance."""
    global _default_vault
    if _default_vault is None:
        _default_vault = Vault(config)
    return _default_vault


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Newton Vault - Encrypted Constraint Storage")
    print("=" * 60)

    vault = Vault(VaultConfig(storage_path=".newton_vault_test", encryption_enabled=True))

    # Register identity
    print("\n[Register Identity]")
    owner_id = vault.register_identity("alice@example.com", "secure_passphrase")
    print(f"  Identity fingerprint: {owner_id}")

    # Store constraints
    print("\n[Store Constraints]")
    constraints = [
        {"field": "amount", "operator": "lt", "value": 1000},
        {"field": "category", "operator": "ne", "value": "blocked"}
    ]
    entry_id = vault.store_constraints(owner_id, constraints, name="spending_limits")
    print(f"  Stored constraint set: {entry_id}")

    # Retrieve
    print("\n[Retrieve Constraints]")
    retrieved = vault.retrieve_constraints(owner_id, entry_id)
    print(f"  Retrieved {len(retrieved)} constraints")

    # List entries
    print("\n[List Entries]")
    entries = vault.list_entries(owner_id)
    for e in entries:
        print(f"  {e['id']} (v{e['version']})")

    # Stats
    print("\n[Vault Stats]")
    stats = vault.stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("Your constraints. Your keys. Your rules.")
