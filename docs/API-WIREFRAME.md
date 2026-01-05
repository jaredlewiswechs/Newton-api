# Newton API Architecture Wireframe

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                              NEWTON SUPERCOMPUTER API                                     │
│                        https://newton-api.onrender.com                                   │
│                                    (Render Web Service)                                  │
└──────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
        ┌──────────────────────────────────┼──────────────────────────────────┐
        │                                  │                                  │
        ▼                                  ▼                                  ▼
┌───────────────────┐          ┌───────────────────┐          ┌───────────────────┐
│   STATIC ROUTES   │          │    API ROUTES     │          │    SYSTEM         │
│   (HTML/JS/CSS)   │          │  (JSON endpoints) │          │    ROUTES         │
└───────────────────┘          └───────────────────┘          └───────────────────┘
        │                                  │                          │
        ├── /                              │                          ├── /health
        ├── /app                           │                          ├── /metrics
        ├── /teachers                      │                          ├── /docs (Swagger)
        ├── /builder                       │                          └── /redoc
        └── /login                         │
                                           │
        ┌──────────────────────────────────┴──────────────────────────────────┐
        │                                                                      │
        ▼                                                                      ▼
┌─────────────────────────────────────┐          ┌─────────────────────────────────────┐
│         CORE VERIFICATION           │          │           EDUCATION MODULE          │
│                                     │          │                                     │
│  POST /ask        Newton Query      │          │  POST /education/lesson   NES Plan  │
│  POST /verify     Safety Check      │          │  POST /education/slides   Deck Gen  │
│  POST /calculate  Verified Compute  │          │  POST /education/assess   Analyze   │
│  POST /constraint CDL Evaluate      │          │  POST /education/plc      PLC Rpt   │
│  POST /ground     Evidence Verify   │          │  GET  /education/teks     TEKS DB   │
│  POST /statistics MAD Analysis      │          │  GET  /education/teks/{code}        │
└─────────────────────────────────────┘          └─────────────────────────────────────┘
        │                                                      │
        ▼                                                      ▼
┌─────────────────────────────────────┐          ┌─────────────────────────────────────┐
│        TEACHER'S AIDE DB            │          │        INTERFACE BUILDER            │
│                                     │          │                                     │
│  ── STUDENTS ──                     │          │  GET  /interface/templates          │
│  POST /teachers/students   Add      │          │  GET  /interface/templates/{id}     │
│  GET  /teachers/students   List     │          │  POST /interface/build     Gen UI   │
│  GET  /teachers/students/{id}       │          │  GET  /interface/components         │
│                                     │          │  GET  /interface/info               │
│  ── CLASSROOMS ──                   │          │                                     │
│  POST /teachers/classrooms          │          └─────────────────────────────────────┘
│  GET  /teachers/classrooms                                   │
│  GET  /teachers/classrooms/{id}                              ▼
│  GET  /teachers/classrooms/{id}/groups  ◄── Differentiation  ┌────────────────────────┐
│  GET  /teachers/classrooms/{id}/reteach                      │    JESTER ANALYZER     │
│                                     │                        │                        │
│  ── ASSESSMENTS ──                  │                        │  POST /jester/analyze  │
│  POST /teachers/assessments         │                        │  POST /jester/cdl      │
│  POST /teachers/assessments/{id}/scores                      │  GET  /jester/info     │
│  POST /teachers/assessments/{id}/quick-scores ◄── Name-based │  GET  /jester/languages│
└─────────────────────────────────────┘                        └────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐          ┌─────────────────────────────────────┐
│         CHATBOT COMPILER            │          │         VOICE INTERFACE (MOAD)      │
│                                     │          │                                     │
│  POST /chatbot/compile   NL→Safe    │          │  POST /voice/ask      NL → App     │
│  POST /chatbot/classify  Risk Eval  │          │  POST /voice/stream   Streaming    │
│  POST /chatbot/batch     Batch      │          │  POST /voice/intent   Classify     │
│  GET  /chatbot/metrics              │          │  GET  /voice/patterns              │
│  GET  /chatbot/types                │          │  GET  /voice/demo                  │
│  GET  /chatbot/example              │          │                                     │
│                                     │          └─────────────────────────────────────┘
│  POST /extract           Fuzzy→CDL  │
│  POST /extract/verify    Plan Check │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐          ┌─────────────────────────────────────┐
│           CARTRIDGES                │          │         STORAGE & AUDIT             │
│       (Media Specification)         │          │                                     │
│                                     │          │  ── VAULT (Encrypted Storage) ──    │
│  POST /cartridge/visual   SVG       │          │  POST /vault/store                  │
│  POST /cartridge/sound    Audio     │          │  POST /vault/retrieve               │
│  POST /cartridge/sequence Video     │          │                                     │
│  POST /cartridge/data     Report    │          │  ── LEDGER (Audit Trail) ──         │
│  POST /cartridge/rosetta  Code Gen  │          │  GET  /ledger                       │
│  POST /cartridge/auto     Auto      │          │  GET  /ledger/{index}               │
│  GET  /cartridge/info               │          │  GET  /ledger/certificate/{index}   │
└─────────────────────────────────────┘          │                                     │
        │                                        │  ── MERKLE ANCHORING ──             │
        ▼                                        │  GET  /merkle/anchors               │
