from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.routers.dependencies import get_current_user
from app.schemas.candidate import CandidateProfileUpdate, TargetCompanyRequest
from app.utils.serializers import serialize


router = APIRouter(prefix="/api/candidate", tags=["candidate"])


@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    profile = await db.candidate_profiles.find_one({"user_id": user["id"]})
    return serialize(profile or {})


@router.put("/profile")
async def update_profile(payload: CandidateProfileUpdate, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    updates = {key: value for key, value in payload.model_dump().items() if value is not None}
    updates["updated_at"] = datetime.now(timezone.utc)
    if "branch" in updates or "graduation_year" in updates:
        user_updates = {key: updates[key] for key in ["branch", "graduation_year"] if key in updates}
        if user_updates:
            await db.users.update_one({"id": user["id"]}, {"$set": user_updates})
    await db.candidate_profiles.update_one({"user_id": user["id"]}, {"$set": updates}, upsert=True)
    return serialize(await db.candidate_profiles.find_one({"user_id": user["id"]}))


@router.post("/target-company")
async def set_target_company(payload: TargetCompanyRequest, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    await db.candidate_profiles.update_one(
        {"user_id": user["id"]},
        {"$set": {"target_company": payload.company_id, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return serialize(await db.candidate_profiles.find_one({"user_id": user["id"]}))


@router.get("/skill-profile")
async def skill_profile(user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    skills = await db.skill_mastery.find({"user_id": user["id"]}).sort("mastery_probability", -1).to_list(length=500)
    profile = await db.candidate_profiles.find_one({"user_id": user["id"]}) or {}
    return serialize({"profile": profile, "skills": skills})


@router.get("/performance")
async def performance(user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    attempts = await db.candidate_attempts.find({"user_id": user["id"]}).sort("timestamp", -1).to_list(length=200)
    total = len(attempts)
    correct = sum(1 for attempt in attempts if attempt.get("correct"))
    by_topic: dict[str, dict[str, int]] = {}
    by_difficulty: dict[str, dict[str, int]] = {}
    for attempt in attempts:
        topic = attempt.get("topic", "General")
        difficulty = attempt.get("difficulty", "Unknown")
        by_topic.setdefault(topic, {"attempts": 0, "correct": 0})
        by_difficulty.setdefault(difficulty, {"attempts": 0, "correct": 0})
        by_topic[topic]["attempts"] += 1
        by_difficulty[difficulty]["attempts"] += 1
        if attempt.get("correct"):
            by_topic[topic]["correct"] += 1
            by_difficulty[difficulty]["correct"] += 1
    return serialize({
        "summary": {
            "attempts": total,
            "correct": correct,
            "accuracy": round(correct / total * 100, 2) if total else 0,
        },
        "topic_accuracy": by_topic,
        "difficulty_accuracy": by_difficulty,
        "recent_attempts": attempts,
    })
