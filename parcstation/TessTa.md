# TessTa
## parcStation Test Architecture

> "Trust the pipeline. Verify the artifact."

---

## Quick Start

```bash
cd parcstation

# Full test suite (smoke + contract + acid + cartridge)
python test.py

# Individual tests
python test.py smoke      # 10s - "Does it boot?"
python test.py contract   # 18s - UI ↔ API boundaries
python test.py acid       # 4s  - ACID compliance
python test.py cartridge  # 34s - Cartridge modules
```

---

## Philosophy

From GPT's advice:

> "UI is a liar. It can look right and be wrong (or feel wrong and be right).
> Tests give you a repeatable yes/no that doesn't depend on vibes, timing, or your mood.
> When your system is generating code fast, you need a brake that's faster than your eyes."

**The fear you're addressing:**
1. **Integration fear**: "This passes unit tests but breaks when wired into the UI."
2. **Mismatch fear**: "The bot 'understood' the task, but not my actual intent."

**The workflow:**
```
1. Make changes
2. python test.py        ← Run BEFORE opening UI
3. If SAFE → open browser
4. If FAIL → fix issues first
```

---

## Test Suites

### 1. Smoke Test (`smoke.py`)

**Purpose:** "Does it boot?" — 10 second answer

**Checks:**
| Check | What it validates |
|-------|-------------------|
| Newton API | Supercomputer running on :8000 |
| Newton Agent | Agent running on :8091 |
| Cartridges | Cartridge server on :8093 (optional) |
| UI Server | HTTP server on :8082 serving HTML |
| API /verify | Verification endpoint responds |
| API /calculate | Calculation returns 1+1=2 |
| JS Contract | app2.js has required classes |
| CSS Contract | style.css has required variables |

**Exit codes:**
- `0` = All systems go
- `1` = One or more systems down

---

### 2. Contract Test (`contract_test.py`)

**Purpose:** Test boundaries between UI ↔ State ↔ Network

> "Most bugs live at boundaries, and boundaries are where humans assume things."

**Categories (45 checks):**

#### HTML Structure (8 checks)
- Has app container (`class="app"` or `id="app"`)
- Has sidebar
- Has main area
- Has chat-panel
- Has chat-fab (floating action button)
- Loads app2.js
- Loads style.css
- No inline onerror handlers

