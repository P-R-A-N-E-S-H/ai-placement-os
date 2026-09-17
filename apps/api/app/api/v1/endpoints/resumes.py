from typing import List
from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import EntityNotFoundError, ValidationError
from app.models.resume import Resume
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.resume import ResumeDetailResponse, ResumeUploadResponse
from app.services.resume_extraction_service import ResumeExtractionService
from app.services.resume_parser import DocumentParser

router = APIRouter(prefix="/resumes", tags=["Resume Intelligence Agent"])


@router.post(
    "/upload",
    response_model=ResumeDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Analyze Candidate Resume",
)
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeDetailResponse:
    """
    Ingest a PDF, DOCX, or TXT resume, extract structured sections, map canonical skills,
    compute ATS score, and synchronize into the candidate's Career Digital Twin.
    """
    file_bytes = await file.read()
    file_name = file.filename or "resume.pdf"

    # 1. Parse document text
    raw_text, file_type, file_size = DocumentParser.parse_document(file_name, file_bytes)

    # 2. Extract, evaluate ATS, and sync to Career Digital Twin
    resume = await ResumeExtractionService.process_and_sync_resume(
        db=db,
        user_id=current_user.id,
        file_name=file_name,
        raw_text=raw_text,
        file_type=file_type,
        file_size_bytes=file_size,
    )

    return ResumeDetailResponse.model_validate(resume)


@router.get(
    "",
    response_model=List[ResumeDetailResponse],
    summary="List Candidate's Uploaded Resumes",
)
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ResumeDetailResponse]:
    """Retrieve all resumes uploaded by the authenticated user."""
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
    )
    resumes = result.scalars().all()
    return [ResumeDetailResponse.model_validate(r) for r in resumes]


@router.get(
    "/{resume_id}",
    response_model=ResumeDetailResponse,
    summary="Get Resume Details & ATS Breakdown",
)
async def get_resume_by_id(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeDetailResponse:
    """Retrieve full parsed data and ATS scorecard for a specific resume."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise EntityNotFoundError(f"Resume with ID '{resume_id}' not found")
    return ResumeDetailResponse.model_validate(resume)


@router.delete(
    "/{resume_id}",
    response_model=MessageResponse,
    summary="Delete Resume",
)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete an uploaded resume record."""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise EntityNotFoundError(f"Resume with ID '{resume_id}' not found")

    await db.delete(resume)
    await db.commit()
    return MessageResponse(message="Resume successfully deleted.")