┌─────────────────────────────────────┐          │  POST /merkle/anchor                │
│        GLASS BOX (Policy)           │          │  GET  /merkle/proof/{index}         │
│                                     │          │  GET  /merkle/latest                │
│  GET  /policy            Active     │          └─────────────────────────────────────┘
│  POST /policy            Create     │
│  DELETE /policy/{id}     Remove     │
│                                     │          ┌─────────────────────────────────────┐
│  ── NEGOTIATOR ──                   │          │       AUTH & LICENSING              │
│  GET  /negotiator/pending           │          │                                     │
│  POST /negotiator/request           │          │  GET  /login                        │
│  POST /negotiator/approve/{id}      │          │  POST /parccloud/signup             │
│  POST /negotiator/reject/{id}       │          │  POST /parccloud/signin             │
└─────────────────────────────────────┘          │  POST /parccloud/logout             │
                                                 │  GET  /parccloud/verify             │
                                                 │                                     │
                                                 │  POST /license/verify               │
                                                 │  GET  /license/info                 │
                                                 │  POST /webhooks/gumroad             │
                                                 └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════

                              DEPLOYMENT ARCHITECTURE

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    RENDER CLOUD                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                        newton-api (Web Service)                                  │   │
│  │                    https://newton-api.onrender.com                               │   │
│  ├─────────────────────────────────────────────────────────────────────────────────┤   │
│  │  Runtime: Python 3.11.4                                                          │   │
│  │  Workers: 4 (Gunicorn + Uvicorn)                                                 │   │
│  │  Entry:   newton_supercomputer:app                                               │   │
│  │  Health:  /health                                                                │   │
│  │                                                                                  │   │
│  │  Serves:                                                                         │   │
│  │    • All API endpoints (117 routes)                                              │   │
│  │    • Static frontends (/app, /teachers, /builder)                                │   │
│  │    • API documentation (/docs, /redoc)                                           │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                               │
│                                         │ (optional separate deployment)                │
│                                         ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                     newton-phone (Static Site) [OPTIONAL]                        │   │
│  │                   https://newton-phone.onrender.com                              │   │
│  ├─────────────────────────────────────────────────────────────────────────────────┤   │
│  │  Runtime: Static                                                                 │   │
│  │  CDN:     Render Global CDN                                                      │   │
│  │  Cache:   1 hour                                                                 │   │
│  │                                                                                  │   │
│  │  Routes:                                                                         │   │
│  │    /          → Newton Phone home                                                │   │
│  │    /app/*     → Newton Supercomputer SPA                                         │   │
│  │    /teachers/* → Teacher's Aide SPA                                              │   │
│  │    /builder/* → Interface Builder SPA                                            │   │
│  │                                                                                  │   │
│  │  API calls → https://newton-api.onrender.com                                     │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════

                              REQUEST FLOW

     ┌────────────┐
     │   CLIENT   │
     │  (Browser) │
     └─────┬──────┘
           │
           │ HTTPS Request
           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               RENDER LOAD BALANCER                                        │
│                              (TLS Termination, CDN)                                       │
└────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                   GUNICORN                                                │
│                              (4 Worker Processes)                                         │
└────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                              UVICORN WORKER                                               │
│                           (ASGI, Async Support)                                           │
└────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                FASTAPI APP                                                │
│                          newton_supercomputer:app                                         │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│    │    CORS      │───▶│ Rate Limit   │───▶│  parcCloud   │───▶│   Router     │         │
│    │  Middleware  │    │  (100/min)   │    │   Gateway    │    │              │         │
│    └──────────────┘    └──────────────┘    │  (optional)  │    └──────┬───────┘         │
│                                            └──────────────┘           │                  │
│                                                                       ▼                  │
│    ┌────────────────────────────────────────────────────────────────────────────────┐   │
│    │                           ROUTE HANDLERS                                        │   │
│    ├────────────────────────────────────────────────────────────────────────────────┤   │
│    │                                                                                 │   │
│    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │   │
│    │  │   FORGE     │  │   VAULT     │  │   LEDGER    │  │  CARTRIDGE  │           │   │
│    │  │ (Verify)    │  │ (Store)     │  │ (Audit)     │  │ (Generate)  │           │   │
│    │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │   │
│    │                                                                                 │   │
│    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │   │
│    │  │  EDUCATION  │  │  TEACHER DB │  │  INTERFACE  │  │   JESTER    │           │   │
│    │  │ (Lessons)   │  │ (Students)  │  │ (UI Build)  │  │ (Analyze)   │           │   │
│    │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │   │
│    │                                                                                 │   │
│    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │   │
│    │  │   VOICE     │  │  CHATBOT    │  │   POLICY    │  │   MERKLE    │           │   │
│    │  │ (MOAD)      │  │ (Compiler)  │  │ (Glass Box) │  │ (Proofs)    │           │   │
│    │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │   │
│    │                                                                                 │   │
│    └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
                               ┌───────────────────┐
                               │  JSON Response    │
                               │  + Headers        │
                               │  (X-RateLimit-*)  │
                               └───────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════

                              API ENDPOINT SUMMARY

┌────────────────────────┬───────┬─────────────────────────────────────────────────────────┐
│ CATEGORY               │ COUNT │ KEY ENDPOINTS                                           │
├────────────────────────┼───────┼─────────────────────────────────────────────────────────┤
│ Core Verification      │   8   │ /ask, /verify, /calculate, /constraint, /ground        │
│ Education              │   8   │ /education/lesson, /slides, /assess, /plc, /teks       │
│ Teacher's Aide DB      │  20   │ /teachers/students, /classrooms, /assessments          │
│ Chatbot & Extraction   │  10   │ /chatbot/compile, /extract, /chatbot/classify          │
│ Voice Interface        │   8   │ /voice/ask, /voice/stream, /voice/intent               │
│ Cartridges             │   7   │ /cartridge/visual, /sound, /sequence, /data, /auto     │
│ Storage & Audit        │   8   │ /vault/store, /ledger, /merkle/anchor                  │
│ Interface Builder      │   5   │ /interface/templates, /build, /components              │
│ Jester Analyzer        │   4   │ /jester/analyze, /cdl, /languages                      │
│ Policy (Glass Box)     │   8   │ /policy, /negotiator/request, /approve, /reject        │
│ Auth & Licensing       │  11   │ /login, /parccloud/*, /license/verify                  │
│ System & Health        │   4   │ /health, /metrics, /docs, /redoc                       │
│ Static Frontend        │   6   │ /, /app, /teachers, /builder, /frontend/*              │
├────────────────────────┼───────┼─────────────────────────────────────────────────────────┤
│ TOTAL                  │ 117   │                                                         │
└────────────────────────┴───────┴─────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════

                              FRONTEND → API CONNECTIONS

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            TEACHER'S AIDE (/teachers)                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │  Lesson Planner │    ───▶  │  POST /education/lesson                          │      │
│  │                 │          │  POST /education/slides                          │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │ Grade & Analyze │    ───▶  │  POST /education/assess                          │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │   PLC Report    │    ───▶  │  POST /education/plc                             │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │  TEKS Browser   │    ───▶  │  GET /education/teks                             │      │
│  │                 │          │  POST /education/teks/search                     │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          INTERFACE BUILDER (/builder)                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │   Templates     │    ───▶  │  GET /interface/templates                        │      │
│  │     View        │          │  GET /interface/templates/{id}                   │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │    Builder      │    ───▶  │  POST /interface/build                           │      │
│  │    Canvas       │          │                                                  │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │   Components    │    ───▶  │  GET /interface/components                       │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         NEWTON SUPERCOMPUTER (/app)                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │   Ask Newton    │    ───▶  │  POST /ask                                       │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │    Verify       │    ───▶  │  POST /verify                                    │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │   Calculate     │    ───▶  │  POST /calculate                                 │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
│  ┌─────────────────┐          ┌─────────────────────────────────────────────────┐      │
│  │   Cartridges    │    ───▶  │  POST /cartridge/auto                            │      │
│  └─────────────────┘          └─────────────────────────────────────────────────┘      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════

                    THE NEWTON INVARIANT: 1 == 1

              "The constraint IS the instruction"
              Execute only when verification passes.

═══════════════════════════════════════════════════════════════════════════════════════════
```

## Render Deployment URLs

| Service | URL | Type |
|---------|-----|------|
| Newton API | https://newton-api.onrender.com | Web Service (Python) |
| Newton Phone | https://newton-phone.onrender.com | Static Site (optional) |

## Quick Start

```bash
# Local Development
uvicorn newton_supercomputer:app --host 0.0.0.0 --port 8000 --reload

# Production (Render auto-deploys from main branch)
# render.yaml handles configuration
```

## Health Check

```bash
curl https://newton-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Newton Supercomputer",
  "version": "1.0.0"
}
```
