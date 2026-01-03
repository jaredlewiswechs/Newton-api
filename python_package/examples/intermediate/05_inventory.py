#!/usr/bin/env python3
"""
05_inventory.py - Inventory Management

An inventory system that can never have negative stock.
Demonstrates practical business logic constraints.
"""

from newton import Blueprint, field, law, forge, when, finfr, LawViolation
from typing import Dict


class Product(Blueprint):
    """A product with stock management."""

    name = field(str, default="Unknown")
    stock = field(int, default=0)
    reserved = field(int, default=0)  # Stock reserved for pending orders
    price = field(float, default=0.0)

    @law
    def no_negative_stock(self):
        """Physical stock cannot be negative."""
        when(self.stock < 0, finfr)

    @law
    def no_negative_reserved(self):
        """Reserved quantity cannot be negative."""
        when(self.reserved < 0, finfr)

    @law
    def reserved_within_stock(self):
        """Cannot reserve more than available stock."""
        when(self.reserved > self.stock, finfr)

    @forge
    def receive(self, quantity: int):
        """Receive stock from supplier."""
        self.stock += quantity
        return f"Received {quantity} units of {self.name}. Stock: {self.stock}"

    @forge
    def reserve(self, quantity: int):
        """Reserve stock for a pending order."""
        self.reserved += quantity
        return f"Reserved {quantity} units. Reserved: {self.reserved}/{self.stock}"

    @forge
    def unreserve(self, quantity: int):
        """Cancel a reservation."""
        self.reserved -= quantity
        return f"Unreserved {quantity} units. Reserved: {self.reserved}/{self.stock}"

    @forge
    def ship(self, quantity: int):
        """Ship reserved stock."""
        self.reserved -= quantity
        self.stock -= quantity
        return f"Shipped {quantity} units of {self.name}. Stock: {self.stock}"

    @forge
    def adjust(self, quantity: int):
        """Inventory adjustment (damage, theft, errors)."""
        self.stock += quantity  # Negative for reductions
        return f"Adjusted {self.name} by {quantity}. Stock: {self.stock}"

    @property
    def available(self) -> int:
        """Stock available for new orders."""
        return self.stock - self.reserved


class Warehouse(Blueprint):
    """A warehouse containing multiple products."""

    products: Dict[str, Product] = field(dict, default=None)

    def __init__(self):
        super().__init__()
        self.products = {}

    @forge
    def add_product(self, sku: str, name: str, price: float):
        """Add a new product to the warehouse."""
        self.products[sku] = Product(name=name, price=price)
        return f"Added product: {name} (SKU: {sku})"

    def get_product(self, sku: str) -> Product:
        """Get a product by SKU."""
        return self.products.get(sku)

    def inventory_report(self) -> str:
        """Generate inventory report."""
        lines = ["Inventory Report", "=" * 40]
        for sku, product in self.products.items():
            lines.append(
                f"{sku}: {product.name} - "
                f"Stock: {product.stock}, "
                f"Reserved: {product.reserved}, "
                f"Available: {product.available}"
            )
        return "\n".join(lines)


def main():
    print("=" * 60)
    print("  INVENTORY MANAGEMENT - Stock Control Demo")
    print("=" * 60)
    print()

    # Create warehouse and products
    warehouse = Warehouse()
    warehouse.add_product("WIDGET-001", "Blue Widget", 29.99)
    warehouse.add_product("GADGET-002", "Red Gadget", 49.99)

    widget = warehouse.get_product("WIDGET-001")
    gadget = warehouse.get_product("GADGET-002")

    # Receive initial stock
    print("--- Receiving Stock ---")
    print(widget.receive(100))
    print(gadget.receive(50))
    print()

    # Reserve for orders
    print("--- Processing Orders ---")
    print(widget.reserve(30))  # Order 1
    print(widget.reserve(20))  # Order 2
    print(f"Widget available: {widget.available}")
    print()

    # Ship an order
    print("--- Shipping ---")
    print(widget.ship(30))  # Ship order 1
    print(f"Widget stock: {widget.stock}, reserved: {widget.reserved}")
    print()

    # Try to reserve more than available
    print("--- Testing Limits ---")
    print(f"Widget available: {widget.available}")
    print("Trying to reserve 60 units (only 50 available)...")
    try:
        widget.reserve(60)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
    print()

    # Try to ship more than reserved
    print("Trying to ship 30 units (only 20 reserved)...")
    try:
        widget.ship(30)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
    print()

    # Inventory adjustment (damage)
    print("--- Inventory Adjustment ---")
    print(gadget.adjust(-5))  # 5 units damaged
    print()

    # Try to adjust below zero
    print("Trying to adjust gadget by -50 (would go negative)...")
    try:
        gadget.adjust(-50)
    except LawViolation as e:
        print(f"BLOCKED: {e}")
    print()

    # Final report
    print("--- Final Report ---")
    print(warehouse.inventory_report())
    print()

    print("=" * 60)
    print("Inventory constraints prevent impossible states.")
    print("Stock can never go negative, and reservations are enforced.")
    print("=" * 60)


if __name__ == "__main__":
    main()
