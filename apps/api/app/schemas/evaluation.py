from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BenchmarkRunRequest(BaseModel):
    benchmark_type: str = Field(
        "ALL",
        description="ALL, RAG_GROUNDEDNESS, MATCHING_PRECISION, INTERVIEW_CALIBRATION, DSA_COMPLEXITY_PROFILER",
    )


class EvaluationBenchmarkRunResponse(BaseModel):
    id: str
    benchmark_type: str
    benchmark_name: str
    status: str
    total_test_cases: int
    passed_test_cases: int
    mean_score: float
    metrics: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int
    summary_report: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BenchmarkSuiteSummaryResponse(BaseModel):
    total_benchmarks_executed: int
    overall_system_score: float
    all_benchmarks_passed: bool
    runs: List[EvaluationBenchmarkRunResponse]
