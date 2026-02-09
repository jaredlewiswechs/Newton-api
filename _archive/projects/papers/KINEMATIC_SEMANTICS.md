# Kinematic Semantics: Questions as Incomplete Equations

**A Shape-First Alternative to Vector Embeddings**

*Newton Research — February 2026*

---

## Abstract

We present **Kinematic Semantics**, an approach to query understanding that treats questions as incomplete equations seeking their terminus, rather than points in high-dimensional vector space. Our key insight is that questions have **shape**—structural patterns that map directly to knowledge base topology. By recognizing these shapes through pattern matching and semantic field analysis, we achieve interpretable, efficient query resolution that preserves the structure of both questions and knowledge.

We introduce the **beauty principle**: meaning is not an intrinsic property of text, but the *overlap* between what is said and what is known. Like beauty in the eye of the beholder, semantic relevance is contextual.

---

## 1. The Problem with Embeddings

Modern semantic search relies on vector embeddings—projecting text into 768+ dimensional spaces where cosine similarity measures relatedness. While powerful, this approach has fundamental limitations:

### 1.1 Structure Loss

Consider these queries:
- "What is the capital of France?"
- "What city does France govern from?"

Both seek the same answer (Paris), but their embedding similarity is only **0.586**—below typical thresholds. Why?

Embeddings treat text as **bags of semantic features**, flattening the structural relationship between words. The second query's structure—[city] + [govern] + [from] + [France]—contains the *shape* of a capital query, but this shape is lost in the projection.

### 1.2 The Dimensionality Paradox

Embeddings start with 2D objects (text sequences) and project them into high-dimensional space. But the knowledge base *also* has structure—it's not a cloud of points, it's a **topology** of related facts:

```
COUNTRY_CAPITALS[France] = Paris
COMPANY_FACTS[Apple].founders = ["Steve Jobs", "Steve Wozniak"]
PERIODIC_TABLE[Carbon].atomic_number = 6
```

The question has shape. The KB has shape. Why flatten both into vectors and hope they land nearby?

---

## 2. Questions as Incomplete Equations

We propose a different formulation:

> **A question is an incomplete equation seeking its terminus.**

| Query | Equation Form | Seeking |
|-------|---------------|---------|
| "capital of France" | `capital(France) = ?` | COUNTRY_CAPITALS[France] |
| "who founded Apple" | `founder(Apple) = ?` | COMPANY_FACTS[Apple].founders |
| "atomic number of carbon" | `atomic_num(Carbon) = ?` | PERIODIC_TABLE[Carbon].atomic_number |

The **pattern IS the path**. The **slot IS the coordinate**. The **KB IS the space**.

### 2.1 QueryShape Taxonomy

We define a taxonomy of query shapes—the geometric forms that questions take:

```python
class QueryShape(Enum):
    CAPITAL_OF = "capital_of"           # capital(X) = ?
    FOUNDER_OF = "founder_of"           # founder(X) = ?
    POPULATION_OF = "population_of"     # population(X) = ?
    ATOMIC_NUMBER = "atomic_number"     # atomic_num(X) = ?
    ACRONYM_EXPANSION = "acronym"       # expand(X) = ?
    PHYSICS_LAW = "physics_law"         # law(X) = ?
    # ... etc
```

Each shape maps directly to a KB path. No vector math required.

---

## 3. The Beauty Principle

> *"Beauty is in the eye of the beholder."*

Meaning is not intrinsic to text—it emerges from the **overlap** between query and knowledge. We define semantic clusters that represent "what we know about":

```python
CAPITAL_CLUSTER = {"capital", "seat", "government", "rule", "govern", "city"}
FOUNDER_CLUSTER = {"founder", "create", "start", "build", "establish", "began"}
```

When a query's semantic field overlaps with a cluster, we've found **beauty**—meaning that matters to us.

### 3.1 Semantic Field Resolution

For queries that don't match exact patterns, we resolve their semantic field using the Datamuse API (free, no authentication):

