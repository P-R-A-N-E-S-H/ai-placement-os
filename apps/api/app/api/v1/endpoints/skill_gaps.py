from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import EntityNotFoundError
from app.models.skill_gap import SkillGapReport
from app.models.user import User
from app.schemas.skill_gap import (
    PrerequisiteEdge,
    PrerequisiteGraph,
    PrerequisiteNode,
    RoleBenchmarkSummary,
    SkillGapJobRequest,
    SkillGapReportResponse,
    SkillGapRoleRequest,
)
from app.services.skill_gap_service import ROLE_BENCHMARKS, SkillGapService
from app.services.skill_graph_service import (
    CANONICAL_PREREQUISITE_EDGES,
    CANONICAL_SKILL_BASE_HOURS,
    SkillGraphService,
)

router = APIRouter(prefix="/skills", tags=["Skill Gap Analysis & Prerequisite DAG"])


@router.get(
    "/roles/benchmarks",
    response_model=List[RoleBenchmarkSummary],
    summary="List Standard Industry Role Benchmarks",
)
async def list_role_benchmarks() -> List[RoleBenchmarkSummary]:
    """Retrieve curated industry benchmarks for AI, Backend, Full-Stack, DevOps, and Data roles."""
    return SkillGapService.list_role_benchmarks()


@router.get(
    "/prerequisites/graph",
    response_model=PrerequisiteGraph,
    summary="Get Full Canonical Prerequisite DAG Taxonomy",
)
async def get_prerequisite_graph() -> PrerequisiteGraph:
    """Returns all nodes and directed dependency edges in the canonical tech prerequisite graph."""
    nodes: List[PrerequisiteNode] = []
    for slug, hours in CANONICAL_SKILL_BASE_HOURS.items():
        nodes.append(
            PrerequisiteNode(
                id=slug,
                name=slug.replace("-", " ").title(),
                category="General",
                current_proficiency=0.0,
                required_proficiency=0.7,
                unlock_status="UNLOCKED",
                is_gap=False,
            )
        )

    edges: List[PrerequisiteEdge] = []
    for src, tgt in CANONICAL_PREREQUISITE_EDGES:
        edges.append(
            PrerequisiteEdge(
                source=SkillGraphService.normalize_slug(src),
                target=SkillGraphService.normalize_slug(tgt),
            )
        )

    return PrerequisiteGraph(nodes=nodes, edges=edges)


@router.post(
    "/gap-analysis/role",
    response_model=SkillGapReportResponse,
    summary="Analyze Skill Gap Against Target Role Benchmark",
)
async def analyze_role_skill_gap(
    payload: SkillGapRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillGapReportResponse:
    """
    Evaluates candidate Career Digital Twin against target role competencies,
    computes DAG prerequisite order, time estimates, and ROI priority matrix.
    """
    return await SkillGapService.analyze_role_gap(
        db=db,
        user_id=current_user.id,
        target_role=payload.target_role,
        weekly_hours=payload.weekly_hours,
    )


@router.post(
    "/gap-analysis/job/{job_id}",
    response_model=SkillGapReportResponse,
    summary="Analyze Skill Gap Against Specific Ingested Job",
)
async def analyze_job_skill_gap(
    job_id: str,
    payload: SkillGapJobRequest = SkillGapJobRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillGapReportResponse:
    """
    Evaluates candidate Career Digital Twin against specific live opportunity requirements.
    """
    return await SkillGapService.analyze_job_gap(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
        weekly_hours=payload.weekly_hours,
    )


@router.get(
    "/gap-analysis/latest",
    response_model=SkillGapReportResponse,
    summary="Get Latest Skill Gap Analysis Report",
)
async def get_latest_gap_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillGapReportResponse:
    """
    Retrieves the most recent skill gap report, or auto-evaluates for candidate's target role.
    """
    report = await SkillGapService.get_latest_gap_report(db=db, user_id=current_user.id)
    if not report:
        raise EntityNotFoundError("No gap report available")
    return report


@router.get(
    "/gap-analysis/report/{report_id}",
    response_model=SkillGapReportResponse,
    summary="Get Specific Skill Gap Report",
)
async def get_gap_report_by_id(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillGapReportResponse:
    """
    Retrieves a specific persisted skill gap report by ID with user isolation.
    """
    res = await db.execute(
        select(SkillGapReport).where(
            SkillGapReport.id == report_id,
            SkillGapReport.user_id == current_user.id,
        )
    )
    report = res.scalar_one_or_none()
    if not report:
        raise EntityNotFoundError(f"Skill gap report with ID '{report_id}' not found")

    from app.schemas.skill_gap import (
        LearningPathwayStep,
        PriorityMatrixQuadrant,
        SkillGapItem,
    )

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
