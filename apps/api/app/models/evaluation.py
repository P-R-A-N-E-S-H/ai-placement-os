from __future__ import annotations

import enum
from typing import Any, Dict, Optional
from sqlalchemy import Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class BenchmarkType(str, enum.Enum):
    RAG_GROUNDEDNESS = "RAG_GROUNDEDNESS"
    MATCHING_PRECISION = "MATCHING_PRECISION"
    INTERVIEW_CALIBRATION = "INTERVIEW_CALIBRATION"
    DSA_COMPLEXITY_PROFILER = "DSA_COMPLEXITY_PROFILER"
    END_TO_END_COPILOT = "END_TO_END_COPILOT"


class EvaluationBenchmarkRun(Base, UUIDMixin, TimestampMixin):
    """Stores benchmark quality evaluation results and score metrics."""
    __tablename__ = "evaluation_benchmark_runs"

    benchmark_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    benchmark_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)
    total_test_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed_test_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mean_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    summary_report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
