"""
===============================================================================
NEWTON MARKETPLACE
Peer-to-Peer Newton Credit Exchange

Sell your Newton credits fast. Find buyers. Get paid.

Features:
- List credits for sale with custom pricing
- Browse available listings
- Execute trades between users
- Automatic escrow via Ledger verification
- Price discovery (see what others are charging)

2025-2026 Jared Lewis Ada Computing Company Houston, Texas
===============================================================================
"""

import secrets
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


# ==============================================================================
# LISTING TYPES
# ==============================================================================

class ListingStatus(Enum):
    """Status of a marketplace listing."""
    ACTIVE = "active"           # Available for purchase
    PENDING = "pending"         # Sale in progress
    SOLD = "sold"               # Completed sale
    CANCELLED = "cancelled"     # Seller cancelled
    EXPIRED = "expired"         # Listing expired


class ListingType(Enum):
    """Types of things you can sell."""
    CREDITS = "credits"             # Verification credits
    API_ACCESS = "api_access"       # Full API access transfer
    TIER_UPGRADE = "tier_upgrade"   # Upgrade tokens


@dataclass
class Listing:
    """A marketplace listing for Newton credits/access."""
    id: str
    seller_email: str
    seller_api_key: str
    listing_type: ListingType
    quantity: int                    # Number of credits/months
    price_cents: int                 # Price in USD cents
    description: str
    status: ListingStatus
    created_at: str
    expires_at: str
    buyer_email: Optional[str] = None
    buyer_api_key: Optional[str] = None
    sold_at: Optional[str] = None

    def to_dict(self, include_private: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        result = {
            "id": self.id,
            "seller": self.seller_email.split("@")[0] + "@...",  # Masked
            "type": self.listing_type.value,
            "quantity": self.quantity,
            "price_usd": self.price_cents / 100,
            "price_per_unit": round(self.price_cents / self.quantity / 100, 2),
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }
        if include_private:
            result["seller_email"] = self.seller_email
            result["buyer_email"] = self.buyer_email
            result["sold_at"] = self.sold_at
        return result


@dataclass
class TradeRecord:
    """Record of a completed trade."""
    id: str
    listing_id: str
    seller_email: str
    buyer_email: str
    listing_type: ListingType
    quantity: int
    price_cents: int
    executed_at: str
    ledger_hash: Optional[str] = None  # Verification hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "type": self.listing_type.value,
            "quantity": self.quantity,
            "price_usd": self.price_cents / 100,
            "executed_at": self.executed_at,
            "verified": self.ledger_hash is not None,
        }


# ==============================================================================
# MARKETPLACE SERVICE
# ==============================================================================

