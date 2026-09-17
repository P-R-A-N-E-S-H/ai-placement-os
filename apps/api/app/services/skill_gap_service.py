import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError, ValidationError
from app.models.job import Job, JobSkill
from app.models.profile import UserProfile
from app.models.skill import Skill, UserSkill
from app.models.skill_gap import SkillGapReport
from app.schemas.skill_gap import (
    GapImportanceEnum,
    GapTypeEnum,
    LearningPathwayStep,
    PrerequisiteEdge,
    PrerequisiteGraph,
    PrerequisiteNode,
    PriorityMatrixQuadrant,
    PriorityTierEnum,
    RoleBenchmarkSummary,
    SkillGapItem,
    SkillGapReportResponse,
    UnlockStatusEnum,
)
from app.services.skill_graph_service import (
    CANONICAL_PREREQUISITE_EDGES,
    SkillGraphService,
)


ROLE_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "ai-engineer": {
        "role_slug": "ai-engineer",
        "role_name": "AI & Autonomous Agent Systems Engineer",
        "category": "AI / ML",
        "description": "Designs, builds, and deploys multi-agent autonomous architectures, LLM reasoning pipelines, RAG systems, and fine-tuned models.",
        "typical_ctc_range": "₹18L - ₹35L / yr",
        "required_skills": [
            {"name": "Python", "slug": "python", "proficiency": 0.8, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "PyTorch", "slug": "pytorch", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "LangGraph", "slug": "langgraph", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "LangChain", "slug": "langchain", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "RAG & Vector DBs", "slug": "vector-embeddings-rag", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "FastAPI", "slug": "fastapi", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "DSA", "slug": "dsa", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "PostgreSQL", "slug": "postgresql", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
        ],
        "preferred_skills": [
            {"name": "Docker", "slug": "docker", "proficiency": 0.6, "importance": GapImportanceEnum.RECOMMENDED.value},
            {"name": "Redis", "slug": "redis", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
            {"name": "Kubernetes", "slug": "kubernetes", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
            {"name": "MLOps", "slug": "mlops", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
        ],
    },
    "backend-engineer": {
        "role_slug": "backend-engineer",
        "role_name": "Backend & Distributed Systems SDE",
        "category": "Backend",
        "description": "Architects high-throughput microservices, distributed caching layers, resilient database models, and scalable cloud APIs.",
        "typical_ctc_range": "₹16L - ₹32L / yr",
        "required_skills": [
            {"name": "Python", "slug": "python", "proficiency": 0.8, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "DSA", "slug": "dsa", "proficiency": 0.8, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "PostgreSQL", "slug": "postgresql", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "FastAPI", "slug": "fastapi", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "System Design", "slug": "system-design", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Redis", "slug": "redis", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Docker", "slug": "docker", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
        ],
        "preferred_skills": [
            {"name": "Kafka", "slug": "kafka", "proficiency": 0.5, "importance": GapImportanceEnum.RECOMMENDED.value},
            {"name": "Kubernetes", "slug": "kubernetes", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
            {"name": "CI/CD", "slug": "ci-cd", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
        ],
    },
    "full-stack-engineer": {
        "role_slug": "full-stack-engineer",
        "role_name": "Full-Stack Product Engineer",
        "category": "Full Stack",
        "description": "Builds end-to-end web applications with modern frontend frameworks, responsive UI systems, and resilient backend services.",
        "typical_ctc_range": "₹14L - ₹28L / yr",
        "required_skills": [
            {"name": "TypeScript", "slug": "typescript", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "React", "slug": "react", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Next.js", "slug": "next-js", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Python", "slug": "python", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "PostgreSQL", "slug": "postgresql", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Tailwind CSS", "slug": "tailwind-css", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "REST APIs", "slug": "rest-apis", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
        ],
        "preferred_skills": [
            {"name": "Docker", "slug": "docker", "proficiency": 0.5, "importance": GapImportanceEnum.RECOMMENDED.value},
            {"name": "Redis", "slug": "redis", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
            {"name": "CI/CD", "slug": "ci-cd", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
        ],
    },
    "devops-engineer": {
        "role_slug": "devops-engineer",
        "role_name": "DevOps & Cloud Infrastructure Engineer",
        "category": "DevOps / Cloud",
        "description": "Manages automated CI/CD pipelines, container orchestration, infrastructure as code, and cloud reliability.",
        "typical_ctc_range": "₹15L - ₹30L / yr",
        "required_skills": [
            {"name": "Linux", "slug": "linux", "proficiency": 0.8, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Docker", "slug": "docker", "proficiency": 0.8, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Kubernetes", "slug": "kubernetes", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "CI/CD", "slug": "ci-cd", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "AWS", "slug": "aws", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Python", "slug": "python", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
        ],
        "preferred_skills": [
            {"name": "Terraform", "slug": "terraform", "proficiency": 0.6, "importance": GapImportanceEnum.RECOMMENDED.value},
            {"name": "System Design", "slug": "system-design", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
        ],
    },
    "data-scientist": {
        "role_slug": "data-scientist",
        "role_name": "Data Scientist & Applied ML Specialist",
        "category": "Data Science",
        "description": "Applies statistical modeling, exploratory data analysis, predictive machine learning, and deep learning architectures.",
        "typical_ctc_range": "₹15L - ₹30L / yr",
        "required_skills": [
            {"name": "Python", "slug": "python", "proficiency": 0.8, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "SQL", "slug": "sql", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Pandas", "slug": "pandas", "proficiency": 0.8, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "NumPy", "slug": "numpy", "proficiency": 0.8, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "Scikit-Learn", "slug": "scikit-learn", "proficiency": 0.7, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "PyTorch", "slug": "pytorch", "proficiency": 0.6, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
            {"name": "DSA", "slug": "dsa", "proficiency": 0.5, "importance": GapImportanceEnum.CRITICAL_REQUIRED.value},
        ],
        "preferred_skills": [
            {"name": "MLOps", "slug": "mlops", "proficiency": 0.5, "importance": GapImportanceEnum.RECOMMENDED.value},
            {"name": "Docker", "slug": "docker", "proficiency": 0.5, "importance": GapImportanceEnum.PREFERRED.value},
        ],
    },
}


class SkillGapService:
    """
    Orchestration Engine for Skill Gap Analysis, DAG Prerequisite Modeling,
    Deterministic Time Estimation, and ROI Priority Quadrant Classification.
    """

    @classmethod
    def list_role_benchmarks(cls) -> List[RoleBenchmarkSummary]:
        """Returns all available standard industry role benchmarks."""
        results: List[RoleBenchmarkSummary] = []
        for role in ROLE_BENCHMARKS.values():
            results.append(
                RoleBenchmarkSummary(
                    role_slug=role["role_slug"],
                    role_name=role["role_name"],
                    description=role["description"],
                    category=role["category"],
                    required_skills=role["required_skills"],
                    preferred_skills=role["preferred_skills"],
                    typical_ctc_range=role["typical_ctc_range"],
                )
            )
        return results

    @classmethod
    async def get_user_skill_profile(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> Tuple[Dict[str, float], Dict[str, UserSkill]]:
        """
        Loads all user verified skills into a proficiency dictionary and user_skill entity lookup.
        """
        result = await db.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill), selectinload(UserSkill.evidence))
            .where(UserSkill.user_id == user_id)
        )
        user_skills = result.scalars().all()

        proficiencies: Dict[str, float] = {}
        lookup: Dict[str, UserSkill] = {}

        for us in user_skills:
            if us.skill:
                slug = SkillGraphService.normalize_slug(us.skill.slug or us.skill.name)
                proficiencies[slug] = us.proficiency
                lookup[slug] = us

        return proficiencies, lookup

    @classmethod
    def compute_gap_item(
        cls,
        skill_name: str,
        skill_slug: str,
        category: str,
        importance: str,
        required_proficiency: float,
        user_proficiencies: Dict[str, float],
    ) -> SkillGapItem:
        """
        Deterministically evaluates an individual skill requirement against candidate state.
        """
        norm_slug = SkillGraphService.normalize_slug(skill_slug)
        curr_prof = user_proficiencies.get(norm_slug, 0.0)

        # Gap Type
        if curr_prof >= required_proficiency:
            gap_type = GapTypeEnum.SATISFIED.value
            deficit = 0.0
        elif curr_prof > 0.0:
            gap_type = GapTypeEnum.PROFICIENCY_DEFICIT.value
            deficit = required_proficiency - curr_prof
        else:
            gap_type = GapTypeEnum.MISSING.value
            deficit = required_proficiency

        # Prerequisite & Unlock Status
        unlock_status, missing_prereqs = SkillGraphService.resolve_unlock_status(
            norm_slug, curr_prof, required_proficiency, user_proficiencies
        )
        direct_prereqs = SkillGraphService.get_prerequisites_for_skill(norm_slug)

        # Effort estimation
        base_hours = SkillGraphService.get_base_hours(norm_slug)
        if gap_type == GapTypeEnum.SATISFIED.value:
            est_hours = 0.0
        else:
            # Multiplier: 1.1 for missing skill, 0.85 for existing skill needing upgrade
            multiplier = 1.1 if gap_type == GapTypeEnum.MISSING.value else 0.85
            est_hours = round(base_hours * deficit * multiplier, 1)

        # Importance weight: CRITICAL = 1.0, RECOMMENDED = 0.6, PREFERRED = 0.3
        imp_weight = 1.0 if importance == GapImportanceEnum.CRITICAL_REQUIRED.value else 0.6 if importance == GapImportanceEnum.RECOMMENDED.value else 0.3

        # ROI score: (Weight * 100) / sqrt(hours + 1.0)
        roi_score = round((imp_weight * 100.0) / math.sqrt(est_hours + 1.0), 2) if est_hours > 0 else 100.0

        # Priority Tier
        if gap_type == GapTypeEnum.SATISFIED.value:
            priority_tier = PriorityTierEnum.P3_ELECTIVE.value
        elif est_hours <= 15.0 and (imp_weight >= 0.6 or unlock_status == UnlockStatusEnum.UNLOCKED.value):
            priority_tier = PriorityTierEnum.P0_QUICK_WIN.value
        elif imp_weight == 1.0 and unlock_status == UnlockStatusEnum.UNLOCKED.value:
            priority_tier = PriorityTierEnum.P1_CORE_PREREQUISITE.value
        elif imp_weight == 1.0 or est_hours > 20.0:
            priority_tier = PriorityTierEnum.P2_MAJOR_MILESTONE.value
        else:
            priority_tier = PriorityTierEnum.P3_ELECTIVE.value

        # Actionable Recommendation
        if gap_type == GapTypeEnum.SATISFIED.value:
            action = f"Strong competence in {skill_name} ({int(curr_prof*100)}%). Ready for advanced assessment."
        elif unlock_status == UnlockStatusEnum.LOCKED.value:
            action = f"Complete prerequisites ({', '.join(missing_prereqs)}) first before tackling {skill_name}."
        elif gap_type == GapTypeEnum.PROFICIENCY_DEFICIT.value:
            action = f"Upgrade {skill_name} from {int(curr_prof*100)}% to {int(required_proficiency*100)}% through targeted project implementation."
        else:
            action = f"Learn foundational {skill_name} core concepts and build a hands-on proof-of-concept project."

        return SkillGapItem(
            skill_name=skill_name,
            slug=norm_slug,
            category=category,
            importance=importance,
            current_proficiency=round(curr_prof, 2),
            required_proficiency=round(required_proficiency, 2),
            gap_type=gap_type,
            priority_tier=priority_tier,
            unlock_status=unlock_status,
            prerequisites=direct_prereqs,
            missing_prerequisites=missing_prereqs,
            estimated_hours=est_hours,
            roi_score=roi_score,
            learning_order_index=0,
            recommended_action=action,
        )

    @classmethod
    async def analyze_role_gap(
        cls,
        db: AsyncSession,
        user_id: str,
        target_role: str,
        weekly_hours: float = 15.0,
    ) -> SkillGapReportResponse:
        """
        Executes complete deterministic skill gap analysis against a standard target role.
        """
        role_slug = SkillGraphService.normalize_slug(target_role)
        benchmark = ROLE_BENCHMARKS.get(role_slug)

        if not benchmark:
            # Fallback to AI Engineer if not found
            benchmark = ROLE_BENCHMARKS.get("ai-engineer")
            role_slug = "ai-engineer"

        user_proficiencies, _ = await cls.get_user_skill_profile(db, user_id)

        all_target_skills = benchmark["required_skills"] + benchmark["preferred_skills"]
        gap_items: List[SkillGapItem] = []

        total_weight = 0.0
        earned_weight = 0.0

        for req in all_target_skills:
            imp = req.get("importance", GapImportanceEnum.CRITICAL_REQUIRED.value)
            weight = 1.0 if imp == GapImportanceEnum.CRITICAL_REQUIRED.value else 0.5
            total_weight += weight

            curr = user_proficiencies.get(SkillGraphService.normalize_slug(req["slug"]), 0.0)
            req_prof = req["proficiency"]
            earned_weight += weight * min(1.0, curr / req_prof if req_prof > 0 else 1.0)

            item = cls.compute_gap_item(
                skill_name=req["name"],
                skill_slug=req["slug"],
                category=benchmark.get("category", "General"),
                importance=imp,
                required_proficiency=req_prof,
                user_proficiencies=user_proficiencies,
            )
            gap_items.append(item)

        # Readiness Score (0 to 100)
        readiness_score = round((earned_weight / total_weight * 100.0) if total_weight > 0 else 0.0, 1)

        # Topological sorting for learning sequence
        slugs_to_sort = [g.slug for g in gap_items if g.gap_type != GapTypeEnum.SATISFIED.value]
        sorted_slugs = SkillGraphService.topological_sort(slugs_to_sort)

        # Assign learning order index
        order_map = {slug: idx + 1 for idx, slug in enumerate(sorted_slugs)}
        for item in gap_items:
            item.learning_order_index = order_map.get(item.slug, 999)

        # Sort gap_items by learning order
        gap_items.sort(key=lambda x: (x.gap_type == GapTypeEnum.SATISFIED.value, x.learning_order_index))

        # Build Learning Pathway steps
        learning_pathway: List[LearningPathwayStep] = []
        for item in gap_items:
            if item.gap_type != GapTypeEnum.SATISFIED.value:
                learning_pathway.append(
                    LearningPathwayStep(
                        order=item.learning_order_index,
                        skill_name=item.skill_name,
                        slug=item.slug,
                        category=item.category,
                        estimated_hours=item.estimated_hours,
                        priority_tier=item.priority_tier,
                        unlock_status=item.unlock_status,
                        prerequisites=item.prerequisites,
                        recommended_action=item.recommended_action,
                    )
                )

        # Build Priority Matrix Quadrants
        matrix = PriorityMatrixQuadrant()
        for item in gap_items:
            if item.gap_type != GapTypeEnum.SATISFIED.value:
                if item.estimated_hours <= 15.0 and item.importance == GapImportanceEnum.CRITICAL_REQUIRED.value:
                    matrix.quick_wins.append(item)
                elif item.estimated_hours > 15.0 and item.importance == GapImportanceEnum.CRITICAL_REQUIRED.value:
                    matrix.major_milestones.append(item)
                elif item.estimated_hours > 15.0:
                    matrix.deep_dives.append(item)
                else:
                    matrix.electives.append(item)

        # Build Prerequisite Graph Visual Representation
        nodes: List[PrerequisiteNode] = []
        node_ids: Set[str] = set()
        for item in gap_items:
            nodes.append(
                PrerequisiteNode(
                    id=item.slug,
                    name=item.skill_name,
                    category=item.category,
                    current_proficiency=item.current_proficiency,
                    required_proficiency=item.required_proficiency,
                    unlock_status=item.unlock_status,
                    is_gap=item.gap_type != GapTypeEnum.SATISFIED.value,
                )
            )
            node_ids.add(item.slug)

        edges: List[PrerequisiteEdge] = []
        for src, tgt in CANONICAL_PREREQUISITE_EDGES:
            norm_src = SkillGraphService.normalize_slug(src)
            norm_tgt = SkillGraphService.normalize_slug(tgt)
            if norm_src in node_ids and norm_tgt in node_ids:
                edges.append(PrerequisiteEdge(source=norm_src, target=norm_tgt))

        prereq_graph = PrerequisiteGraph(nodes=nodes, edges=edges)

        # Metrics
        total_skills_required = len(gap_items)
        matched_skills_count = sum(1 for g in gap_items if g.gap_type == GapTypeEnum.SATISFIED.value)
        missing_critical_count = sum(
            1 for g in gap_items
            if g.gap_type == GapTypeEnum.MISSING.value and g.importance == GapImportanceEnum.CRITICAL_REQUIRED.value
        )
        proficiency_gap_count = sum(1 for g in gap_items if g.gap_type == GapTypeEnum.PROFICIENCY_DEFICIT.value)
        total_estimated_hours = round(sum(g.estimated_hours for g in gap_items), 1)
        estimated_weeks = round(total_estimated_hours / max(1.0, weekly_hours), 1)

        # Persist to database (Upsert)
        existing_report_res = await db.execute(
            select(SkillGapReport).where(
                SkillGapReport.user_id == user_id,
                SkillGapReport.target_type == "ROLE",
                SkillGapReport.target_id == role_slug,
            )
        )
        report = existing_report_res.scalar_one_or_none()

        gap_items_dicts = [g.model_dump() for g in gap_items]
        graph_dict = prereq_graph.model_dump()
        matrix_dict = matrix.model_dump()
        pathway_dicts = [p.model_dump() for p in learning_pathway]

        if report:
            report.target_title = benchmark["role_name"]
            report.target_company = None
            report.readiness_score = readiness_score
            report.total_skills_required = total_skills_required
            report.matched_skills_count = matched_skills_count
            report.missing_critical_count = missing_critical_count
            report.proficiency_gap_count = proficiency_gap_count
            report.total_estimated_hours = total_estimated_hours
            report.estimated_weeks = estimated_weeks
            report.gap_items = gap_items_dicts
            report.prerequisite_graph = graph_dict
            report.priority_matrix = matrix_dict
            report.learning_pathway = pathway_dicts
            report.updated_at = datetime.now(timezone.utc)
        else:
            report = SkillGapReport(
                user_id=user_id,
                target_type="ROLE",
                target_id=role_slug,
                target_title=benchmark["role_name"],
                target_company=None,
                readiness_score=readiness_score,
                total_skills_required=total_skills_required,
                matched_skills_count=matched_skills_count,
                missing_critical_count=missing_critical_count,
                proficiency_gap_count=proficiency_gap_count,
                total_estimated_hours=total_estimated_hours,
                estimated_weeks=estimated_weeks,
                gap_items=gap_items_dicts,
                prerequisite_graph=graph_dict,
                priority_matrix=matrix_dict,
                learning_pathway=pathway_dicts,
            )
            db.add(report)

        await db.commit()
        await db.refresh(report)

        return SkillGapReportResponse(
            id=report.id,
            user_id=report.user_id,
            target_type=report.target_type,
            target_id=report.target_id,
            target_title=report.target_title,
            target_company=report.target_company,
            readiness_score=report.readiness_score,
            total_skills_required=report.total_skills_required,
            matched_skills_count=report.matched_skills_count,
            missing_critical_count=report.missing_critical_count,
            proficiency_gap_count=report.proficiency_gap_count,
            total_estimated_hours=report.total_estimated_hours,
            estimated_weeks=report.estimated_weeks,
            gap_items=gap_items,
            prerequisite_graph=prereq_graph,
            priority_matrix=matrix,
            learning_pathway=learning_pathway,
            created_at=report.created_at,
        )

    @classmethod
    async def analyze_job_gap(
        cls,
        db: AsyncSession,
        user_id: str,
        job_id: str,
        weekly_hours: float = 15.0,
    ) -> SkillGapReportResponse:
        """
        Executes complete deterministic skill gap analysis against a specific live opportunity.
        """
        job_res = await db.execute(
            select(Job)
            .options(selectinload(Job.job_skills).selectinload(JobSkill.skill))
            .where(Job.id == job_id)
        )
        job = job_res.scalar_one_or_none()
        if not job:
            raise EntityNotFoundError(f"Job with ID '{job_id}' not found")

        user_proficiencies, _ = await cls.get_user_skill_profile(db, user_id)

        gap_items: List[SkillGapItem] = []
        total_weight = 0.0
        earned_weight = 0.0

        for js in job.job_skills:
            skill_name = js.skill.name if js.skill else "Skill"
            skill_slug = js.skill.slug if js.skill else SkillGraphService.normalize_slug(skill_name)
            skill_category = js.skill.category if js.skill else "General"

            imp = GapImportanceEnum.CRITICAL_REQUIRED.value if js.is_required else GapImportanceEnum.PREFERRED.value
            weight = 1.0 if js.is_required else 0.5
            total_weight += weight

            req_prof = 0.7 if js.is_required else 0.5
            curr = user_proficiencies.get(SkillGraphService.normalize_slug(skill_slug), 0.0)
            earned_weight += weight * min(1.0, curr / req_prof if req_prof > 0 else 1.0)

            item = cls.compute_gap_item(
                skill_name=skill_name,
                skill_slug=skill_slug,
                category=skill_category,
                importance=imp,
                required_proficiency=req_prof,
                user_proficiencies=user_proficiencies,
            )
            gap_items.append(item)

        # If job had no tagged skills, add fallback
        if not gap_items:
            gap_items.append(
                cls.compute_gap_item(
                    skill_name="Python",
                    skill_slug="python",
                    category="Programming Language",
                    importance=GapImportanceEnum.CRITICAL_REQUIRED.value,
                    required_proficiency=0.7,
                    user_proficiencies=user_proficiencies,
                )
            )
            total_weight = 1.0
            earned_weight = min(1.0, user_proficiencies.get("python", 0.0) / 0.7)

        readiness_score = round((earned_weight / total_weight * 100.0) if total_weight > 0 else 0.0, 1)

        # Topological sort for sequence
        slugs_to_sort = [g.slug for g in gap_items if g.gap_type != GapTypeEnum.SATISFIED.value]
        sorted_slugs = SkillGraphService.topological_sort(slugs_to_sort)

        order_map = {slug: idx + 1 for idx, slug in enumerate(sorted_slugs)}
        for item in gap_items:
            item.learning_order_index = order_map.get(item.slug, 999)

        gap_items.sort(key=lambda x: (x.gap_type == GapTypeEnum.SATISFIED.value, x.learning_order_index))

        # Learning pathway
        learning_pathway: List[LearningPathwayStep] = []
        for item in gap_items:
            if item.gap_type != GapTypeEnum.SATISFIED.value:
                learning_pathway.append(
                    LearningPathwayStep(
                        order=item.learning_order_index,
                        skill_name=item.skill_name,
                        slug=item.slug,
                        category=item.category,
                        estimated_hours=item.estimated_hours,
                        priority_tier=item.priority_tier,
                        unlock_status=item.unlock_status,
                        prerequisites=item.prerequisites,
                        recommended_action=item.recommended_action,
                    )
                )

        # Priority matrix
        matrix = PriorityMatrixQuadrant()
        for item in gap_items:
            if item.gap_type != GapTypeEnum.SATISFIED.value:
                if item.estimated_hours <= 15.0 and item.importance == GapImportanceEnum.CRITICAL_REQUIRED.value:
                    matrix.quick_wins.append(item)
                elif item.estimated_hours > 15.0 and item.importance == GapImportanceEnum.CRITICAL_REQUIRED.value:
                    matrix.major_milestones.append(item)
                elif item.estimated_hours > 15.0:
                    matrix.deep_dives.append(item)
                else:
                    matrix.electives.append(item)

        # Graph
        nodes: List[PrerequisiteNode] = []
        node_ids: Set[str] = set()
        for item in gap_items:
            nodes.append(
                PrerequisiteNode(
                    id=item.slug,
                    name=item.skill_name,
                    category=item.category,
                    current_proficiency=item.current_proficiency,
                    required_proficiency=item.required_proficiency,
                    unlock_status=item.unlock_status,
                    is_gap=item.gap_type != GapTypeEnum.SATISFIED.value,
                )
            )
            node_ids.add(item.slug)

        edges: List[PrerequisiteEdge] = []
        for src, tgt in CANONICAL_PREREQUISITE_EDGES:
            norm_src = SkillGraphService.normalize_slug(src)
            norm_tgt = SkillGraphService.normalize_slug(tgt)
            if norm_src in node_ids and norm_tgt in node_ids:
                edges.append(PrerequisiteEdge(source=norm_src, target=norm_tgt))

        prereq_graph = PrerequisiteGraph(nodes=nodes, edges=edges)

        # Metrics
        total_skills_required = len(gap_items)
        matched_skills_count = sum(1 for g in gap_items if g.gap_type == GapTypeEnum.SATISFIED.value)
        missing_critical_count = sum(
            1 for g in gap_items
            if g.gap_type == GapTypeEnum.MISSING.value and g.importance == GapImportanceEnum.CRITICAL_REQUIRED.value
        )
        proficiency_gap_count = sum(1 for g in gap_items if g.gap_type == GapTypeEnum.PROFICIENCY_DEFICIT.value)
        total_estimated_hours = round(sum(g.estimated_hours for g in gap_items), 1)
        estimated_weeks = round(total_estimated_hours / max(1.0, weekly_hours), 1)

        # Upsert report
        existing_report_res = await db.execute(
            select(SkillGapReport).where(
                SkillGapReport.user_id == user_id,
                SkillGapReport.target_type == "JOB",
                SkillGapReport.target_id == job.id,
            )
        )
        report = existing_report_res.scalar_one_or_none()

        gap_items_dicts = [g.model_dump() for g in gap_items]
        graph_dict = prereq_graph.model_dump()
        matrix_dict = matrix.model_dump()
        pathway_dicts = [p.model_dump() for p in learning_pathway]

        if report:
            report.target_title = job.title
            report.target_company = job.company
            report.readiness_score = readiness_score
            report.total_skills_required = total_skills_required
            report.matched_skills_count = matched_skills_count
            report.missing_critical_count = missing_critical_count
            report.proficiency_gap_count = proficiency_gap_count
            report.total_estimated_hours = total_estimated_hours
            report.estimated_weeks = estimated_weeks
            report.gap_items = gap_items_dicts
            report.prerequisite_graph = graph_dict
            report.priority_matrix = matrix_dict
            report.learning_pathway = pathway_dicts
            report.updated_at = datetime.now(timezone.utc)
        else:
            report = SkillGapReport(
                user_id=user_id,
                target_type="JOB",
                target_id=job.id,
                target_title=job.title,
                target_company=job.company,
                readiness_score=readiness_score,
                total_skills_required=total_skills_required,
                matched_skills_count=matched_skills_count,
                missing_critical_count=missing_critical_count,
                proficiency_gap_count=proficiency_gap_count,
                total_estimated_hours=total_estimated_hours,
                estimated_weeks=estimated_weeks,
                gap_items=gap_items_dicts,
                prerequisite_graph=graph_dict,
                priority_matrix=matrix_dict,
                learning_pathway=pathway_dicts,
            )
            db.add(report)

        await db.commit()
        await db.refresh(report)

        return SkillGapReportResponse(
            id=report.id,
            user_id=report.user_id,
            target_type=report.target_type,
            target_id=report.target_id,
            target_title=report.target_title,
            target_company=report.target_company,
            readiness_score=report.readiness_score,
            total_skills_required=report.total_skills_required,
            matched_skills_count=report.matched_skills_count,
            missing_critical_count=report.missing_critical_count,
            proficiency_gap_count=report.proficiency_gap_count,
            total_estimated_hours=report.total_estimated_hours,
            estimated_weeks=report.estimated_weeks,
            gap_items=gap_items,
            prerequisite_graph=prereq_graph,
            priority_matrix=matrix,
            learning_pathway=learning_pathway,
            created_at=report.created_at,
        )

    @classmethod
    async def get_latest_gap_report(
        cls,
        db: AsyncSession,
        user_id: str,
    ) -> Optional[SkillGapReportResponse]:
        """
        Retrieves the latest evaluated gap report for the candidate.
        If none exists, automatically runs evaluation for candidate's primary target role.
        """
        result = await db.execute(
            select(SkillGapReport)
            .where(SkillGapReport.user_id == user_id)
            .order_by(SkillGapReport.updated_at.desc())
            .limit(1)
        )
        report = result.scalar_one_or_none()

        if not report:
            # Check user's preferred target role from UserProfile
            prof_res = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
            user_profile = prof_res.scalar_one_or_none()
            target_role = "ai-engineer"
            if user_profile and user_profile.target_roles and len(user_profile.target_roles) > 0:
                target_role = user_profile.target_roles[0]

            return await cls.analyze_role_gap(db, user_id, target_role)

        # Deserialize into response model
        gap_items = [SkillGapItem(**item) for item in report.gap_items]
        graph = PrerequisiteGraph(**report.prerequisite_graph)
        matrix = PriorityMatrixQuadrant(**report.priority_matrix)
        pathway = [LearningPathwayStep(**step) for step in report.learning_pathway]

        return SkillGapReportResponse(
            id=report.id,
            user_id=report.user_id,
            target_type=report.target_type,
            target_id=report.target_id,
            target_title=report.target_title,
            target_company=report.target_company,
            readiness_score=report.readiness_score,
            total_skills_required=report.total_skills_required,
            matched_skills_count=report.matched_skills_count,
            missing_critical_count=report.missing_critical_count,
            proficiency_gap_count=report.proficiency_gap_count,
            total_estimated_hours=report.total_estimated_hours,
            estimated_weeks=report.estimated_weeks,
            gap_items=gap_items,
            prerequisite_graph=graph,
            priority_matrix=matrix,
            learning_pathway=pathway,
            created_at=report.created_at,
        )
