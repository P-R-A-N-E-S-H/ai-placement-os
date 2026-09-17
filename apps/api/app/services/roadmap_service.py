import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError, ValidationError
from app.models.profile import UserProfile
from app.models.roadmap import (
    LearningRoadmap,
    ModuleStatus,
    RoadmapModule,
    RoadmapStatus,
    RoadmapTask,
    TaskType,
)
from app.models.skill import EvidenceSourceType, SkillEvidence, UserSkill
from app.models.skill_gap import SkillGapReport
from app.schemas.roadmap import (
    LearningRoadmapResponse,
    LearningRoadmapSummary,
    RoadmapGenerateRequest,
    RoadmapModuleResponse,
    RoadmapTaskResponse,
    TaskResourceItem,
    TaskToggleRequest,
)
from app.services.skill_gap_service import ROLE_BENCHMARKS, SkillGapService
from app.services.skill_graph_service import SkillGraphService
from app.services.skill_service import SkillService


CURATED_SKILL_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "python": [
        {"title": "Official Python 3 Documentation & Standard Library", "url": "https://docs.python.org/3/", "type": "DOCS"},
        {"title": "Python AsyncIO & High-Performance Concurrency Guide", "url": "https://docs.python.org/3/library/asyncio.html", "type": "DOCS"},
        {"title": "Awesome Python Production Best Practices", "url": "https://github.com/vinta/awesome-python", "type": "GITHUB"},
    ],
    "pytorch": [
        {"title": "PyTorch Deep Learning Official Tutorials", "url": "https://pytorch.org/tutorials/", "type": "DOCS"},
        {"title": "Deep Learning with PyTorch Zero-to-Mastery", "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html", "type": "VIDEO"},
        {"title": "PyTorch Model Zoo & Tensor Computation Starter", "url": "https://github.com/pytorch/examples", "type": "GITHUB"},
    ],
    "langchain": [
        {"title": "LangChain Python Conceptual Framework & Architecture", "url": "https://python.langchain.com/docs/", "type": "DOCS"},
        {"title": "LangChain Production RAG & Tool Calling Recipes", "url": "https://python.langchain.com/docs/use_cases/question_answering/", "type": "LAB"},
        {"title": "LangChain AI Official GitHub Repository", "url": "https://github.com/langchain-ai/langchain", "type": "GITHUB"},
    ],
    "langgraph": [
        {"title": "LangGraph Autonomous Multi-Agent Orchestration Docs", "url": "https://langchain-ai.github.io/langgraph/", "type": "DOCS"},
        {"title": "Building Hierarchical Multi-Agent Workflows Tutorial", "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/", "type": "VIDEO"},
        {"title": "LangGraph Multi-Agent Workflows & StateGraph Starter", "url": "https://github.com/langchain-ai/langgraph", "type": "GITHUB"},
    ],
    "vector-embeddings-rag": [
        {"title": "Pinecone RAG Mastery & Vector Search Architecture", "url": "https://www.pinecone.io/learn/series/rag/", "type": "DOCS"},
        {"title": "Advanced Retrieval Augmented Generation (Chunking & Re-ranking)", "url": "https://docs.llamaindex.ai/en/stable/optimizing/production_rag/", "type": "LAB"},
        {"title": "pgvector PostgreSQL Vector Similarity Search Extension", "url": "https://github.com/pgvector/pgvector", "type": "GITHUB"},
    ],
    "rag": [
        {"title": "Retrieval Augmented Generation System Design", "url": "https://www.pinecone.io/learn/series/rag/", "type": "DOCS"},
        {"title": "Building End-to-End Hybrid RAG with Vector & BM25", "url": "https://github.com/qdrant/qdrant", "type": "GITHUB"},
    ],
    "fastapi": [
        {"title": "FastAPI Official Documentation & Tutorial", "url": "https://fastapi.tiangolo.com/", "type": "DOCS"},
        {"title": "Async Microservices & Dependency Injection in FastAPI", "url": "https://fastapi.tiangolo.com/tutorial/dependencies/", "type": "LAB"},
        {"title": "Full-Stack FastAPI & PostgreSQL Production Template", "url": "https://github.com/tiangolo/full-stack-fastapi-template", "type": "GITHUB"},
    ],
    "docker": [
        {"title": "Docker Official Containerization Guide", "url": "https://docs.docker.com/get-started/", "type": "DOCS"},
        {"title": "Multi-Stage Docker Builds for Python & AI Services", "url": "https://docs.docker.com/build/building/multi-stage/", "type": "LAB"},
        {"title": "Awesome Docker Compose & Production Microservices", "url": "https://github.com/docker/awesome-compose", "type": "GITHUB"},
    ],
    "postgresql": [
        {"title": "PostgreSQL Documentation & Query Optimization", "url": "https://www.postgresql.org/docs/", "type": "DOCS"},
        {"title": "Indexing Strategies & Transaction Isolation in Postgres", "url": "https://use-the-index-luke.com/", "type": "DOCS"},
    ],
    "redis": [
        {"title": "Redis In-Memory Data Store & Caching Patterns", "url": "https://redis.io/docs/", "type": "DOCS"},
        {"title": "Distributed Caching & Pub/Sub Queue Implementation", "url": "https://redis.io/docs/manual/pubsub/", "type": "LAB"},
    ],
    "kubernetes": [
        {"title": "Kubernetes Official Concepts & Pod Lifecycle", "url": "https://kubernetes.io/docs/concepts/", "type": "DOCS"},
        {"title": "Deploying Microservices on Kubernetes (Minikube / EKS)", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "LAB"},
    ],
    "dsa": [
        {"title": "LeetCode NeetCode 150 Blind Placement Patterns", "url": "https://neetcode.io/practice", "type": "LAB"},
        {"title": "Algorithms & Data Structures in Python Reference", "url": "https://github.com/TheAlgorithms/Python", "type": "GITHUB"},
    ],
    "system-design": [
        {"title": "System Design Primer by Donne Martin", "url": "https://github.com/donnemartin/system-design-primer", "type": "GITHUB"},
        {"title": "Designing Data-Intensive Applications Core Summaries", "url": "https://github.com/ept/ddia-references", "type": "DOCS"},
    ],
    "typescript": [
        {"title": "TypeScript Official Handbook & Generics", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "type": "DOCS"},
        {"title": "TypeScript Deep Dive & Advanced Utility Types", "url": "https://basarat.gitbook.io/typescript", "type": "DOCS"},
    ],
    "react": [
        {"title": "React Official Docs & Hooks Deep Dive", "url": "https://react.dev/", "type": "DOCS"},
        {"title": "Full-Stack React & Server Components", "url": "https://nextjs.org/docs", "type": "DOCS"},
    ],
    "next-js": [
        {"title": "Next.js App Router & Server Actions Guide", "url": "https://nextjs.org/docs", "type": "DOCS"},
        {"title": "Building Production Full-Stack Next.js Applications", "url": "https://github.com/vercel/next.js/tree/canary/examples", "type": "GITHUB"},
    ],
    "linux": [
        {"title": "Linux Command Line & Shell Scripting Mastery", "url": "https://linuxjourney.com/", "type": "DOCS"},
        {"title": "Bash Scripting Cheat Sheet & Automation Labs", "url": "https://devhints.io/bash", "type": "DOCS"},
    ],
    "ci-cd": [
        {"title": "GitHub Actions Official Workflow Documentation", "url": "https://docs.github.com/en/actions", "type": "DOCS"},
        {"title": "Automated Testing & Multi-Environment CI/CD Pipelines", "url": "https://github.com/actions/starter-workflows", "type": "GITHUB"},
    ],
    "mlops": [
        {"title": "MLOps Guide: CI/CD/CT for Machine Learning", "url": "https://ml-ops.org/", "type": "DOCS"},
        {"title": "Model Serving & Monitoring with MLflow / Prometheus", "url": "https://mlflow.org/docs/latest/index.html", "type": "LAB"},
    ],
}