#### CSS Contract (10 checks)
- Has `--bg-primary` variable
- Has `--glass-bg` variable
- Has `--accent` variable
- Has verified color (#10B981)
- Has unverified color (#EF4444)
- Has `pointer-events` defined (critical for clickability!)
- Sheet visibility rules
- Overlay visibility rules
- Chat panel styled
- Chat messages styled

#### JavaScript Contract (12 checks)
- `ParcStationApp` class exists
- `NewtonClient` class exists
- `NewtonAgentClient` class exists
- `DataStore` class exists
- `bindEvents` method exists
- `bindChatEvents` method exists
- Render methods exist
- Newton URL configured (localhost:8000)
- Agent URL configured (localhost:8091)
- Click handlers attached
- DOMContentLoaded handler
- Reasonable console.error count

#### API Contract - Newton (6 checks)
- `/verify` returns `{ verified: bool }`
- `/calculate` returns `{ result: any }`
- `/ground` returns `{ status: string }`
- `/ledger` returns `{ entries: [] }`

#### API Contract - Agent (4 checks)
- `/health` responds 200
- `/stats` returns data
- `/history` returns `{ turns: [] }`
- `/models` returns list

#### Boundary Wiring (5 checks)
- JS has fetch to `/verify`
- JS has fetch to `/ground`
- JS has fetch to `/chat`
- Error handling (catch blocks)
- JSON parsing

**Prints usage snippet before running** — helps spot intent drift instantly.

---

### 3. ACID Test (`test_acid.py`)

**Purpose:** Verify Newton compliance with database-level guarantees (11 checks)

#### Atomicity (Complete or Nothing)
- **Atomic Verification**: Verify operation completes fully or not at all
- **Atomic Grounding**: Grounding operation is atomic

#### Consistency (Deterministic)
- **Consistent Verification**: Same input → same output, every time
- **Consistent Calculation**: `3*4+5` always equals `17`

#### Isolation (No Interference)
- **Isolated Concurrent Verify**: 5 concurrent requests don't interfere

#### Durability (Persistent)
- **Durable Ledger**: Operations recorded to audit trail

#### Newton Agent
- **Agent Health**: Service responding
- **Agent Stats**: Statistics endpoint works
- **Agent History**: Conversation history persists

#### Integration
- **Full Verification Pipeline**: claim → ground → verify → ledger
- **Calculation Types**: Various expression operations work

---

### 4. Cartridge Test (`test_cartridges.py`)

**Purpose:** Verify all cartridge modules work correctly (36 checks)

#### Service Health (3 checks)
- Service running on :8093
- Cartridges endpoint responds
- Has all expected cartridges

#### Wikipedia Cartridge (7 checks)
- Summary endpoint responds
- Summary found for valid topics
- Has title field
- Has summary content (>50 chars)
- Has Wikipedia URL
- Search endpoint responds
- Returns search results

#### arXiv Cartridge (5 checks)
- Search endpoint responds
- Returns paper results
- Papers have titles
- Papers have authors
- Papers have arXiv URLs

#### Calendar Cartridge (8 checks)
- Now endpoint returns datetime
- Has day_of_week
- Parse 'today'
- Parse 'tomorrow'
- Parse 'next friday'
- Parse 'in 3 days'
- Parse 'end of month'

#### Export Cartridge (6 checks)
- JSON export endpoint
- JSON has content
- JSON has filename
- Markdown export endpoint
- Markdown has content
- Markdown has filename

#### Code Cartridge (4 checks)
- Code evaluate endpoint
- Returns result
- Result is verified
- Complex math works

#### Dictionary Cartridge (3 checks)
- Dictionary endpoint responds
- Word found
- Has definitions

---

## Adding New Tests

### Adding a Smoke Check

```python
# In smoke.py, add to smoke() function:

# N. Your new check
try:
    r = requests.get("http://localhost:XXXX/endpoint", timeout=2)
    ok = r.status_code == 200
    checks.append(("Check Name", ok, f"detail"))
except:
    checks.append(("Check Name", False, "DOWN"))
```

### Adding a Contract Check

```python
# In contract_test.py, add to run() method:

self.check("Description", condition_expression, "error detail")
```

### Adding an ACID Test

```python
# In test_acid.py

async def test_my_new_test(self, session: aiohttp.ClientSession):
    """Docstring explaining the test."""
    start = time.time()
    try:
        # Your test logic here
        async with session.post(f"{URL}/endpoint", json=payload) as resp:
            data = await resp.json()
            passed = some_condition(data)
            self.record(TestResult(
                name="Test Name",
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                details=f"useful debug info"
            ))
    except Exception as e:
        self.record(TestResult(
            name="Test Name",
            passed=False,
            duration_ms=(time.time() - start) * 1000,
            error=str(e)
        ))

# Then add to run_all():
await self.test_my_new_test(session)
```

---

## Test Design Principles

### 1. Fast Agent Tests
Use endpoints that don't call the LLM:
- ✅ `/health`, `/stats`, `/history`, `/models`
- ❌ `/chat` (slow - calls Ollama/qwen)

### 2. Timeouts
- Fast endpoints: 2-3 seconds
- Grounding (web search): 5-10 seconds
- Never wait forever

### 3. Contract Over Implementation
Test what the UI expects, not how it's built:
```python
# Good: Test the contract
self.check("/verify returns 'verified'", "verified" in data)

# Bad: Test implementation details
self.check("Uses aiohttp", "aiohttp" in source_code)
```

### 4. Boundary First
Focus on where systems meet:
- UI ↔ JavaScript
- JavaScript ↔ API
- API ↔ Database/Ledger

---

## Troubleshooting

### "Newton Agent DOWN"
```bash
# Start agent in separate terminal
cd newton_agent
python server.py
```

### "UI Server DOWN"
```bash
# Start HTTP server
python -m http.server 8082 -d parcstation
```

### "Newton API DOWN"
```bash
# Start supercomputer
python newton_supercomputer.py
```

### Contract test timeout on /chat
Chat calls the LLM which is slow. The tests now use fast endpoints instead.

### Click not working in UI
Check for `pointer-events: none` on overlays. Fixed by ensuring:
```css
.sheet-overlay { pointer-events: none; }
.sheet-overlay.visible { pointer-events: auto; }
```

---

## File Structure

```
parcstation/
├── test.py           # Main test runner (runs all suites)
├── smoke.py          # Quick boot check
├── contract_test.py  # UI/API boundary tests  
├── test_acid.py      # ACID compliance tests
├── test_cartridges.py  # Cartridge module tests (36 checks)
├── TessTa.md           # This file
└── StationReadMe.md    # Architecture docs
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | One or more tests failed |

---

## Output Format

```
╔═══════════════════════════════════════════════════════════════════════════╗
║   parcStation Test Suite                                                  ║
║   Trust the pipeline. Verify the artifact.                                ║
╚═══════════════════════════════════════════════════════════════════════════╝

▶ Running Smoke Test...
   ✓ Newton API      PASS 2010ms
   ✓ Newton Agent    PASS 2034ms
   ✓ Cartridges      PASS 2019ms
   ...

▶ Running Contract Test...
   ✓ 45/45 checks passed (100%)

▶ Running ACID Test...
   ✓ 11/11 tests passed

▶ Running Cartridge Test...
   ✓ 36/36 checks passed

═══════════════════════════════════════════════════════════════════════════

  ███████╗ █████╗ ███████╗███████╗
  ██╔════╝██╔══██╗██╔════╝██╔════╝
  ███████╗███████║█████╗  █████╗  
  ╚════██║██╔══██║██╔══╝  ██╔══╝  
  ███████║██║  ██║██║     ███████╗
  ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝
  
  All 4 test suites passed in 67.1s
  
  → UI is safe to open
```

---

© 2026 Ada Computing Company · Houston, Texas
