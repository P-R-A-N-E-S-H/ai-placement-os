from app.core.config import Settings


def test_settings_initialization():
    """Test that default settings initialize properly with required properties."""
    s = Settings()
    assert s.PROJECT_NAME == "AI PlacementOS"
    assert s.API_V1_STR == "/api/v1"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert s.PRIMARY_LLM_PROVIDER in ["openai", "anthropic", "ollama", "mock"]
