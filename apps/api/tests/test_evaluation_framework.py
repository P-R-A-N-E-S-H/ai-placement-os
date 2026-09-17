import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import BenchmarkType, EvaluationBenchmarkRun
from app.schemas.evaluation import BenchmarkRunRequest
from app.services.evaluation_service import EvaluationService


@pytest.mark.asyncio
async def test_evaluate_rag_groundedness(db_session: AsyncSession):
    """Test automated RAG faithfulness and citation benchmark execution."""
    run = await EvaluationService.evaluate_rag_groundedness(db_session)
    assert run.benchmark_type == BenchmarkType.RAG_GROUNDEDNESS.value
    assert run.status == "PASSED"
    assert run.total_test_cases == 4
    assert run.passed_test_cases == 4
    assert run.mean_score >= 80.0
    assert "faithfulness_rate" in run.metrics
    assert run.duration_ms >= 0


@pytest.mark.asyncio
async def test_evaluate_interview_rubric_calibration(db_session: AsyncSession):
    """Test 4-rubric interview scoring calibration and exemplar discrimination."""
    run = await EvaluationService.evaluate_interview_rubric_calibration(db_session)
    assert run.benchmark_type == BenchmarkType.INTERVIEW_CALIBRATION.value
    assert run.status == "PASSED"
    assert run.total_test_cases == 2
    assert run.passed_test_cases == 2
    assert run.mean_score > 0
    assert "exemplar_discrimination_margin" in run.metrics


@pytest.mark.asyncio
async def test_evaluate_dsa_complexity_profiler(db_session: AsyncSession):
    """Test AST static code analysis Big-O benchmark."""
    run = await EvaluationService.evaluate_dsa_complexity_profiler(db_session)
    assert run.benchmark_type == BenchmarkType.DSA_COMPLEXITY_PROFILER.value
    assert run.status == "PASSED"
    assert run.total_test_cases == 4
    assert run.passed_test_cases == 4
    assert run.mean_score == 100.0



@pytest.mark.asyncio
async def test_run_suite_composite(db_session: AsyncSession):
    """Test running full composite benchmark suite."""
    req = BenchmarkRunRequest(benchmark_type="ALL")
    summary = await EvaluationService.run_suite(db_session, req)
    assert summary.total_benchmarks_executed == 3
    assert summary.all_benchmarks_passed is True
    assert summary.overall_system_score >= 85.0
    assert len(summary.runs) == 3

    # Test listing runs
    runs = await EvaluationService.list_runs(db_session, limit=10)
    assert len(runs) >= 3
