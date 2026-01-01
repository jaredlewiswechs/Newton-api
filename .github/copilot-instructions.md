# GitHub Copilot Instructions for Newton Supercomputer

## Project Overview

Newton Supercomputer is a **verified computation system** where:
- The **constraint** IS the instruction
- The **verification** IS the computation  
- The **network** IS the processor

This is a Python-based distributed verification system with FastAPI, implementing deterministic constraint evaluation, verified Turing-complete computation, and immutable audit trails.

## Core Architecture

### Components (from README architecture diagram)

- **CDL (Constraint Definition Language)**: Conditionals, temporal ops, aggregations
- **Logic Engine**: Verified computation engine - Turing complete with bounded loops
- **Forge**: Verification engine - Parallel constraint evaluation, <1ms
- **Vault**: Encrypted storage - AES-256-GCM, identity-derived keys
- **Ledger**: Immutable history - Hash-chained, Merkle proofs
- **Bridge**: Distributed protocol - PBFT consensus, Byzantine fault tolerant
- **Robust**: Adversarial statistics - MAD over mean, locked baselines

### File Structure

```
/core/              # Core verification components
  cdl.py           # Constraint Definition Language
  logic.py         # Verified computation engine
  forge.py         # Verification engine
  vault.py         # Encrypted storage
  ledger.py        # Immutable audit trail
  bridge.py        # Distributed consensus
  robust.py        # Adversarial statistics
  grounding.py     # Evidence grounding
/tests/            # Property-based tests using Hypothesis
newton_supercomputer.py  # Main FastAPI server
```

## Coding Conventions

### Python Style
- Use Python 3.9+ features
- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Use dataclasses for structured data with `@dataclass` decorator
- Prefer descriptive variable names that reflect the verification/constraint domain

### Documentation Style
- Use docstrings with clear purpose statements
- Include ASCII art headers with `═` characters for major sections
- Document invariants and guarantees explicitly
- Example from codebase:
  ```python
  """
  ═══════════════════════════════════════════════════════════════
  COMPONENT NAME
  Brief description
  ═══════════════════════════════════════════════════════════════
  """
  ```

### Core Principles

1. **Determinism**: Same input ALWAYS produces same output
2. **Termination**: All computations must be bounded and guaranteed to terminate
3. **Verification**: Every operation must be verifiable
4. **Immutability**: Once written to ledger, data cannot be changed

### Bounded Execution

All computations must respect `ExecutionBounds`:
- `max_iterations`: Prevent infinite loops (default: 10,000)
- `max_recursion_depth`: Prevent stack overflow (default: 100)
- `max_operations`: Prevent runaway compute (default: 1,000,000)
- `timeout_seconds`: Prevent endless waits (default: 30.0)

These bounds are hard-capped and cannot be exceeded.

## Testing

### Test Framework
- Use `pytest` for all tests
- Use `hypothesis` for property-based testing
- Tests are in `/tests/` directory

### Property-Based Testing Pattern
The project uses Hypothesis to prove properties:
```python
@given(st.integers(), st.floats())
@settings(max_examples=200)
def test_property(self, value, threshold):
    # Test that property holds for all inputs
    assert property_holds(value, threshold)
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with hypothesis
pytest tests/test_properties.py
```

## Building and Running

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python newton_supercomputer.py
```

Server runs at `http://localhost:8000`

### Docker
```bash
docker build -t newton-supercomputer .
docker run -p 8000:8000 newton-supercomputer
```

### Requirements
- FastAPI 0.109.0
- Uvicorn 0.27.0
- Pydantic 2.5.3
- googlesearch-python 1.2.5 (for grounding engine)
- pytest 7.4.4 (testing)
- hypothesis 6.92.1 (property-based testing)

## API Patterns

### Request Models
Use Pydantic `BaseModel` for all request/response schemas:
```python
class ExampleRequest(BaseModel):
    """Clear docstring describing the request."""
    field: str
    optional_field: Optional[Dict[str, Any]] = None
```

### Endpoints
- Use FastAPI decorators: `@app.post()`, `@app.get()`
- Return proper HTTP status codes
- Include timing metrics in responses (`elapsed_us`)
- All verification results should include a `verified` boolean

### Core Endpoints
- `/ask` - Full verification pipeline (POST)
- `/verify` - Content verification (POST)
- `/verify/batch` - Batch verification (POST)
- `/constraint` - CDL constraint evaluation (POST)
- `/ground` - Ground claims in external evidence (POST)
- `/calculate` - Verified computation (POST)
- `/calculate/examples` - Get example expressions (POST)
- `/statistics` - Robust statistical analysis (POST)
- `/vault/store` - Store encrypted data (POST)
- `/vault/retrieve` - Retrieve encrypted data (POST)
- `/ledger` - View audit trail (GET)
- `/ledger/{index}` - Get entry with Merkle proof (GET)
- `/ledger/certificate/{index}` - Export verification certificate (GET)
- `/health` - System status (GET)
- `/metrics` - Performance metrics (GET)

## Verification Patterns

### CDL Constraints
Constraints are JSON objects with operators:
- **Comparison**: `eq`, `ne`, `lt`, `gt`, `le`, `ge`
- **String**: `contains`, `matches` (regex)
- **Set**: `in`, `not_in`
- **Existence**: `exists`, `empty`
- **Temporal**: `within`, `after`, `before`
- **Aggregation**: `sum_lt`, `count_lt`, `avg_lt`

### Logic Operations
Expression-based computation uses nested JSON:
```json
{"op": "+", "args": [2, 3]}  // → 5
{"op": "if", "args": [condition, then_val, else_val]}
{"op": "for", "args": ["i", start, end, body]}
```

## Security Considerations

- Never allow unbounded loops or recursion
- Always enforce `ExecutionBounds`
- Validate all input against constraints before processing
- Use encrypted storage (Vault) for sensitive data
- Maintain immutable audit trail (Ledger) for all operations
- Check for harm/medical/legal/security pattern violations

## Error Handling

- Use FastAPI's `HTTPException` for API errors
- Include descriptive error messages
- Return appropriate HTTP status codes
- Log errors for audit trail

## Common Tasks

### Adding a New Constraint Operator
1. Add to `Operator` enum in `core/cdl.py`
2. Implement evaluation logic in `CDLEvaluator._evaluate_atomic()`
3. Add tests in `tests/test_properties.py`
4. Prove termination with property-based tests

### Adding a New Logic Operation
1. Add to operator handling in `core/logic.py`
2. Ensure bounded execution (no infinite loops)
3. Add to `LogicEngine.evaluate()`
4. Test with property-based tests

### Adding a New API Endpoint
1. Create Pydantic request/response models
2. Add route in `newton_supercomputer.py`
3. Implement handler with proper error handling
4. Add timing metrics
5. Test with both unit and integration tests

## Key Files to Reference

- `newton_supercomputer.py` - Main API server, endpoint patterns
- `core/logic.py` - Verified computation patterns
- `core/cdl.py` - Constraint evaluation patterns
- `tests/test_properties.py` - Testing patterns with Hypothesis
- `README.md` - API documentation and examples
- `DEPLOYMENT.md` - Deployment configuration

## Philosophy

> "1 == 1. The cloud is weather. We're building shelter."

The fundamental law: `newton(current, goal)` returns `current == goal`
- When true → execute
- When false → halt

This isn't a feature. It's the architecture.

## License

- **Open Source (Non-Commercial)**: Personal projects, academic research, non-profit
- **Commercial License Required**: SaaS, enterprise, revenue-generating applications
