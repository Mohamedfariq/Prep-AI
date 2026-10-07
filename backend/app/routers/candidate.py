from datetime import datetime, timezone
import logging
from typing import Any
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.candidate import CandidateProfile, CandidateTargetCompany, SkillProfile
from app.models.company import Company
from app.models.diagnostic import DiagnosticQuestion
from app.models.user import User
from app.routers.dependencies import get_current_user
from app.schemas.candidate import (
    CandidateProfileResponse,
    CandidateProfileUpdate,
    DiagnosticQuestionOut,
    DiagnosticResultResponse,
    DiagnosticSubmitRequest,
    ResumeUploadResponse,
    SelfRatingRequest,
    SkillProfileOut,
    TargetCompanyRequest,
)
from app.services.resume_parser import (
    extract_text_from_pdf,
    parse_resume_with_llm,
    strip_pii,
)
from app.services.supabase_storage import (
    delete_resume_file,
    get_resume_signed_url,
    upload_resume_file,
)
from app.services.taxonomy_service import (
    calculate_bkt_prior,
    load_taxonomy,
    sync_user_taxonomy_skills,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/candidate", tags=["candidate"])


@router.get("/profile", response_model=CandidateProfileResponse)
async def get_profile(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # Ensure profile exists
    res = await session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )
    profile = res.scalars().first()
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        session.add(profile)
        await session.flush()

    # Get target companies
    tc_res = await session.execute(
        select(CandidateTargetCompany).where(CandidateTargetCompany.user_id == user.id)
    )
    target_companies = [
        {
            "company_id": tc.company_id,
            "company_name": tc.company_name,
            "is_primary": tc.is_primary,
        }
        for tc in tc_res.scalars().all()
    ]

    signed_url = None
    if profile.resume_storage_path:
        signed_url = get_resume_signed_url(profile.resume_storage_path)

    return CandidateProfileResponse(
        id=profile.id,
        user_id=user.id,
        name=user.name,
        email=user.email,
        branch=user.branch,
        graduation_year=user.graduation_year,
        bio=profile.bio,
        target_company=profile.target_company,
        resume_filename=profile.resume_filename,
        resume_uploaded_at=profile.resume_uploaded_at,
        resume_signed_url=signed_url,
        parsed_skills=profile.parsed_skills or [],
        parsed_projects=profile.parsed_projects or [],
        parsed_education=profile.parsed_education or [],
        overall_mastery=profile.overall_mastery or 0.0,
        accuracy=profile.accuracy or 0.0,
        average_time=profile.average_time or 0.0,
        questions_attempted=profile.questions_attempted or 0,
        questions_solved=profile.questions_solved or 0,
        current_streak=profile.current_streak or 0,
        target_companies=target_companies,
    )


@router.put("/profile")
async def update_profile(
    payload: CandidateProfileUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # Update User table fields if present
    if payload.branch is not None:
        user.branch = payload.branch
    if payload.graduation_year is not None:
        user.graduation_year = payload.graduation_year

    res = await session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )
    profile = res.scalars().first()
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        session.add(profile)

    if payload.bio is not None:
        profile.bio = payload.bio
    if payload.target_company is not None:
        profile.target_company = payload.target_company

    profile.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return {"message": "Profile updated successfully"}


@router.get("/taxonomy")
async def get_taxonomy():
    """Returns the full topic taxonomy (~40 topics) across DSA, CS Fundamentals, and Languages."""
    return {"topics": load_taxonomy()}


@router.post("/target-company")
async def set_target_company(
    payload: TargetCompanyRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    company_name = payload.company_name or payload.company_id.capitalize()

    # If setting as primary, unset other primaries
    if payload.is_primary:
        existing_targets = await session.execute(
            select(CandidateTargetCompany).where(CandidateTargetCompany.user_id == user.id)
        )
        for target in existing_targets.scalars().all():
            target.is_primary = False

    # Check if target already exists
    res = await session.execute(
        select(CandidateTargetCompany).where(
            CandidateTargetCompany.user_id == user.id,
            CandidateTargetCompany.company_id == payload.company_id,
        )
    )
    target = res.scalars().first()
    if target:
        target.is_primary = payload.is_primary
        target.company_name = company_name
    else:
        target = CandidateTargetCompany(
            user_id=user.id,
            company_id=payload.company_id,
            company_name=company_name,
            is_primary=payload.is_primary,
        )
        session.add(target)

    # Also update primary target_company on CandidateProfile
    if payload.is_primary:
        prof_res = await session.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user.id)
        )
        prof = prof_res.scalars().first()
        if prof:
            prof.target_company = payload.company_id

    await session.commit()
    return {"message": f"Target company '{company_name}' updated"}


