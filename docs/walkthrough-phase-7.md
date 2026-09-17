# AI PlacementOS — Phase 7 Walkthrough
## Adaptive Learning Roadmap Generator & Career Twin Synchronization

### 🌟 Executive Summary
Phase 7 synthesizes the topological prerequisite ordering from **Phase 6 Skill Gaps** into an actionable, structured, week-by-week personalized learning curriculum. It breaks high-level skill milestones down into granular daily study units (Concept, Hands-on Practice Lab, Production Deliverable, Evaluation Quiz), attaches authoritative curated learning resources (Official Docs, Deep Dive Videos, GitHub Starters, Interactive Labs), and establishes a bidirectional verification loop with the **Career Digital Twin (Phase 2)**. Completing daily tasks automatically logs verified `SkillEvidence`, upgrades candidate skill proficiencies, and auto-unlocks downstream modules.

---

### 🏗️ Architecture & Core Components

```
                    PHASE 6 SKILL GAP REPORT
               (Topological DAG + Missing Skills)
                              │
                              ▼
           ┌────────────────────────────────────────┐
           │     PHASE 7: ROADMAP GENERATOR         │
           │  • Weekly Module Partitioning          │
           │  • Daily Task Sequencing               │
           │  • Resource Synthesis (Docs/Repo/Lab)  │
           └──────────────────┬─────────────────────┘
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
       Weekly Milestones               Daily Tasks
     (Unlocked / In Progress)      (Concept/Practice/Lab)
               │                             │
               │                             ▼
               │                   Task Completion Toggle
               │                   (Proof of Work Link)
               │                             │
               ▼                             ▼
       Progress Bar Update           Career Twin Sync
    (Module Auto-Unlock)       (+0.15 Proficiency Gain & Evidence)
```

---

### 🚀 Key Technical Deliverables

#### 1. Database Schema & Models (`apps/api/app/models/roadmap.py`)
- **`LearningRoadmap`**:
  - `user_id`, `gap_report_id`, `title`, `description`, `target_role`, `target_job_id`, `target_job_title`, `target_job_company`
  - Metrics: `total_weeks`, `weekly_hours`, `total_estimated_hours`, `total_tasks`, `completed_tasks`, `progress_percentage`, `status` (`ACTIVE`, `PAUSED`, `COMPLETED`)
  - Cascading relations to `RoadmapModule` and `RoadmapTask`.
- **`RoadmapModule`**:
  - `roadmap_id`, `week_number`, `title`, `description`, `focus_skills` (JSON array), `estimated_hours`, `status` (`LOCKED`, `UNLOCKED`, `IN_PROGRESS`, `COMPLETED`), `order_index`.
- **`RoadmapTask`**:
  - `roadmap_id`, `module_id`, `day_number`, `title`, `description`, `task_type` (`CONCEPT`, `PRACTICE`, `PROJECT`, `QUIZ`), `skill_slug`, `estimated_minutes`, `resources` (JSON list), `is_completed`, `completed_at`, `evidence_text`, `evidence_source_id`, `order_index`.

#### 2. Curriculum Synthesis Engine (`apps/api/app/services/roadmap_service.py`)
- **Curated Resource Library**: Standardized authoritative resource mappings covering 50+ canonical skills (Official Docs, Architecture Handbooks, LeetCode / NeetCode DSA sets, GitHub repositories, and interactive sandboxes).
- **Module & Task Partitioning**:
  - Clusters topological gap skills into weekly milestones.
  - Generates 4 structured tasks per module:
    1. `Day 1 - CONCEPT`: Core architectural fundamentals & theory.
    2. `Day 2 - PRACTICE`: Hands-on implementation lab / algorithm patterns.
    3. `Day 3 - PROJECT`: End-to-end repository deliverable or microservice.
    4. `Day 4 - QUIZ`: Knowledge assessment & system evaluation.
- **Career Twin Synchronization**:
  - Toggling a task complete automatically inserts a `SkillEvidence` record (`source_type="LEARNING"`) into the database.
  - Updates `UserSkill.proficiency` by $+0.15$ up to target proficiency.
  - Recomputes roadmap completion percentage and automatically unlocks the next weekly module when all tasks in the current module are fulfilled.

#### 3. REST API Endpoints (`apps/api/app/api/v1/endpoints/roadmaps.py`)
- `POST /api/v1/learning/roadmaps/generate`: Synthesizes or regenerates roadmap from role benchmark or live job.
- `GET /api/v1/learning/roadmaps/active`: Retrieves current active roadmap with all modules and daily tasks.
- `GET /api/v1/learning/roadmaps/{roadmap_id}`: Retrieves specific historical or targeted roadmap.
- `GET /api/v1/learning/roadmaps`: Lists all candidate roadmaps with high-level progress summaries.
- `PATCH /api/v1/learning/roadmaps/tasks/{task_id}/toggle`: Toggles task state with optional proof-of-work link and notes.

#### 4. Frontend Adaptive Learning Hub (`apps/web/src/app/learning/page.tsx` & `apps/web/src/lib/api/roadmaps.ts`)
- **Synthesizer Control Panel**: Role Benchmark selector, Live Job selector, dynamic study commitment range slider (5–40 hrs/week), and velocity selector.
- **Top Scorecard**: Real-time progress bar, total weeks, estimated hours, and completed/total task counters.
- **Week-by-Week Accordion**: Status badges (`LOCKED`, `UNLOCKED`, `IN_PROGRESS`, `COMPLETED`), focus skills tags, and daily task breakdown.
- **Interactive Task Checklist**: One-click completion toggle, type-specific badges (`CONCEPT`, `PRACTICE LAB`, `DELIVERABLE`, `EVALUATION`), direct resource links with platform icons.
- **Proof-of-Work Submission Modal**: Allows candidates to submit GitHub repository links and implementation summaries to verify their skills in the Career Digital Twin.
- **Direct Link to Phase 8**: Interactive banner connecting practice tasks to the upcoming DSA Preparation Sandbox.

---

### 🧪 Automated Test Suite (69/69 Tests Passing)
- `tests/test_roadmap_generator.py`: Verifies topological curriculum synthesis from role benchmarks and accelerated schedules for candidates with pre-acquired skills.
- `tests/test_roadmap_progress_and_evidence.py`: Verifies task toggling, automatic module unlocking, progress calculation, and `SkillEvidence` creation in Career Twin.
- `tests/test_roadmap_api.py`: Full REST API workflow including auth validation, generation, retrieval, and task toggling.

---

### 🔜 Transition to Phase 8
Phase 7 provides the direct learning curriculum and milestone sequencing. **Phase 8 (DSA Preparation Engine & Code Execution Sandbox)** will power the interactive algorithmic practice tasks with real-time code evaluation in Python, C++, Java, and TypeScript.
