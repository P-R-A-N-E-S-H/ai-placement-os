import pytest
from app.services.job_sources.curated_provider import CuratedPlacementProvider
from app.services.job_sources.public_feed_provider import ArbeitnowFeedProvider


@pytest.mark.asyncio
async def test_curated_placement_provider_fetch():
    provider = CuratedPlacementProvider()
    assert await provider.health_check() is True

    jobs = await provider.fetch_jobs(limit=5)
    assert len(jobs) > 0
    assert len(jobs) <= 5

    first = jobs[0]
    assert first.title != ""
    assert first.company != ""
    assert first.source_name == "curated_placement"
    assert first.salary_currency == "INR"
    assert len(first.raw_tags) > 0


@pytest.mark.asyncio
async def test_arbeitnow_provider_health_check_or_fallback():
    provider = ArbeitnowFeedProvider()
    # Should not raise exception regardless of network connectivity
    health = await provider.health_check()
    assert isinstance(health, bool)

    jobs = await provider.fetch_jobs(limit=2)
    assert isinstance(jobs, list)