@router.post("/skills/self-rate")
async def update_self_ratings(
    payload: SelfRatingRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Submits user self-ratings (1.0 to 5.0) for taxonomy topics and updates the BKT prior P(L0).
    """
    await sync_user_taxonomy_skills(session, user.id)
    rating_map = {r.topic_id: r.rating for r in payload.ratings}

    res = await session.execute(
        select(SkillProfile).where(SkillProfile.user_id == user.id)
    )
    skills = res.scalars().all()

    for skill in skills:
        if skill.topic_id in rating_map:
            new_rating = rating_map[skill.topic_id]
            skill.self_rating = new_rating
            skill.mastery_probability = calculate_bkt_prior(
                diagnostic_score=skill.diagnostic_score,
                self_rating=new_rating,
            )

    await session.commit()
    return {"message": "Self-ratings updated successfully"}


@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Uploads candidate resume PDF:
    1. Validates file format and size
    2. Uploads to private Supabase storage bucket
    3. Extracts text via pdfplumber
    4. Sanitizes PII before sending to LLM
    5. Extracts structured JSON via Qwen2.5-3B (or fallback)
    6. Stores parsed data in candidate profile
    7. Returns signed URL with 15-min expiration
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resume files are supported",
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume size must be under 10MB",
        )

    # 1. Upload to Supabase Private Bucket
    storage_path = upload_resume_file(
        user_id=user.id,
        file_bytes=content,
        original_filename=file.filename,
    )

    # 2. Extract text with pdfplumber
    try:
        raw_text = extract_text_from_pdf(content)
    except Exception as e:
        logger.error(f"pdfplumber extraction failed: {e}")
        raw_text = ""

    # 3. Strip PII
    sanitized_text = strip_pii(raw_text)

    # 4. LLM Extraction (Qwen2.5-3B) with JSON schema
    parsed_data = await parse_resume_with_llm(sanitized_text)

    # 5. Save in database
    prof_res = await session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )
    profile = prof_res.scalars().first()
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        session.add(profile)

    # Delete previous file in storage if replacing
    if profile.resume_storage_path and profile.resume_storage_path != storage_path:
        delete_resume_file(profile.resume_storage_path)

    profile.resume_storage_path = storage_path
    profile.resume_filename = file.filename
    profile.resume_uploaded_at = datetime.now(timezone.utc)
    profile.parsed_skills = parsed_data.skills
    profile.parsed_projects = [p.model_dump() for p in parsed_data.projects]
    profile.parsed_education = [e.model_dump() for e in parsed_data.education]

    await session.commit()

    # Generate temporary signed URL
    signed_url = get_resume_signed_url(storage_path)

    return ResumeUploadResponse(
        message="Resume uploaded and parsed successfully",
        filename=file.filename,
        signed_url=signed_url,
        parsed=parsed_data,
    )


@router.delete("/resume")
async def delete_resume(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Deletes the resume from Supabase Storage and clears all resume data from profile
    (satisfies Privacy and Delete endpoint requirements).
    """
    prof_res = await session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )
    profile = prof_res.scalars().first()
    if profile and profile.resume_storage_path:
        delete_resume_file(profile.resume_storage_path)
        profile.resume_storage_path = None
        profile.resume_filename = None
        profile.resume_uploaded_at = None
        profile.parsed_skills = []
        profile.parsed_projects = []
        profile.parsed_education = []
        await session.commit()

    return {"message": "Resume and associated profile data deleted successfully"}


