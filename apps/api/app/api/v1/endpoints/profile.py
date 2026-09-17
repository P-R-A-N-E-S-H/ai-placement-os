from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.profile import (
    ProfileCompletionBreakdown,
    UserProfileResponse,
    UserProfileUpdate,
)
from app.schemas.skill import (
    SkillEvidenceCreate,
    SkillEvidenceResponse,
    UserSkillCreate,
    UserSkillResponse,
)
from app.services.profile_service import ProfileService
from app.services.skill_service import SkillService

router = APIRouter(prefix="/profile", tags=["Career Digital Twin & Profile"])


@router.get(
    "",
    response_model=UserProfileResponse,
    summary="Get Career Profile",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Retrieve the candidate's Career Digital Twin profile."""
    profile = await ProfileService.get_or_create_profile(db, current_user.id)
    return UserProfileResponse.model_validate(profile)


@router.post(
    "",
    response_model=UserProfileResponse,
    summary="Create or Update Profile",
)
@router.patch(
    "",
    response_model=UserProfileResponse,
    summary="Update Career Profile",
)
async def update_profile(
    payload: UserProfileUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Update profile attributes and recalculate completion score."""
    request_id = getattr(request.state, "request_id", None)
    profile = await ProfileService.update_profile(
        db=db,
        user_id=current_user.id,
        payload=payload,
        request_id=request_id,
    )
    return UserProfileResponse.model_validate(profile)


@router.get(
    "/completion",
    response_model=ProfileCompletionBreakdown,
    summary="Get Profile Completion Breakdown",
)
async def get_profile_completion(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileCompletionBreakdown:
    """Return a detailed 7-factor completion score and missing fields."""
    profile = await ProfileService.get_or_create_profile(db, current_user.id)
    return await ProfileService.calculate_completion(db, profile)


@router.get(
    "/skills",
    response_model=List[UserSkillResponse],
    summary="Get Candidate's Skills",
)
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[UserSkillResponse]:
    """Return all skills and associated evidence for the authenticated user."""
    skills = await SkillService.get_user_skills(db, current_user.id)
    return [UserSkillResponse.model_validate(s) for s in skills]


@router.post(
    "/skills",
    response_model=UserSkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add or Update Candidate Skill",
)
async def add_user_skill(
    payload: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSkillResponse:
    """Associate a canonical skill with proficiency (0.0-1.0) and optional evidence."""
    user_skill = await SkillService.add_or_update_user_skill(db, current_user.id, payload)
    
    # Recalculate profile completion after adding skill
    profile = await ProfileService.get_or_create_profile(db, current_user.id)
    completion = await ProfileService.calculate_completion(db, profile)
    profile.profile_completion = completion.overall_completion
    await db.commit()

    return UserSkillResponse.model_validate(user_skill)


@router.delete(
    "/skills/{skill_id}",
    response_model=MessageResponse,
    summary="Remove Candidate Skill",
)
async def remove_user_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Remove a skill from the candidate's Career Digital Twin."""
    await SkillService.remove_user_skill(db, current_user.id, skill_id)
    return MessageResponse(message="Skill successfully removed from profile.")


@router.post(
    "/skills/evidence",
    response_model=SkillEvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Attach Verifiable Evidence to Skill",
)
async def add_skill_evidence(
    payload: SkillEvidenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillEvidenceResponse:
    """Attach verifiable proof (resume bullet, github repo, project) to a candidate skill."""
    evidence = await SkillService.add_evidence(db, current_user.id, payload)
    return SkillEvidenceResponse.model_validate(evidence)
