import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def split_topics(value: str) -> list[str]:
    return [topic.strip() for topic in (value or "").split(",") if topic.strip()]


async def import_questions(db, csv_path: Path | None = None) -> dict:
    csv_path = csv_path or ROOT / "data" / "company_questions.csv"
    if not csv_path.exists():
        return {"imported": 0, "reason": f"Missing {csv_path}"}

    companies: dict[str, dict] = {}
    questions: dict[str, dict] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            company_key = row["company_key"]
            companies[company_key] = {
                "company_id": company_key,
                "name": row["company"],
                "logo": row["company"][:2].upper(),
                "description": f"Company-specific OA preparation profile for {row['company']}.",
            }
            question_id = row["question_id"] or row["question_key"]
            existing = questions.setdefault(question_id, {
                "question_id": question_id,
                "question_key": row["question_key"],
                "title": row["title"],
                "leetcode_url": row["leetcode_url"],
                "difficulty": row["difficulty"],
                "topics": split_topics(row["topics"]),
                "frequency_percent": float(row["frequency_percent"] or 0),
                "acceptance_rate_percent": float(row["acceptance_rate_percent"] or 0),
                "recency_buckets": row["recency_buckets"],
                "has_thirty_days": row["has_thirty_days"] == "1",
                "has_three_months": row["has_three_months"] == "1",
                "has_six_months": row["has_six_months"] == "1",
                "has_more_than_six_months": row["has_more_than_six_months"] == "1",
                "has_all": row["has_all"] == "1",
                "companies": [],
                "cluster": None,
            })
            if company_key not in existing["companies"]:
                existing["companies"].append(company_key)

    if companies:
        await db.companies.bulk_write([
            __import__("pymongo").UpdateOne({"company_id": item["company_id"]}, {"$set": item}, upsert=True)
            for item in companies.values()
        ])
    if questions:
        await db.questions.bulk_write([
            __import__("pymongo").UpdateOne({"question_id": item["question_id"]}, {"$set": item}, upsert=True)
            for item in questions.values()
        ])
    return {"companies": len(companies), "questions": len(questions)}


async def import_company_profiles(db, json_path: Path | None = None) -> dict:
    json_path = json_path or ROOT / "outputs" / "company_oa_profiles.json"
    if not json_path.exists():
        return {"imported": 0, "reason": f"Missing {json_path}"}
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    profiles = payload.get("companies", {})
    operations = []
    for company_id, profile in profiles.items():
        document = {
            "company_id": company_id,
            "total_questions": profile.get("data_summary", {}).get("total_questions", 0),
            "unique_questions": profile.get("data_summary", {}).get("unique_questions", 0),
            "topic_profile": profile.get("topic_profile", {}),
            "difficulty_profile": profile.get("difficulty_profile", {}),
            "frequency_profile": profile.get("frequency_profile", {}),
            "acceptance_profile": profile.get("acceptance_profile", {}),
            "recency_profile": profile.get("recency_profile", {}),
            "cluster_profile": profile.get("cluster_profile", {}),
        }
        operations.append(__import__("pymongo").UpdateOne({"company_id": company_id}, {"$set": document}, upsert=True))
    if operations:
        await db.company_oa_profiles.bulk_write(operations)
    return {"company_oa_profiles": len(operations)}
