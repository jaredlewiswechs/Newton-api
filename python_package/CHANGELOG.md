# Changelog

All notable changes to Newton Computer will be documented in this file.

## [1.0.0] - 2026-01-03

### Added
- Initial release of newton-computer Python package
- TinyTalk constraint language with Blueprint, field, law, forge
- Matter types for type-safe units (Money, Mass, Distance, Temperature, etc.)
- Kinetic Engine for bounded state transitions
- Newton client for remote server communication
- CLI with serve, demo, calc, verify, health, init commands
- Comprehensive documentation and examples
- Support for Python 3.9, 3.10, 3.11, 3.12, 3.13

### Core Features
- `Blueprint` base class for constrained objects
- `@law` decorator for governance rules
- `@forge` decorator for state mutations
- `finfr` (finality) for forbidden states
- `fin` (closure) for reopenable stops
- `ratio(f, g)` for dimensional analysis
- Automatic rollback on law violations

### Matter Types
- `Money` - Currency values
- `Mass` - Weight (kg)
- `Distance` - Length (m)
- `Temperature` - Heat (C/F/K with conversion)
- `Pressure` - Force/area (PSI)
- `Volume` - Capacity (L)
- `Time` - Duration (s)
- `Velocity` - Speed (m/s)
- `FlowRate` - Flow (L/min)

### Kinetic Engine
- `Presence` - State snapshots
- `Delta` - State differences
- `KineticEngine` - Motion resolution with boundaries
- `motion()` - Quick delta calculation
- Interpolation for smooth animations

### Client
- `Newton` class for server communication
- Health checks
- Verified calculations
- Content verification
- Constraint evaluation
- Grounding (fact-checking)
- Robust statistics

### CLI
- `newton serve` - Start local server
- `newton demo` - Run TinyTalk demo
- `newton calc` - Calculate expressions
- `newton verify` - Verify content
- `newton health` - Check server status
- `newton init` - Create new project

## Future Plans

### [1.1.0] - Planned
- Education cartridge with TEKS standards
- Interface Builder cartridge
- Knowledge navigation system
- Gradebook with cryptographic proofs

### [1.2.0] - Planned
- Glass Box policy engine
- Human-in-the-loop negotiation
- Merkle anchor proofs
- Distributed Bridge protocol
