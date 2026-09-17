# 🚀 AI PlacementOS — Autonomous Multi-Agent Career Intelligence & Placement Operating System

> **Enterprise-grade, zero-mock, deterministic-first autonomous career intelligence platform** powered by LangGraph, FastAPI, PostgreSQL (pgvector), Redis, and Next.js 14.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00.svg)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_+_pgvector-4169E1.svg?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Pytest](https://img.shields.io/badge/Pytest-106%2F106%20Passing-brightgreen.svg?logo=pytest&logoColor=white)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---


## 🌟 Master 15-Phase Architecture & Completion Matrix

All **15 Phases** are fully implemented with **zero mock data**, deterministic calculations, real-time database state, and bi-directional Career Digital Twin synchronization:

| Phase | Module | Status | Technical Capabilities |
| :--- | :--- | :---: | :--- |
| **Phase 1** | **Monorepo & Design System** | ✅ | Next.js 14 App Router, Dark Neon Glassmorphic design tokens, responsive sidebar & headers |
| **Phase 2** | **Auth & Career Digital Twin** | ✅ | JWT Bearer auth, refresh token rotation, canonical skill graph, confidence-weighted evidence engine |
| **Phase 3** | **Resume Intel & ATS Engine** | ✅ | PDF/DOCX multi-section extraction, ATS keyword matching, quantification scoring, LaTeX generator |
| **Phase 4** | **Job Discovery & Ingestion** | ✅ | Multi-provider job scraping (Greenhouse, Lever, LinkedIn), SHA-256 deduplication, skill extraction |
| **Phase 5** | **Hybrid Matching Engine** | ✅ | 6-factor hybrid match scoring (Dense embeddings + Required + Preferred + Exp + Edu + Project) |
| **Phase 6** | **Skill Gap Analysis & DAG** | ✅ | Topological sort prerequisite DAG, critical path blockers, estimated effort calculations |
| **Phase 7** | **Adaptive Learning Roadmap** | ✅ | Milestone sequencing, multi-modal tasks (DSA, Labs, System Design), Twin progress synchronization |
| **Phase 8** | **DSA Engine & AST Sandbox** | ✅ | Multi-test runner, AST Big-O static complexity analyzer ($O(1)$, $O(N)$, $O(N^2)$, $O(N^3)$), memory & runtime profiling |
| **Phase 9** | **Mock Interview Simulation** | ✅ | Turn-by-turn simulation, 4-rubric heuristics (STAR structure, Technical depth, Clarity, Tradeoffs) |
| **Phase 10** | **Hybrid RAG & Knowledge Graph** | ✅ | Recursive semantic chunking, dense cosine similarity, sparse Okapi BM25, RRF ($k=60$), grounded citations |
| **Phase 11** | **LangGraph Multi-Agent Copilot**| ✅ | Unified StateGraph router executing multi-agent pipelines across Skill Gaps, RAG, Roadmaps, DSA & Interviews |
| **Phase 12** | **SaaS Dashboard & Pipeline** | ✅ | Application Kanban board, CSV export, interview stage tracking, platform observability metrics |
| **Phase 13** | **Security Hardening & Guardrails**| ✅ | Token bucket sliding-window rate limiter, AST execution sandbox, prompt injection scanner, PII masking |
| **Phase 14** | **Evaluation & Benchmark Suite** | ✅ | RAG Faithfulness SLA ($\ge 95\%$), 4-rubric interview calibration, AST complexity profiler benchmarks |
| **Phase 15** | **Production Readiness & CI/CD** | ✅ | Multi-stage Dockerfiles, Docker Compose stack, GitHub Actions CI/CD matrix, deployment health probes |

---

## 💎 Signature Platform Highlights

- **🏗️ Project Lab (`/projects`)**: 5 production capstone tracks (Autonomous GraphRAG, Distributed Raft Store, C++20 Limit Order Book, Kubernetes GitOps Engine, CRDT Architecture Studio) with interactive system diagrams, recruiter STAR bullet points, and 1-click Skill Twin evidence sync.
- **🛡️ GitHub Portfolio Auditor (`/github`)**: Recruiter Quality Score meter (0–100) scoring across README clarity (35%), Architecture docs (25%), CI/CD automation (20%), and Git hygiene (20%) with copyable fixes and PlacementOS Verified README badges.
- **📊 Applications Pipeline Tracker (`/applications`)**: 1-click Kanban stage advance/rewind steppers, CSV data export for spreadsheet tracking, dynamic salary formatting (USD/INR/EUR), and direct links to mock interview prep.
- **⚡ AST Big-O Complexity Profiler & DSA Sandbox (`/dsa`)**: In-browser Python code execution with static AST Big-O runtime/memory complexity analysis without external execution vulnerabilities.
- **🎙️ AI Mock Interview Simulation Studio (`/interview`)**: Interactive turn-by-turn simulation scored against STAR adherence, technical depth, clarity, and architectural tradeoffs.
- **🧠 Hybrid GraphRAG Retrieval Engine (`/rag`)**: Reciprocal Rank Fusion (RRF $k=60$) combining dense semantic vectors and sparse Okapi BM25 keyword matching with knowledge graph citation verification.

----

## 🏛️ System Architecture

```mermaid
graph TD
   User["👤 Candidate / Placement Aspirant"]\

    subgraph Frontend["Frontend Tier (Next.js 14 Standalone)"]
        WebUI["Web Application (20 Pre-Rendered Routes)"]
        Dashboard["Executive Dashboard & Career Twin"]
        InterviewRoom["Interactive Mock Interview Studio"]
        DSASandbox["DSA Editor & AST Profiler"]
        KanbanBoard["Application Pipeline Kanban"]
        BenchmarkQA["Evaluation & QA Dashboard"]
    end

    subgraph Backend["Backend API Gateway (FastAPI + LangGraph)"]
        API["FastAPI 0.115+ Async Core"]
        SecurityMW["Security Headers & Sliding-Window Rate Limiter"]
        Guardrails["AST Code Sandbox & Prompt Injection Guardrails"]
        Orchestrator["LangGraph Multi-Agent Orchestrator"]

        subgraph Agents["Specialist Autonomous AI Agents"]
            ResumeAgent["Resume Intelligence & ATS Agent"]
            JobAgent["Job Discovery & Ingestion Agent"]
            MatchEngine["Hybrid Job-Resume Matching Engine"]
            SkillGapAgent["Skill Gap Analysis & Prerequisite DAG"]
            RoadmapAgent["Adaptive Learning Roadmap Generator"]
            DSAAgent["DSA Engine & Sandbox Runner"]
            InterviewAgent["Mock Interview Simulation Agent"]
            RAGAgent["Hybrid GraphRAG Retrieval Agent"]
            EvalAgent["Automated Benchmark & QA Agent"]
        end
    end

    subgraph Data["Persistence & Storage Layer"]
        PG[("PostgreSQL 16 + pgvector")]
        RedisCache[("Redis 7 Distributed Cache")]
    end

    User --> WebUI
    WebUI --> API
    API --> SecurityMW
    SecurityMW --> Guardrails
    Guardrails --> Orchestrator
    Orchestrator --> Agents
    Agents --> PG
    Agents --> RedisCache
```
---

## 📂 Monorepo Structure

```text
AI PlacementOS/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD test, lint & build matrix
├── apps/
│   ├── api/                       # FastAPI Async Backend
│   │   ├── app/
│   │   │   ├── api/v1/endpoints/  # 15 domain REST endpoints (Auth, Twin, RAG, etc.)
│   │   │   ├── core/              # Security, Database, Rate Limiter, Guardrails
│   │   │   ├── models/            # SQLAlchemy 2.0 ORM database models
│   │   │   ├── schemas/           # Pydantic v2 validation schemas
│   │   │   └── services/          # Deterministic business logic engines
│   │   ├── scripts/               # Database seeding and health probes
│   │   ├── tests/                 # 106 unit & integration tests (100% passing)
│   │   ├── Dockerfile             # Production multi-worker API container
│   │   └── requirements.txt
│   │
│   └── web/                       # Next.js 14 App Router Frontend
│       ├── src/
│       │   ├── app/               # 20 standalone client pages
│       │   ├── components/        # Glassmorphic UI components & Sidebar navigation
│       │   ├── context/           # AuthContext & global state providers
│       │   └── lib/               # API clients & design tokens
│       ├── Dockerfile             # Production 3-stage Alpine container
│       └── package.json
│
├── docs/                          # Detailed Phase 1 to 15 walkthrough specifications
├── scripts/
│   └── healthcheck.py             # Automated service readiness probe
├── docker-compose.yml             # Complete 4-service production container stack
├── .env.example                   # Global configuration template
└── README.md
```

---

## 🛠️ Quick Start Guide

### Option 1: Local Development

#### 1. Backend Setup
```bash
cd apps/api
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

#### 2. Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```
- Web Application: `http://localhost:3000`

---

### Option 2: Production Deployment with Docker Compose

To launch the full containerized stack (PostgreSQL + pgvector, Redis, FastAPI Backend, Next.js Frontend):

```bash
docker compose up --build -d
```

Verify service readiness with the built-in health probe:
```bash
python scripts/healthcheck.py
```
---

## 🧪 Automated Testing & Quality Gating

Execute the complete backend test suite:
```bash
cd apps/api
python -m pytest tests/
```
Output:
```text
============================ 106 passed in 48.22s =============================
```

---

## 📄 License
MIT License. Built for placement preparation, skill mastery, and autonomous career acceleration.
