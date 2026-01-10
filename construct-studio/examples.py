#!/usr/bin/env python3
"""
Construct Studio Examples
=========================

Runnable examples demonstrating Construct Studio v0.1

Run with: python examples.py
"""

import sys
import os

# Allow running from within the construct-studio directory
_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)

from datetime import datetime

# Import compatibility - works whether installed or run directly
try:
    import construct_studio
except ImportError:
    # Create a mock module for direct execution
    import types
    construct_studio = types.ModuleType('construct_studio')
    from core import Matter, Floor, Construct, attempt, OntologicalDeath
    from ledger import Ledger, global_ledger
    from engine import ConstructEngine, SimulationMode
    construct_studio.Matter = Matter
    construct_studio.Floor = Floor
    construct_studio.Construct = Construct
    construct_studio.attempt = attempt
    construct_studio.OntologicalDeath = OntologicalDeath
    construct_studio.Ledger = Ledger
    construct_studio.global_ledger = global_ledger
    construct_studio.ConstructEngine = ConstructEngine
    construct_studio.SimulationMode = SimulationMode
    sys.modules['construct_studio'] = construct_studio

    # Also handle cartridges
    construct_studio_cartridges = types.ModuleType('construct_studio.cartridges')
    sys.modules['construct_studio.cartridges'] = construct_studio_cartridges

    from cartridges import finance as _finance
    from cartridges import infrastructure as _infrastructure
    from cartridges import risk as _risk

    construct_studio_cartridges.finance = _finance
    construct_studio_cartridges.infrastructure = _infrastructure
    construct_studio_cartridges.risk = _risk
    sys.modules['construct_studio.cartridges.finance'] = _finance
    sys.modules['construct_studio.cartridges.infrastructure'] = _infrastructure
    sys.modules['construct_studio.cartridges.risk'] = _risk


def example_1_basic_force():
    """
    Example 1: Basic Force Application

    The fundamental physics of constraint satisfaction.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Force Application")
    print("="*60 + "\n")

    from construct_studio import Matter, Floor

    # Define a Floor (constraint container)
    class CorporateCard(Floor):
        budget = Matter(5000, "USD")

    # Create the floor instance
    card = CorporateCard()
    print(f"Created: {card}")
    print(f"Budget capacity: {card._capacities['budget'].maximum}")
    print()

    # Create matter (typed value)
    expense = Matter(1500, "USD", "Office supplies")
    print(f"Created matter: {expense}")

    # Apply force
    result = expense >> card._capacities["budget"]
    print(f"\nApplied force: {expense} >> CorporateCard.budget")
    print(f"Result: {'SUCCESS' if result.success else 'DEATH'}")
    print(f"Ratio: {result.ratio.percentage:.1f}%")
    print(f"Remaining: {card._capacities['budget'].remaining}")


def example_2_ontological_death():
    """
    Example 2: Ontological Death

    What happens when constraints are violated.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Ontological Death")
    print("="*60 + "\n")

    from construct_studio import Matter, Floor, attempt, OntologicalDeath

    class SmallBudget(Floor):
        limit = Matter(100, "USD")

    budget = SmallBudget()

    # This will cause death
    big_expense = Matter(500, "USD", "Way too much")

    print(f"Budget limit: {budget._capacities['limit'].maximum}")
    print(f"Attempting: {big_expense}")
    print()

    # In strict mode, this would raise
    # Let's use attempt() for soft failure
    with attempt():
        result = big_expense >> budget._capacities["limit"]

        if not result:
            print("ONTOLOGICAL DEATH")
            print(f"  Overflow: {result.ratio.overflow} USD")
            print(f"  Available: {budget._capacities['limit'].remaining}")
            print(f"  The illegal state cannot exist.")


