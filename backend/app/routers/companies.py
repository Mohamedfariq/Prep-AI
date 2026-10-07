from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.candidate import CandidateProfile
from app.models.company import Company
from app.routers.dependencies import get_current_user

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("")
async def get_companies(
    search: str | None = None,
    letter: str | None = None,
    limit: int = 1000,
    user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Company)
    if search:
        stmt = stmt.where(Company.name.ilike(f"%{search}%"))
    if letter and letter.upper() != "ALL":
        if letter == "#":
            stmt = stmt.where(Company.name.regexp_match(r"^[0-9]"))
        else:
            stmt = stmt.where(Company.name.ilike(f"{letter}%"))
    stmt = stmt.order_by(Company.name.asc()).limit(limit)
    rows = (await session.execute(stmt)).scalars().all()

    prof = (
        await session.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user.id)
        )
    ).scalars().first()
    target_company = prof.target_company if prof else None

    companies_list = [
        {
            "id": c.id,
            "company_id": c.company_id,
            "name": c.name,
            "logo": c.logo or c.name[:2].upper(),
            "description": c.description,
            "tier": c.tier,
            "total_questions": c.total_questions,
            "unique_questions": c.unique_questions,
        }
        for c in rows
    ]
    return {"target_company": target_company, "companies": companies_list}


@router.get("/{company_id}")
async def get_company_detail(
    company_id: str,
    user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Company).where(Company.company_id == company_id)
    c = (await session.execute(stmt)).scalars().first()
    if not c:
        raise HTTPException(status_code=404, detail="Company not found")

    prof = (
        await session.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user.id)
        )
    ).scalars().first()
    candidate_data = {
        "user_id": user.id,
        "target_company": prof.target_company if prof else None,
        "overall_mastery": prof.overall_mastery if prof else 0.0,
    }

    oa_profile = {
        "company_id": c.company_id,
        "total_questions": c.total_questions,
        "unique_questions": c.unique_questions,
        "topic_profile": c.topic_profile or {},
        "difficulty_profile": c.difficulty_profile or {},
        "frequency_profile": c.frequency_profile or {},
        "acceptance_profile": c.acceptance_profile or {},
        "recency_profile": c.recency_profile or {},
        "cluster_profile": c.cluster_profile or {},
    }

    company_data = {
        "id": c.id,
        "company_id": c.company_id,
        "name": c.name,
        "logo": c.logo or c.name[:2].upper(),
        "description": c.description,
        "tier": c.tier,
        "hiring_stages": c.hiring_stages or [],
    }

    return {"company": company_data, "oa_profile": oa_profile, "candidate_profile": candidate_data}


@router.get("/{company_id}/profile")
async def get_company_profile(
    company_id: str,
    user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Company).where(Company.company_id == company_id)
    c = (await session.execute(stmt)).scalars().first()
    if not c:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "company_id": c.company_id,
        "total_questions": c.total_questions,
        "unique_questions": c.unique_questions,
        "topic_profile": c.topic_profile or {},
        "difficulty_profile": c.difficulty_profile or {},
        "frequency_profile": c.frequency_profile or {},
        "acceptance_profile": c.acceptance_profile or {},
        "recency_profile": c.recency_profile or {},
        "cluster_profile": c.cluster_profile or {},
    }
