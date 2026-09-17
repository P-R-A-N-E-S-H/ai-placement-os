# AI PlacementOS — Phase 5 Walkthrough
## Hybrid Job–Resume Matching Engine (Deterministic 6-Factor Algorithm)

### 🌟 Executive Summary
Phase 5 establishes the core matching brain connecting **Career Digital Twin profiles & resumes (Phases 2 & 3)** with **deduplicated job opportunities (Phase 4)**. It implements a zero-mock, deterministic 6-factor matching engine with true domain-semantic subspace embeddings, fine-grained skill gap extraction, and deep explanation generation.

---

### 🏗️ Architecture & Mathematical Formula

$$\text{Overall Score} = \sum_{i=1}^{6} (w_i \times S_i)$$

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Deterministic 6-Factor Weights                     │
├──────────────────────────────┬──────────┬──────────────────────────────┤
│ Factor                       │ Weight   │ Evaluation Logic             │
├──────────────────────────────┼──────────┼──────────────────────────────┤
│ 1. Skill Match               │ 30%      │ 75% Req + 25% Pref Skills    │
│ 2. Experience Level Fit      │ 20%      │ Level & Project Count        │
│ 3. Domain-Semantic Cosine    │ 15%      │ 128D Subspace Cosine Sim     │
│ 4. Verified Skill Evidence   │ 15%      │ Proof items in Career Twin   │
│ 5. Education Relevance       │ 10%      │ Degree, Branch & CGPA        │
│ 6. Preference Alignment      │ 10%      │ Remote/Hybrid & Target Roles │
└──────────────────────────────┴──────────┴──────────────────────────────┘
```

---

### 🚀 Key Technical Deliverables

#### 1. Database Model & Persistence (`apps/api/app/models/match.py`)
- **Table**: `job_matches`
- **Fields**:
  - `user_id`, `job_id`, `overall_score`
  - 6 Sub-scores: `skill_score`, `experience_score`, `education_score`, `semantic_score`, `evidence_score`, `preference_score`
  - Canonical lists: `matched_required_skills`, `missing_required_skills`, `matched_preferred_skills`, `missing_preferred_skills`
  - `breakdown`: JSON telemetry with exact weights and raw ratios
  - `explanation`: JSON structured with `strengths`, `gaps`, `recommendations`
  - Unique constraint on `(user_id, job_id)` with fast indexed lookups

#### 2. Domain-Semantic Vector Subspace (`apps/api/app/services/job_embedding_service.py`)
- Upgraded to 128-dimensional domain subspace coordinates with term-frequency weighting:
  - `AI_ML` (Indices 0–23)
  - `BACKEND_DISTRIBUTED` (Indices 24–47)
  - `FRONTEND_WEB` (Indices 48–71)
  - `DEVOPS_CLOUD` (Indices 72–95)
  - `DSA_ALGORITHMS` (Indices 96–111)
  - General n-grams (Indices 112–127)
- L2 unit normalization ($\|v\|=1.0$) and Cosine Similarity $\cos(\theta) = \mathbf{u} \cdot \mathbf{v}$.
- Validated: Cosine similarity between AI Engineer resume and AI Job is $> 0.55$, while orthogonal domains (Frontend vs AI) stay $< 0.35$.

#### 3. Matching Engine & Service (`apps/api/app/services/matching_engine.py`, `match_service.py`)
- Aggregates `UserProfile`, `UserSkill` (with evidence items), and parsed resume text into a unified candidate representation.
- Computes deterministic factor scores, categorizes skills into matched/missing, and synthesizes tailored strengths and action plans.
- Supports single-job calculation and batch ranking across all active database opportunities.

#### 4. REST API Endpoints (`apps/api/app/api/v1/endpoints/matches.py`)
- `POST /api/v1/matches/calculate/{job_id}`: Evaluates or recalculates match for specific job.
- `POST /api/v1/matches/batch?limit=50`: Batch-evaluates top jobs and persists rankings.
- `GET /api/v1/matches?min_score=60&page=1&page_size=20`: Lists matches sorted by score descending.
- `GET /api/v1/matches/{job_id}`: Retrieves existing cached match scorecard.

#### 5. Frontend UI & UX (`apps/web/src/app/matches/page.tsx` & `jobs/page.tsx`)
- **Match Hub (`/matches`)**:
  - Live radial score meters with color coding (Emerald $\ge 80\%$, Indigo $\ge 60\%$, Amber $< 60\%$).
  - 6-factor breakdown mini progress bars.
  - Interactive "Batch Re-Evaluate All Jobs" trigger.
  - Matched vs Missing Required Skills badges with direct deep link to Phase 6 Skill Gap Analysis.
- **Job Discovery Integration (`/jobs`)**:
  - Match Scorecard integrated into the Job Detail drawer with 1-click live evaluation.
- **Navigation**:
  - Updated Sidebar with live "Job Matching" link.

---

### 🧪 Verification & Test Results

#### Automated Backend Test Suite
```bash
pytest -v
============================= 51 passed in 25.85s =============================
```
- `tests/test_semantic_embedding.py`: Validated true domain-semantic vector correlation.
- `tests/test_matching_engine.py`: Validated skill coverage, experience scaling, evidence bonus, and explanation generation.
- `tests/test_match_api.py`: Validated single-job match, batch ranking, score filtering, and cross-user isolation.

#### Frontend Build Verification
```bash
npm run build
✓ Compiled successfully
✓ Generating static pages (11/11)
  ├ ○ /matches (Phase 5 Match Hub)
  └ ○ /jobs (Job Discovery with live scorecard drawer)
```
Exit Code: 0. 0 TypeScript errors.

---

### 🔜 Hand-Off to Phase 6 (Skill Gap Analysis Agent)
Phase 5 cleanly outputs `missing_required_skills` and `missing_preferred_skills`, which will directly feed into Phase 6 to construct the **Prerequisite Graph, Priority Matrix, and Effort Estimator**.
