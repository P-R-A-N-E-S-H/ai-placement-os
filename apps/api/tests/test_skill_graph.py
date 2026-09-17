import pytest
from app.services.skill_graph_service import SkillGraphService


def test_topological_sort_preserves_prerequisite_dependencies():
    # Input skills in reverse / mixed order
    skills = ["langgraph", "langchain", "pytorch", "python", "rag"]
    ordered = SkillGraphService.topological_sort(skills)

    # Validate Python comes before PyTorch, PyTorch before RAG, RAG before LangChain, LangChain before LangGraph
    python_idx = ordered.index("python")
    pytorch_idx = ordered.index("pytorch")
    rag_idx = ordered.index("rag")
    langchain_idx = ordered.index("langchain")
    langgraph_idx = ordered.index("langgraph")

    assert python_idx < pytorch_idx, "Python must precede PyTorch"
    assert pytorch_idx < rag_idx or pytorch_idx < langchain_idx, "PyTorch must precede RAG / LangChain"
    assert rag_idx < langchain_idx or pytorch_idx < langchain_idx, "RAG/PyTorch must precede LangChain"
    assert langchain_idx < langgraph_idx, "LangChain must precede LangGraph"


def test_topological_sort_backend_chain():
    skills = ["system-design", "microservices", "fastapi", "python", "sql", "postgresql"]
    ordered = SkillGraphService.topological_sort(skills)

    python_idx = ordered.index("python")
    sql_idx = ordered.index("sql")
    fastapi_idx = ordered.index("fastapi")
    postgres_idx = ordered.index("postgresql")
    microservices_idx = ordered.index("microservices")
    system_design_idx = ordered.index("system-design")

    assert python_idx < fastapi_idx
    assert sql_idx < postgres_idx
    assert fastapi_idx < microservices_idx
    assert microservices_idx < system_design_idx


def test_unlock_status_resolution():
    # 1. User has no skills: PyTorch requires Python -> PyTorch should be LOCKED
    user_profs = {}
    status, missing = SkillGraphService.resolve_unlock_status("pytorch", 0.0, 0.7, user_profs)
    assert status == "LOCKED"
    assert "python" in missing

    # 2. User has learned Python (0.8) -> PyTorch should be UNLOCKED
    user_profs = {"python": 0.8}
    status, missing = SkillGraphService.resolve_unlock_status("pytorch", 0.0, 0.7, user_profs)
    assert status == "UNLOCKED"
    assert len(missing) == 0

    # 3. User has PyTorch (0.8) which exceeds required 0.7 -> should be ACQUIRED
    user_profs = {"python": 0.8, "pytorch": 0.8}
    status, missing = SkillGraphService.resolve_unlock_status("pytorch", 0.8, 0.7, user_profs)
    assert status == "ACQUIRED"
    assert len(missing) == 0


def test_ancestor_prerequisites():
    ancestors = SkillGraphService.get_all_ancestor_prerequisites("langgraph")
    assert "langchain" in ancestors
    assert "transformers" in ancestors or "rag" in ancestors or "pytorch" in ancestors or "python" in ancestors