@router.get("/diagnostic/questions", response_model=list[DiagnosticQuestionOut])
async def get_diagnostic_questions(session: AsyncSession = Depends(get_db)):
    """
    Returns the 15 diagnostic questions for initial mastery calibration.
    Correct answers are hidden from the candidate.
    """
    res = await session.execute(select(DiagnosticQuestion).order_by(DiagnosticQuestion.id))
    questions = res.scalars().all()
    return questions


@router.post("/diagnostic/submit", response_model=DiagnosticResultResponse)
async def submit_diagnostic(
    payload: DiagnosticSubmitRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Evaluates the 15 diagnostic answers and updates P(L0) = 0.70*diag + 0.30*(self_rating/5).
    """
    res = await session.execute(select(DiagnosticQuestion))
    all_questions = {q.id: q for q in res.scalars().all()}

    correct_count = 0
    total_questions = len(payload.answers)
    topic_results: dict[str, list[bool]] = {}

    for ans in payload.answers:
        q = all_questions.get(ans.question_id)
        if q:
            is_correct = (ans.selected_index == q.correct_index)
            if is_correct:
                correct_count += 1
            topic_results.setdefault(q.topic_id, []).append(is_correct)

    accuracy_pct = round((correct_count / total_questions * 100), 2) if total_questions > 0 else 0.0

    # Ensure all user skills are initialized
    await sync_user_taxonomy_skills(session, user.id)

    skill_res = await session.execute(
        select(SkillProfile).where(SkillProfile.user_id == user.id)
    )
    skills = skill_res.scalars().all()
    topic_scores: dict[str, float] = {}

    for skill in skills:
        if skill.topic_id in topic_results:
            results = topic_results[skill.topic_id]
            topic_score = sum(1 for r in results if r) / len(results)
            topic_scores[skill.topic_id] = round(topic_score, 2)
            skill.diagnostic_score = round(topic_score, 2)
            skill.mastery_probability = calculate_bkt_prior(
                diagnostic_score=topic_score,
                self_rating=skill.self_rating,
            )

    # Update overall mastery on CandidateProfile
    all_mastery = [s.mastery_probability for s in skills]
    avg_mastery = round(sum(all_mastery) / len(all_mastery), 4) if all_mastery else 0.0

    prof_res = await session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )
    profile = prof_res.scalars().first()
    if profile:
        profile.overall_mastery = avg_mastery
        profile.accuracy = accuracy_pct

    await session.commit()

    return DiagnosticResultResponse(
        total_questions=total_questions,
        correct_count=correct_count,
        accuracy_percentage=accuracy_pct,
        topic_scores=topic_scores,
        updated_mastery_profiles=[SkillProfileOut.from_orm(s) for s in skills],
    )


@router.get("/skill-profile")
async def get_skill_profile(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Returns the user's skill profiles across all taxonomy topics.
    """
    await sync_user_taxonomy_skills(session, user.id)

    res = await session.execute(
        select(SkillProfile).where(SkillProfile.user_id == user.id).order_by(SkillProfile.category, SkillProfile.topic_name)
    )
    skills = res.scalars().all()

    prof_res = await session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )
    profile = prof_res.scalars().first()

    skills_data = [
        {
            "topic_id": s.topic_id,
            "topic": s.topic_name,
            "category": s.category,
            "self_rating": s.self_rating,
            "diagnostic_score": s.diagnostic_score,
            "mastery_probability": s.mastery_probability,
            "attempts": s.attempts,
        }
        for s in skills
    ]

    return {
        "profile": {
            "overall_mastery": profile.overall_mastery if profile else 0.0,
            "accuracy": profile.accuracy if profile else 0.0,
            "target_company": profile.target_company if profile else None,
        },
        "skills": skills_data,
    }


@router.get("/performance")
async def get_performance(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Returns candidate performance summary."""
    prof_res = await session.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )
    profile = prof_res.scalars().first()

    return {
        "summary": {
            "overall_mastery": profile.overall_mastery if profile else 0.0,
            "accuracy": profile.accuracy if profile else 0.0,
            "questions_attempted": profile.questions_attempted if profile else 0,
            "questions_solved": profile.questions_solved if profile else 0,
            "current_streak": profile.current_streak if profile else 0,
        },
        "topic_accuracy": {},
        "difficulty_accuracy": {},
        "recent_attempts": [],
    }
