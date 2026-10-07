import json
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import Base, engine, AsyncSessionLocal
from app.models import Company, DiagnosticQuestion
from app.models.user import User
from app.models.candidate import CandidateProfile, SkillProfile, CandidateTargetCompany


INITIAL_COMPANIES = [
    {
        "company_id": "google",
        "name": "Google",
        "tier": "Tier-1",
        "hiring_stages": ["Online Assessment", "Technical Round 1", "Technical Round 2", "Googliness & Behavioral"]
    },
    {
        "company_id": "amazon",
        "name": "Amazon",
        "tier": "Tier-1",
        "hiring_stages": ["Online Assessment (OA)", "Technical Interview 1", "Technical Interview 2", "Bar Raiser"]
    },
    {
        "company_id": "microsoft",
        "name": "Microsoft",
        "tier": "Tier-1",
        "hiring_stages": ["Codility OA", "DSA Round", "System Design & LLD", "AA Interview"]
    },
    {
        "company_id": "uber",
        "name": "Uber",
        "tier": "Tier-1",
        "hiring_stages": ["HackerRank OA", "Algorithms Round", "Concurrency & Architecture", "Engineering Manager"]
    },
    {
        "company_id": "atlassian",
        "name": "Atlassian",
        "tier": "Tier-1",
        "hiring_stages": ["Karat Interview", "Coding & Data Structures", "System Design", "Values Interview"]
    }
]


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed diagnostic questions and companies if not present
    async with AsyncSessionLocal() as session:
        # Check diagnostic questions
        res = await session.execute(select(DiagnosticQuestion).limit(1))
        if not res.scalars().first():
            json_path = Path(__file__).resolve().parent.parent / "config" / "diagnostic_questions.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    questions_data = json.load(f)
                    for q in questions_data:
                        diag = DiagnosticQuestion(
                            id=q["id"],
                            topic_id=q["topic_id"],
                            topic_name=q["topic_name"],
                            question=q["question"],
                            options=q["options"],
                            correct_index=q["correct_index"],
                            explanation=q.get("explanation", ""),
                        )
                        session.add(diag)

        # Check companies
        comp_res = await session.execute(select(Company).limit(1))
        if not comp_res.scalars().first():
            for c in INITIAL_COMPANIES:
                company = Company(
                    company_id=c["company_id"],
                    name=c["name"],
                    tier=c["tier"],
                    hiring_stages=c["hiring_stages"],
                )
                session.add(company)

        await session.commit()
