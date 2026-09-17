import pytest
from app.models.interview import InterviewQuestion, QuestionCategory
from app.services.interview_service import InterviewService


def test_evaluate_response_high_quality_technical_and_star():
    """Verify that a technical answer with STAR structure and quantitative metrics scores high."""
    question = InterviewQuestion(
        session_id="dummy-session",
        question_index=0,
        category=QuestionCategory.TECHNICAL_DEEP_DIVE.value,
        question_text="Explain how you architect a production RAG pipeline.",
        target_competencies=["rag", "vector-embeddings", "langchain"],
        evaluation_criteria={"key_concepts": ["hybrid search", "re-ranking", "chunking", "citations"]},
    )

    candidate_text = (
        "Situation: In our previous AI product, RAG retrieval was inaccurate and hallucinatory. "
        "Task: I was responsible for architecting a production hybrid RAG pipeline with sub-200ms latency. "
        "Action: I implemented LangChain with recursive document chunking, hybrid search in pgvector using vector-embeddings and BM25, "
        "followed by cross-encoder re-ranking and strict citation guardrails. "
        "Result: We reduced hallucinations by 85%, improved response accuracy to 94%, and cut p95 latency by 40%."
    )

    metrics = InterviewService.evaluate_response_heuristics(question=question, response_text=candidate_text)

    assert metrics["score"] >= 80.0
    assert metrics["technical_depth_score"] >= 75.0
    assert metrics["structure_star_score"] >= 80.0
    assert metrics["communication_clarity_score"] >= 80.0
    assert len(metrics["strengths"]) >= 2
    assert "Situation" in metrics["star_breakdown"]
    assert metrics["star_breakdown"]["Result"] == "Quantified"


def test_evaluate_response_low_quality_short_answer():
    """Verify that a brief unstructured answer receives appropriate constructive feedback."""
    question = InterviewQuestion(
        session_id="dummy-session",
        question_index=0,
        category=QuestionCategory.BEHAVIORAL_STAR.value,
        question_text="Tell me about a challenging bug you fixed.",
        target_competencies=["debugging"],
        evaluation_criteria={},
    )

    candidate_text = "I had a bug and I fixed it by reading logs."

    metrics = InterviewService.evaluate_response_heuristics(question=question, response_text=candidate_text)

    assert metrics["score"] < 65.0
    assert len(metrics["improvements"]) >= 1
    assert any("STAR" in imp or "metric" in imp or "domain" in imp for imp in metrics["improvements"])
