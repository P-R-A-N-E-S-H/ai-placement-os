# AI PlacementOS — System Design & Architecture Document

## 1. System Philosophy
AI PlacementOS is built around three core pillars:
1. **Deterministic Foundations First**: Wherever deterministic logic provides consistency (hybrid scoring formulas, skill taxonomy graphs, ATS checklist audits, RBAC authorization, JWT validation), rule-based algorithms are used. LLMs are reserved for non-deterministic cognitive tasks (intent parsing, contextual explanation, dynamic interview dialogue).
2. **Explicit Multi-Agent State Machine**: Powered by LangGraph with strongly typed state transitions (`CareerState`), bounded iteration limits, and human-in-the-loop approval gates.
3. **Defense-in-Depth Security**: All external input (resumes, job listings, chat prompts) crosses an input sanitization boundary before reaching LLMs or database execution.

---

## 2. Component Topology

* **FastAPI Backend (`apps/api`)**: High-concurrency async REST and Server-Sent Event gateway.
* **Next.js 14 Web Frontend (`apps/web`)**: Modern React Server Components + Client Components with Tailwind CSS, Lucide icons, Framer Motion, and Recharts.
* **PostgreSQL + pgvector**: Relational storage for profiles, jobs, interviews, submissions with vector search on embeddings.
* **Redis**: Ephemeral cache, session store, and background task queue.
* **LangGraph Agent Runtime**: Autonomous career orchestrator coordinating specialist agents.
