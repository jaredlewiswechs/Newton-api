"""
═══════════════════════════════════════════════════════════════════════════════
GUMROAD INTEGRATION FOR NEWTON SUPERCOMPUTER
Multi-Product Revenue Engine

Products:
1. Teacher's Aide Pro ($9/month) - AI lesson planning for K-8 teachers
2. Newton API Access ($19-49 one-time) - Verified computation for developers
3. AI Safety Shield ($29-99/month) - Real-time AI output verification

This module handles:
- License key verification via Gumroad API
- Multi-product tier management
- Webhook processing for purchases/refunds
- API key generation with tier-based permissions
- Usage tracking and limits
- Feedback collection

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
from typing import Dict, List, Optional, Any
from enum import Enum
import requests


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

class ProductTier(Enum):
    """Product tiers with different capabilities."""
    # Teacher's Aide
    TEACHER_AIDE_PRO = "teacher_aide_pro"

    # Newton API
    API_STARTER = "api_starter"
    API_PRO = "api_pro"

    # AI Safety Shield
    SAFETY_STARTUP = "safety_startup"
    SAFETY_SCALE = "safety_scale"
    SAFETY_ENTERPRISE = "safety_enterprise"

    # Legacy/Test
    LEGACY_BETA = "legacy_beta"
    TEST = "test"


@dataclass
class ProductConfig:
    """Configuration for a specific product tier."""
    tier: ProductTier
    name: str
    price_cents: int
    is_recurring: bool
    monthly_verifications: int  # -1 = unlimited
    features: List[str]
    endpoints: List[str]  # Allowed API endpoint patterns


# Product catalog - the money makers
PRODUCT_CATALOG: Dict[str, ProductConfig] = {
    # Teacher's Aide Pro - $9/month
    "teacher_aide_pro": ProductConfig(
        tier=ProductTier.TEACHER_AIDE_PRO,
        name="Teacher's Aide Pro",
        price_cents=900,
        is_recurring=True,
        monthly_verifications=50000,
        features=[
            "TEKS-aligned lesson generation",
            "Auto-differentiation (4 tiers)",
            "Assessment analysis with MAD",
            "PLC report generation",
            "Student grouping",
            "50-minute NES lesson structure"
        ],
        endpoints=[
            "/education/*",
            "/teachers/*",
            "/ask",
            "/statistics"
        ]
    ),

    # Newton API Starter - $19 one-time
    "api_starter": ProductConfig(
        tier=ProductTier.API_STARTER,
        name="Newton API Starter",
        price_cents=1900,
        is_recurring=False,
        monthly_verifications=10000,
        features=[
            "Full verification pipeline",
            "Constraint evaluation (CDL 3.0)",
            "Content safety checking",
            "Basic audit trail",
            "Personal/non-commercial use"
        ],
        endpoints=[
            "/ask",
            "/verify",
            "/calculate",
            "/constraint",
            "/ground",
            "/statistics"
        ]
    ),

    # Newton API Pro - $49 one-time
    "api_pro": ProductConfig(
        tier=ProductTier.API_PRO,
        name="Newton API Pro",
        price_cents=4900,
        is_recurring=False,
        monthly_verifications=-1,  # Unlimited
        features=[
            "Everything in Starter",
            "Unlimited verifications",
            "Vault encrypted storage",
            "Full Ledger access",
            "Glass Box transparency",
            "Commercial use license",
            "Priority support"
        ],
        endpoints=[
            "/ask",
            "/verify",
            "/verify/batch",
            "/calculate",
            "/constraint",
            "/ground",
            "/statistics",
            "/vault/*",
            "/ledger/*",
            "/policy/*",
            "/negotiator/*",
            "/merkle/*",
            "/cartridge/*"
        ]
    ),

    # AI Safety Shield Startup - $29/month
    "safety_startup": ProductConfig(
        tier=ProductTier.SAFETY_STARTUP,
        name="AI Safety Shield - Startup",
        price_cents=2900,
        is_recurring=True,
        monthly_verifications=50000,
        features=[
            "Real-time content verification",
            "Harm detection",
            "Medical/legal/financial safety",
            "Audit trail",
            "Email support"
        ],
        endpoints=[
            "/verify",
            "/verify/batch",
            "/ask",
            "/ledger",
            "/ledger/*"
        ]
    ),

    # AI Safety Shield Scale - $99/month
    "safety_scale": ProductConfig(
        tier=ProductTier.SAFETY_SCALE,
        name="AI Safety Shield - Scale",
        price_cents=9900,
        is_recurring=True,
        monthly_verifications=500000,
        features=[
            "Everything in Startup",
            "Custom policies",
            "Webhook alerts",
            "Priority support",
            "SLA guarantee"
        ],
        endpoints=[
            "/verify",
            "/verify/batch",
            "/ask",
            "/ledger",
            "/ledger/*",
            "/policy/*",
            "/negotiator/*"
        ]
    ),

    # AI Safety Shield Enterprise - Custom
    "safety_enterprise": ProductConfig(
        tier=ProductTier.SAFETY_ENTERPRISE,
        name="AI Safety Shield - Enterprise",
        price_cents=49900,  # Starting price
        is_recurring=True,
        monthly_verifications=-1,  # Unlimited
        features=[
            "Everything in Scale",
            "Unlimited verifications",
            "On-premise deployment option",
            "Dedicated support",
            "Custom integration",
            "Custom SLA"
        ],
        endpoints=["*"]  # All endpoints
    ),

    # Legacy beta tier (grandfather existing users)
    "legacy_beta": ProductConfig(
        tier=ProductTier.LEGACY_BETA,
        name="Newton Beta Access",
        price_cents=500,
        is_recurring=False,
        monthly_verifications=10000,
        features=["Full API access (beta)"],
        endpoints=["*"]
    ),

    # Test tier for development
    "test": ProductConfig(
        tier=ProductTier.TEST,
        name="Test Access",
        price_cents=0,
        is_recurring=False,
        monthly_verifications=1000,
        features=["Development testing"],
        endpoints=["*"]
    )
}


def get_product_config(product_name: str) -> ProductConfig:
    """Get product config by Gumroad product name."""
    # Map Gumroad product names to our config keys
    name_mapping = {
        "Teacher's Aide Pro": "teacher_aide_pro",
        "Newton API Starter": "api_starter",
        "Newton API Pro": "api_pro",
        "Newton API — Verified Computation for Developers": "api_starter",
        "AI Safety Shield - Startup": "safety_startup",
        "AI Safety Shield - Scale": "safety_scale",
        "AI Safety Shield - Enterprise": "safety_enterprise",
        "AI Safety Shield — Real-Time AI Output Verification": "safety_startup",
        "Newton Supercomputer Access": "legacy_beta",
        "Newton Supercomputer Access (TEST)": "test",
    }

    config_key = name_mapping.get(product_name, "legacy_beta")
    return PRODUCT_CATALOG.get(config_key, PRODUCT_CATALOG["legacy_beta"])


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

    # Multiple products support
    teacher_aide_product_id: str = field(default_factory=lambda: os.getenv("GUMROAD_TEACHER_AIDE_ID", ""))
    api_starter_product_id: str = field(default_factory=lambda: os.getenv("GUMROAD_API_STARTER_ID", ""))
    api_pro_product_id: str = field(default_factory=lambda: os.getenv("GUMROAD_API_PRO_ID", ""))
    safety_startup_product_id: str = field(default_factory=lambda: os.getenv("GUMROAD_SAFETY_STARTUP_ID", ""))
    safety_scale_product_id: str = field(default_factory=lambda: os.getenv("GUMROAD_SAFETY_SCALE_ID", ""))

    # API settings
    verify_url: str = "https://api.gumroad.com/v2/licenses/verify"

    # Rate limiting
    max_requests_per_minute: int = 60

    # Key settings
    key_prefix: str = "newton_"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Customer:
    """A Newton customer with tier-based access."""
    email: str
    license_key: str
    api_key: str
    purchase_date: str
    uses: int = 0
    active: bool = True
    sale_id: Optional[str] = None
    product_name: Optional[str] = None
    tier: str = "legacy_beta"  # Product tier key
    monthly_usage: int = 0  # Current month's verification count
    usage_reset_date: str = ""  # When to reset monthly usage

    def to_dict(self) -> Dict[str, Any]:
        config = PRODUCT_CATALOG.get(self.tier, PRODUCT_CATALOG["legacy_beta"])
        return {
            "email": self.email,
            "license_key": self.license_key[-8:] + "...",  # Masked
            "api_key": self.api_key[:12] + "...",  # Masked
            "purchase_date": self.purchase_date,
            "uses": self.uses,
            "active": self.active,
            "product_name": self.product_name,
            "tier": self.tier,
            "tier_name": config.name,
            "monthly_limit": config.monthly_verifications,
            "monthly_usage": self.monthly_usage,
            "features": config.features
        }

    def check_usage_limit(self) -> bool:
        """Check if customer is within their usage limit."""
        config = PRODUCT_CATALOG.get(self.tier, PRODUCT_CATALOG["legacy_beta"])
        if config.monthly_verifications == -1:  # Unlimited
            return True
        return self.monthly_usage < config.monthly_verifications

    def increment_usage(self) -> bool:
        """Increment usage counter. Returns False if limit exceeded."""
        # Reset monthly usage if needed
        if self.usage_reset_date:
            reset_date = datetime.fromisoformat(self.usage_reset_date)
            if datetime.now() >= reset_date:
                self.monthly_usage = 0
                self.usage_reset_date = (datetime.now() + timedelta(days=30)).isoformat()

        if not self.check_usage_limit():
            return False

        self.uses += 1
        self.monthly_usage += 1
        return True

    def can_access_endpoint(self, endpoint: str) -> bool:
        """Check if customer's tier allows access to an endpoint."""
        import fnmatch
        config = PRODUCT_CATALOG.get(self.tier, PRODUCT_CATALOG["legacy_beta"])
        for pattern in config.endpoints:
            if pattern == "*" or fnmatch.fnmatch(endpoint, pattern):
                return True
        return False


