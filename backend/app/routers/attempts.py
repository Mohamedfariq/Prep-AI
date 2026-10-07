from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.bkt.service import apply_attempt_update
from app.database.mongodb import get_database
from app.routers.dependencies import get_current_user
from app.schemas.attempts import AttemptCreate
from app.utils.serializers import serialize


router = APIRouter(prefix="/api/attempts", tags=["attempts"])


@router.post("")
async def create_attempt(payload: AttemptCreate, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    now = datetime.now(timezone.utc)
    attempt = {**payload.model_dump(), "user_id": user["id"], "timestamp": now}
    await db.candidate_attempts.insert_one(attempt)
    skill = await apply_attempt_update(db, user["id"], payload.topic, payload.correct)

    attempts = await db.candidate_attempts.find({"user_id": user["id"]}).to_list(length=10000)
    solved = sum(1 for item in attempts if item.get("correct"))
    total_time = sum(float(item.get("time_taken", 0)) for item in attempts)
    await db.candidate_profiles.update_one(
        {"user_id": user["id"]},
        {"$set": {
            "questions_attempted": len(attempts),
            "questions_solved": solved,
            "accuracy": round(solved / len(attempts) * 100, 2) if attempts else 0,
            "average_time": round(total_time / len(attempts), 2) if attempts else 0,
            "updated_at": now,
        }},
        upsert=True,
    )
    return serialize({"attempt": attempt, "updated_skill": skill})


@router.get("")
async def get_attempts(user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    rows = await db.candidate_attempts.find({"user_id": user["id"]}).sort("timestamp", -1).to_list(length=500)
    return serialize(rows)


@router.get("/history")
async def history(user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    rows = await db.candidate_attempts.find({"user_id": user["id"]}).sort("timestamp", -1).to_list(length=500)
    return serialize({"items": rows})
