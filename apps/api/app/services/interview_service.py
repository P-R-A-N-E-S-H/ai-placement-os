import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError, ValidationError
from app.models.interview import (
    InterviewDifficulty,
    InterviewQuestion,
    InterviewResponse,
    InterviewSession,
    InterviewSessionStatus,
    InterviewType,
    QuestionCategory,
)
from app.models.skill import EvidenceSourceType, Skill, SkillEvidence, UserSkill
from app.schemas.interview import (
    InterviewCreateRequest,
    InterviewQuestionResponse,
    InterviewRespondRequest,
    InterviewSessionDetail,
    InterviewSessionSummary,
    InterviewSubmitTurnResult,
    InterviewTurnResponse,
)
from app.services.skill_service import slugify


INTERVIEW_QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    "AI Engineer": [
        {
            "category": QuestionCategory.TECHNICAL_DEEP_DIVE.value,
            "question_text": "Explain how you would architect a production Retrieval-Augmented Generation (RAG) pipeline to minimize hallucinations and manage multi-turn conversational context.",
            "context_or_scenario": "You are building an AI agent for a fintech company that must query complex loan regulations and explain decisions accurately.",
            "target_competencies": ["rag", "vector-embeddings", "langchain", "prompt-engineering"],
            "evaluation_criteria": {
                "key_concepts": ["hybrid search", "chunking strategy", "re-ranking", "semantic cache", "grounding", "guardrails"],
                "ideal_structure": "Architecture overview -> Ingestion & Chunking -> Vector + Keyword Search -> Re-ranking -> LLM synthesis with citations",
            },
            "exemplary_answer": "In production RAG, I implement a two-stage hybrid retrieval architecture. During ingestion, documents are recursively chunked (500 tokens with 10% overlap) and indexed in pgvector alongside BM25 keyword indices. On user queries, we perform hybrid retrieval with reciprocal rank fusion (RRF) and pass the top 20 candidates through a cross-encoder re-ranker (e.g. Cohere / BGE). Context window memory is maintained via a summarized rolling buffer. Finally, system prompts enforce strict grounding with source citations and guardrail validation.",
        },
        {
            "category": QuestionCategory.SYSTEM_DESIGN.value,
            "question_text": "How do you design a stateful multi-agent system using LangGraph or StateGraph where agents can execute asynchronous tool calls and handle human-in-the-loop approvals?",
            "context_or_scenario": "The system processes resume improvements and automatically commits code changes to candidate GitHub repositories, requiring human verification for critical edits.",
            "target_competencies": ["langgraph", "multi-agent", "asyncio", "state-machine"],
            "evaluation_criteria": {
                "key_concepts": ["StateGraph", "checkpointing", "interrupt_before", "tool node", "cyclic graph", "state persistence"],
            },
            "exemplary_answer": "I model this as a directed StateGraph where state is a TypedDict containing messages and execution flags. Nodes represent specialized agents (Planner, Generator, Reviewer, ToolExecutor). For human-in-the-loop, I configure 'interrupt_before' on high-risk tool nodes (e.g. git push). State is persisted using a PostgreSQL checkpoint saver, allowing execution to pause, await candidate approval via API, and resume seamlessly.",
        },
        {
            "category": QuestionCategory.BEHAVIORAL_STAR.value,
            "question_text": "Describe a challenging AI/ML bug or performance bottleneck you encountered in a project, and how you diagnosed and resolved it.",
            "context_or_scenario": "Focus on root cause analysis, methodical profiling, and measurable performance improvements.",
            "target_competencies": ["problem-solving", "debugging", "profiling", "star-methodology"],
            "evaluation_criteria": {
                "star_components": ["Situation", "Task", "Action", "Result"],
            },
            "exemplary_answer": "Situation: In our semantic search service, latency spiked from 120ms to 2.4s under high concurrency. Task: I was tasked with profiling the inference pipeline and bringing p95 latency below 200ms. Action: Using Py-Spy and cProfile, I discovered that embedding generation was running synchronously on the main event loop, blocking async FastAPI workers. I offloaded batch embeddings to a dedicated GPU worker pool via Celery/Redis with batching. Result: p95 latency dropped by 88% to 140ms, and throughput increased from 50 to 800 QPS.",
        },
    ],
    "Backend Engineer": [
        {
            "category": QuestionCategory.TECHNICAL_DEEP_DIVE.value,
            "question_text": "Compare PostgreSQL index types (B-Tree, Hash, GIN, BRIN) and explain how you would diagnose a slow query executing a sequential scan on a 50M-row table.",
            "context_or_scenario": "A high-frequency API endpoint is timing out during peak traffic hours.",
            "target_competencies": ["postgresql", "database-indexing", "query-optimization"],
            "evaluation_criteria": {
                "key_concepts": ["EXPLAIN ANALYZE", "B-Tree vs GIN", "Composite Index", "Partial Index", "Index Scan vs Seq Scan"],
            },
            "exemplary_answer": "I first run EXPLAIN (ANALYZE, BUFFERS) to inspect the query execution plan, checking cost, buffer hit ratio, and actual rows. Standard equality and range filters use B-Tree indices. For JSONB or full-text columns, GIN is optimal. For append-only timestamped tables, BRIN provides minuscule index size. If a sequential scan occurs, I check index cardinality, verify column collation, or construct a composite/partial index covering the query WHERE and ORDER BY clauses.",
        },
        {
            "category": QuestionCategory.SYSTEM_DESIGN.value,
            "question_text": "Design a distributed rate-limiting and token-bucket service capable of handling 500,000 requests per second with sub-5ms latency.",
            "context_or_scenario": "Protecting public microservices against DDoS and API abuse across multiple geographical regions.",
            "target_competencies": ["system-design", "redis", "concurrency", "distributed-systems"],
            "evaluation_criteria": {
                "key_concepts": ["Redis sliding window / token bucket", "Lua script atomicity", "local caching", "clock drift", "graceful degradation"],
            },
            "exemplary_answer": "I implement a hybrid Token Bucket algorithm using Redis Clusters with Lua scripting for atomic execution without distributed locks. To achieve 500k RPS and <5ms latency, edge gateways maintain in-memory local token buffers (syncing with Redis every 50ms in batches). If Redis fails, we fail-open with local rate limits to prevent cascading outages.",
        },
        {
            "category": QuestionCategory.BEHAVIORAL_STAR.value,
            "question_text": "Tell me about a time you had a technical disagreement with a teammate regarding system architecture or API design. How was it resolved?",
            "context_or_scenario": "Highlight collaboration, data-driven decision making, and professional tradeoff analysis.",
            "target_competencies": ["collaboration", "communication", "tradeoffs", "star-methodology"],
            "evaluation_criteria": {
                "star_components": ["Situation", "Task", "Action", "Result"],
            },
            "exemplary_answer": "Situation: During our capstone architecture design, my teammate proposed a pure microservices architecture with 8 services, while I favored a modular monolith for faster iteration. Task: We needed to align within 48 hours to meet our semester milestone. Action: I organized a structured tradeoff session. We benchmarked deployment complexity, serialization overhead, and team velocity. I proposed starting with cleanly bounded domain modules in a single repo with gRPC-ready interfaces. Result: We shipped on time with zero network overhead, and successfully split the video rendering service into a standalone worker later when load required it.",
        },
    ],
    "BEHAVIORAL_UNIVERSAL": [
        {
            "category": QuestionCategory.BEHAVIORAL_STAR.value,
            "question_text": "Tell me about a project where you had to quickly learn an unfamiliar technology or framework under tight placement deadlines.",
            "context_or_scenario": "Demonstrate rapid learning velocity, self-direction, and successful execution.",
            "target_competencies": ["adaptability", "learning-velocity", "execution", "star-methodology"],
            "evaluation_criteria": {
                "star_components": ["Situation", "Task", "Action", "Result"],
            },
            "exemplary_answer": "Situation: For our placement hackathon, we needed to build an autonomous agent platform in 48 hours using LangGraph, which I had never used. Task: Build and deploy the multi-agent graph with memory within two days. Action: I read the official docs, studied open-source template repositories, built minimal reproduction scripts to verify state transitions, and modularized agent nodes. Result: Our team won 1st place, and the platform handled 500+ live concurrent demo sessions with zero state corruption.",
        },
        {
            "category": QuestionCategory.BEHAVIORAL_STAR.value,
            "question_text": "Describe a situation where a software project you built failed or did not meet user expectations. What did you learn and how did you iterate?",
            "context_or_scenario": "Focus on accountability, root cause reflection, and continuous improvement.",
            "target_competencies": ["resilience", "growth-mindset", "quality", "star-methodology"],
            "evaluation_criteria": {
                "star_components": ["Situation", "Task", "Action", "Result"],
            },
            "exemplary_answer": "Situation: In our first campus placement resume checker, 40% of student PDF uploads failed to parse due to multi-column formatting. Task: Overhaul the ingestion engine to achieve >95% extraction accuracy. Action: I conducted a post-mortem, wrote a test suite with 50 diverse resume layouts, implemented deterministic section boundary heuristics with regex fallbacks, and added ATS scoring diagnostics. Result: Extraction accuracy rose to 98.4%, and over 1,200 students successfully optimized their resumes for placements.",
        },
    ],
}


