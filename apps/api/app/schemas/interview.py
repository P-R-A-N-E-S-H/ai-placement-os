from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InterviewCreateRequest(BaseModel):
    interview_type: str = Field(default="MIXED", description="TECHNICAL, BEHAVIORAL, SYSTEM_DESIGN, MIXED")
    target_role: str = Field(default="AI Engineer", description="Target role e.g. AI Engineer, Backend Engineer")
    target_company: Optional[str] = Field(default=None, description="Optional target company name")
    difficulty: str = Field(default="MEDIUM", description="EASY, MEDIUM, HARD")
    total_questions: int = Field(default=5, ge=2, le=10, description="Total questions to simulate")


class InterviewRespondRequest(BaseModel):
    candidate_response_text: str = Field(..., min_length=5, description="Candidate's spoken or typed answer")
    audio_duration_seconds: Optional[float] = Field(default=None, description="Audio duration if spoken")


class InterviewQuestionResponse(BaseModel):
    id: str
    question_index: int
    category: str
    question_text: str
    context_or_scenario: Optional[str] = None
    target_competencies: List[str] = []
    evaluation_criteria: Dict[str, Any] = {}
    suggested_duration_seconds: int = 180

    class Config:
        from_attributes = True


class InterviewTurnResponse(BaseModel):
    id: str
    session_id: str
    question_id: str
    turn_index: int
    candidate_response_text: str
    audio_duration_seconds: Optional[float] = None
    score: float
    technical_depth_score: float
    structure_star_score: float
    communication_clarity_score: float
    tradeoff_score: float
    strengths: List[str] = []
    improvements: List[str] = []
    star_breakdown: Dict[str, str] = {}
    exemplary_answer: Optional[str] = None
    ai_feedback_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewSessionSummary(BaseModel):
    id: str
    user_id: str
    title: str
    interview_type: str
    target_role: str
    target_company: Optional[str] = None
    difficulty: str
    status: str
    current_question_index: int
    total_questions: int
    overall_score: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InterviewSessionDetail(BaseModel):
    id: str
    user_id: str
    title: str
    interview_type: str
    target_role: str
    target_company: Optional[str] = None
    difficulty: str
    status: str
    current_question_index: int
    total_questions: int
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    behavioral_score: Optional[float] = None
    communication_score: Optional[float] = None
    tradeoff_score: Optional[float] = None
    summary_feedback: Optional[str] = None
    strengths: List[str] = []
    improvements: List[str] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[InterviewQuestionResponse] = []
    responses: List[InterviewTurnResponse] = []

    class Config:
        from_attributes = True


class InterviewSubmitTurnResult(BaseModel):
    session_id: str
    turn_response: InterviewTurnResponse
    next_question: Optional[InterviewQuestionResponse] = None
    is_session_completed: bool
    overall_session_score: Optional[float] = None
