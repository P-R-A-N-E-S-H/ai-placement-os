import pytest
from app.models.application import ApplicationStage
from app.models.user import User
from app.schemas.application import ApplicationCreateRequest, ApplicationUpdateRequest
from app.services.application_service import ApplicationService
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_application_service_lifecycle():
    """Verify application creation, stage update, statistics, and deletion."""
    async with TestingSessionLocal() as db:
        user = User(email="app_tracker@example.com", password_hash="hashed_pw_test", is_active=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # 1. Create applications in different stages
        app1 = await ApplicationService.create_application(
            db=db,
            user_id=user.id,
            request=ApplicationCreateRequest(
                company_name="Google",
                job_title="AI Engineer",
                location="Mountain View, CA",
                stage=ApplicationStage.TECHNICAL_ROUND.value,
                salary_offered="$180k - $240k",
                match_score=94.5,
            ),
        )
        assert app1.id is not None
        assert app1.company_name == "Google"
        assert app1.stage == ApplicationStage.TECHNICAL_ROUND.value

        app2 = await ApplicationService.create_application(
            db=db,
            user_id=user.id,
            request=ApplicationCreateRequest(
                company_name="Amazon",
                job_title="SDE II",
                location="Seattle, WA",
                stage=ApplicationStage.OA_SCHEDULED.value,
                match_score=88.0,
            ),
        )

        # 2. List applications with filter
        tech_apps = await ApplicationService.list_applications(
            db=db,
            user_id=user.id,
            stage=ApplicationStage.TECHNICAL_ROUND.value,
        )
        assert len(tech_apps) == 1
        assert tech_apps[0].company_name == "Google"

        # 3. Update stage to OFFER_EXTENDED
        updated_app = await ApplicationService.update_application(
            db=db,
            user_id=user.id,
            application_id=app1.id,
            request=ApplicationUpdateRequest(
                stage=ApplicationStage.OFFER_EXTENDED.value,
                notes="Cleared hiring committee and offer packet approved!",
            ),
        )
        assert updated_app.stage == ApplicationStage.OFFER_EXTENDED.value

        # 4. Check Pipeline Stats
        stats = await ApplicationService.get_application_stats(db=db, user_id=user.id)
        assert stats.total_applications == 2
        assert stats.offers_count == 1
        assert stats.oa_scheduled_count == 1

        # 5. Delete application
        deleted = await ApplicationService.delete_application(db=db, user_id=user.id, application_id=app2.id)
        assert deleted is True
        remaining = await ApplicationService.list_applications(db=db, user_id=user.id)
        assert len(remaining) == 1
