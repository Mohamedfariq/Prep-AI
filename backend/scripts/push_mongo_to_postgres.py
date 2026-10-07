import asyncio
import json
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.config.settings import get_settings
from app.database.postgres import AsyncSessionLocal, engine, Base
from app.models.question import Question
from app.models.company import Company


async def push_data():
    settings = get_settings()
    print("--- Fast Bulk Pushing Questions & Companies to PostgreSQL ---")

    # 1. Connect to MongoDB
    mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    mongo_db = mongo_client[settings.database_name]

    print("Fetching questions from MongoDB...")
    mongo_questions = await mongo_db.questions.find({}).to_list(length=10000)
    print(f"Found {len(mongo_questions)} questions in MongoDB.")

    print("Fetching companies from MongoDB...")
    mongo_companies = await mongo_db.companies.find({}).to_list(length=2000)
    mongo_oa_profiles = await mongo_db.company_oa_profiles.find({}).to_list(length=2000)
    print(f"Found {len(mongo_companies)} companies and {len(mongo_oa_profiles)} OA profiles.")

    oa_profiles_by_company = {p["company_id"]: p for p in mongo_oa_profiles if "company_id" in p}

    # 2. Bulk insert companies
    company_dicts = []
    seen_companies = set()
    for c in mongo_companies:
        cid = c.get("company_id")
        if not cid or cid in seen_companies:
            continue
        seen_companies.add(cid)
        oa = oa_profiles_by_company.get(cid, {})
        company_dicts.append({
            "company_id": cid,
            "name": c.get("name") or cid.capitalize(),
            "logo": c.get("logo") or cid[:2].upper(),
            "description": c.get("description") or f"Company-specific OA preparation profile for {c.get('name', cid)}.",
            "tier": c.get("tier") or "Tier-1",
            "hiring_stages": c.get("hiring_stages") or ["Online Assessment", "Technical Interview 1", "Technical Interview 2", "HR/Behavioral"],
            "total_questions": oa.get("total_questions", 0),
            "unique_questions": oa.get("unique_questions", 0),
            "topic_profile": oa.get("topic_profile", {}),
            "difficulty_profile": oa.get("difficulty_profile", {}),
            "frequency_profile": oa.get("frequency_profile", {}),
            "acceptance_profile": oa.get("acceptance_profile", {}),
            "recency_profile": oa.get("recency_profile", {}),
            "cluster_profile": oa.get("cluster_profile", {}),
        })

    print(f"Prepared {len(company_dicts)} unique companies. Inserting in batches...")
    chunk_size = 200
    for i in range(0, len(company_dicts), chunk_size):
        chunk = company_dicts[i:i + chunk_size]
        async with AsyncSessionLocal() as session:
            stmt = pg_insert(Company).values(chunk)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Company.company_id],
                set_={
                    "name": stmt.excluded.name,
                    "description": stmt.excluded.description,
                    "total_questions": stmt.excluded.total_questions,
                    "unique_questions": stmt.excluded.unique_questions,
                    "topic_profile": stmt.excluded.topic_profile,
                    "difficulty_profile": stmt.excluded.difficulty_profile,
                    "frequency_profile": stmt.excluded.frequency_profile,
                    "acceptance_profile": stmt.excluded.acceptance_profile,
                    "recency_profile": stmt.excluded.recency_profile,
                    "cluster_profile": stmt.excluded.cluster_profile,
                }
            )
            await session.execute(stmt)
            await session.commit()
            print(f"Upserted {min(i + chunk_size, len(company_dicts))} / {len(company_dicts)} companies...")

    # 3. Bulk insert questions
    question_dicts = []
    seen_questions = set()
    for q in mongo_questions:
        qid = str(q.get("question_id") or q.get("question_key"))
        if not qid or qid in seen_questions:
            continue
        seen_questions.add(qid)
        question_dicts.append({
            "question_id": qid,
            "question_key": str(q.get("question_key") or qid),
            "title": q.get("title") or "Untitled Problem",
            "leetcode_url": q.get("leetcode_url") or "",
            "difficulty": q.get("difficulty") or "Medium",
            "topics": q.get("topics") or [],
            "frequency_percent": float(q.get("frequency_percent") or 0.0),
            "acceptance_rate_percent": float(q.get("acceptance_rate_percent") or 0.0),
            "companies": q.get("companies") or [],
            "recency_buckets": str(q.get("recency_buckets") or ""),
            "has_thirty_days": bool(q.get("has_thirty_days")),
            "has_three_months": bool(q.get("has_three_months")),
            "has_six_months": bool(q.get("has_six_months")),
            "has_more_than_six_months": bool(q.get("has_more_than_six_months")),
            "has_all": bool(q.get("has_all")),
        })

    print(f"Prepared {len(question_dicts)} unique questions. Inserting in batches...")
    q_chunk_size = 250
    for i in range(0, len(question_dicts), q_chunk_size):
        chunk = question_dicts[i:i + q_chunk_size]
        async with AsyncSessionLocal() as session:
            stmt = pg_insert(Question).values(chunk)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Question.question_id],
                set_={
                    "title": stmt.excluded.title,
                    "leetcode_url": stmt.excluded.leetcode_url,
                    "difficulty": stmt.excluded.difficulty,
                    "topics": stmt.excluded.topics,
                    "frequency_percent": stmt.excluded.frequency_percent,
                    "acceptance_rate_percent": stmt.excluded.acceptance_rate_percent,
                    "companies": stmt.excluded.companies,
                    "recency_buckets": stmt.excluded.recency_buckets,
                    "has_thirty_days": stmt.excluded.has_thirty_days,
                    "has_three_months": stmt.excluded.has_three_months,
                    "has_six_months": stmt.excluded.has_six_months,
                    "has_more_than_six_months": stmt.excluded.has_more_than_six_months,
                    "has_all": stmt.excluded.has_all,
                }
            )
            await session.execute(stmt)
            await session.commit()
            print(f"Upserted {min(i + q_chunk_size, len(question_dicts))} / {len(question_dicts)} questions...")

    # 4. Final Verification
    async with AsyncSessionLocal() as session:
        q_count = (await session.execute(select(func.count(Question.id)))).scalar()
        c_count = (await session.execute(select(func.count(Company.id)))).scalar()
        print(f"\n[DONE] Successfully verified in Supabase PostgreSQL:")
        print(f"   -> {q_count} Questions")
        print(f"   -> {c_count} Companies")


if __name__ == "__main__":
    asyncio.run(push_data())
