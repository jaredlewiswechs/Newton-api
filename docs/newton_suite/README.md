# Newton Suite

A curated collection of Newton Supercomputer components for development and deployment.

## Components Included

This suite includes the following Newton projects:

- **realTinyTalk** - The verified general-purpose programming language with Monaco editor
- **adan** - Advanced agent framework
- **adan_portable** - Portable version of the agent framework
- **newton_agent** - Core Newton agent implementation
- **statsy** - Statistical analysis and visualization tools

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the realTinyTalk Monaco editor:
   ```bash
   python realTinyTalk/web/server.py
   ```
   Then visit http://localhost:5555

3. Run Newton demos:
   ```bash
   python -m newton_sdk.cli demo
   ```

## Architecture

The Newton Supercomputer implements verified computation where:
- The constraint IS the instruction
- The verification IS the computation
- The network IS the processor

All computations are bounded, deterministic, and cryptographically verifiable.

## Documentation

See the main [Newton README](../README.md) for comprehensive documentation, API reference, and guides.

## License

See [LICENSE](../LICENSE) and [USAGE_AGREEMENT.md](../USAGE_AGREEMENT.md) for licensing terms.