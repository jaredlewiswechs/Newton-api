#!/usr/bin/env python3
"""
Construct Studio CLI
====================

Interactive command-line interface for Construct Studio.

Usage:
    python -m construct_studio              # Start REPL
    python -m construct_studio demo         # Run demo scenarios
    python -m construct_studio simulate     # Run simulation from file

Commands in REPL:
    floor <name> <capacity> <value> <unit>  - Create a floor
    matter <value> <unit> [label]           - Create matter
    force <matter_id> >> <floor>            - Apply force
    status                                  - Show all floors
    ledger                                  - Show ledger
    reset                                   - Reset all floors
    demo                                    - Run demo scenarios
    help                                    - Show help
    quit                                    - Exit
"""

from __future__ import annotations
import sys
import cmd
import json
import argparse
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from .core import Matter, Floor, Force, attempt, ConstructError, OntologicalDeath
    from .ledger import Ledger, global_ledger
    from .engine import ConstructEngine, SimulationMode, SimulationResult
    from .cartridges.finance import CorporateCard, spend, simulate_spending
    from .cartridges.infrastructure import DeploymentQuota, DeploymentSpec, simulate_deployments
    from .cartridges.risk import RiskBudget, RiskPosition, simulate_portfolio
except ImportError:
    from core import Matter, Floor, Force, attempt, ConstructError, OntologicalDeath
    from ledger import Ledger, global_ledger
    from engine import ConstructEngine, SimulationMode, SimulationResult
    from cartridges.finance import CorporateCard, spend, simulate_spending
    from cartridges.infrastructure import DeploymentQuota, DeploymentSpec, simulate_deployments
    from cartridges.risk import RiskBudget, RiskPosition, simulate_portfolio


# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def colored(text: str, color: str) -> str:
    """Apply color to text."""
    return f"{color}{text}{Colors.ENDC}"


