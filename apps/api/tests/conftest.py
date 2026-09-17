import asyncio
import os
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set testing environment variables before importing app
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.core.database import Base, get_db
import app.models  # Ensures all ORM models are registered in Base.metadata
from app.main import app

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def prepare_database():
    """Create all tables in memory before each test, seed canonical skills, and drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed canonical skills
    from scripts.seed_skills import CANONICAL_SKILLS
    from app.models.skill import Skill, SkillAlias
    from app.services.skill_service import slugify
    async with TestingSessionLocal() as session:
        seen_aliases = set()
        for item in CANONICAL_SKILLS:
            name = item["name"]
            slug = slugify(name)
            category = item["category"]
            aliases = item.get("aliases", [])
            skill = Skill(name=name, slug=slug, category=category)
            session.add(skill)
            await session.flush()
            all_aliases = set([name.lower(), slug] + [a.lower() for a in aliases])
            for a in all_aliases:
                if a and a not in seen_aliases:
                    alias_obj = SkillAlias(alias=a, canonical_skill_id=skill.id)
                    session.add(alias_obj)
                    seen_aliases.add(a)
        await session.commit()

    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    """Override database dependency to use in-memory SQLite session."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def db_session():
    """Database session fixture for unit tests."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def async_client():
    """Async test client fixture for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

