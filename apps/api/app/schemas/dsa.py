from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DsaTestCaseResponse(BaseModel):
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    explanation: Optional[str] = None
    order_index: int

    class Config:
        from_attributes = True


class DsaProblemSummary(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str
    category: str
    expected_time_complexity: str
    expected_space_complexity: str
    acceptance_rate: float
    order_index: int
    is_solved: bool = False
    attempts_count: int = 0

    class Config:
        from_attributes = True


class DsaProblemDetail(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str
    category: str
    description: str
    constraints: List[str]
    hints: List[str]
    starter_code: Dict[str, str]
    expected_time_complexity: str
    expected_space_complexity: str
    acceptance_rate: float
    order_index: int
    is_solved: bool = False
    last_submitted_code: Optional[str] = None
    last_language: Optional[str] = None
    test_cases: List[DsaTestCaseResponse] = []

    class Config:
        from_attributes = True


class DsaRunRequest(BaseModel):
    language: str = Field(default="python", description="Programming language: python, javascript, cpp, java")
    code: str = Field(..., description="Candidate solution code")
    custom_input: Optional[str] = Field(default=None, description="Optional custom input data")


class DsaSubmitRequest(BaseModel):
    language: str = Field(default="python", description="Programming language: python, javascript, cpp, java")
    code: str = Field(..., description="Candidate solution code")


class TestCaseRunResult(BaseModel):
    test_case_index: int
    input_data: str
    expected_output: str
    actual_output: Optional[str] = None
    passed: bool
    runtime_ms: float = 0.0
    error_message: Optional[str] = None


class DsaRunResponse(BaseModel):
    status: str
    runtime_ms: float
    memory_mb: float
    passed_count: int
    total_count: int
    results: List[TestCaseRunResult]
    compile_error: Optional[str] = None


class DsaSubmissionResponse(BaseModel):
    id: str
    user_id: str
    problem_id: str
    problem_title: Optional[str] = None
    problem_slug: Optional[str] = None
    difficulty: Optional[str] = None
    language: str
    code: str
    status: str
    runtime_ms: float
    memory_mb: float
    passed_test_cases: int
    total_test_cases: int
    error_message: Optional[str] = None
    failed_test_case_input: Optional[str] = None
    failed_test_case_expected: Optional[str] = None
    failed_test_case_actual: Optional[str] = None
    ai_feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DsaStatsResponse(BaseModel):
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    total_problems: int
    overall_accuracy_percentage: float
    total_submissions: int
    topic_breakdown: Dict[str, Dict[str, int]]