def example_3_corporate_card_simulation():
    """
    Example 3: Corporate Card Spending Simulation

    A complete spending scenario with multiple transactions.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Corporate Card Simulation")
    print("="*60 + "\n")

    from construct_studio.cartridges.finance import simulate_spending

    transactions = [
        (1500, "Office supplies"),
        (800, "Team lunch"),
        (2000, "Software license"),
        (1200, "Conference tickets"),  # This will die
    ]

    print("Transactions to process:")
    for amount, desc in transactions:
        print(f"  ${amount:,.2f} - {desc}")
    print()

    result = simulate_spending(transactions)

    print("Results:")
    for txn in result["transactions"]:
        status = "✓" if txn["status"] == "approved" else "✗"
        print(f"  {status} ${txn['amount']:,.2f} - {txn['description']}")
        if txn["status"] == "rejected":
            print(f"      Reason: {txn.get('reason', 'Exceeds budget')}")

    print()
    print(f"Summary: {result['approved']} approved, {result['rejected']} rejected")
    print(f"Total spent: ${result['total_spent']:,.2f}")
    print(f"Remaining: ${result['remaining_budget']:,.2f}")


def example_4_deployment_quotas():
    """
    Example 4: Infrastructure Deployment Quotas

    Constraint-first governance for cloud resources.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Deployment Quotas")
    print("="*60 + "\n")

    from construct_studio.cartridges.infrastructure import (
        DeploymentSpec, simulate_deployments
    )

    specs = [
        DeploymentSpec("api-server", cpu=4, memory=8, replicas=3),
        DeploymentSpec("worker", cpu=8, memory=16, replicas=4),
        DeploymentSpec("database", cpu=16, memory=64, replicas=1),
        DeploymentSpec("ml-service", cpu=32, memory=128, replicas=2),  # Dies
    ]

    print("Deployments to create (Quota: 64 vCPU, 256 GB):")
    for spec in specs:
        print(f"  {spec.name}: {spec.total_cpu} vCPU, {spec.total_memory} GB ({spec.replicas} replicas)")
    print()

    result = simulate_deployments(specs)

    print("Results:")
    for dep in result["deployments"]:
        status = "✓" if dep["status"] == "deployed" else "✗"
        print(f"  {status} {dep['name']}")
        if dep["status"] == "rejected":
            for reason in dep.get("reasons", []):
                print(f"      {reason}")

    print()
    print(f"Summary: {result['deployed']} deployed, {result['rejected']} rejected")
    print(f"Remaining: {result['remaining']['cpu']} vCPU, {result['remaining']['memory']} GB")


def example_5_risk_portfolio():
    """
    Example 5: Risk Budget Management

    Probability-based constraint governance.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Risk Budget")
    print("="*60 + "\n")

    from construct_studio.cartridges.risk import (
        RiskPosition, simulate_portfolio
    )

    positions = [
        RiskPosition("Stock Portfolio", 50000, probability_of_loss=0.05),
        RiskPosition("Bond Holdings", 30000, probability_of_loss=0.02),
        RiskPosition("Crypto", 10000, probability_of_loss=0.08),
        RiskPosition("Venture Fund", 20000, probability_of_loss=0.10),  # Dies
    ]

    print("Risk positions (Budget: 20% total probability):")
    for pos in positions:
        print(f"  {pos.name}: ${pos.value:,.0f}, p(loss)={pos.probability_of_loss:.0%}")
    print()

    result = simulate_portfolio(positions)

    print("Results:")
    for pos in result["positions"]:
        status = "✓" if pos["status"] == "accepted" else "✗"
        print(f"  {status} {pos['name']} (p={pos['probability']:.1%})")
        if pos["status"] == "rejected":
            print(f"      {pos.get('reason', 'Exceeds risk budget')}")

    print()
    print(f"Summary: {result['accepted']} accepted, {result['rejected']} rejected")
    print(f"Total probability: {result['total_probability']:.1%}")
    print(f"Remaining budget: {result['remaining_budget']:.1%}")


def example_6_engine_simulation():
    """
    Example 6: Engine-Based Simulation

    Using the ConstructEngine for complex scenarios.
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Engine Simulation")
    print("="*60 + "\n")

    try:
        from construct_studio import Matter, Floor
        from construct_studio.engine import ConstructEngine, SimulationMode
    except ImportError:
        from core import Matter, Floor
        from engine import ConstructEngine, SimulationMode

    class TestBudget(Floor):
        funds = Matter(10000, "USD")

    # Create engine in soft mode
    engine = ConstructEngine("demo", SimulationMode.SOFT)
    engine.register_floor(TestBudget, "Budget")

    print("Registered floor: Budget (10,000 USD)")
    print()

    # Take initial snapshot
    engine.snapshot("initial")

    # Define operations
    operations = [
        ("force", {"value": 3000, "unit": "USD", "floor": "Budget", "capacity": "funds"}),
        ("force", {"value": 4000, "unit": "USD", "floor": "Budget", "capacity": "funds"}),
        ("force", {"value": 5000, "unit": "USD", "floor": "Budget", "capacity": "funds"}),  # Dies
    ]

    print("Operations:")
    for op_name, kwargs in operations:
        print(f"  {kwargs['value']} USD >> Budget.funds")
    print()

    # Run simulation
    result = engine.simulate(operations)

    print(f"Simulation result: {result}")
    print(f"  Total operations: {len(result.operations)}")
    print(f"  Successes: {result.success_count}")
    print(f"  Deaths: {result.death_count}")
    print(f"  Duration: {result.duration_ms:.2f}ms")

    print()
    print("Final state:")
    for floor_name, caps in result.final_state.items():
        for cap_name, state in caps.items():
            print(f"  {floor_name}.{cap_name}:")
            print(f"    Current: {state['current']}")
            print(f"    Remaining: {state['remaining']}")
            print(f"    Utilization: {state['utilization']:.1%}")