class RoadmapService:
    """
    Adaptive Learning Roadmap Engine.
    Synthesizes multi-week curriculum from Phase 6 Skill Gaps, generates daily tasks,
    and synchronizes task progress and proof-of-work evidence with Career Digital Twin.
    """

    @classmethod
    def get_resources_for_skill(cls, skill_slug: str) -> List[Dict[str, Any]]:
        """Returns authoritative curated learning resources for a skill."""
        norm = SkillGraphService.normalize_slug(skill_slug)
        if norm in CURATED_SKILL_RESOURCES:
            return CURATED_SKILL_RESOURCES[norm]
        return [
            {
                "title": f"{skill_slug.replace('-', ' ').title()} Technical Documentation",
                "url": f"https://www.google.com/search?q={skill_slug}+official+documentation",
                "type": "DOCS",
            },
            {
                "title": f"Hands-on {skill_slug.replace('-', ' ').title()} Practice Projects",
                "url": f"https://github.com/topics/{skill_slug}",
                "type": "GITHUB",
            },
        ]

    @classmethod
    async def generate_roadmap(
        cls,
        db: AsyncSession,
        user_id: str,
        payload: RoadmapGenerateRequest,
    ) -> LearningRoadmapResponse:
        """
        Synthesizes a structured adaptive learning roadmap from Phase 6 Skill Gap Report.
        """
        target_role = payload.target_role or "ai-engineer"
        target_role_slug = SkillGraphService.normalize_slug(target_role)
        total_weeks = payload.total_weeks or 6
        weekly_hours = payload.weekly_hours or 15.0

        # 1. Fetch or generate Skill Gap Report for target
        if payload.target_job_id:
            gap_report = await SkillGapService.analyze_job_gap(
                db=db, user_id=user_id, job_id=payload.target_job_id, weekly_hours=weekly_hours
            )
        else:
            gap_report = await SkillGapService.analyze_role_gap(
                db=db, user_id=user_id, target_role=target_role_slug, weekly_hours=weekly_hours
            )

        # 2. Extract non-satisfied gap items in topological learning order
        pathway_items = [g for g in gap_report.gap_items if g.gap_type != "SATISFIED"]

        # If user has no gaps, include all role skills in advanced mode
        if not pathway_items:
            pathway_items = gap_report.gap_items

        # 3. Deactivate previous active roadmaps for this user
        existing_active = await db.execute(
            select(LearningRoadmap).where(
                LearningRoadmap.user_id == user_id,
                LearningRoadmap.status == RoadmapStatus.ACTIVE.value,
            )
        )
        for old_map in existing_active.scalars().all():
            old_map.status = RoadmapStatus.PAUSED.value

        # 4. Cluster skills into weekly modules
        total_gaps = len(pathway_items)
        skills_per_week = max(1, math.ceil(total_gaps / total_weeks))

        roadmap_title = (
            f"{gap_report.target_title} — {total_weeks}-Week Adaptive Master Plan"
        )
        roadmap_desc = (
            f"Personalized career acceleration plan targeting {gap_report.target_title} with "
            f"{gap_report.total_estimated_hours}h estimated learning effort across {total_weeks} structured modules."
        )

        roadmap = LearningRoadmap(
            user_id=user_id,
            gap_report_id=gap_report.id,
            title=roadmap_title,
            description=roadmap_desc,
            target_role=target_role_slug,
            target_job_id=payload.target_job_id,
            target_job_title=gap_report.target_title if gap_report.target_type == "JOB" else None,
            target_job_company=gap_report.target_company if gap_report.target_type == "JOB" else None,
            total_weeks=total_weeks,
            weekly_hours=weekly_hours,
            total_estimated_hours=gap_report.total_estimated_hours,
            total_tasks=0,
            completed_tasks=0,
            progress_percentage=0.0,
            status=RoadmapStatus.ACTIVE.value,
        )
        db.add(roadmap)
        await db.flush()

        task_counter = 0

        # 5. Build Modules and Daily Tasks
        for week_idx in range(total_weeks):
            week_num = week_idx + 1
            start_idx = week_idx * skills_per_week
            end_idx = min(total_gaps, (week_idx + 1) * skills_per_week)
            week_skills = pathway_items[start_idx:end_idx] if start_idx < total_gaps else [pathway_items[-1]]

            focus_names = [s.skill_name for s in week_skills]
            focus_slugs = [s.slug for s in week_skills]
            est_module_hours = sum(s.estimated_hours for s in week_skills) or weekly_hours

            module_status = (
                ModuleStatus.IN_PROGRESS.value if week_num == 1 else ModuleStatus.LOCKED.value
            )

            module_title = f"Week {week_num}: {', '.join(focus_names[:2])} Mastery"
            module_desc = (
                f"Deep dive into {', '.join(focus_names)} with theoretical foundations, hands-on lab exercises, "
                f"and verifiable capstone project deliverables."
            )

            module = RoadmapModule(
                roadmap_id=roadmap.id,
                week_number=week_num,
                title=module_title,
                description=module_desc,
                focus_skills=focus_slugs,
                estimated_hours=round(est_module_hours, 1),
                status=module_status,
                order_index=week_num,
            )
            db.add(module)
            await db.flush()

            # Create 4 structured daily tasks per module
            primary_skill = week_skills[0]

            tasks_data = [
                {
                    "day": 1,
                    "title": f"Core Foundations & Architectural Deep Dive: {primary_skill.skill_name}",
                    "desc": f"Study core architecture, syntax, and design patterns for {primary_skill.skill_name}. Review official documentation and master key APIs.",
                    "type": TaskType.CONCEPT.value,
                    "mins": 90,
                    "skill": primary_skill.slug,
                },
                {
                    "day": 2,
                    "title": f"Hands-on Implementation Lab & Exercises: {primary_skill.skill_name}",
                    "desc": f"Complete hands-on coding exercises and algorithmic problem solving with {primary_skill.skill_name}. Write modular, tested code.",
                    "type": TaskType.PRACTICE.value,
                    "mins": 120,
                    "skill": primary_skill.slug,
                },
                {
                    "day": 3,
                    "title": f"Capstone Project Deliverable: {primary_skill.skill_name} Production Feature",
                    "desc": f"Build and deploy a functional mini-project using {primary_skill.skill_name}. Commit to GitHub to generate verifiable Career Twin proof of work.",
                    "type": TaskType.PROJECT.value,
                    "mins": 180,
                    "skill": primary_skill.slug,
                },
                {
                    "day": 4,
                    "title": f"Placement Assessment & Interview Checkpoint: {primary_skill.skill_name}",
                    "desc": f"Self-assess your competency in {primary_skill.skill_name} with technical interview questions and scenario-based system design challenges.",
                    "type": TaskType.QUIZ.value,
                    "mins": 60,
                    "skill": primary_skill.slug,
                },
            ]

            for t_info in tasks_data:
                task_counter += 1
                task_resources = cls.get_resources_for_skill(t_info["skill"])

                task = RoadmapTask(
                    roadmap_id=roadmap.id,
                    module_id=module.id,
                    day_number=t_info["day"],
                    title=t_info["title"],
                    description=t_info["desc"],
                    task_type=t_info["type"],
                    skill_slug=t_info["skill"],
                    estimated_minutes=t_info["mins"],
                    resources=task_resources,
                    is_completed=False,
                    order_index=task_counter,
                )
                db.add(task)

        roadmap.total_tasks = task_counter
        await db.commit()

        # Reload complete roadmap with relations
        return await cls.get_roadmap_by_id(db, user_id, roadmap.id)

    @classmethod
    async def get_roadmap_by_id(
        cls,
        db: AsyncSession,
        user_id: str,
        roadmap_id: str,
    ) -> LearningRoadmapResponse:
        """
        Retrieves roadmap by ID with eager-loaded modules, tasks, and progress telemetry.
        """
        res = await db.execute(
            select(LearningRoadmap)
            .options(
                selectinload(LearningRoadmap.modules).selectinload(RoadmapModule.tasks),
                selectinload(LearningRoadmap.tasks),
            )
            .where(LearningRoadmap.id == roadmap_id, LearningRoadmap.user_id == user_id)
        )
        roadmap = res.scalar_one_or_none()
        if not roadmap:
            raise EntityNotFoundError(f"Roadmap with ID '{roadmap_id}' not found")

        # Build response hierarchy
        module_responses: List[RoadmapModuleResponse] = []
        total_completed = 0
        total_tasks_count = 0

        for mod in sorted(roadmap.modules, key=lambda m: m.week_number):
            task_responses: List[RoadmapTaskResponse] = []
            mod_completed = 0

            for t in sorted(mod.tasks, key=lambda x: x.order_index):
                if t.is_completed:
                    mod_completed += 1
                    total_completed += 1
                total_tasks_count += 1

                task_responses.append(
                    RoadmapTaskResponse(
                        id=t.id,
                        roadmap_id=t.roadmap_id,
                        module_id=t.module_id,
                        day_number=t.day_number,
                        title=t.title,
                        description=t.description,
                        task_type=t.task_type,
                        skill_slug=t.skill_slug,
                        estimated_minutes=t.estimated_minutes,
                        resources=[TaskResourceItem(**r) for r in t.resources],
                        is_completed=t.is_completed,
                        completed_at=t.completed_at,
                        evidence_text=t.evidence_text,
                        evidence_source_id=t.evidence_source_id,
                        order_index=t.order_index,
                    )
                )

            mod_total = len(mod.tasks)
            mod_progress = round((mod_completed / mod_total * 100.0) if mod_total > 0 else 0.0, 1)

            module_responses.append(
                RoadmapModuleResponse(
                    id=mod.id,
                    roadmap_id=mod.roadmap_id,
                    week_number=mod.week_number,
                    title=mod.title,
                    description=mod.description,
                    focus_skills=mod.focus_skills,
                    estimated_hours=mod.estimated_hours,
                    status=mod.status,
                    order_index=mod.order_index,
                    tasks=task_responses,
                    completed_task_count=mod_completed,
                    total_task_count=mod_total,
                    progress_percentage=mod_progress,
                )
            )

        overall_progress = round(
            (total_completed / total_tasks_count * 100.0) if total_tasks_count > 0 else 0.0, 1
        )

        return LearningRoadmapResponse(
            id=roadmap.id,
            user_id=roadmap.user_id,
            gap_report_id=roadmap.gap_report_id,
            title=roadmap.title,
            description=roadmap.description,
            target_role=roadmap.target_role,
            target_job_id=roadmap.target_job_id,
            target_job_title=roadmap.target_job_title,
            target_job_company=roadmap.target_job_company,
            total_weeks=roadmap.total_weeks,
            weekly_hours=roadmap.weekly_hours,
            total_estimated_hours=roadmap.total_estimated_hours,
            total_tasks=total_tasks_count,
            completed_tasks=total_completed,
            progress_percentage=overall_progress,
            status=roadmap.status,
            modules=module_responses,
            created_at=roadmap.created_at,
            updated_at=roadmap.updated_at,
        )

    @classmethod
    async def get_active_roadmap(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> Optional[LearningRoadmapResponse]:
        """
        Retrieves current active learning roadmap, or auto-generates one from candidate's profile.
        """
        res = await db.execute(
            select(LearningRoadmap)
            .where(
                LearningRoadmap.user_id == user_id,
                LearningRoadmap.status == RoadmapStatus.ACTIVE.value,
            )
            .order_by(LearningRoadmap.updated_at.desc())
            .limit(1)
        )
        active = res.scalar_one_or_none()

        if active:
            return await cls.get_roadmap_by_id(db, user_id, active.id)

        # Auto-generate if none exists
        prof_res = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        user_prof = prof_res.scalar_one_or_none()
        target_role = "ai-engineer"
        if user_prof and user_prof.target_roles and len(user_prof.target_roles) > 0:
            target_role = user_prof.target_roles[0]

        return await cls.generate_roadmap(
            db, user_id, RoadmapGenerateRequest(target_role=target_role, total_weeks=6, weekly_hours=15.0)
        )

    @classmethod
    async def list_roadmaps(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> List[LearningRoadmapSummary]:
        """Lists all roadmaps for candidate."""
        res = await db.execute(
            select(LearningRoadmap)
            .where(LearningRoadmap.user_id == user_id)
            .order_by(LearningRoadmap.created_at.desc())
        )
        roadmaps = res.scalars().all()
        return [
            LearningRoadmapSummary(
                id=r.id,
                title=r.title,
                target_role=r.target_role,
                target_job_title=r.target_job_title,
                total_weeks=r.total_weeks,
                weekly_hours=r.weekly_hours,
                total_tasks=r.total_tasks,
                completed_tasks=r.completed_tasks,
                progress_percentage=r.progress_percentage,
                status=r.status,
                created_at=r.created_at,
            )
            for r in roadmaps
        ]

    @classmethod
    async def toggle_task_completion(
        cls,
        db: AsyncSession,
        user_id: str,
        task_id: str,
        payload: TaskToggleRequest,
    ) -> RoadmapTaskResponse:
        """
        Toggles completion state of a task.
        If completed:
          1. Sets is_completed=True, completed_at=now.
          2. Automatically logs verifiable SkillEvidence in Career Twin.
          3. Upgrades UserSkill proficiency.
          4. Unlocks next module if all tasks in current module are done.
          5. Updates overall roadmap progress percentage.
        """
        task_res = await db.execute(
            select(RoadmapTask)
            .options(selectinload(RoadmapTask.roadmap), selectinload(RoadmapTask.module))
            .where(RoadmapTask.id == task_id)
        )
        task = task_res.scalar_one_or_none()
        if not task or task.roadmap.user_id != user_id:
            raise EntityNotFoundError(f"Task with ID '{task_id}' not found")

        task.is_completed = not task.is_completed

        if task.is_completed:
            task.completed_at = datetime.now(timezone.utc)
            task.evidence_text = payload.evidence_text or f"Completed learning roadmap study task: '{task.title}'"
            task.evidence_source_id = payload.evidence_source_id or f"roadmap-task-{task.id}"

            # Bidirectional Career Twin Sync: Auto-log SkillEvidence & Upgrade Proficiency
            canonical_skill = await SkillService.get_or_create_canonical_skill(
                db, task.skill_slug.replace("-", " ").title()
            )

            evidence = SkillEvidence(
                user_id=user_id,
                skill_id=canonical_skill.id,
                source_type=EvidenceSourceType.LEARNING.value,
                source_id=task.evidence_source_id,
                evidence_text=task.evidence_text,
                confidence=0.85,
                verified=True,
            )
            db.add(evidence)

            # Upgrade UserSkill proficiency (+0.15 up to 0.9)
            user_skill_res = await db.execute(
                select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == canonical_skill.id)
            )
            user_skill = user_skill_res.scalar_one_or_none()
            if user_skill:
                user_skill.proficiency = min(1.0, round(user_skill.proficiency + 0.15, 2))
                user_skill.confidence = min(1.0, round(user_skill.confidence + 0.1, 2))
                user_skill.last_verified_at = datetime.now(timezone.utc)
            else:
                user_skill = UserSkill(
                    user_id=user_id,
                    skill_id=canonical_skill.id,
                    proficiency=0.6,
                    confidence=0.75,
                    years_experience=0.5,
                    source=EvidenceSourceType.LEARNING.value,
                    last_verified_at=datetime.now(timezone.utc),
                )
                db.add(user_skill)
        else:
            task.completed_at = None

        await db.flush()

        # Recalculate Module & Roadmap progress
        module_tasks_res = await db.execute(
            select(RoadmapTask).where(RoadmapTask.module_id == task.module_id)
        )
        mod_tasks = module_tasks_res.scalars().all()
        all_mod_completed = all(t.is_completed for t in mod_tasks)

        if all_mod_completed:
            task.module.status = ModuleStatus.COMPLETED.value
            # Unlock next module
            next_mod_res = await db.execute(
                select(RoadmapModule).where(
                    RoadmapModule.roadmap_id == task.roadmap_id,
                    RoadmapModule.week_number == task.module.week_number + 1,
                )
            )
            next_mod = next_mod_res.scalar_one_or_none()
            if next_mod and next_mod.status == ModuleStatus.LOCKED.value:
                next_mod.status = ModuleStatus.IN_PROGRESS.value
        else:
            task.module.status = ModuleStatus.IN_PROGRESS.value

        # Recalculate Roadmap totals
        all_tasks_res = await db.execute(
            select(RoadmapTask).where(RoadmapTask.roadmap_id == task.roadmap_id)
        )
        all_tasks = all_tasks_res.scalars().all()
        completed_count = sum(1 for t in all_tasks if t.is_completed)
        total_count = len(all_tasks)

        task.roadmap.completed_tasks = completed_count
        task.roadmap.progress_percentage = round(
            (completed_count / total_count * 100.0) if total_count > 0 else 0.0, 1
        )
        if completed_count == total_count and total_count > 0:
            task.roadmap.status = RoadmapStatus.COMPLETED.value
        else:
            task.roadmap.status = RoadmapStatus.ACTIVE.value

        await db.commit()
        await db.refresh(task)

        return RoadmapTaskResponse(
            id=task.id,
            roadmap_id=task.roadmap_id,
            module_id=task.module_id,
            day_number=task.day_number,
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            skill_slug=task.skill_slug,
            estimated_minutes=task.estimated_minutes,
            resources=[TaskResourceItem(**r) for r in task.resources],
            is_completed=task.is_completed,
            completed_at=task.completed_at,
            evidence_text=task.evidence_text,
            evidence_source_id=task.evidence_source_id,
            order_index=task.order_index,
        )
