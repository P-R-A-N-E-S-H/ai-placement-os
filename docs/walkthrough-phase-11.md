# Phase 11: LangGraph Multi-Agent Orchestrator & AI Career Copilot — Walkthrough

## Overview
Phase 11 implements the central **LangGraph Multi-Agent Orchestrator** and conversational **AI Career Copilot** in AI PlacementOS. It coordinates all specialized domain agents into an autonomous state-graph workflow:

```
                            USER HIGH-LEVEL PLACEMENT GOAL
                                          │
                                          ▼
                      ┌─────────────────────────────────────────┐
                      │        Supervisor / Planner Node        │
                      │  • Goal Intent Decomposition            │
                      │  • Multi-Agent DAG Plan Generation      │
                      └───────────────────┬─────────────────────┘
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  ▼                       ▼                       ▼
      ┌───────────────────────┐ ┌───────────────────┐ ┌───────────────────────┐
      │  Skill Gap DAG Agent  │ │  Roadmap Agent    │ │   DSA Sandbox Agent   │
      │  • Deficit Resolution │ │  • 8-Week Tracks  │ │   • AST Complexity    │
      └───────────┬───────────┘ └─────────┬─────────┘ └───────────┬───────────┘
                  │                       │                       │
                  └───────────────────────┼───────────────────────┘
                                          ▼
                      ┌─────────────────────────────────────────┐
                      │    Hybrid RAG & Knowledge Graph Agent   │
                      │  • Company Placement Archives           │
                      │  • Grounded Synthesis & Citations       │
                      └───────────────────┬─────────────────────┘
                                          │
                                          ▼
                      ┌─────────────────────────────────────────┐
                      │     Mock Interview Simulation Agent     │
                      │  • 4-Rubric Real-Time Technical Stage   │
                      └───────────────────┬─────────────────────┘
                                          │
                                          ▼
                      ┌─────────────────────────────────────────┐
                      │      Response Synthesizer Node          │
                      │  • Actionable Telemetry & Deep-Links    │
                      │  • Career Twin State Synchronization    │
                      └─────────────────────────────────────────┘
```

---

## Key Deliverables

1. **Database Models & State Schema** ([apps/api/app/models/orchestrator.py](file:///c:/Users/PRANESH.M/OneDrive/Desktop/AI%20PlacementOS/apps/api/app/models/orchestrator.py)):
   - `AgentWorkflowSession`: Master session tracking goal, plan steps, status, and summary.
   - `AgentWorkflowStep`: Step-level telemetry recording assigned agent, action, inputs, outputs, duration ms, and error states.
2. **Orchestrator Service Engine** ([apps/api/app/services/orchestrator_service.py](file:///c:/Users/PRANESH.M/OneDrive/Desktop/AI%20PlacementOS/apps/api/app/services/orchestrator_service.py)):
   - Automated supervisor planner mapping user goals to sub-agent actions.
   - Dynamic tool dispatch invoking Skill Gap, RAG Knowledge Hub, Roadmap Generator, DSA Sandbox, and Mock Interview simulator.
   - Synthesizer node building structured executive reports and deep-link action recommendations.
3. **REST API Endpoints** ([apps/api/app/api/v1/endpoints/orchestrator.py](file:///c:/Users/PRANESH.M/OneDrive/Desktop/AI%20PlacementOS/apps/api/app/api/v1/endpoints/orchestrator.py)):
   - `POST /api/v1/orchestrator/chat`
   - `POST /api/v1/orchestrator/workflows/create`
   - `GET /api/v1/orchestrator/workflows/{id}`
   - `GET /api/v1/orchestrator/workflows`
4. **AI Career Copilot Frontend Hub** ([apps/web/src/app/ai-assistant/page.tsx](file:///c:/Users/PRANESH.M/OneDrive/Desktop/AI%20PlacementOS/apps/web/src/app/ai-assistant/page.tsx)):
   - Interactive chat interface with real-time multi-agent execution badges, sub-agent telemetry inspector, and deep-link action cards.

---

## Verification Results

### Backend Pytest Suite
- **92/92 tests passing** across the entire backend:
  - `tests/test_orchestrator_service.py`
  - `tests/test_orchestrator_api.py`

### Next.js Production Build
- `npm run build` compiled 17/17 routes with 0 errors.
