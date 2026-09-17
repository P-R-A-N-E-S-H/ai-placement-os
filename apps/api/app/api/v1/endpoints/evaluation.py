from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user
from app.models.evaluation import EvaluationBenchmarkRun
from app.models.user import User
from app.schemas.evaluation import (
    BenchmarkRunRequest,
    BenchmarkSuiteSummaryResponse,
    EvaluationBenchmarkRunResponse,
)
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmark Framework"])


@router.post("/run", response_model=BenchmarkSuiteSummaryResponse)
async def run_evaluation_benchmarks(
    request: Optional[BenchmarkRunRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> BenchmarkSuiteSummaryResponse:
    """Execute automated benchmark suites (RAG Groundedness, 4-Rubric Interview Calibration, DSA Complexity Profiler)."""
    payload = request or BenchmarkRunRequest()
    return await EvaluationService.run_suite(db=db, request=payload)


@router.get("/runs", response_model=List[EvaluationBenchmarkRunResponse])
async def list_evaluation_runs(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> List[EvaluationBenchmarkRunResponse]:
    """Retrieve historical evaluation run records."""
    runs = await EvaluationService.list_runs(db=db, limit=limit)
    return [EvaluationBenchmarkRunResponse.model_validate(r) for r in runs]


@router.get("/runs/{run_id}", response_model=EvaluationBenchmarkRunResponse)
async def get_evaluation_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> EvaluationBenchmarkRunResponse:
    """Get detailed metrics and summary report for a specific evaluation benchmark run."""
    stmt = select(EvaluationBenchmarkRun).where(EvaluationBenchmarkRun.id == run_id)
    res = await db.execute(stmt)
    run = res.scalar_one_or_none()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark run with id '{run_id}' not found",
        )
    return EvaluationBenchmarkRunResponse.model_validate(run)