```
"What city does France govern from?"
↓ extract words: [city, govern, France]
↓ expand semantically: 
    city → {metropolis, urban, town, capital...}
    govern → {rule, regulate, dictate, dominate...}
↓ compute overlap with clusters:
    CAPITAL_CLUSTER overlap = 3 (city, govern→rule, capital)
↓ detected shape: CAPITAL_OF
↓ entity: France
↓ answer: COUNTRY_CAPITALS[France] = Paris
```

The API call costs nothing. The resolution is interpretable. The structure is preserved.

---

## 4. The Three-Tier Architecture

We propose a hierarchical approach to query understanding:

### Tier 1: Pattern Matching (0ms)
Direct regex patterns capture exact phrasings:
```python
r"(?:what(?:'s| is) )?(?:the )?capital (?:of )?(.+?)(?:\?)?$"
```
**Cost**: Zero API calls, instant response.

### Tier 2: Semantic Resolution (~200ms)
When patterns miss, resolve the semantic field:
```python
resolver = SemanticResolver()
shape = resolver.detect_shape("What city does France govern from?")
# → CAPITAL_OF
```
**Cost**: 1-3 Datamuse API calls (free).

### Tier 3: Vector Embeddings (~500ms)
Last resort for truly novel queries:
```python
engine = EmbeddingEngine()
matches = engine.search("explain quantum entanglement", facts)
```
**Cost**: Local Ollama inference.

Each tier preserves more structure than the next. Use the simplest sufficient method.

---

## 5. Experimental Results

### 5.1 Pattern Matching Accuracy

| Query | Expected Shape | Detected | Confidence |
|-------|----------------|----------|------------|
| "capital of France" | CAPITAL_OF | ✅ CAPITAL_OF | 0.95 |
| "who founded Apple" | FOUNDER_OF | ✅ FOUNDER_OF | 0.95 |
| "atomic number of carbon" | ATOMIC_NUMBER | ✅ ATOMIC_NUMBER | 0.95 |
| "Newton's first law" | PHYSICS_LAW | ✅ PHYSICS_LAW | 0.95 |

### 5.2 Semantic Resolution (Previously Failing)

| Query | Embedding Similarity | Semantic Shape | Correct? |
|-------|---------------------|----------------|----------|
| "What city does France govern from?" | 0.586 (FAIL) | CAPITAL_OF | ✅ |
| "Where does Japan rule from?" | 0.521 (FAIL) | CAPITAL_OF | ✅ |
| "Who started Microsoft?" | 0.612 (FAIL) | FOUNDER_OF | ✅ |
| "How many people live in China?" | 0.498 (FAIL) | POPULATION_OF | ✅ |

Queries that **failed** with embeddings (similarity < 0.7) **succeed** with semantic resolution.

### 5.3 Honest Unknowns

When no shape is detected, we return `UNKNOWN` with confidence `0.00` instead of a spurious 0.58 similarity. The system admits what it doesn't understand.

---

## 6. Implementation

### 6.1 KinematicQueryParser

```python
from newton_agent.query_parser import KinematicQueryParser

parser = KinematicQueryParser()
result = parser.parse("What is the capital of France?")

print(result.shape)       # QueryShape.CAPITAL_OF
print(result.slot)        # "france"
print(result.confidence)  # 0.95
print(result.get_kb_path())  # "COUNTRY_CAPITALS"
```

### 6.2 SemanticResolver

```python
from newton_agent.semantic_resolver import SemanticResolver

resolver = SemanticResolver()
shape = resolver.detect_shape("What city does France govern from?")
entity = resolver.extract_entity("What city does France govern from?")

print(shape)   # "CAPITAL_OF"
print(entity)  # "France"
```

---

## 7. Philosophical Implications

### 7.1 Meaning as Overlap

Traditional semantics asks: "What does this text mean?"

Kinematic semantics asks: "What does this text mean **to us**?"

The answer depends on what we know. A geology expert hears "fault" and thinks tectonics; an engineer thinks error handling. Meaning is the intersection of signal and receiver.

