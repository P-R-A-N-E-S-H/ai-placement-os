import pytest
from app.services.job_deduplicator import JobDeduplicator
from app.services.job_sources.base import RawJobData


def test_fingerprint_normalization_and_invariance():
    fp1 = JobDeduplicator.compute_fingerprint(
        company="Uber Technologies",
        title="Software Engineer I",
        location="Bengaluru, India",
        description="We are hiring a backend engineer for distributed systems.",
    )

    # Identical with whitespace and case variations
    fp2 = JobDeduplicator.compute_fingerprint(
        company="Uber technologies  ",
        title="  Software Engineer I",
        location="bengaluru, INDIA",
        description="We are   hiring a backend engineer for distributed systems.",
    )

    assert fp1 == fp2
    assert len(fp1) == 64  # SHA-256


def test_fingerprint_distinguishes_different_jobs():
    fp1 = JobDeduplicator.compute_fingerprint(
        company="Uber",
        title="Software Engineer",
        location="Bengaluru",
        description="Backend Go role",
    )

    fp2 = JobDeduplicator.compute_fingerprint(
        company="Microsoft",
        title="Software Engineer",
        location="Bengaluru",
        description="Backend Go role",
    )

    assert fp1 != fp2
