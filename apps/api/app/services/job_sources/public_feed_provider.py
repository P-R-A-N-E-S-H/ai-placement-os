import logging
from datetime import datetime, timezone
from typing import List
import httpx

from app.models.job import EmploymentType, JobSourceType, LocationType
from app.services.job_sources.base import JobSourceProvider, RawJobData

logger = logging.getLogger("placement_os.job_provider.public_feed")


class ArbeitnowFeedProvider(JobSourceProvider):
    """Fetches real-time tech jobs from Arbeitnow public job board API with retry/fallback."""

    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def __init__(self):
        super().__init__(name="arbeitnow_feed", source_type=JobSourceType.PUBLIC_FEED)

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(self.API_URL)
                return res.status_code == 200
        except Exception:
            return False

    async def fetch_jobs(self, limit: int = 30) -> List[RawJobData]:
        jobs: List[RawJobData] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.API_URL)
                if response.status_code != 200:
                    logger.warning(f"Arbeitnow API returned status {response.status_code}")
                    return jobs

                payload = response.json()
                data_items = payload.get("data", [])

                for item in data_items[:limit]:
                    slug = item.get("slug", "")
                    title = item.get("title", "Software Engineer")
                    company = item.get("company_name", "Tech Company")
                    remote = item.get("remote", False)
                    location = item.get("location", "Remote" if remote else "Hybrid")
                    url = item.get("url", f"https://www.arbeitnow.com/jobs/{slug}")
                    description = item.get("description", "")
                    tags = item.get("tags", [])
                    job_types = item.get("job_types", [])

                    loc_type = LocationType.REMOTE.value if remote else LocationType.HYBRID.value
                    emp_type = EmploymentType.FULL_TIME.value
                    if "internship" in [t.lower() for t in job_types]:
                        emp_type = EmploymentType.INTERNSHIP.value
                    elif "part-time" in [t.lower() for t in job_types]:
                        emp_type = EmploymentType.PART_TIME.value

                    created_at_ts = item.get("created_at")
                    posted_at = datetime.now(timezone.utc)
                    if created_at_ts:
                        try:
                            posted_at = datetime.fromtimestamp(created_at_ts, tz=timezone.utc)
                        except Exception:
                            pass

                    jobs.append(
                        RawJobData(
                            source_name=self.name,
                            source_job_id=slug or url,
                            source_url=url,
                            title=title,
                            company=company,
                            location=location,
                            location_type=loc_type,
                            employment_type=emp_type,
                            min_experience_years=1.0 if "senior" not in title.lower() else 4.0,
                            max_experience_years=None,
                            min_salary=None,
                            max_salary=None,
                            salary_currency="EUR",
                            description=description,
                            raw_tags=tags,
                            posted_at=posted_at,
                        )
                    )
        except Exception as e:
            logger.warning(f"Failed to fetch jobs from {self.name}: {str(e)}")

        return jobs
