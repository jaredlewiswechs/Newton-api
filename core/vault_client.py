#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
VAULT CLIENT - SIMPLIFIED VAULT INTERFACE
Client wrapper for Vault operations with provenance tracking.

Part of Glass Box activation - provides clean interface for logging
verification results to encrypted storage.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
import hashlib
import time

from .vault import Vault, VaultConfig


@dataclass
class ProvenanceRecord:
    """Record of a verification operation with full provenance."""
    operation: str
    input_hash: str
    result: str
    timestamp: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "input_hash": self.input_hash,
            "result": self.result,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class VaultClient:
    """
    Client for logging verification operations to the Vault.
    
    This provides a simplified interface for the Forge to log
    all verification operations with full provenance tracking.
    """
    
    def __init__(self, vault: Vault, identity: str = "forge", passphrase: str = "forge_key"):
        """
        Initialize VaultClient.
        
        Args:
            vault: The Vault instance to use
            identity: Identity for the Vault owner
            passphrase: Passphrase for encryption
        """
        self.vault = vault
        self.identity = identity
        self.passphrase = passphrase
        self.owner_id = vault.register_identity(identity, passphrase)
    
    def log_verification(
        self,
        operation: str,
        input_data: str,
        result: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a verification operation to the Vault.
        
        Args:
            operation: Type of operation (e.g., "verify", "calculate")
            input_data: Input data being verified
            result: Result of verification ("pass", "fail", etc.)
            metadata: Additional metadata
        
        Returns:
            Entry ID of the logged record
        """
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()[:16]
        
        record = ProvenanceRecord(
            operation=operation,
            input_hash=input_hash,
            result=result,
            timestamp=int(time.time() * 1000),
            metadata=metadata or {}
        )
        
        entry_id = self.vault.store(
            self.owner_id,
            record.to_dict(),
            metadata={"type": "provenance", "operation": operation}
        )
        
        return entry_id
    
    def get_verification(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a verification record from the Vault.
        
        Args:
            entry_id: ID of the entry to retrieve
        
        Returns:
            The verification record, or None if not found
        """
        try:
            return self.vault.retrieve(self.owner_id, entry_id)
        except (KeyError, ValueError):
            return None
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about logged verifications."""
        return self.vault.stats()


def get_vault_client(vault: Optional[Vault] = None) -> VaultClient:
    """
    Get a VaultClient instance.
    
    Args:
        vault: Optional Vault instance. If not provided, creates a new one.
    
    Returns:
        VaultClient instance
    """
    if vault is None:
        from .vault import get_vault
        vault = get_vault(VaultConfig())
    
    return VaultClient(vault)