def example_7_ledger():
    """
    Example 7: Ledger Audit Trail

    Inspecting the immutable record of all operations.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Ledger Audit Trail")
    print("="*60 + "\n")

    from construct_studio import Matter, Floor, global_ledger, attempt

    # Clear previous entries
    global_ledger.clear()

    class AuditDemo(Floor):
        limit = Matter(1000, "USD")

    floor = AuditDemo()
    cap = floor._capacities["limit"]

    # Generate some entries
    for amount in [200, 300, 400, 500]:  # 500 will fail
        with attempt():
            m = Matter(amount, "USD", f"Transaction {amount}")
            m >> cap

    print("Ledger entries:")
    for entry in global_ledger.entries:
        status = "SUCCESS" if entry.success else "DEATH"
        print(f"  [{entry.entry_id}] {status}: {entry.matter_value} {entry.matter_unit}")

    print()
    global_ledger.print_summary()


def example_8_what_if_analysis():
    """
    Example 8: What-If Analysis

    Testing hypotheticals without committing changes.
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: What-If Analysis")
    print("="*60 + "\n")

    try:
        from construct_studio import Matter, Floor
        from construct_studio.engine import ConstructEngine, SimulationMode
    except ImportError:
        from core import Matter, Floor
        from engine import ConstructEngine, SimulationMode

    class PlanningBudget(Floor):
        marketing = Matter(50000, "USD")
        engineering = Matter(100000, "USD")

    engine = ConstructEngine("planning", SimulationMode.ANALYZE)
    engine.register_floor(PlanningBudget, "Budget")

    print("Budget Floor:")
    print("  Marketing: $50,000")
    print("  Engineering: $100,000")
    print()

    # Test various scenarios
    scenarios = [
        (30000, "USD", "marketing"),
        (75000, "USD", "engineering"),
        (60000, "USD", "marketing"),  # Would overflow
    ]

    print("What-If Scenarios:")
    for value, unit, capacity in scenarios:
        result = engine.what_if(value, unit, "Budget", capacity)
        key = f"Budget.{capacity}"
        if key in result:
            info = result[key]
            status = "✓ Would fit" if info["would_fit"] else "✗ Would overflow"
            print(f"  ${value:,} >> {capacity}: {status}")
            if not info["would_fit"]:
                print(f"      Overflow: ${info['overflow']:,}")
    print()


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("       CONSTRUCT STUDIO v0.1 - EXAMPLES")
    print("       Constraint-First Execution Environment")
    print("="*60)

    examples = [
        example_1_basic_force,
        example_2_ontological_death,
        example_3_corporate_card_simulation,
        example_4_deployment_quotas,
        example_5_risk_portfolio,
        example_6_engine_simulation,
        example_7_ledger,
        example_8_what_if_analysis,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")

    print("\n" + "="*60)
    print("Examples complete. The constraint IS the instruction.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