class NewtonMarketplace:
    """
    Peer-to-peer marketplace for Newton credits and access.

    "Bored with Newton? Sell it. Want Newton? Buy it."
    """

    def __init__(self):
        self._listings: Dict[str, Listing] = {}
        self._trades: List[TradeRecord] = []
        self._user_listings: Dict[str, List[str]] = {}  # email -> listing_ids

        # Market stats
        self._stats = {
            "total_listings": 0,
            "active_listings": 0,
            "total_trades": 0,
            "total_volume_cents": 0,
        }

    # --------------------------------------------------------------------------
    # SELLING
    # --------------------------------------------------------------------------

    def create_listing(
        self,
        seller_email: str,
        seller_api_key: str,
        listing_type: str,
        quantity: int,
        price_cents: int,
        description: str = "",
        expires_hours: int = 72,
    ) -> Dict[str, Any]:
        """
        List your Newton credits for sale.

        Args:
            seller_email: Your email
            seller_api_key: Your API key (for verification)
            listing_type: "credits", "api_access", or "tier_upgrade"
            quantity: How many credits/months to sell
            price_cents: Your asking price in cents
            description: Optional description
            expires_hours: Hours until listing expires (default 72)

        Returns:
            The created listing
        """
        # Validate listing type
        try:
            ltype = ListingType(listing_type)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid listing type. Use: {[t.value for t in ListingType]}"
            }

        # Validate quantity and price
        if quantity <= 0:
            return {"success": False, "error": "Quantity must be positive"}
        if price_cents <= 0:
            return {"success": False, "error": "Price must be positive"}

        # Generate listing ID
        listing_id = f"NWL-{secrets.token_hex(6).upper()}"

        now = datetime.now()
        listing = Listing(
            id=listing_id,
            seller_email=seller_email,
            seller_api_key=seller_api_key,
            listing_type=ltype,
            quantity=quantity,
            price_cents=price_cents,
            description=description or f"Selling {quantity} Newton {ltype.value}",
            status=ListingStatus.ACTIVE,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=expires_hours)).isoformat(),
        )

        # Store listing
        self._listings[listing_id] = listing

        if seller_email not in self._user_listings:
            self._user_listings[seller_email] = []
        self._user_listings[seller_email].append(listing_id)

        self._stats["total_listings"] += 1
        self._stats["active_listings"] += 1

        return {
            "success": True,
            "listing": listing.to_dict(),
            "message": f"Listed! Buyers can find you at listing {listing_id}",
            "share_url": f"/marketplace/{listing_id}",
        }

    def cancel_listing(self, listing_id: str, seller_api_key: str) -> Dict[str, Any]:
        """Cancel your listing."""
        listing = self._listings.get(listing_id)
        if not listing:
            return {"success": False, "error": "Listing not found"}

        if listing.seller_api_key != seller_api_key:
            return {"success": False, "error": "Not your listing"}

        if listing.status != ListingStatus.ACTIVE:
            return {"success": False, "error": f"Cannot cancel listing in {listing.status.value} status"}

        listing.status = ListingStatus.CANCELLED
        self._stats["active_listings"] -= 1

        return {
            "success": True,
            "message": "Listing cancelled",
            "listing": listing.to_dict(),
        }

    # --------------------------------------------------------------------------
    # BROWSING / DISCOVERY
    # --------------------------------------------------------------------------

    def browse_listings(
        self,
        listing_type: Optional[str] = None,
        max_price_cents: Optional[int] = None,
        min_quantity: Optional[int] = None,
        sort_by: str = "price",  # "price", "quantity", "newest"
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Browse available listings.

        Args:
            listing_type: Filter by type
            max_price_cents: Maximum price filter
            min_quantity: Minimum quantity filter
            sort_by: Sort order
            limit: Max results

        Returns:
            List of matching listings
        """
        # Expire old listings first
        self._expire_listings()

        # Filter active listings
        results = [
            l for l in self._listings.values()
            if l.status == ListingStatus.ACTIVE
        ]

        # Apply filters
        if listing_type:
            try:
                ltype = ListingType(listing_type)
                results = [l for l in results if l.listing_type == ltype]
            except ValueError:
                pass

        if max_price_cents:
            results = [l for l in results if l.price_cents <= max_price_cents]

        if min_quantity:
            results = [l for l in results if l.quantity >= min_quantity]

        # Sort
        if sort_by == "price":
            results.sort(key=lambda l: l.price_cents / l.quantity)  # Best value first
        elif sort_by == "quantity":
            results.sort(key=lambda l: -l.quantity)  # Most credits first
        elif sort_by == "newest":
            results.sort(key=lambda l: l.created_at, reverse=True)

        # Limit
        results = results[:limit]

        return {
            "success": True,
            "count": len(results),
            "listings": [l.to_dict() for l in results],
            "market_summary": self._get_market_summary(),
        }

    def get_listing(self, listing_id: str) -> Dict[str, Any]:
        """Get details of a specific listing."""
        listing = self._listings.get(listing_id)
        if not listing:
            return {"success": False, "error": "Listing not found"}

        return {
            "success": True,
            "listing": listing.to_dict(),
        }

    # --------------------------------------------------------------------------
    # BUYING
    # --------------------------------------------------------------------------

    def buy_listing(
        self,
        listing_id: str,
        buyer_email: str,
        buyer_api_key: str,
    ) -> Dict[str, Any]:
        """
        Purchase a listing.

        Note: In production, this would integrate with Stripe/payment processor.
        For now, it records the intent to buy and provides payment instructions.

        Args:
            listing_id: The listing to buy
            buyer_email: Buyer's email
            buyer_api_key: Buyer's API key

        Returns:
            Purchase confirmation or payment instructions
        """
        listing = self._listings.get(listing_id)
        if not listing:
            return {"success": False, "error": "Listing not found"}

        if listing.status != ListingStatus.ACTIVE:
            return {"success": False, "error": f"Listing is {listing.status.value}"}

        if listing.seller_email == buyer_email:
            return {"success": False, "error": "Cannot buy your own listing"}

        # Mark as pending
        listing.status = ListingStatus.PENDING
        listing.buyer_email = buyer_email
        listing.buyer_api_key = buyer_api_key

        # Generate trade ID
        trade_id = f"NWT-{secrets.token_hex(6).upper()}"

        return {
            "success": True,
            "trade_id": trade_id,
            "listing": listing.to_dict(),
            "payment": {
                "amount_usd": listing.price_cents / 100,
                "seller_contact": listing.seller_email,
                "instructions": "Contact seller to arrange payment. Once payment confirmed, seller will release credits.",
            },
            "next_steps": [
                f"1. Send ${listing.price_cents / 100:.2f} to seller",
                "2. Seller confirms payment received",
                "3. Credits transferred to your account",
            ],
        }

    def confirm_sale(
        self,
        listing_id: str,
        seller_api_key: str,
        payment_confirmed: bool = True,
    ) -> Dict[str, Any]:
        """
        Seller confirms payment and releases credits.

        Args:
            listing_id: The listing
            seller_api_key: Seller's API key
            payment_confirmed: Whether payment was received

        Returns:
            Trade completion details
        """
        listing = self._listings.get(listing_id)
        if not listing:
            return {"success": False, "error": "Listing not found"}

        if listing.seller_api_key != seller_api_key:
            return {"success": False, "error": "Not your listing"}

        if listing.status != ListingStatus.PENDING:
            return {"success": False, "error": "Listing not in pending state"}

        if not payment_confirmed:
            # Seller disputes - return to active
            listing.status = ListingStatus.ACTIVE
            listing.buyer_email = None
            listing.buyer_api_key = None
            return {
                "success": True,
                "message": "Sale cancelled. Listing returned to active.",
                "listing": listing.to_dict(),
            }

        # Complete the sale
        listing.status = ListingStatus.SOLD
        listing.sold_at = datetime.now().isoformat()

        # Record trade
        trade = TradeRecord(
            id=f"NWT-{secrets.token_hex(6).upper()}",
            listing_id=listing_id,
            seller_email=listing.seller_email,
            buyer_email=listing.buyer_email or "",
            listing_type=listing.listing_type,
            quantity=listing.quantity,
            price_cents=listing.price_cents,
            executed_at=listing.sold_at,
        )
        self._trades.append(trade)

        # Update stats
        self._stats["active_listings"] -= 1
        self._stats["total_trades"] += 1
        self._stats["total_volume_cents"] += listing.price_cents

        return {
            "success": True,
            "trade": trade.to_dict(),
            "message": f"Sale complete! {listing.quantity} {listing.listing_type.value} transferred to {listing.buyer_email}",
            "seller_payout": f"${listing.price_cents / 100:.2f}",
        }

    # --------------------------------------------------------------------------
    # USER HISTORY
    # --------------------------------------------------------------------------

    def my_listings(self, seller_email: str) -> Dict[str, Any]:
        """Get all listings for a user."""
        listing_ids = self._user_listings.get(seller_email, [])
        listings = [self._listings[lid] for lid in listing_ids if lid in self._listings]

        return {
            "success": True,
            "count": len(listings),
            "listings": [l.to_dict(include_private=True) for l in listings],
            "active": sum(1 for l in listings if l.status == ListingStatus.ACTIVE),
            "sold": sum(1 for l in listings if l.status == ListingStatus.SOLD),
        }

    def my_trades(self, email: str) -> Dict[str, Any]:
        """Get trade history for a user (as buyer or seller)."""
        trades = [
            t for t in self._trades
            if t.seller_email == email or t.buyer_email == email
        ]

        bought = [t for t in trades if t.buyer_email == email]
        sold = [t for t in trades if t.seller_email == email]

        return {
            "success": True,
            "total_trades": len(trades),
            "bought": {
                "count": len(bought),
                "total_spent_usd": sum(t.price_cents for t in bought) / 100,
                "trades": [t.to_dict() for t in bought],
            },
            "sold": {
                "count": len(sold),
                "total_earned_usd": sum(t.price_cents for t in sold) / 100,
                "trades": [t.to_dict() for t in sold],
            },
        }

    # --------------------------------------------------------------------------
    # MARKET DATA
    # --------------------------------------------------------------------------

    def _expire_listings(self):
        """Expire old listings."""
        now = datetime.now()
        for listing in self._listings.values():
            if listing.status == ListingStatus.ACTIVE:
                expires = datetime.fromisoformat(listing.expires_at)
                if now > expires:
                    listing.status = ListingStatus.EXPIRED
                    self._stats["active_listings"] -= 1

    def _get_market_summary(self) -> Dict[str, Any]:
        """Get market summary stats."""
        active = [l for l in self._listings.values() if l.status == ListingStatus.ACTIVE]

        if not active:
            return {
                "active_listings": 0,
                "avg_price_per_credit": None,
                "cheapest_credit": None,
                "total_credits_available": 0,
            }

        credit_listings = [l for l in active if l.listing_type == ListingType.CREDITS]

        total_credits = sum(l.quantity for l in credit_listings) if credit_listings else 0
        avg_price = (
            sum(l.price_cents / l.quantity for l in credit_listings) / len(credit_listings)
            if credit_listings else None
        )
        cheapest = (
            min(l.price_cents / l.quantity for l in credit_listings)
            if credit_listings else None
        )

        return {
            "active_listings": len(active),
            "avg_price_per_credit_usd": round(avg_price / 100, 4) if avg_price else None,
            "cheapest_credit_usd": round(cheapest / 100, 4) if cheapest else None,
            "total_credits_available": total_credits,
            "total_volume_usd": self._stats["total_volume_cents"] / 100,
            "total_trades": self._stats["total_trades"],
        }

    def market_stats(self) -> Dict[str, Any]:
        """Get overall market statistics."""
        self._expire_listings()
        return {
            "success": True,
            "stats": self._stats,
            "market": self._get_market_summary(),
        }


# ==============================================================================
# SINGLETON
# ==============================================================================

_marketplace: Optional[NewtonMarketplace] = None


def get_marketplace() -> NewtonMarketplace:
    """Get or create the marketplace singleton."""
    global _marketplace
    if _marketplace is None:
        _marketplace = NewtonMarketplace()
    return _marketplace
