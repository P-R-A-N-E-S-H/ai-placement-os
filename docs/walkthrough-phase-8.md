# AI PlacementOS — Phase 8 Walkthrough
## DSA Preparation Engine & Code Execution Sandbox

### 🌟 Executive Summary
Phase 8 establishes the interactive algorithmic execution and interview practice foundation for **AI PlacementOS**. It introduces a canonical curated placement problem bank covering foundational and advanced patterns (Arrays & Hashing, Sliding Window, Two Pointers, Stack, Binary Search, Dynamic Programming, Heaps, Trees, and Graphs), an isolated multi-language code execution sandbox with deterministic AST-based Big-O complexity analysis, and direct bidirectional synchronization with the **Career Digital Twin (Phase 2)** and **Adaptive Learning Roadmaps (Phase 7)**.

---

### 🏗️ Architecture & Component Flow

```
                  CANDIDATE CODE IN IDE
             (Python, JS, C++, Java Templates)
                            │
                            ▼
          ┌──────────────────────────────────────┐
          │     PHASE 8: CODE SANDBOX ENGINE     │
          │  • AST Syntax Parsing & Validation   │
          │  • Multi-Test Case Evaluation Loop   │
          │  • Wall-Clock Timeout Protection     │
          │  • Output Normalization & Diffing    │
          │  • AST Big-O Complexity Profiler     │
          └──────────────────┬───────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
       Execution Results            Career Twin Sync
     (Accepted / Wrong Answer)    (Skill Evidence + Proficiency)
              │                             │
              ▼                             ▼
       Console Output Diff         +0.05 DSA Proficiency
     (Runtime ms, Memory MB)      (Verifiable Proof Record)
```

---

### 🚀 Key Technical Deliverables

#### 1. Database Models (`apps/api/app/models/dsa.py`)
- **`DsaProblem`**:
  - `title`, `slug`, `difficulty` (`EASY`, `MEDIUM`, `HARD`), `category` (`ARRAYS_HASHING`, `SLIDING_WINDOW`, `DYNAMIC_PROGRAMMING`, etc.), `description` (Markdown examples), `constraints`, `hints`, `starter_code` (JSON map for Python/JS/C++/Java), `expected_time_complexity`, `expected_space_complexity`, `acceptance_rate`, `order_index`, `is_active`.
- **`DsaTestCase`**:
  - `problem_id`, `input_data`, `expected_output`, `is_hidden` (visible sample test cases vs hidden evaluation test cases), `explanation`, `order_index`.
- **`DsaSubmission`**:
  - `user_id`, `problem_id`, `language`, `code`, `status` (`ACCEPTED`, `WRONG_ANSWER`, `TIME_LIMIT_EXCEEDED`, `RUNTIME_ERROR`, `SYNTAX_ERROR`), `runtime_ms`, `memory_mb`, `passed_test_cases`, `total_test_cases`, `error_message`, `failed_test_case_input`, `failed_test_case_expected`, `failed_test_case_actual`, `ai_feedback`.
- **`UserDsaProgress`**:
  - `user_id`, `problem_id`, `is_solved`, `attempts_count`, `first_solved_at`, `best_runtime_ms`, `last_submitted_code`, `last_language`.

#### 2. Code Execution Sandbox & Evaluator (`apps/api/app/services/dsa_sandbox_service.py`)
- **Execution Harness**:
  - Isolated namespace execution supporting `Solution` class instantiation or standalone algorithmic functions.
  - Wall-clock timeout timer protecting against infinite loops ($O(\infty)$).
  - Output normalizer handling numeric formatting, boolean casing, whitespace, and JSON data structures.
- **AST Big-O Complexity Profiler**:
  - Traverses Abstract Syntax Trees (AST) to measure nested loop depths, recursive calls, and hash structures.
  - Automatically identifies $O(1)$, $O(\log N)$, $O(N)$, $O(N \log N)$, $O(N^2)$, $O(N^3)$, and $O(2^N)$ patterns.
  - Generates placement coach architectural notes (e.g. suggesting hash maps to optimize quadratic time scans).

#### 3. Core Problem Catalog & Career Twin Service (`apps/api/app/services/dsa_service.py`)
- **Curated Placement Problem Bank**:
  - Two Sum, Valid Anagram, Best Time to Buy and Sell Stock, Valid Parentheses, Binary Search, Maximum Subarray (Kadane's Algorithm), Top K Frequent Elements, Coin Change.
- **Career Twin Synchronization**:
  - Submitting an accepted solution automatically creates a `SkillEvidence` entry (`source_type="DSA"`, verified=True) containing runtime performance and Big-O complexity notes.
  - Increments candidate `UserSkill.proficiency` for DSA and related topics by $+0.05$ up to 1.0.
  - Updates candidate stats: total solved, easy/medium/hard breakdown, and topic mastery.

#### 4. REST API Endpoints (`apps/api/app/api/v1/endpoints/dsa.py`)
- `GET /api/v1/dsa/problems`: Lists problems with search, topic category, difficulty filters, and candidate solved flags.
- `GET /api/v1/dsa/problems/{identifier}`: Returns problem statement, constraints, hints, starter code, and sample test cases.
- `POST /api/v1/dsa/problems/{identifier}/run`: Runs code on sample test cases without persisting submission.
- `POST /api/v1/dsa/problems/{identifier}/submit`: Full test evaluation against all hidden cases, persists submission, and syncs Career Twin.
- `GET /api/v1/dsa/submissions`: Lists candidate historical submission attempts.
- `GET /api/v1/dsa/stats`: Returns candidate DSA analytics and topic mastery breakdown.

#### 5. Frontend DSA Arena & IDE (`apps/web/src/app/dsa/page.tsx` & `apps/web/src/lib/api/dsa.ts`)
- **Problem Explorer View**:
  - Search bar with live fuzzy search.
  - Topic category dropdown and difficulty filters.
  - Solved checkboxes, acceptance rates, and target Big-O complexity tags.
- **Split-Pane Placement IDE**:
  - Left Pane: Markdown problem statement, constraints list, placement hints tab, and submission history tab.
  - Right Pane: Multi-language code editor (Python 3, JavaScript, C++, Java), sample test case selector, "Run Tests" vs "Submit" triggers, and real-time console with diff views and AI Placement Coach insights.
  - Header Scorecard: Total solved counter, Easy/Med/Hard distribution pills, and accuracy percentage.

---

### 🧪 Automated Test Suite (78/78 Tests Passing)
- `tests/test_dsa_sandbox.py`: Verifies optimal Python execution, wrong answer output diffs, syntax error handling, and AST Big-O complexity profiler.
- `tests/test_dsa_service.py`: Verifies problem seeding, sample test running, code submission, progress record creation, and Career Twin `SkillEvidence` logging.
- `tests/test_dsa_api.py`: Full REST API integration workflow including problem discovery, detail retrieval, test execution, submission, and statistics.

---

### 🔜 Transition to Phase 9
With DSA preparation and code evaluation fully operational, **Phase 9 (Mock Interview Simulation Agent)** will build the conversational multi-modal technical interview engine with speech-to-text, behavioral & architectural evaluation, and real-time coding interview simulations.