class InterviewService:
    """
    Mock Interview Simulation Engine.
    Handles dynamic question synthesis, turn-by-turn multi-rubric evaluation,
    STAR structural analysis, and Career Digital Twin synchronization.
    """

    @classmethod
    def evaluate_response_heuristics(
        cls,
        question: InterviewQuestion,
        response_text: str,
    ) -> Dict[str, Any]:
        """
        Deterministic multi-rubric scoring evaluating Technical Depth,
        STAR structure, Communication Clarity, and Tradeoffs.
        """
        text = response_text.strip()
        word_count = len(text.split())
        lower_text = text.lower()

        # 1. Technical Depth Score (0 - 100)
        eval_criteria = question.evaluation_criteria or {}
        key_concepts = eval_criteria.get("key_concepts", [])
        competencies = question.target_competencies or []

        all_target_terms = [c.lower() for c in key_concepts] + [c.lower() for c in competencies]
        matched_terms = [t for t in all_target_terms if t in lower_text]

        term_coverage = len(matched_terms) / max(1, len(all_target_terms)) if all_target_terms else 0.8
        base_depth = min(95.0, 50.0 + (term_coverage * 45.0) + min(10.0, word_count / 20.0))

        # 2. STAR Structural Adherence Score (0 - 100)
        star_markers = {
            "Situation": bool(re.search(r"\b(situation|background|context|initially|when i was|working on|project)\b", lower_text)),
            "Task": bool(re.search(r"\b(task|goal|objective|needed to|responsible for|target|requirement)\b", lower_text)),
            "Action": bool(re.search(r"\b(action|implemented|designed|built|architected|profiled|refactored|wrote)\b", lower_text)),
            "Result": bool(re.search(r"\b(result|outcome|improved|reduced|increased|achieved|percent|%|qps|ms|latency)\b", lower_text)),
        }

        star_hits = sum(1 for v in star_markers.values() if v)
        has_metrics = bool(re.search(r"\b(\d+%|\d+\s*(ms|s|qps|users|x|times))\b", lower_text))

        star_score = 45.0 + (star_hits * 11.0) + (10.0 if has_metrics else 0.0)
        star_score = min(98.0, star_score)

        # 3. Communication Clarity Score (0 - 100)
        clarity_score = 75.0
        if word_count < 25:
            clarity_score = 45.0
        elif 60 <= word_count <= 250:
            clarity_score = 90.0
        elif word_count > 400:
            clarity_score = 78.0  # slightly too verbose

        # 4. Tradeoffs & System Impact Score (0 - 100)
        tradeoff_markers = bool(re.search(r"\b(tradeoff|trade-off|alternative|compared to|overhead|bottleneck|latency|memory|scale|concurrency)\b", lower_text))
        tradeoff_score = 85.0 if tradeoff_markers else 65.0

        # Weighted Overall Score
        overall_score = round(
            (base_depth * 0.35) + (star_score * 0.30) + (clarity_score * 0.20) + (tradeoff_score * 0.15),
            1,
        )

        # Strengths & Constructive Improvements
        strengths = []
        improvements = []

        if term_coverage >= 0.5:
            strengths.append(f"Strong technical vocabulary: effectively referenced {', '.join(matched_terms[:3])}.")
        else:
            improvements.append("Incorporate deeper technical domain terms (e.g. indexing strategies, caching layers, or state persistence).")

        if star_hits >= 3:
            strengths.append("Clear structural articulation following the STAR (Situation, Task, Action, Result) framework.")
        else:
            improvements.append("Structure your response more explicitly with Situation -> Task -> Action -> Result.")

        if has_metrics:
            strengths.append("Excellent quantification of engineering impact (metrics, latency, or throughput gains).")
        else:
            improvements.append("Quantify your results with concrete metrics (e.g., 'reduced latency by 40%', 'handled 5k RPS').")

        star_breakdown = {
            "Situation": "Identified" if star_markers["Situation"] else "Missing explicit context",
            "Task": "Identified" if star_markers["Task"] else "Missing problem scope",
            "Action": "Identified" if star_markers["Action"] else "Detail concrete implementation steps",
            "Result": "Quantified" if has_metrics else ("Identified" if star_markers["Result"] else "Add measurable business impact"),
        }

        ai_feedback = (
            f"Overall Turn Score: {overall_score}/100.\n"
            f"Key Strengths: {'; '.join(strengths)}\n"
            f"Actionable Feedback: {'; '.join(improvements)}"
        )

        return {
            "score": overall_score,
            "technical_depth_score": round(base_depth, 1),
            "structure_star_score": round(star_score, 1),
            "communication_clarity_score": round(clarity_score, 1),
            "tradeoff_score": round(tradeoff_score, 1),
            "strengths": strengths,
            "improvements": improvements,
            "star_breakdown": star_breakdown,
            "ai_feedback_text": ai_feedback,
        }

    @classmethod
    async def create_session(
        cls,
        db: AsyncSession,
        user_id: str,
        payload: InterviewCreateRequest,
    ) -> InterviewSessionDetail:
        """
        Synthesizes structured multi-round interview questions and creates active session.
        """
        role = payload.target_role or "AI Engineer"
        total_q = min(10, max(2, payload.total_questions))

        # Gather role-specific questions + behavioral pool
        role_pool = INTERVIEW_QUESTION_BANK.get(role, INTERVIEW_QUESTION_BANK["AI Engineer"])
        universal_pool = INTERVIEW_QUESTION_BANK["BEHAVIORAL_UNIVERSAL"]
        combined_pool = role_pool + universal_pool

        # Select up to total_q questions
        selected_questions = (combined_pool * 3)[:total_q]

        session = InterviewSession(
            user_id=user_id,
            title=f"{role} Placement Simulation ({payload.interview_type})",
            interview_type=payload.interview_type,
            target_role=role,
            target_company=payload.target_company,
            difficulty=payload.difficulty,
            status=InterviewSessionStatus.IN_PROGRESS.value,
            current_question_index=0,
            total_questions=len(selected_questions),
            started_at=datetime.now(timezone.utc),
        )
        db.add(session)
        await db.flush()

        # Add questions
        for idx, q_data in enumerate(selected_questions):
            question = InterviewQuestion(
                session_id=session.id,
                question_index=idx,
                category=q_data["category"],
                question_text=q_data["question_text"],
                context_or_scenario=q_data.get("context_or_scenario"),
                target_competencies=q_data.get("target_competencies", []),
                evaluation_criteria=q_data.get("evaluation_criteria", {}),
                suggested_duration_seconds=180,
            )
            db.add(question)

        await db.commit()
        return await cls.get_session_by_id(db=db, user_id=user_id, session_id=session.id)

    @classmethod
    async def get_session_by_id(
        cls,
        db: AsyncSession,
        user_id: str,
        session_id: str,
    ) -> InterviewSessionDetail:
        """Retrieves complete interview session with questions and turn responses."""
        query = (
            select(InterviewSession)
            .options(
                selectinload(InterviewSession.questions),
                selectinload(InterviewSession.responses),
            )
            .where(
                InterviewSession.id == session_id,
                InterviewSession.user_id == user_id,
            )
        )
        session = (await db.execute(query)).scalar_one_or_none()
        if not session:
            raise EntityNotFoundError("InterviewSession", session_id)

        questions_dto = [
            InterviewQuestionResponse(
                id=q.id,
                question_index=q.question_index,
                category=q.category,
                question_text=q.question_text,
                context_or_scenario=q.context_or_scenario,
                target_competencies=q.target_competencies,
                evaluation_criteria=q.evaluation_criteria,
                suggested_duration_seconds=q.suggested_duration_seconds,
            )
            for q in sorted(session.questions, key=lambda x: x.question_index)
        ]

        responses_dto = [
            InterviewTurnResponse(
                id=r.id,
                session_id=r.session_id,
                question_id=r.question_id,
                turn_index=r.turn_index,
                candidate_response_text=r.candidate_response_text,
                audio_duration_seconds=r.audio_duration_seconds,
                score=r.score,
                technical_depth_score=r.technical_depth_score,
                structure_star_score=r.structure_star_score,
                communication_clarity_score=r.communication_clarity_score,
                tradeoff_score=r.tradeoff_score,
                strengths=r.strengths,
                improvements=r.improvements,
                star_breakdown=r.star_breakdown,
                exemplary_answer=r.exemplary_answer,
                ai_feedback_text=r.ai_feedback_text,
                created_at=r.created_at,
            )
            for r in sorted(session.responses, key=lambda x: x.turn_index)
        ]

        return InterviewSessionDetail(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            interview_type=session.interview_type,
            target_role=session.target_role,
            target_company=session.target_company,
            difficulty=session.difficulty,
            status=session.status,
            current_question_index=session.current_question_index,
            total_questions=session.total_questions,
            overall_score=session.overall_score,
            technical_score=session.technical_score,
            behavioral_score=session.behavioral_score,
            communication_score=session.communication_score,
            tradeoff_score=session.tradeoff_score,
            summary_feedback=session.summary_feedback,
            strengths=session.strengths,
            improvements=session.improvements,
            started_at=session.started_at,
            completed_at=session.completed_at,
            questions=questions_dto,
            responses=responses_dto,
        )

    @classmethod
    async def get_active_session(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> Optional[InterviewSessionDetail]:
        """Retrieves candidate's most recent in-progress interview session."""
        query = (
            select(InterviewSession)
            .where(
                InterviewSession.user_id == user_id,
                InterviewSession.status == InterviewSessionStatus.IN_PROGRESS.value,
            )
            .order_by(InterviewSession.started_at.desc())
            .limit(1)
        )
        session = (await db.execute(query)).scalar_one_or_none()
        if not session:
            return None
        return await cls.get_session_by_id(db=db, user_id=user_id, session_id=session.id)

    @classmethod
    async def respond_to_question(
        cls,
        db: AsyncSession,
        user_id: str,
        session_id: str,
        payload: InterviewRespondRequest,
    ) -> InterviewSubmitTurnResult:
        """
        Evaluates candidate response for the current question, records turn metrics,
        and advances to next question or completes session.
        """
        query = (
            select(InterviewSession)
            .options(
                selectinload(InterviewSession.questions),
                selectinload(InterviewSession.responses),
            )
            .where(
                InterviewSession.id == session_id,
                InterviewSession.user_id == user_id,
            )
        )
        session = (await db.execute(query)).scalar_one_or_none()
        if not session:
            raise EntityNotFoundError("InterviewSession", session_id)

        sorted_questions = sorted(session.questions, key=lambda x: x.question_index)
        curr_idx = session.current_question_index

        if curr_idx >= len(sorted_questions):
            raise ValidationError("All questions in this interview session have already been answered.")

        current_question = sorted_questions[curr_idx]

        # 1. Evaluate Turn
        eval_metrics = cls.evaluate_response_heuristics(
            question=current_question,
            response_text=payload.candidate_response_text,
        )

        turn_response = InterviewResponse(
            session_id=session.id,
            question_id=current_question.id,
            turn_index=curr_idx,
            candidate_response_text=payload.candidate_response_text,
            audio_duration_seconds=payload.audio_duration_seconds,
            score=eval_metrics["score"],
            technical_depth_score=eval_metrics["technical_depth_score"],
            structure_star_score=eval_metrics["structure_star_score"],
            communication_clarity_score=eval_metrics["communication_clarity_score"],
            tradeoff_score=eval_metrics["tradeoff_score"],
            strengths=eval_metrics["strengths"],
            improvements=eval_metrics["improvements"],
            star_breakdown=eval_metrics["star_breakdown"],
            exemplary_answer=current_question.evaluation_criteria.get("exemplary_answer"),
            ai_feedback_text=eval_metrics["ai_feedback_text"],
        )
        db.add(turn_response)

        # 2. Advance Question Index
        session.current_question_index += 1
        is_completed = session.current_question_index >= len(sorted_questions)

        next_q_dto = None
        if not is_completed:
            next_q = sorted_questions[session.current_question_index]
            next_q_dto = InterviewQuestionResponse(
                id=next_q.id,
                question_index=next_q.question_index,
                category=next_q.category,
                question_text=next_q.question_text,
                context_or_scenario=next_q.context_or_scenario,
                target_competencies=next_q.target_competencies,
                evaluation_criteria=next_q.evaluation_criteria,
                suggested_duration_seconds=next_q.suggested_duration_seconds,
            )
        else:
            # Complete session
            await cls._finalize_session_internal(db=db, session=session, user_id=user_id)

        await db.commit()
        await db.refresh(turn_response)

        return InterviewSubmitTurnResult(
            session_id=session.id,
            turn_response=InterviewTurnResponse(
                id=turn_response.id,
                session_id=turn_response.session_id,
                question_id=turn_response.question_id,
                turn_index=turn_response.turn_index,
                candidate_response_text=turn_response.candidate_response_text,
                audio_duration_seconds=turn_response.audio_duration_seconds,
                score=turn_response.score,
                technical_depth_score=turn_response.technical_depth_score,
                structure_star_score=turn_response.structure_star_score,
                communication_clarity_score=turn_response.communication_clarity_score,
                tradeoff_score=turn_response.tradeoff_score,
                strengths=turn_response.strengths,
                improvements=turn_response.improvements,
                star_breakdown=turn_response.star_breakdown,
                exemplary_answer=turn_response.exemplary_answer,
                ai_feedback_text=turn_response.ai_feedback_text,
                created_at=turn_response.created_at,
            ),
            next_question=next_q_dto,
            is_session_completed=is_completed,
            overall_session_score=session.overall_score,
        )

    @classmethod
    async def _finalize_session_internal(
        cls,
        db: AsyncSession,
        session: InterviewSession,
        user_id: str,
    ) -> None:
        """Internal helper calculating aggregate session metrics and syncing Career Twin."""
        # Query all responses for session
        res_list = (
            await db.execute(
                select(InterviewResponse).where(InterviewResponse.session_id == session.id)
            )
        ).scalars().all()

        if not res_list:
            session.overall_score = 70.0
            return

        avg_overall = sum(r.score for r in res_list) / len(res_list)
        avg_tech = sum(r.technical_depth_score for r in res_list) / len(res_list)
        avg_star = sum(r.structure_star_score for r in res_list) / len(res_list)
        avg_comm = sum(r.communication_clarity_score for r in res_list) / len(res_list)
        avg_tradeoff = sum(r.tradeoff_score for r in res_list) / len(res_list)

        all_strengths = [s for r in res_list for s in r.strengths]
        all_improvements = [i for r in res_list for i in r.improvements]

        session.overall_score = round(avg_overall, 1)
        session.technical_score = round(avg_tech, 1)
        session.behavioral_score = round(avg_star, 1)
        session.communication_score = round(avg_comm, 1)
        session.tradeoff_score = round(avg_tradeoff, 1)
        session.strengths = list(set(all_strengths))[:4]
        session.improvements = list(set(all_improvements))[:4]
        session.status = InterviewSessionStatus.COMPLETED.value
        session.completed_at = datetime.now(timezone.utc)
        session.summary_feedback = (
            f"Completed {session.total_questions}-question simulation for {session.target_role}. "
            f"Overall Placement Readiness Score: {session.overall_score}/100. "
            f"Technical Depth: {session.technical_score}%, STAR Framework: {session.behavioral_score}%, Communication: {session.communication_score}%."
        )

        # Career Digital Twin Synchronization
        interv_skill = (
            await db.execute(select(Skill).where(Skill.slug == "mock-interview"))
        ).scalar_one_or_none()
        if not interv_skill:
            interv_skill = (
                await db.execute(select(Skill).where(Skill.slug == "system-design"))
            ).scalar_one_or_none()
        if not interv_skill:
            # Create canonical mock-interview skill on demand
            interv_skill = Skill(
                name="Mock Interview & Communication",
                slug="mock-interview",
                category="SOFT_SKILL",
            )
            db.add(interv_skill)
            await db.flush()

        evidence = SkillEvidence(
            user_id=user_id,
            skill_id=interv_skill.id,
            source_type=EvidenceSourceType.INTERVIEW.value,
            source_id=f"interview:{session.id}",
            evidence_text=f"Achieved {session.overall_score}/100 score in {session.target_role} mock interview simulation ({session.total_questions} rounds).",
            confidence=min(0.95, round(session.overall_score / 100.0, 2)),
            verified=True,
        )
        db.add(evidence)

        # Update UserSkill
        user_skill = (
            await db.execute(
                select(UserSkill).where(
                    UserSkill.user_id == user_id,
                    UserSkill.skill_id == interv_skill.id,
                )
            )
        ).scalar_one_or_none()

        if user_skill:
            user_skill.proficiency = min(1.0, round((user_skill.proficiency + (session.overall_score / 100.0)) / 2.0, 2))
            user_skill.confidence = max(user_skill.confidence, 0.90)
            user_skill.last_verified_at = datetime.now(timezone.utc)
        else:
            user_skill = UserSkill(
                user_id=user_id,
                skill_id=interv_skill.id,
                proficiency=round(session.overall_score / 100.0, 2),
                confidence=0.90,
                years_experience=1.0,
                source=EvidenceSourceType.INTERVIEW.value,
                last_verified_at=datetime.now(timezone.utc),
            )
            db.add(user_skill)

    @classmethod
    async def list_user_sessions(
        cls,
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
    ) -> List[InterviewSessionSummary]:
        """Lists historical interview sessions for a candidate."""
        query = (
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.started_at.desc())
            .limit(limit)
        )
        sessions = (await db.execute(query)).scalars().all()

        return [
            InterviewSessionSummary(
                id=s.id,
                user_id=s.user_id,
                title=s.title,
                interview_type=s.interview_type,
                target_role=s.target_role,
                target_company=s.target_company,
                difficulty=s.difficulty,
                status=s.status,
                current_question_index=s.current_question_index,
                total_questions=s.total_questions,
                overall_score=s.overall_score,
                started_at=s.started_at,
                completed_at=s.completed_at,
            )
            for s in sessions
        ]