@dataclass
class Feedback:
    """Customer feedback."""
    id: str
    email: str
    message: str
    rating: Optional[int]  # 1-5 stars
    category: str  # bug, feature, general, praise
    timestamp: str
    api_key: Optional[str] = None  # Optional - allow anonymous feedback

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email if self.api_key else "anonymous",
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
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# GUMROAD SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class GumroadService:
    """
    Gumroad integration service for Newton Supercomputer.

    Handles license verification, customer management, and feedback collection.
    """

    def __init__(self, config: Optional[GumroadConfig] = None):
        self.config = config or GumroadConfig()

        # In-memory storage (use database in production)
        self._customers: Dict[str, Customer] = {}  # api_key -> Customer
        self._customers_by_license: Dict[str, str] = {}  # license_key -> api_key
        self._customers_by_email: Dict[str, str] = {}  # email -> api_key
        self._feedback: List[Feedback] = []

        # Rate limiting
        self._request_times: List[float] = []

        # Stats
        self._stats = {
            "total_purchases": 0,
            "total_verifications": 0,
            "failed_verifications": 0,
            "total_feedback": 0,
            "total_api_calls": 0
        }

    # ─────────────────────────────────────────────────────────────────────────
    # LICENSE VERIFICATION
    # ─────────────────────────────────────────────────────────────────────────

    def verify_license(self, license_key: str, increment_uses: bool = True) -> LicenseVerification:
        """
        Verify a Gumroad license key.

        Args:
            license_key: The license key from Gumroad purchase
            increment_uses: Whether to increment the use count

        Returns:
            LicenseVerification with result
        """
        self._stats["total_verifications"] += 1

        # Check if we have this license cached
        if license_key in self._customers_by_license:
            api_key = self._customers_by_license[license_key]
            customer = self._customers.get(api_key)
            if customer and customer.active:
                if increment_uses:
                    customer.uses += 1
                return LicenseVerification(
                    valid=True,
                    email=customer.email,
                    uses=customer.uses,
                    purchase_date=customer.purchase_date,
                    product_name=customer.product_name
                )

        # Verify with Gumroad API
        if not self.config.product_id or not self.config.access_token:
            # Development mode - accept any license for testing
            if license_key.startswith("TEST_") or license_key.startswith("test_"):
                return self._create_test_customer(license_key)

            self._stats["failed_verifications"] += 1
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

                    return LicenseVerification(
                        valid=True,
                        email=customer.email,
                        uses=purchase.get("uses", 1),
                        purchase_date=purchase.get("created_at", datetime.now().isoformat()),
                        product_name=customer.product_name
                    )

            self._stats["failed_verifications"] += 1
            return LicenseVerification(
                valid=False,
                error="Invalid license key"
            )

        except requests.RequestException as e:
            self._stats["failed_verifications"] += 1
            return LicenseVerification(
                valid=False,
                error=f"Could not verify license: {str(e)}"
            )

    def _create_test_customer(self, license_key: str) -> LicenseVerification:
        """Create a test customer for development."""
        email = f"test_{license_key[-6:]}@newton.test"
        customer = self._register_customer(
            email=email,
            license_key=license_key,
            product_name="Newton Supercomputer Access (TEST)"
        )
        return LicenseVerification(
            valid=True,
            email=customer.email,
            uses=1,
            purchase_date=customer.purchase_date,
            product_name=customer.product_name
        )

    # ─────────────────────────────────────────────────────────────────────────
    # CUSTOMER MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def _register_customer(
        self,
        email: str,
        license_key: str,
        sale_id: Optional[str] = None,
        product_name: Optional[str] = None
    ) -> Customer:
        """Register a new customer or return existing one."""

        # Check if already registered
        if license_key in self._customers_by_license:
            api_key = self._customers_by_license[license_key]
            return self._customers[api_key]

        # Generate new API key
        api_key = self._generate_api_key()

        # Determine tier from product name
        product_config = get_product_config(product_name or "Newton Supercomputer Access")

        customer = Customer(
            email=email,
            license_key=license_key,
            api_key=api_key,
            purchase_date=datetime.now().isoformat(),
            sale_id=sale_id,
            product_name=product_name or "Newton Supercomputer Access",
            tier=product_config.tier.value,
            monthly_usage=0,
            usage_reset_date=(datetime.now() + timedelta(days=30)).isoformat()
        )

        # Store customer
        self._customers[api_key] = customer
        self._customers_by_license[license_key] = api_key
        self._customers_by_email[email] = api_key

        self._stats["total_purchases"] += 1

        return customer

    def _generate_api_key(self) -> str:
        """Generate a secure API key."""
        random_part = secrets.token_urlsafe(32)
        return f"{self.config.key_prefix}{random_part}"

    def get_customer_by_api_key(self, api_key: str) -> Optional[Customer]:
        """Get customer by API key."""
        return self._customers.get(api_key)

    def validate_api_key(self, api_key: str) -> bool:
        """Check if an API key is valid and active."""
        customer = self._customers.get(api_key)
        if customer and customer.active:
            customer.uses += 1
            self._stats["total_api_calls"] += 1
            return True
        return False

    def get_api_key_for_license(self, license_key: str) -> Optional[str]:
        """Get the API key associated with a license."""
        return self._customers_by_license.get(license_key)

    # ─────────────────────────────────────────────────────────────────────────
    # WEBHOOK HANDLING
    # ─────────────────────────────────────────────────────────────────────────

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Gumroad webhook signature.

        Args:
            payload: Raw request body
            signature: The X-Gumroad-Signature header

        Returns:
            True if signature is valid
        """
        if not self.config.webhook_secret:
            # No secret configured - accept in dev mode
            return True

        expected = hmac.new(
            self.config.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def process_webhook(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Gumroad webhook event.

        Supported events:
        - sale: New purchase
        - refund: Refund processed
        - dispute: Dispute opened
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

        return {
            "processed": True,
            "event": "sale",
            "customer_email": email,
            "api_key": customer.api_key,
            "message": f"Welcome to Newton! Your API key has been generated."
        }

    def _handle_refund(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refund webhook - deactivate customer."""
        email = data.get("email", "")

        if email in self._customers_by_email:
            api_key = self._customers_by_email[email]
            customer = self._customers.get(api_key)
            if customer:
                customer.active = False
                return {
                    "processed": True,
                    "event": "refund",
                    "customer_email": email,
                    "message": "Customer access deactivated due to refund"
                }

        return {"processed": True, "event": "refund", "message": "No matching customer found"}

    def _handle_dispute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dispute webhook - temporarily suspend access."""
        email = data.get("email", "")

        if email in self._customers_by_email:
            api_key = self._customers_by_email[email]
            customer = self._customers.get(api_key)
            if customer:
                customer.active = False
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

        if email in self._customers_by_email:
            api_key = self._customers_by_email[email]
            customer = self._customers.get(api_key)
            if customer:
                customer.active = True
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
            api_key=api_key
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
            "feedback_count": len(self._feedback)
        }

    def get_pricing_info(self) -> Dict[str, Any]:
        """Get current pricing information for all products."""
        products = []
        for key, config in PRODUCT_CATALOG.items():
            if key in ["test", "legacy_beta"]:
                continue  # Skip internal tiers
            products.append({
                "id": key,
                "name": config.name,
                "price": f"${config.price_cents / 100:.2f}",
                "price_cents": config.price_cents,
                "currency": "USD",
                "type": "recurring" if config.is_recurring else "one-time",
                "monthly_verifications": config.monthly_verifications if config.monthly_verifications > 0 else "unlimited",
                "features": config.features,
                "endpoints": config.endpoints
            })

        return {
            "products": products,
            "categories": {
                "education": {
                    "name": "Teacher's Aide Pro",
                    "description": "AI lesson planning for K-8 teachers",
                    "starting_price": "$9/month",
                    "products": ["teacher_aide_pro"]
                },
                "developers": {
                    "name": "Newton API",
                    "description": "Verified computation for developers",
                    "starting_price": "$19 one-time",
                    "products": ["api_starter", "api_pro"]
                },
                "ai_safety": {
                    "name": "AI Safety Shield",
                    "description": "Real-time AI output verification",
                    "starting_price": "$29/month",
                    "products": ["safety_startup", "safety_scale", "safety_enterprise"]
                }
            },
            "guarantee": "30-day money-back guarantee on all products",
            "support": "Email support included with all tiers"
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
