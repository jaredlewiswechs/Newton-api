#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON CLI VERIFIER
Standalone CLI tool for verification and Merkle proof verification.

Part of Glass Box activation - enables external verification of Newton proofs
without requiring access to the main API.
═══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import json
import sys
import hashlib
from typing import Dict, Any, List


def verify_merkle_proof(
    entry_hash: str,
    proof_path: List[Dict[str, str]],
    merkle_root: str
) -> bool:
    """
    Verify a Merkle proof.
    
    Args:
        entry_hash: Hash of the entry
        proof_path: Path from entry to root
        merkle_root: Expected Merkle root
    
    Returns:
        True if proof is valid
    """
    current_hash = entry_hash
    
    print(f"Starting verification:")
    print(f"  Entry hash: {entry_hash}")
    print(f"  Target root: {merkle_root}")
    print(f"  Proof steps: {len(proof_path)}")
    print()
    
    for i, step in enumerate(proof_path):
        sibling = step.get("hash", "")
        direction = step.get("direction", "left")
        
        print(f"  Step {i + 1}:")
        print(f"    Current: {current_hash}")
        print(f"    Sibling: {sibling}")
        print(f"    Direction: {direction}")
        
        if direction == "left":
            combined = sibling + current_hash
        else:
            combined = current_hash + sibling
        
        current_hash = hashlib.sha256(combined.encode()).hexdigest()
        print(f"    Result: {current_hash}")
        print()
    
    valid = current_hash == merkle_root
    print(f"Final result: {current_hash}")
    print(f"Expected root: {merkle_root}")
    print(f"Verification: {'✓ VALID' if valid else '✗ INVALID'}")
    
    return valid


def verify_certificate(certificate_path: str) -> bool:
    """
    Verify a certificate file.
    
    Args:
        certificate_path: Path to certificate JSON file
    
    Returns:
        True if certificate is valid
    """
    try:
        with open(certificate_path, 'r') as f:
            data = json.load(f)
        
        print("=" * 60)
        print("NEWTON CERTIFICATE VERIFIER")
        print("=" * 60)
        print()
        
        # Extract certificate data
        cert = data.get("certificate", {})
        proof = data.get("proof", {})
        
        print(f"Certificate Type: {cert.get('type')}")
        print(f"Version: {cert.get('version')}")
        print(f"Entry Index: {cert.get('entry_index')}")
        print(f"Entry Hash: {cert.get('entry_hash')}")
        print(f"Merkle Root: {cert.get('merkle_root')}")
        print(f"Generated At: {cert.get('generated_at')}")
        print()
        
        # Verify the proof
        entry_hash = cert.get("entry_hash")
        merkle_root = cert.get("merkle_root")
        proof_path = proof.get("path", [])
        
        if not entry_hash or not merkle_root:
            print("✗ Invalid certificate: missing required fields")
            return False
        
        valid = verify_merkle_proof(entry_hash, proof_path, merkle_root)
        
        print()
        print("=" * 60)
        return valid
        
    except FileNotFoundError:
        print(f"Error: Certificate file not found: {certificate_path}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in certificate file")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def verify_inline_proof(
    entry_hash: str,
    merkle_root: str,
    proof_json: str
) -> bool:
    """
    Verify a proof provided as JSON string.
    
    Args:
        entry_hash: Hash of the entry
        merkle_root: Expected Merkle root
        proof_json: JSON string containing proof path
    
    Returns:
        True if proof is valid
    """
    try:
        proof_path = json.loads(proof_json)
        
        print("=" * 60)
        print("NEWTON INLINE PROOF VERIFIER")
        print("=" * 60)
        print()
        
        return verify_merkle_proof(entry_hash, proof_path, merkle_root)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON in proof")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Newton CLI Verifier - Verify Merkle proofs and certificates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify a certificate file
  python cli_verifier.py --certificate proof.json
  
  # Verify inline proof
  python cli_verifier.py --entry-hash abc123... --merkle-root def456... --proof '[...]'
  
  # Export certificate from API and verify
  curl http://localhost:8000/merkle/proof/0 > proof.json
  python cli_verifier.py --certificate proof.json
        """
    )
    
    parser.add_argument(
        "--certificate",
        "-c",
        help="Path to certificate JSON file"
    )
    
    parser.add_argument(
        "--entry-hash",
        help="Entry hash for inline verification"
    )
    
    parser.add_argument(
        "--merkle-root",
        help="Expected Merkle root for inline verification"
    )
    
    parser.add_argument(
        "--proof",
        help="Proof path as JSON string for inline verification"
    )
    
    args = parser.parse_args()
    
    # Certificate verification
    if args.certificate:
        valid = verify_certificate(args.certificate)
        sys.exit(0 if valid else 1)
    
    # Inline verification
    elif args.entry_hash and args.merkle_root and args.proof:
        valid = verify_inline_proof(args.entry_hash, args.merkle_root, args.proof)
        sys.exit(0 if valid else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
