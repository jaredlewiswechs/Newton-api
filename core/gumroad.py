"""
═══════════════════════════════════════════════════════════════════════════════
GUMROAD INTEGRATION FOR NEWTON SUPERCOMPUTER
Access to the Newton Supercomputer - $5 during testing

This module handles:
- License key verification via Gumroad API (with rate limiting)
- Webhook processing for new purchases (with signature verification)
- API key generation and lifecycle management
- Feedback collection from users
- Security audit logging

© 2025-2026 Jared Lewis · Ada Computing Company · Houston, Texas
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import hmac
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import requests


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GumroadConfig:
    """Configuration for Gumroad integration."""
    # Set these via environment variables
    product_id: str = field(default_factory=lambda: os.getenv("GUMROAD_PRODUCT_ID", ""))
    access_token: str = field(default_factory=lambda: os.getenv("GUMROAD_ACCESS_TOKEN", ""))
    webhook_secret: str = field(default_factory=lambda: os.getenv("GUMROAD_WEBHOOK_SECRET", ""))

    # Product pricing (in cents)
    price_cents: int = 500  # $5.00 during testing

    # API settings
    verify_url: str = "https://api.gumroad.com/v2/licenses/verify"

    # Rate limiting - per IP
    max_verify_attempts_per_minute: int = 10  # Prevent brute force
    max_verify_attempts_per_hour: int = 30
    lockout_duration_minutes: int = 15

    # API key settings
    key_prefix: str = "newton_"
    key_expiry_days: int = 365  # Keys expire after 1 year (renewable)
    max_keys_per_license: int = 3  # Multiple keys for different projects


# ═══════════════════════════════════════════════════════════════════════════════
# SECURITY AUDIT LOG
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SecurityEvent:
    """A security-relevant event for audit logging."""
    timestamp: str
    event_type: str  # verify_attempt, verify_success, verify_fail, rate_limit, key_revoked, etc.
    ip_address: Optional[str]
    license_key_hash: Optional[str]  # SHA256 hash, not the actual key
    api_key_prefix: Optional[str]  # First 12 chars only
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "ip_address": self.ip_address,
            "license_key_hash": self.license_key_hash,
            "api_key_prefix": self.api_key_prefix,
            "details": self.details
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class APIKey:
    """An API key with lifecycle management."""
    key: str
    created_at: str
    expires_at: str
    active: bool = True
    name: Optional[str] = None  # e.g., "Production", "Development"
    last_used: Optional[str] = None
    use_count: int = 0

    def is_expired(self) -> bool:
        return datetime.fromisoformat(self.expires_at) < datetime.now()

    def is_valid(self) -> bool:
        return self.active and not self.is_expired()

    def to_dict(self, mask: bool = True) -> Dict[str, Any]:
        return {
            "key": self.key[:16] + "..." if mask else self.key,
            "name": self.name,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "active": self.active,
            "is_valid": self.is_valid(),
            "last_used": self.last_used,
            "use_count": self.use_count
        }


@dataclass
class Customer:
    """A Newton customer with full key management."""
    email: str
    license_key_hash: str  # Store hash, not actual key
    purchase_date: str
    api_keys: List[APIKey] = field(default_factory=list)
    active: bool = True
    sale_id: Optional[str] = None
    product_name: Optional[str] = None
    total_uses: int = 0

    def get_active_keys(self) -> List[APIKey]:
        return [k for k in self.api_keys if k.is_valid()]

    def get_primary_key(self) -> Optional[APIKey]:
        active = self.get_active_keys()
        return active[0] if active else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "purchase_date": self.purchase_date,
            "active": self.active,
            "product_name": self.product_name,
            "api_keys": [k.to_dict() for k in self.api_keys],
            "active_key_count": len(self.get_active_keys()),
            "total_uses": self.total_uses
        }


@dataclass
class Feedback:
    """Customer feedback."""
    id: str
    email: str
    message: str
    rating: Optional[int]  # 1-5 stars
    category: str  # bug, feature, general, praise
    timestamp: str
    api_key_prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email if self.api_key_prefix else "anonymous",
            "message": self.message,
            "rating": self.rating,
            "category": self.category,
            "timestamp": self.timestamp
        }


@dataclass
class LicenseVerification:
    """Result of license verification."""
    valid: bool
    email: Optional[str] = None
    uses: int = 0
    purchase_date: Optional[str] = None
    error: Optional[str] = None
    product_name: Optional[str] = None
    rate_limited: bool = False
    retry_after_seconds: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"valid": self.valid}
        if self.valid:
            result.update({
                "email": self.email,
                "uses": self.uses,
                "purchase_date": self.purchase_date,
                "product_name": self.product_name
            })
        else:
            result["error"] = self.error
            if self.rate_limited:
                result["rate_limited"] = True
                result["retry_after_seconds"] = self.retry_after_seconds
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITER
# ═══════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """
    Per-IP rate limiting for license verification.

    Prevents brute force attacks on license keys.
    """

    def __init__(self, config: GumroadConfig):
        self.config = config
        # IP -> list of (timestamp, success) tuples
        self._attempts: Dict[str, List[Tuple[float, bool]]] = defaultdict(list)
        # IP -> lockout expiry timestamp
        self._lockouts: Dict[str, float] = {}

    def _cleanup_old_attempts(self, ip: str) -> None:
        """Remove attempts older than 1 hour."""
        now = time.time()
        hour_ago = now - 3600
        self._attempts[ip] = [
            (ts, success) for ts, success in self._attempts[ip]
            if ts > hour_ago
        ]

    def check_rate_limit(self, ip: str) -> Tuple[bool, Optional[int]]:
        """
        Check if IP is rate limited.

        Returns:
            (allowed, retry_after_seconds)
        """
        now = time.time()

        # Check lockout
        if ip in self._lockouts:
            if now < self._lockouts[ip]:
                retry_after = int(self._lockouts[ip] - now)
                return False, retry_after
            else:
                del self._lockouts[ip]

        self._cleanup_old_attempts(ip)
        attempts = self._attempts[ip]

        # Check per-minute limit
        minute_ago = now - 60
        recent_attempts = [ts for ts, _ in attempts if ts > minute_ago]
        if len(recent_attempts) >= self.config.max_verify_attempts_per_minute:
            return False, 60

        # Check per-hour limit
        hour_attempts = len(attempts)
        if hour_attempts >= self.config.max_verify_attempts_per_hour:
            # Lockout for configured duration
            lockout_until = now + (self.config.lockout_duration_minutes * 60)
            self._lockouts[ip] = lockout_until
            return False, self.config.lockout_duration_minutes * 60

        return True, None

    def record_attempt(self, ip: str, success: bool) -> None:
        """Record a verification attempt."""
        self._attempts[ip].append((time.time(), success))

        # If too many failures in a row, trigger lockout
        recent = self._attempts[ip][-5:]
        if len(recent) >= 5 and all(not s for _, s in recent):
            lockout_until = time.time() + (self.config.lockout_duration_minutes * 60)
            self._lockouts[ip] = lockout_until


# ═══════════════════════════════════════════════════════════════════════════════
# GUMROAD SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class GumroadService:
    """
    Gumroad integration service for Newton Supercomputer.

    Handles license verification, customer management, and feedback collection
    with proper security controls.
    """

    def __init__(self, config: Optional[GumroadConfig] = None):
        self.config = config or GumroadConfig()

        # In-memory storage (use database in production)
        self._customers: Dict[str, Customer] = {}  # license_key_hash -> Customer
        self._api_keys: Dict[str, str] = {}  # api_key -> license_key_hash
        self._feedback: List[Feedback] = []

        # Security
        self._rate_limiter = RateLimiter(self.config)
        self._security_log: List[SecurityEvent] = []

        # Stats
        self._stats = {
            "total_purchases": 0,
            "total_verifications": 0,
            "failed_verifications": 0,
            "rate_limited_requests": 0,
            "total_feedback": 0,
            "total_api_calls": 0,
            "keys_regenerated": 0,
            "keys_revoked": 0
        }

    def _hash_license_key(self, license_key: str) -> str:
        """Hash a license key for secure storage."""
        return hashlib.sha256(license_key.encode()).hexdigest()

    def _log_security_event(
        self,
        event_type: str,
        ip_address: Optional[str] = None,
        license_key: Optional[str] = None,
        api_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a security event."""
        event = SecurityEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            ip_address=ip_address,
            license_key_hash=self._hash_license_key(license_key)[:16] if license_key else None,
            api_key_prefix=api_key[:12] if api_key else None,
            details=details or {}
        )
        self._security_log.append(event)

        # Keep only last 10000 events
        if len(self._security_log) > 10000:
            self._security_log = self._security_log[-10000:]

    # ─────────────────────────────────────────────────────────────────────────
    # LICENSE VERIFICATION
    # ─────────────────────────────────────────────────────────────────────────

    def verify_license(
        self,
        license_key: str,
        ip_address: Optional[str] = None,
        increment_uses: bool = True
    ) -> LicenseVerification:
        """
        Verify a Gumroad license key with rate limiting and security logging.

        Args:
            license_key: The license key from Gumroad purchase
            ip_address: Client IP for rate limiting
            increment_uses: Whether to increment the use count

        Returns:
            LicenseVerification with result
        """
        self._stats["total_verifications"] += 1
        ip = ip_address or "unknown"

        # Check rate limit
        allowed, retry_after = self._rate_limiter.check_rate_limit(ip)
        if not allowed:
            self._stats["rate_limited_requests"] += 1
            self._log_security_event(
                "rate_limit",
                ip_address=ip,
                license_key=license_key,
                details={"retry_after": retry_after}
            )
            return LicenseVerification(
                valid=False,
                error="Too many verification attempts. Please try again later.",
                rate_limited=True,
                retry_after_seconds=retry_after
            )

        license_hash = self._hash_license_key(license_key)

        # Check if we have this license cached
        if license_hash in self._customers:
            customer = self._customers[license_hash]
            if customer.active:
                primary_key = customer.get_primary_key()
                if primary_key:
                    if increment_uses:
                        customer.total_uses += 1
                        primary_key.use_count += 1
                        primary_key.last_used = datetime.now().isoformat()

                    self._rate_limiter.record_attempt(ip, True)
                    self._log_security_event(
                        "verify_success_cached",
                        ip_address=ip,
                        license_key=license_key,
                        api_key=primary_key.key
                    )

                    return LicenseVerification(
                        valid=True,
                        email=customer.email,
                        uses=customer.total_uses,
                        purchase_date=customer.purchase_date,
                        product_name=customer.product_name
                    )

        # Verify with Gumroad API
        if not self.config.product_id or not self.config.access_token:
            # Development mode - accept test licenses
            if license_key.startswith("TEST_") or license_key.startswith("test_"):
                result = self._create_test_customer(license_key, ip)
                self._rate_limiter.record_attempt(ip, True)
                return result

            self._stats["failed_verifications"] += 1
            self._rate_limiter.record_attempt(ip, False)
            self._log_security_event(
                "verify_fail_not_configured",
                ip_address=ip,
                license_key=license_key
            )
            return LicenseVerification(
                valid=False,
                error="Gumroad not configured. Set GUMROAD_PRODUCT_ID and GUMROAD_ACCESS_TOKEN."
            )

        try:
            response = requests.post(
                self.config.verify_url,
                data={
                    "product_id": self.config.product_id,
                    "license_key": license_key,
                    "increment_uses_count": str(increment_uses).lower()
                },
                headers={"Authorization": f"Bearer {self.config.access_token}"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    purchase = data.get("purchase", {})

                    # Create/update customer
                    customer = self._register_customer(
                        email=purchase.get("email", "unknown@email.com"),
                        license_key=license_key,
                        sale_id=purchase.get("sale_id"),
                        product_name=purchase.get("product_name", "Newton Supercomputer Access")
                    )

                    self._rate_limiter.record_attempt(ip, True)
                    self._log_security_event(
                        "verify_success_gumroad",
                        ip_address=ip,
                        license_key=license_key,
                        details={"email": customer.email}
                    )

                    return LicenseVerification(
                        valid=True,
                        email=customer.email,
                        uses=purchase.get("uses", 1),
                        purchase_date=purchase.get("created_at", datetime.now().isoformat()),
                        product_name=customer.product_name
                    )

            self._stats["failed_verifications"] += 1
            self._rate_limiter.record_attempt(ip, False)
            self._log_security_event(
                "verify_fail_invalid",
                ip_address=ip,
                license_key=license_key,
                details={"status_code": response.status_code}
            )
            return LicenseVerification(
                valid=False,
                error="Invalid license key"
            )

        except requests.RequestException as e:
            self._stats["failed_verifications"] += 1
            self._rate_limiter.record_attempt(ip, False)
            self._log_security_event(
                "verify_fail_error",
                ip_address=ip,
                license_key=license_key,
                details={"error": str(e)}
            )
            return LicenseVerification(
                valid=False,
                error=f"Could not verify license: {str(e)}"
            )

    def _create_test_customer(self, license_key: str, ip: str) -> LicenseVerification:
        """Create a test customer for development."""
        email = f"test_{license_key[-6:]}@newton.test"
        customer = self._register_customer(
            email=email,
            license_key=license_key,
            product_name="Newton Supercomputer Access (TEST)"
        )
        self._log_security_event(
            "verify_success_test",
            ip_address=ip,
            license_key=license_key,
            details={"email": email}
        )
        return LicenseVerification(
            valid=True,
            email=customer.email,
            uses=1,
            purchase_date=customer.purchase_date,
            product_name=customer.product_name
        )

    # ─────────────────────────────────────────────────────────────────────────
    # CUSTOMER & API KEY MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def _register_customer(
        self,
        email: str,
        license_key: str,
        sale_id: Optional[str] = None,
        product_name: Optional[str] = None
    ) -> Customer:
        """Register a new customer or return existing one."""
        license_hash = self._hash_license_key(license_key)

        # Check if already registered
        if license_hash in self._customers:
            return self._customers[license_hash]

        # Generate primary API key
        api_key = self._generate_api_key()
        now = datetime.now()

        key_obj = APIKey(
            key=api_key,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(days=self.config.key_expiry_days)).isoformat(),
            name="Primary"
        )

        customer = Customer(
            email=email,
            license_key_hash=license_hash,
            purchase_date=now.isoformat(),
            api_keys=[key_obj],
            sale_id=sale_id,
            product_name=product_name or "Newton Supercomputer Access"
        )

        # Store customer and key mappings
        self._customers[license_hash] = customer
        self._api_keys[api_key] = license_hash

        self._stats["total_purchases"] += 1

        return customer

    def _generate_api_key(self) -> str:
        """Generate a secure API key."""
        random_part = secrets.token_urlsafe(32)
        return f"{self.config.key_prefix}{random_part}"

    def get_customer_by_api_key(self, api_key: str) -> Optional[Customer]:
        """Get customer by API key."""
        license_hash = self._api_keys.get(api_key)
        if license_hash:
            return self._customers.get(license_hash)
        return None

    def validate_api_key(self, api_key: str) -> bool:
        """Check if an API key is valid and active."""
        license_hash = self._api_keys.get(api_key)
        if not license_hash:
            return False

        customer = self._customers.get(license_hash)
        if not customer or not customer.active:
            return False

        # Find and validate the specific key
        for key_obj in customer.api_keys:
            if key_obj.key == api_key:
                if key_obj.is_valid():
                    key_obj.use_count += 1
                    key_obj.last_used = datetime.now().isoformat()
                    customer.total_uses += 1
                    self._stats["total_api_calls"] += 1
                    return True
                return False

        return False

    def get_api_key_for_license(self, license_key: str) -> Optional[str]:
        """Get the primary API key associated with a license."""
        license_hash = self._hash_license_key(license_key)
        customer = self._customers.get(license_hash)
        if customer:
            primary = customer.get_primary_key()
            return primary.key if primary else None
        return None

    def regenerate_api_key(
        self,
        license_key: str,
        key_name: Optional[str] = None
    ) -> Optional[APIKey]:
        """
        Generate a new API key for a license, optionally revoking old ones.

        Args:
            license_key: The original license key
            key_name: Optional name for the new key

        Returns:
            The new APIKey object, or None if license not found
        """
        license_hash = self._hash_license_key(license_key)
        customer = self._customers.get(license_hash)

        if not customer or not customer.active:
            return None

        # Check key limit
        active_keys = customer.get_active_keys()
        if len(active_keys) >= self.config.max_keys_per_license:
            # Revoke oldest key
            oldest = min(active_keys, key=lambda k: k.created_at)
            oldest.active = False
            if oldest.key in self._api_keys:
                del self._api_keys[oldest.key]
            self._stats["keys_revoked"] += 1

        # Generate new key
        new_key = self._generate_api_key()
        now = datetime.now()

        key_obj = APIKey(
            key=new_key,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(days=self.config.key_expiry_days)).isoformat(),
            name=key_name or f"Key {len(customer.api_keys) + 1}"
        )

        customer.api_keys.append(key_obj)
        self._api_keys[new_key] = license_hash
        self._stats["keys_regenerated"] += 1

        self._log_security_event(
            "key_regenerated",
            license_key=license_key,
            api_key=new_key,
            details={"key_name": key_name}
        )

        return key_obj

    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key.

        Args:
            api_key: The API key to revoke

        Returns:
            True if key was found and revoked
        """
        license_hash = self._api_keys.get(api_key)
        if not license_hash:
            return False

        customer = self._customers.get(license_hash)
        if not customer:
            return False

        for key_obj in customer.api_keys:
            if key_obj.key == api_key:
                key_obj.active = False
                del self._api_keys[api_key]
                self._stats["keys_revoked"] += 1
                self._log_security_event(
                    "key_revoked",
                    api_key=api_key
                )
                return True

        return False

    def list_api_keys(self, license_key: str) -> List[Dict[str, Any]]:
        """List all API keys for a license."""
        license_hash = self._hash_license_key(license_key)
        customer = self._customers.get(license_hash)
        if customer:
            return [k.to_dict() for k in customer.api_keys]
        return []

    # ─────────────────────────────────────────────────────────────────────────
    # WEBHOOK HANDLING
    # ─────────────────────────────────────────────────────────────────────────

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Gumroad webhook signature.

        Gumroad signs webhooks using HMAC-SHA256 with your webhook secret.
        The signature is sent in the X-Gumroad-Signature header.

        Args:
            payload: Raw request body (form-encoded data)
            signature: The X-Gumroad-Signature header value

        Returns:
            True if signature is valid
        """
        if not self.config.webhook_secret:
            # No secret configured - log warning but accept in dev mode
            self._log_security_event(
                "webhook_no_secret",
                details={"warning": "Webhook secret not configured - accepting without verification"}
            )
            return True

        if not signature:
            self._log_security_event(
                "webhook_missing_signature",
                details={"error": "No signature provided"}
            )
            return False

        # Gumroad uses HMAC-SHA256
        expected = hmac.new(
            self.config.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        valid = hmac.compare_digest(expected, signature)

        if not valid:
            self._log_security_event(
                "webhook_invalid_signature",
                details={"provided": signature[:16] + "...", "expected_prefix": expected[:16] + "..."}
            )

        return valid

    def process_webhook(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Gumroad webhook event.

        Supported events:
        - sale: New purchase
        - refund: Refund processed (auto-revokes API keys)
        - dispute: Dispute opened (suspends access)
        - dispute_won: Dispute resolved in seller's favor

        Args:
            event_type: Type of webhook event
            data: Webhook payload data

        Returns:
            Processing result
        """
        handlers = {
            "sale": self._handle_sale,
            "refund": self._handle_refund,
            "dispute": self._handle_dispute,
            "dispute_won": self._handle_dispute_won
        }

        handler = handlers.get(event_type)
        if handler:
            return handler(data)

        return {"processed": False, "reason": f"Unknown event type: {event_type}"}

    def _handle_sale(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new sale webhook."""
        email = data.get("email", "")
        license_key = data.get("license_key", "")
        sale_id = data.get("sale_id", "")
        product_name = data.get("product_name", "Newton Supercomputer Access")

        if not email or not license_key:
            return {"processed": False, "error": "Missing email or license_key"}

        customer = self._register_customer(
            email=email,
            license_key=license_key,
            sale_id=sale_id,
            product_name=product_name
        )

        self._log_security_event(
            "webhook_sale",
            license_key=license_key,
            details={"email": email, "sale_id": sale_id}
        )

        primary_key = customer.get_primary_key()

        return {
            "processed": True,
            "event": "sale",
            "customer_email": email,
            "api_key": primary_key.key if primary_key else None,
            "message": "Welcome to Newton! Your API key has been generated."
        }

    def _handle_refund(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refund webhook - deactivate customer and revoke all keys."""
        email = data.get("email", "")
        license_key = data.get("license_key", "")

        if license_key:
            license_hash = self._hash_license_key(license_key)
        else:
            # Find by email
            license_hash = None
            for lh, customer in self._customers.items():
                if customer.email == email:
                    license_hash = lh
                    break

        if license_hash and license_hash in self._customers:
            customer = self._customers[license_hash]
            customer.active = False

            # Revoke all API keys
            for key_obj in customer.api_keys:
                key_obj.active = False
                if key_obj.key in self._api_keys:
                    del self._api_keys[key_obj.key]
                self._stats["keys_revoked"] += 1

            self._log_security_event(
                "webhook_refund",
                license_key=license_key if license_key else None,
                details={"email": email, "keys_revoked": len(customer.api_keys)}
            )

            return {
                "processed": True,
                "event": "refund",
                "customer_email": email,
                "keys_revoked": len(customer.api_keys),
                "message": "Customer access deactivated and all API keys revoked"
            }

        return {"processed": True, "event": "refund", "message": "No matching customer found"}

    def _handle_dispute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dispute webhook - temporarily suspend access."""
        email = data.get("email", "")
        license_key = data.get("license_key", "")

        if license_key:
            license_hash = self._hash_license_key(license_key)
            customer = self._customers.get(license_hash)
        else:
            customer = None
            for c in self._customers.values():
                if c.email == email:
                    customer = c
                    break

        if customer:
            customer.active = False
            self._log_security_event(
                "webhook_dispute",
                details={"email": email}
            )
            return {
                "processed": True,
                "event": "dispute",
                "customer_email": email,
                "message": "Customer access suspended pending dispute resolution"
            }

        return {"processed": True, "event": "dispute", "message": "No matching customer found"}

    def _handle_dispute_won(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dispute won webhook - reactivate access."""
        email = data.get("email", "")

        for customer in self._customers.values():
            if customer.email == email:
                customer.active = True
                self._log_security_event(
                    "webhook_dispute_won",
                    details={"email": email}
                )
                return {
                    "processed": True,
                    "event": "dispute_won",
                    "customer_email": email,
                    "message": "Customer access reactivated after dispute resolution"
                }

        return {"processed": True, "event": "dispute_won", "message": "No matching customer found"}

    # ─────────────────────────────────────────────────────────────────────────
    # FEEDBACK COLLECTION
    # ─────────────────────────────────────────────────────────────────────────

    def submit_feedback(
        self,
        message: str,
        email: str = "anonymous",
        rating: Optional[int] = None,
        category: str = "general",
        api_key: Optional[str] = None
    ) -> Feedback:
        """
        Submit feedback.

        Args:
            message: The feedback message
            email: Customer email (or "anonymous")
            rating: Optional 1-5 star rating
            category: bug, feature, general, or praise
            api_key: Optional API key to associate with feedback

        Returns:
            The created Feedback object
        """
        # Validate rating
        if rating is not None:
            rating = max(1, min(5, rating))

        # Validate category
        valid_categories = ["bug", "feature", "general", "praise"]
        if category not in valid_categories:
            category = "general"

        feedback = Feedback(
            id=f"FB{len(self._feedback) + 1:06d}",
            email=email,
            message=message,
            rating=rating,
            category=category,
            timestamp=datetime.now().isoformat(),
            api_key_prefix=api_key[:12] if api_key else None
        )

        self._feedback.append(feedback)
        self._stats["total_feedback"] += 1

        return feedback

    def get_feedback(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Feedback]:
        """Get feedback, optionally filtered by category."""
        feedback = self._feedback

        if category:
            feedback = [f for f in feedback if f.category == category]

        return feedback[-limit:]

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get feedback summary statistics."""
        total = len(self._feedback)
        if total == 0:
            return {
                "total": 0,
                "by_category": {},
                "average_rating": None,
                "rating_distribution": {}
            }

        by_category = {}
        ratings = []
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for f in self._feedback:
            by_category[f.category] = by_category.get(f.category, 0) + 1
            if f.rating:
                ratings.append(f.rating)
                rating_dist[f.rating] += 1

        avg_rating = sum(ratings) / len(ratings) if ratings else None

        return {
            "total": total,
            "by_category": by_category,
            "average_rating": round(avg_rating, 2) if avg_rating else None,
            "rating_distribution": rating_dist,
            "rated_count": len(ratings)
        }

    # ─────────────────────────────────────────────────────────────────────────
    # STATS & INFO
    # ─────────────────────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self._stats,
            "active_customers": sum(1 for c in self._customers.values() if c.active),
            "total_customers": len(self._customers),
            "total_api_keys": len(self._api_keys),
            "feedback_count": len(self._feedback),
            "security_events": len(self._security_log)
        }

    def get_security_log(self, limit: int = 100, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent security events."""
        events = self._security_log
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return [e.to_dict() for e in events[-limit:]]

    def get_pricing_info(self) -> Dict[str, Any]:
        """Get current pricing information with tier upgrade hints."""
        return {
            "product": "Newton Supercomputer Access",
            "current_tier": "Beta Access",
            "price": "$5.00",
            "price_cents": self.config.price_cents,
            "currency": "USD",
            "type": "one-time",
            "includes": [
                "Full API access to Newton Supercomputer",
                "Verified computation engine (Turing complete, bounded)",
                "Constraint evaluation (CDL 3.0)",
                "Content safety verification (Forge)",
                "Encrypted storage (Vault)",
                "Immutable audit trail (Ledger)",
                "Education module (TEKS-aligned)",
                "Interface Builder",
                "Up to 3 API keys per license",
                "1 year key validity (renewable)",
                "Priority support during beta"
            ],
            "limits": {
                "api_keys_per_license": self.config.max_keys_per_license,
                "key_validity_days": self.config.key_expiry_days
            },
            "upcoming_tiers": {
                "note": "Full pricing tiers coming after beta",
                "planned": [
                    {
                        "tier": "Core",
                        "price": "$299/year",
                        "for": "Individual developers and small teams"
                    },
                    {
                        "tier": "Professional",
                        "price": "$999/year",
                        "for": "Growing businesses with higher volume"
                    },
                    {
                        "tier": "Enterprise",
                        "price": "Custom",
                        "for": "Large organizations with compliance needs"
                    }
                ]
            },
            "beta_note": "Lock in beta pricing now. Early supporters get grandfather pricing when tiers launch."
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON ACCESSOR
# ═══════════════════════════════════════════════════════════════════════════════

_gumroad_service: Optional[GumroadService] = None


def get_gumroad_service(config: Optional[GumroadConfig] = None) -> GumroadService:
    """Get or create the Gumroad service singleton."""
    global _gumroad_service
    if _gumroad_service is None:
        _gumroad_service = GumroadService(config)
    return _gumroad_service