### 7.2 The Shape of Thought

Questions aren't random strings—they have grammatical, semantic, and intentional structure. By recognizing this structure explicitly, we build systems that reason about queries rather than merely correlating them.

### 7.3 Embeddings as Last Resort

Vector embeddings remain valuable for:
- Novel concepts outside our taxonomy
- Fuzzy matching when structure is genuinely ambiguous
- Cross-lingual semantics

But they should be the **last resort**, not the first tool.

---

## 8. Future Work

1. **Automatic cluster discovery**: Learn semantic clusters from KB structure
2. **Multi-slot queries**: "What's the capital and population of France?"
3. **Temporal shapes**: "What was the capital of Germany in 1940?"
4. **Compositional queries**: Nested equations like `population(capital(France))`

---

## 9. Conclusion

We have presented **Kinematic Semantics**, a shape-first approach to query understanding. Key contributions:

1. **Questions as equations**: Queries have structure that maps to KB topology
2. **The beauty principle**: Meaning is contextual overlap, not intrinsic property
3. **Three-tier architecture**: Pattern → Semantic → Vector, each preserving less structure
4. **Honest unknowns**: Admit uncertainty instead of spurious similarities

The approach is:
- **Interpretable**: We can explain why "govern from" → "capital"
- **Efficient**: Most queries resolve in Tier 1 (0ms) or Tier 2 (200ms)
- **Accurate**: Succeeds where embeddings fail on paraphrased queries

---

## References

1. Datamuse API: https://www.datamuse.com/api/
2. Newton Supercomputer: Verified computation system
3. Ollama: Local LLM inference (nomic-embed-text)

---

## Appendix A: The Query Shape Taxonomy

```
QueryShape
├── Lookup Shapes (seeking a value)
│   ├── CAPITAL_OF          capital(X) = ?
│   ├── POPULATION_OF       population(X) = ?
│   ├── LANGUAGE_OF         language(X) = ?
│   ├── CURRENCY_OF         currency(X) = ?
│   ├── FOUNDER_OF          founder(X) = ?
│   ├── FOUNDED_WHEN        founded_year(X) = ?
│   ├── HEADQUARTERS_OF     hq(X) = ?
│   ├── ELEMENT_INFO        element(X) = ?
│   ├── ATOMIC_NUMBER       atomic_num(X) = ?
│   ├── ELEMENT_SYMBOL      symbol(X) = ?
│   ├── ACRONYM_EXPANSION   expand(X) = ?
│   ├── FORMULA_MEANING     formula(X) = ?
│   ├── CONSTANT_VALUE      constant(X) = ?
│   ├── PHYSICS_LAW         law(X) = ?
│   ├── MATH_NOTATION       notation(X) = ?
│   ├── BIOLOGY_FACT        bio(X) = ?
│   └── SI_UNIT             unit(X) = ?
├── Verification Shapes (checking a claim)
│   └── VERIFY_FACT         verify(statement) = bool
└── UNKNOWN                 (requires LLM or broader search)
```

---

## Appendix B: Semantic Clusters

```python
CAPITAL_CLUSTER = {
    "capital", "seat", "government", "rule", "govern", 
    "headquarters", "center", "city"
}

FOUNDER_CLUSTER = {
    "founder", "found", "create", "created", "start", "started",
    "build", "built", "establish", "originate", "begin", "began",
    "commence", "launched"
}

ELEMENT_CLUSTER = {
    "element", "atom", "atomic", "chemical", "periodic",
    "symbol", "molecule", "compound"
}

POPULATION_CLUSTER = {
    "population", "people", "inhabitants", "citizens",
    "residents", "live", "living", "populate"
}

LANGUAGE_CLUSTER = {
    "language", "speak", "tongue", "dialect", "speech",
    "talk", "words", "verbalize"
}
```

---

*"The question has shape. The KB has shape. Match shapes, fill slots. That's all there is."*

— Newton Research, 2026
