# AI PlacementOS — Phase 6 Walkthrough
## Skill Gap Analysis Agent & Prerequisite Graph Engine

### 🌟 Executive Summary
Phase 6 establishes the analytical bridge translating **Career Digital Twin profile state & resume extraction (Phases 2 & 3)** and **target industry roles or specific jobs (Phases 4 & 5)** into a structured, deterministic learning pathway. It implements a zero-mock Directed Acyclic Graph (DAG) topological dependency engine, calculates realistic time & effort estimates, and generates an actionable 4-quadrant ROI Priority Matrix.

---

### 🏗️ Architecture & Core Mathematical Models

$$\text{Readiness Score} = 100 \times \frac{\sum_{i=1}^{N} \left( w_i \times \min\left(1.0, \frac{\text{Proficiency}_{\text{curr}, i}}{\text{Proficiency}_{\text{req}, i}}\right) \right)}{\sum_{i=1}^{N} w_i}$$

$$\text{ROI Priority Score} = \frac{\text{Importance Weight} \times 100}{\sqrt{\text{Estimated Hours} + 1.0}}$$

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      4-Quadrant ROI Priority Matrix                     │
├───────────────────────────────┬─────────────────────────────────────────┤
│ Quadrant                      │ Criteria & Action                       │
├───────────────────────────────┼─────────────────────────────────────────┤
│ 1. Quick Wins                 │ Low Effort (≤15h) + High ROI (Critical) │
│ 2. Major Milestones           │ High Effort (>15h) + Critical Core Req  │
│ 3. Deep Dives                 │ High Effort (>15h) + Recommended/Bonus  │
│ 4. Electives & Polish         │ Low Effort (≤15h) + Preferred Tooling   │
└───────────────────────────────┴─────────────────────────────────────────┘
```

---

### 🚀 Key Technical Deliverables

#### 1. Database Model & Persistence (`apps/api/app/models/skill_gap.py`)
- **Table**: `skill_gap_reports`
- **Fields**:
  - `user_id`, `target_type` (`ROLE` or `JOB`), `target_id`, `target_title`, `target_company`
  - Metrics: `readiness_score`, `total_skills_required`, `matched_skills_count`, `missing_critical_count`, `proficiency_gap_count`, `total_estimated_hours`, `estimated_weeks`
  - Structured Payloads: `gap_items`, `prerequisite_graph`, `priority_matrix`, `learning_pathway`
  - Unique constraint on `(user_id, target_type, target_id)` with fast query indexing

#### 2. Directed Acyclic Graph (DAG) Engine (`apps/api/app/services/skill_graph_service.py`)
- Standardized directed prerequisite edges spanning AI/ML, Backend, Frontend, DevOps, and DSA chains.
- Implemented Kahn's Algorithm topological sort with cycle detection, guaranteeing that no skill is recommended before its upstream foundational prerequisites are acquired.
- Node state resolution:
  - `ACQUIRED`: Current verified proficiency $\ge$ required proficiency.
  - `UNLOCKED`: Prerequisites met in Career Twin; ready to learn immediately.
  - `LOCKED`: One or more upstream prerequisite dependencies are unsatisfied.

#### 3. Skill Gap Analysis Service (`apps/api/app/services/skill_gap_service.py`)
- Standard Role Benchmarks catalog:
  - **AI & Autonomous Agent Systems Engineer** (`ai-engineer`)
  - **Backend & Distributed Systems SDE** (`backend-engineer`)
  - **Full-Stack Product Engineer** (`full-stack-engineer`)
  - **DevOps & Cloud Infrastructure Engineer** (`devops-engineer`)
  - **Data Scientist & Applied ML Specialist** (`data-scientist`)
- Dual-mode evaluation supporting both curated role benchmarks and specific live ingested jobs (`Job.job_skills`).
- Dynamic weekly learning pace slider adjusting `estimated_weeks`.

#### 4. REST API Endpoints (`apps/api/app/api/v1/endpoints/skill_gaps.py`)
- `POST /api/v1/skills/gap-analysis/role`: Evaluates Career Twin against industry role benchmark.
- `POST /api/v1/skills/gap-analysis/job/{job_id}`: Evaluates Career Twin against specific job opportunity.
- `GET /api/v1/skills/gap-analysis/latest`: Retrieves or auto-evaluates latest candidate gap report.
- `GET /api/v1/skills/gap-analysis/report/{report_id}`: Retrieves specific persisted report.
- `GET /api/v1/skills/roles/benchmarks`: Public endpoint listing all role benchmarks.
- `GET /api/v1/skills/prerequisites/graph`: Public endpoint returning the full prerequisite DAG taxonomy.

#### 5. Frontend Web UI & Navigation (`apps/web/src/app/skills/page.tsx`)
- **Interactive Target Switcher**: Toggle between 5 standard role benchmarks and live ingested jobs.
- **Dynamic Study Pace Slider**: 5 to 40 hrs/week with instant recalculation of readiness timeline.
- **Executive Scorecard**: Readiness gauge, total effort hours, estimated weeks, and deficit counts.
- **Interactive Views**:
  - **ROI Priority Matrix (4 Quadrants)**: Color-coded cards for Quick Wins, Major Milestones, Deep Dives, and Electives.
  - **Topological Pathway Table**: Strictly ordered linear sequence ($1, 2, 3...$) with direct action recommendations.
  - **Prerequisite DAG Grid**: Live node status cards (`ACQUIRED`, `UNLOCKED`, `LOCKED`) with proficiency progress bars.
- Direct handoff CTA to Phase 7: "Generate Adaptive Learning Roadmap".

---

### 🧪 Verification & Test Results

#### Automated Backend Test Suite
```bash
pytest -v
============================= 63 passed in 37.45s =============================
```
- `tests/test_skill_graph.py`: Validated topological dependency sorting, ancestor resolution, and unlock status state transitions.
- `tests/test_skill_gap_analysis.py`: Validated deterministic gap item calculation, satisfied/deficit/missing classification, and ROI score prioritization.
- `tests/test_skill_gap_api.py`: Validated role-based and job-based REST endpoints, public graph APIs, auth enforcement, and cross-user isolation.

#### Frontend Build Verification
```bash
npm run build
✓ Compiled successfully
✓ Generating static pages (12/12)
  ├ ○ /skills (Phase 6 Skill Gap Hub)
  ├ ○ /matches (Phase 5 Match Hub)
  └ ○ /jobs (Phase 4 Discovery)
```
Exit Code: 0. 0 TypeScript errors.

---

### 🔜 Hand-Off to Phase 7 (Adaptive Learning Roadmap Generator)
Phase 6 produces the exact ordered `learning_pathway` and `priority_matrix`, which will directly feed into Phase 7 to construct week-by-week modular learning plans, daily study tasks, and curated resources.
