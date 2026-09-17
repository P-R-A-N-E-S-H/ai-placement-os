import hashlib
import re
from typing import Optional, Tuple
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.services.job_sources.base import RawJobData


class JobDeduplicator:
    """Multi-factor content fingerprinting and deduplication engine."""

    @staticmethod
    def compute_fingerprint(company: str, title: str, location: str, description: str) -> str:
        """
        Generate a deterministic SHA-256 semantic fingerprint from company, title, location,
        and normalized description summary.
        """
        company_norm = re.sub(r"[^a-z0-9]", "", company.lower())
        title_norm = re.sub(r"[^a-z0-9]", "", title.lower())
        location_norm = re.sub(r"[^a-z0-9]", "", location.lower())

        # Clean description whitespace and take first 350 significant characters
        desc_clean = re.sub(r"\s+", " ", description.lower().strip())[:350]
        desc_hash = hashlib.sha256(desc_clean.encode("utf-8")).hexdigest()[:16]

        composite = f"{company_norm}::{title_norm}::{location_norm}::{desc_hash}"
        return hashlib.sha256(composite.encode("utf-8")).hexdigest()

    @classmethod
    async def find_existing_job(
        cls,
        db: AsyncSession,
        raw: RawJobData,
        fingerprint: str,
    ) -> Optional[Job]:
        """
        Check for duplicates using:
        1. Exact content fingerprint
        2. Exact Source + Source Job ID
        3. Exact canonical Source URL
        """
        conditions = [Job.fingerprint == fingerprint]

        if raw.source_job_id:
            conditions.append(
                (Job.source == raw.source_name) & (Job.source_job_id == raw.source_job_id)
            )

        if raw.source_url:
            conditions.append(Job.source_url == raw.source_url)

        query = select(Job).where(or_(*conditions))
        result = await db.execute(query)
        return result.scalars().first()