def print_banner():
    """Print the Construct Studio banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗ ██████╗ ███╗   ██╗███████╗████████╗██████╗ ██╗   ██╗║
    ║  ██╔════╝██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║   ██║║
    ║  ██║     ██║   ██║██╔██╗ ██║███████╗   ██║   ██████╔╝██║   ██║║
    ║  ██║     ██║   ██║██║╚██╗██║╚════██║   ██║   ██╔══██╗██║   ██║║
    ║  ╚██████╗╚██████╔╝██║ ╚████║███████║   ██║   ██║  ██║╚██████╔╝║
    ║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ║
    ║                                                               ║
    ║              S T U D I O   v 0 . 1                             ║
    ║                                                               ║
    ║         Constraint-First Execution Environment                ║
    ║              The illegal state cannot exist.                  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(colored(banner, Colors.CYAN))


def print_help():
    """Print help information."""
    help_text = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  CONSTRUCT STUDIO COMMANDS                                    ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║                                                               ║
    ║  FLOORS & MATTER                                              ║
    ║  ─────────────────                                            ║
    ║  floor <name>              Create floor with presets          ║
    ║  matter <val> <unit>       Create matter (e.g., matter 100 USD)║
    ║  force <val> <unit> >> <floor>   Apply force                  ║
    ║                                                               ║
    ║  SIMULATION                                                   ║
    ║  ──────────                                                   ║
    ║  demo                      Run all demo scenarios             ║
    ║  demo finance              Corporate card demo                ║
    ║  demo infra                Infrastructure quota demo          ║
    ║  demo risk                 Risk budget demo                   ║
    ║                                                               ║
    ║  INSPECTION                                                   ║
    ║  ──────────                                                   ║
    ║  status                    Show all floor states              ║
    ║  ledger [n]                Show last n ledger entries         ║
    ║  analyze                   Analyze utilization                ║
    ║                                                               ║
    ║  CONTROL                                                      ║
    ║  ───────                                                      ║
    ║  reset                     Reset all floors                   ║
    ║  clear                     Clear screen                       ║
    ║  quit / exit               Exit REPL                          ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(colored(help_text, Colors.CYAN))


class ConstructREPL(cmd.Cmd):
    """Interactive REPL for Construct Studio."""

    intro = colored("\n  Type 'help' for commands, 'demo' to see it in action.\n", Colors.DIM)
    prompt = colored("construct> ", Colors.GREEN)

    def __init__(self):
        super().__init__()
        self.engine = ConstructEngine("repl", SimulationMode.SOFT)
        self.ledger = Ledger("repl")
        self.matter_store: Dict[str, Matter] = {}
        self.matter_counter = 0

    def preloop(self):
        """Print banner before starting."""
        print_banner()

    def default(self, line: str):
        """Handle unknown commands."""
        # Check for >> operator
        if ">>" in line:
            self.do_force(line)
        else:
            print(colored(f"  Unknown command: {line}", Colors.RED))
            print(colored("  Type 'help' for available commands.", Colors.DIM))

    def do_help(self, arg: str):
        """Show help."""
        print_help()

    def do_quit(self, arg: str):
        """Exit the REPL."""
        print(colored("\n  Goodbye. The constraints remain.\n", Colors.DIM))
        return True

    def do_exit(self, arg: str):
        """Exit the REPL."""
        return self.do_quit(arg)

    def do_EOF(self, arg: str):
        """Handle Ctrl+D."""
        print()
        return self.do_quit(arg)

    def do_clear(self, arg: str):
        """Clear the screen."""
        print("\033[2J\033[H")
        print_banner()

    # ========================================================================
    # FLOOR COMMANDS
    # ========================================================================

    def do_floor(self, arg: str):
        """Create or list floors."""
        parts = arg.strip().split()

        if not parts:
            # List floors
            if self.engine._floors:
                print(colored("\n  Registered Floors:", Colors.BOLD))
                for name, floor in self.engine._floors.items():
                    print(f"    - {name}")
                print()
            else:
                print(colored("  No floors registered. Use 'floor <preset>' to create one.", Colors.DIM))
                print(colored("  Presets: card, quota, risk", Colors.DIM))
            return

        preset = parts[0].lower()

        if preset in ("card", "corporate", "finance"):
            floor = self.engine.register_floor(CorporateCard, "CorporateCard")
            print(colored(f"  Created CorporateCard floor (budget: 5000 USD)", Colors.GREEN))

        elif preset in ("quota", "deploy", "infra"):
            floor = self.engine.register_floor(DeploymentQuota, "DeploymentQuota")
            print(colored(f"  Created DeploymentQuota floor (cpu: 64 vCPU, memory: 256 GB)", Colors.GREEN))

        elif preset in ("risk", "budget"):
            floor = self.engine.register_floor(RiskBudget, "RiskBudget")
            print(colored(f"  Created RiskBudget floor (total: 0.20 probability)", Colors.GREEN))

        else:
            print(colored(f"  Unknown preset: {preset}", Colors.RED))
            print(colored("  Available presets: card, quota, risk", Colors.DIM))

    # ========================================================================
    # MATTER COMMANDS
    # ========================================================================

    def do_matter(self, arg: str):
        """Create matter."""
        parts = arg.strip().split()

        if len(parts) < 2:
            print(colored("  Usage: matter <value> <unit> [label]", Colors.RED))
            return

        try:
            value = float(parts[0])
            unit = parts[1]
            label = " ".join(parts[2:]) if len(parts) > 2 else None

            self.matter_counter += 1
            matter_id = f"m{self.matter_counter}"

            matter = Matter(value, unit, label)
            self.matter_store[matter_id] = matter

            print(colored(f"  Created {matter_id}: {matter}", Colors.GREEN))

        except ValueError as e:
            print(colored(f"  Error: {e}", Colors.RED))

    # ========================================================================
    # FORCE COMMANDS
    # ========================================================================

    def do_force(self, arg: str):
        """Apply force: force <value> <unit> >> <floor>[.<capacity>]"""
        if ">>" not in arg:
            print(colored("  Usage: force <value> <unit> >> <floor>[.<capacity>]", Colors.RED))
            print(colored("  Example: force 1500 USD >> CorporateCard", Colors.DIM))
            return

        # Parse: <matter> >> <target>
        left, right = arg.replace("force", "").strip().split(">>")
        left = left.strip()
        right = right.strip()

        # Parse matter (value unit)
        left_parts = left.split()
        if len(left_parts) < 2:
            print(colored("  Error: specify value and unit (e.g., 1500 USD)", Colors.RED))
            return

        try:
            value = float(left_parts[0])
            unit = left_parts[1]
        except ValueError:
            print(colored(f"  Error: invalid value '{left_parts[0]}'", Colors.RED))
            return

        # Parse target (floor.capacity or just floor)
        target_parts = right.split(".")
        floor_name = target_parts[0]
        capacity_name = target_parts[1] if len(target_parts) > 1 else None

        # Find floor
        floor = self.engine.get_floor(floor_name)
        if floor is None:
            print(colored(f"  Error: floor '{floor_name}' not found", Colors.RED))
            print(colored(f"  Use 'floor <preset>' to create one first.", Colors.DIM))
            return

        # Find capacity
        if capacity_name:
            capacity = floor._capacities.get(capacity_name)
            if capacity is None:
                print(colored(f"  Error: capacity '{capacity_name}' not found in {floor_name}", Colors.RED))
                return
        else:
            # Use first matching unit
            capacity = None
            for cap in floor._capacities.values():
                if cap.current.unit == unit:
                    capacity = cap
                    break
            if capacity is None:
                capacity = list(floor._capacities.values())[0]

        # Apply force
        matter = Matter(value, unit)

        print()
        print(colored(f"  Applying force: {matter} >> {floor_name}.{capacity.name}", Colors.CYAN))
        print(colored(f"  ─────────────────────────────────────────", Colors.DIM))

        with attempt():
            result = matter >> capacity

            if result.success:
                print(colored(f"  ✓ FORCE ABSORBED", Colors.GREEN))
                print(f"    Ratio: {result.ratio.percentage:.1f}%")
                print(f"    Remaining: {capacity.remaining}")
                print(f"    Utilization: {capacity.utilization:.1%}")
            else:
                print(colored(f"  ✗ ONTOLOGICAL DEATH", Colors.RED))
                print(f"    Overflow: {result.ratio.overflow} {unit}")
                print(f"    Available: {capacity.remaining}")
                print(f"    Requested: {value} {unit}")

        print()

    # ========================================================================
    # STATUS COMMANDS
    # ========================================================================

    def do_status(self, arg: str):
        """Show status of all floors."""
        if not self.engine._floors:
            print(colored("  No floors registered. Use 'floor <preset>' to create one.", Colors.DIM))
            return

        print()
        print(colored("  ╔════════════════════════════════════════════╗", Colors.CYAN))
        print(colored("  ║          CONSTRUCT STATUS                  ║", Colors.CYAN))
        print(colored("  ╚════════════════════════════════════════════╝", Colors.CYAN))
        print()

        for name, floor in self.engine._floors.items():
            print(colored(f"  {name}", Colors.BOLD))
            print(colored("  ────────────────────────────────────────────", Colors.DIM))

            for cap_name, capacity in floor._capacities.items():
                util = capacity.utilization
                bar_width = 30
                filled = int(bar_width * util)

                if util >= 1.0:
                    bar_color = Colors.RED
                elif util >= 0.8:
                    bar_color = Colors.YELLOW
                else:
                    bar_color = Colors.GREEN

                bar = colored("█" * filled, bar_color) + colored("░" * (bar_width - filled), Colors.DIM)

                print(f"    {cap_name}:")
                print(f"      [{bar}] {util:.1%}")
                print(f"      {capacity.current.value:.1f}/{capacity.maximum.value:.1f} {capacity.current.unit}")
                print()

    def do_analyze(self, arg: str):
        """Analyze current state."""
        if not self.engine._floors:
            print(colored("  No floors to analyze.", Colors.DIM))
            return

        analysis = self.engine.analyze()

        print()
        print(colored("  ╔════════════════════════════════════════════╗", Colors.CYAN))
        print(colored("  ║          ANALYSIS REPORT                   ║", Colors.CYAN))
        print(colored("  ╚════════════════════════════════════════════╝", Colors.CYAN))
        print()

        summary = analysis["summary"]
        print(f"    Total Capacities: {summary['total_capacities']}")
        print(f"    Fully Utilized:   {summary['fully_utilized']}")
        print(f"    Partial:          {summary['partially_utilized']}")
        print(f"    Empty:            {summary['empty']}")
        print()

        if analysis["warnings"]:
            print(colored("  Warnings:", Colors.YELLOW))
            for warning in analysis["warnings"]:
                print(colored(f"    ⚠ {warning}", Colors.YELLOW))
            print()

    # ========================================================================
    # LEDGER COMMANDS
    # ========================================================================

    def do_ledger(self, arg: str):
        """Show ledger entries."""
        n = int(arg) if arg.strip().isdigit() else 10

        entries = global_ledger.get_recent(n)

        if not entries:
            print(colored("  Ledger is empty.", Colors.DIM))
            return

        print()
        print(colored("  ╔════════════════════════════════════════════╗", Colors.CYAN))
        print(colored("  ║          LEDGER                            ║", Colors.CYAN))
        print(colored("  ╚════════════════════════════════════════════╝", Colors.CYAN))
        print()

        for entry in entries:
            if entry.death:
                status = colored("DEATH", Colors.RED)
            else:
                status = colored("OK   ", Colors.GREEN)

            print(f"    [{entry.entry_id}] {status} {entry.matter_value} {entry.matter_unit} >> {entry.target_name}")

        print()

        stats = global_ledger.stats
        print(colored(f"  Total: {stats['total_entries']} | Successes: {stats['successes']} | Deaths: {stats['deaths']}", Colors.DIM))
        print()

    # ========================================================================
    # DEMO COMMANDS
    # ========================================================================

    def do_demo(self, arg: str):
        """Run demo scenarios."""
        demos = {
            "finance": self._demo_finance,
            "infra": self._demo_infrastructure,
            "risk": self._demo_risk,
        }

        if arg.strip().lower() in demos:
            demos[arg.strip().lower()]()
        else:
            # Run all demos
            print(colored("\n  Running all demos...\n", Colors.BOLD))
            for name, demo_func in demos.items():
                print(colored(f"  {'='*50}", Colors.DIM))
                print(colored(f"  DEMO: {name.upper()}", Colors.BOLD))
                print(colored(f"  {'='*50}\n", Colors.DIM))
                demo_func()
                print()

    def _demo_finance(self):
        """Finance demo: corporate card spending."""
        print(colored("  Scenario: Corporate card with $5,000 budget\n", Colors.CYAN))

        transactions = [
            (1500, "Office supplies"),
            (800, "Team lunch"),
            (2000, "Software license"),
            (1200, "Conference tickets"),  # This would exceed budget
        ]

        result = simulate_spending(transactions)

        print(colored("  Transactions:", Colors.BOLD))
        for txn in result["transactions"]:
            if txn["status"] == "approved":
                status = colored("✓ APPROVED", Colors.GREEN)
                detail = f"(remaining: ${txn['remaining']:.2f})"
            else:
                status = colored("✗ REJECTED", Colors.RED)
                detail = txn.get("reason", "")

            print(f"    ${txn['amount']:.2f} - {txn['description']}")
            print(f"      {status} {detail}")
            print()

        print(colored(f"  Summary: {result['approved']} approved, {result['rejected']} rejected", Colors.BOLD))
        print(colored(f"  Total spent: ${result['total_spent']:.2f}", Colors.DIM))
        print(colored(f"  Remaining: ${result['remaining_budget']:.2f}", Colors.DIM))

    def _demo_infrastructure(self):
        """Infrastructure demo: deployment quotas."""
        print(colored("  Scenario: Cluster with 64 vCPU, 256 GB RAM\n", Colors.CYAN))

        specs = [
            DeploymentSpec("api-server", cpu=4, memory=8, replicas=3),
            DeploymentSpec("worker", cpu=8, memory=16, replicas=4),
            DeploymentSpec("database", cpu=16, memory=64, replicas=1),
            DeploymentSpec("ml-service", cpu=32, memory=128, replicas=2),  # Exceeds quota
        ]

        result = simulate_deployments(specs)

        print(colored("  Deployments:", Colors.BOLD))
        for dep in result["deployments"]:
            if dep["status"] == "deployed":
                status = colored("✓ DEPLOYED", Colors.GREEN)
                detail = f"(cpu: {dep['cpu']}, mem: {dep['memory']} GB)"
            else:
                status = colored("✗ REJECTED", Colors.RED)
                detail = "; ".join(dep.get("reasons", []))

            print(f"    {dep['name']}")
            print(f"      {status} {detail}")
            print()

        print(colored(f"  Summary: {result['deployed']} deployed, {result['rejected']} rejected", Colors.BOLD))
        print(colored(f"  Remaining: cpu={result['remaining']['cpu']} vCPU, memory={result['remaining']['memory']} GB", Colors.DIM))

    def _demo_risk(self):
        """Risk demo: probability budget."""
        print(colored("  Scenario: Risk budget of 20% total probability\n", Colors.CYAN))

        positions = [
            RiskPosition("Stock Portfolio", 50000, probability_of_loss=0.05),
            RiskPosition("Bond Holdings", 30000, probability_of_loss=0.02),
            RiskPosition("Crypto", 10000, probability_of_loss=0.08),
            RiskPosition("Venture Fund", 20000, probability_of_loss=0.10),  # Exceeds
        ]

        result = simulate_portfolio(positions)

        print(colored("  Positions:", Colors.BOLD))
        for pos in result["positions"]:
            if pos["status"] == "accepted":
                status = colored("✓ ACCEPTED", Colors.GREEN)
                detail = f"(p={pos['probability']:.1%})"
            else:
                status = colored("✗ REJECTED", Colors.RED)
                detail = pos.get("reason", "")

            print(f"    {pos['name']}")
            print(f"      {status} {detail}")
            print()

        print(colored(f"  Summary: {result['accepted']} accepted, {result['rejected']} rejected", Colors.BOLD))
        print(colored(f"  Total probability: {result['total_probability']:.1%}", Colors.DIM))
        print(colored(f"  Remaining budget: {result['remaining_budget']:.1%}", Colors.DIM))

    def do_reset(self, arg: str):
        """Reset all floors."""
        self.engine.reset_all()
        global_ledger.clear()
        print(colored("  All floors reset to initial state.", Colors.GREEN))


def run_demo():
    """Run demo without REPL."""
    print_banner()
    repl = ConstructREPL()
    repl.do_demo("")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Construct Studio - Constraint-First Execution Environment"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="repl",
        choices=["repl", "demo", "version"],
        help="Command to run"
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "version":
        print("Construct Studio v0.1.0")
    else:
        repl = ConstructREPL()
        repl.cmdloop()


if __name__ == "__main__":
    main()
