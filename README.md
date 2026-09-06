# LapIQ — Laptop Purchase Intelligence Platform

> An engineering reference implementation of a multi-criteria decision system built with Clean Architecture, deterministic candidate ranking, and asynchronous Server-Sent Events (SSE) explanation streaming.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139.2-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.2-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-8.0-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Gemini API](https://img.shields.io/badge/Gemini_API-2.5_Flash-8E7CC3?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![CI](https://github.com/rohit-sinha-76/LapIQ-reccomendation-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/rohit-sinha-76/LapIQ-reccomendation-engine/actions)
[![Pytest](https://img.shields.io/badge/Tests-58%20Passed-2EA44F?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)

---

## Motivation & Problem Statement

Consumer electronics purchases in the Indian laptop market present distinct decision-making challenges:

1. **Spec Sheet Ambiguity**: Technical specifications are presented inconsistently across retailers. Factors critical to performance (such as CPU sustained clock speeds, Total Graphics Power / TGP, and thermal headroom) are frequently obscured behind marketing labels.
2. **Affiliate & Commercial Bias**: Consumer review platforms are heavily monetized through commercial retail affiliate incentives, often prioritizing high-margin SKUs over objective performance-to-price metrics.
3. **Generative Hallucination Risks**: When prompted directly for product recommendations, standard generative Large Language Models (LLMs) frequently hallucinate non-existent hardware configurations (e.g. invalid CPU-GPU pairings, fabricated display refresh rates, or incorrect retail pricing).

LapIQ addresses these problems through **architectural state isolation**: all candidate filtering, multi-attribute scoring, and ranking decisions are strictly deterministic and mathematically audited. The generative model (Gemini 2.5 Flash) is strictly bounded to post-ranking natural-language explanation streaming over Server-Sent Events (SSE).

---

## Dataset Scope & Currency

> [!NOTE]
> Recommendations are generated from an audited catalog of 479 Indian market laptop configurations. Like any catalog-based system, recommendations depend on dataset freshness and reflect the hardware generations and baseline prices at the time of data collection. Retail prices fluctuate and newer silicon will naturally age a static dataset over time.

---

## System Architecture

The application is structured according to Clean Architecture principles, ensuring that core business rules remain completely isolated from database drivers, external APIs, and presentation frameworks.

```text
+-------------------------------------------------------------------+
|                       PRESENTATION LAYER                          |
|  Next.js 16 (App Router) | React 19 | Framer Motion (motion/react) |
|  Recommendation Form     | Comparison View  | Inspector Scores UI │
|  useSSEStream Hook (EventSource Client)                           |
+-------------------------------------------------------------------+
                                  │ REST + SSE
+-------------------------------------------------------------------+
|                         API LAYER (FastAPI)                       |
|  POST /api/v1/recommend      | GET /api/v1/recommend/{id}/stream |
|  GET /api/v1/health          | GET /api/meta                      |
+-------------------------------------------------------------------+
                                  │ Dependency Injection
+-------------------------------------------------------------------+
|                      APPLICATION LAYER                            |
|  RecommendationOrchestrator  | HybridRetriever (Extension Spec)   |
|  ExplanationBuilder          | EvaluationRunner                   |
+-------------------------------------------------------------------+
                                  │ Domain Interfaces
+-------------------------------------------------------------------+
|                        DOMAIN LAYER                               |
|  Catalog Module   |  Pricing Module      | Evidence Module        |
|  Scoring Engine   |  Business Rules      | Ranking Engine         |
|  Confidence Scorer|  RecommendationPolicy| Inspector Engine       |
+-------------------------------------------------------------------+
                                  │ Repository Pattern
+-------------------------------------------------------------------+
|                    INFRASTRUCTURE LAYER                           |
|  PostgreSQL 16 + pgvector (Relational Specs + 1536-dim Vectors)   |
|  Redis 8.0 (Multi-tier session, request & candidate cache)        |
|  GeminiReasoningProvider (google-genai SDK async streaming)       |
+-------------------------------------------------------------------+
```

### Architectural Invariants

1. **Deterministic Candidate Selection**: The LLM is never permitted to filter or rank products. All candidate ranking is executed via pure, rule-based mathematical scoring.
2. **Domain Layer Isolation**: The domain layer contains zero imports from the infrastructure or API layer.
3. **LLM Fault Tolerance**: If the Gemini API experiences network timeouts, 429 rate limits, or upstream outages, the orchestrator immediately falls back to structured markdown summaries derived from database specifications.
4. **SSE Buffering Mitigation**: Reverse proxy configurations explicitly disable downstream buffer caching (`proxy_buffering off; X-Accel-Buffering no;`), ensuring token streaming arrives at the client without artificial latency.

---

## Core Engineering Features

- **Multi-Criteria Scoring Engine**: Evaluates candidate variants across normalized performance benchmarks (Cinebench R23 multi-core scores and 3DMark GPU benchmarks), value headroom relative to budget, and segment suitability weights:
  - **Students**: Weights battery efficiency, portability (<1.8 kg), and value-for-money.
  - **Gamers**: Weights dedicated GPU compute, high refresh rate panels (≥120Hz), and thermal ceiling.
  - **Creators**: Weights multi-core CPU capacity, memory headroom (≥16GB), and panel color gamut.
  - **Professionals**: Weights chassis build, display resolution, ergonomics, and weight.
- **Two-Phase Request Lifecycle**:
  - Phase 1 (`POST /api/v1/recommend`): Relational filtering, scoring, and ranking complete in under 20ms. The result context is cached in Redis with an explicit TTL.
  - Phase 2 (`GET /api/v1/recommend/{id}/stream`): Client mounts the SSE stream to asynchronously render natural-language synthesis without blocking the initial UI paint.
- **Audited Catalog Pipeline**: 479 deduplicated Indian market configurations sanitized from 941 raw Flipkart e-commerce records via an 8-point regression audit (`scripts/verify_knowledge_base.py`).

---

## Technical Specifications

| Layer | Technology | Version | Engineering Rationale |
|---|---|---|---|
| **Backend Language** | Python | 3.13 | Strict type annotations, standard asyncio primitives |
| **Backend Framework** | FastAPI | 0.139.2 | Asynchronous REST endpoints, OpenAPI generation & Pydantic v2 schemas |
| **ASGI Server** | Uvicorn | 0.51.0 | Asynchronous ASGI runtime |
| **Database ORM** | SQLAlchemy (async) | 2.0.51 | Async engine with `Mapped[]` and `mapped_column()` typing |
| **Database Driver** | asyncpg | 0.30.0 | High-throughput asynchronous PostgreSQL driver |
| **Relational & Vector DB** | PostgreSQL + pgvector | 16 | Relational specs catalog + 1536-dim vector embeddings |
| **Cache & Session** | Redis | 8.0.0 | Request state caching for SSE correlation and candidate retrieval cache |
| **AI LLM SDK** | `google-genai` | 1.0.0 | Official Google GenAI SDK for async `client.aio.models` streaming |
| **Frontend Framework** | Next.js | 16.2.10 | App Router with Server & Client components |
| **UI Runtime** | React | 19.0.0 | Concurrent React runtime |
| **Animations** | motion (`motion/react`) | 12.42.0 | Micro-interactions and modal transitions |
| **Icons** | lucide-react | 1.25.0 | SVG icon library |
| **Testing Suite** | pytest / pytest-asyncio | 9.1.1 / 1.4.0 | Unit, integration, edge-case, and benchmark test suites |

---

## Quickstart & Local Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.13+
- Node.js 20+
- Google Gemini API Key ([Google AI Studio](https://aistudio.google.com/))

---

### Step 1: Environment Configuration

```bash
git clone https://github.com/rohit-sinha-76/LapIQ-reccomendation-engine.git
cd LapIQ-reccomendation-engine

# Copy environment variable template
cp .env.example .env
```

Configure your `.env` file with your credentials:
```env
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-minimum-32-chars-length
GEMINI_API_KEY=your_gemini_api_key_here
```

---

### Step 2: Running via Docker Compose (Recommended)

Launch the complete 5-container architecture (PostgreSQL 16 + pgvector, Redis 8, FastAPI backend, background worker, Next.js frontend):

```bash
docker compose up -d
```

Service endpoints:
- Frontend Application: [http://localhost:3000](http://localhost:3000)
- Hardware Comparison: [http://localhost:3000/compare](http://localhost:3000/compare)
- FastAPI Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Service Health Endpoint: [http://localhost:8000/health](http://localhost:8000/health)

---

### Step 3: Manual Local Development

If executing services directly on host environments:

#### 1. Start Supporting Services:
```bash
docker compose up -d postgres redis
```

#### 2. Configure Backend:
```bash
cd backend
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

pip install -e .[dev]
```

#### 3. Ingest Data & Run Migrations:
```bash
python ../scripts/verify_knowledge_base.py
python ../scripts/generate_embeddings.py
```

#### 4. Start Application Servers:
Terminal 1 (Backend):
```bash
uvicorn lapiq.api.main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm install
npm run dev
```

---

## Testing & Quality Assurance

```bash
# Execute Pytest backend test suite
cd backend
pytest tests/ -v --asyncio-mode=auto

# Run Persona Regression Benchmark
python ../scripts/run_evaluation_benchmark.py
```

### Persona Regression Suite Summary

| Persona ID | Target Profile | Segment | Budget (INR) | Top-1 Verification | Top-3 Verification |
|---|---|---|---|---|---|
| `p-student-01` | CS Student | Students | INR 60,000 | PASS | PASS |
| `p-gamer-01` | Competitive Gamer | Gamers | INR 135,000 | PASS | PASS |
| `p-creator-01` | Video Editor | Creators | INR 165,000 | PASS | PASS |
| `p-pro-01` | Corporate Professional | Professionals | INR 75,000 | PASS | PASS |
| `p-budget-01` | Budget Student | Students | INR 35,000 | PASS | PASS |

---

## API Reference

### `POST /api/v1/recommend`
Executes candidate filtering, multi-criteria scoring, and assigns confidence ratings.

**Request Payload:**
```json
{
  "budget_inr": 60000,
  "use_case": "software development and occasional photo editing",
  "target_segment": "Students",
  "min_ram_gb": 8,
  "requires_dedicated_gpu": false,
  "prefers_lightweight": true
}
```

**Response Payload:**
```json
{
  "request_id": "9a2f4c1e-7210-4d32-b918-0246813579ab",
  "is_partial": false,
  "recommendations": [
    {
      "variant_id": 142,
      "laptop_brand": "Acer",
      "laptop_model": "Aspire 14 Core i7 13th Gen",
      "price_inr": 58990,
      "min_discount_price_inr": 51911,
      "max_mrp_price_inr": 69608,
      "max_discount_percentage": 25.4,
      "cpu_model": "Intel Core i7-1355U",
      "gpu_model": "Intel Iris Xe",
      "ram_gb": 16,
      "storage_gb": 512,
      "storage_type": "SSD",
      "display_size_inches": 14.0,
      "total_score": 0.81,
      "confidence_score": 0.94
    }
  ]
}
```

### `GET /api/v1/recommend/{request_id}/stream`
Streams tokenized natural-language justification over Server-Sent Events (`text/event-stream`).

---

## Repository Structure

```text
lapiq/
├── .github/
│   └── workflows/ci.yml        # Automated GitHub Actions CI (pytest + type-check)
├── backend/
│   ├── alembic/                # Database migration scripts
│   ├── src/lapiq/
│   │   ├── api/                # FastAPI routes, CORS & schemas
│   │   ├── application/        # Orchestrator & retriever services
│   │   ├── core/               # Configuration settings (Pydantic BaseSettings)
│   │   ├── domain/             # Pure business rules, scoring, & ranking
│   │   └── infrastructure/     # Database ORM, Redis cache, & Gemini provider
│   └── tests/                  # Pytest unit, integration & evaluation suite
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router (home, recommend, compare)
│   │   ├── components/         # UI components (Form, Cards, Comparison, Inspector)
│   │   ├── hooks/              # SSE event-stream hook
│   │   └── types/              # TypeScript data interfaces
├── data/                       # Curated datasets (knowledge_base.csv, laptops_clean.json)
├── scripts/                    # Ingestion, verification, embedding & benchmark CLI scripts
├── docker-compose.yml          # Container orchestration stack
├── evaluation_report.md        # Persona benchmark validation artifact
└── README.md                   # System documentation
```

---

## Architectural Trade-offs & Engineering Decisions

1. **Deterministic Scoring vs. Generative Recommendations**:
   Recommendation ranking was deliberately implemented using a rule-based scoring engine rather than prompt-engineered LLM outputs. In product catalogs with strict numeric boundaries (budgets, RAM capacity, display sizes), mathematical scoring provides guarantees of idempotency, zero hallucination, and sub-millisecond calculation times.
2. **Decoupled Two-Phase Request Flow**:
   Streaming an LLM response directly during a synchronous recommendation request introduces 1.5 to 3.0 seconds of latency before any candidate cards can render. Decoupling the pipeline into a fast JSON response (`POST /recommend`) followed by an asynchronous EventSource stream (`GET /stream`) ensures the user interface paints immediately.
3. **Relational Hot-Path vs. Vector Search Scalability**:
   While `HybridRetriever` implements vector similarity search via `pgvector` for unstructured semantic catalog queries, the primary online recommendation path deliberately relies on indexed relational B-tree lookups. On catalogs under 1,000 SKUs, relational filters execute in under 5ms, avoiding the index scan overhead of high-dimensional vector distances until scale demands it.

---

## License

Distributed under the MIT License.
