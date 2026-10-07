from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.routers.dependencies import get_current_user
from app.schemas.assessments import AssessmentStartRequest, AssessmentSubmitRequest
from app.utils.serializers import serialize


router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.post("/start")
async def start_assessment(payload: AssessmentStartRequest, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    query = {"companies": payload.company_id} if payload.company_id else {}
    questions = await db.questions.find(query).sort("frequency_percent", -1).limit(payload.question_count).to_list(length=payload.question_count)
    assessment = {
        "user_id": user["id"],
        "company_id": payload.company_id,
        "duration_minutes": payload.duration_minutes,
        "question_ids": [question["question_id"] for question in questions],
        "status": "in_progress",
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.assessments.insert_one(assessment)
    assessment["_id"] = result.inserted_id
    return serialize({"assessment": assessment, "questions": questions})


@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    from bson import ObjectId
    assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id), "user_id": user["id"]})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    questions = await db.questions.find({"question_id": {"$in": assessment.get("question_ids", [])}}).to_list(length=50)
    return serialize({"assessment": assessment, "questions": questions})


@router.post("/{assessment_id}/submit")
async def submit_assessment(assessment_id: str, payload: AssessmentSubmitRequest, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    from bson import ObjectId
    score = sum(1 for answer in payload.answers if answer.get("correct"))
    total = len(payload.answers)
    result = {
        "status": "submitted",
        "score": score,
        "accuracy": round(score / total * 100, 2) if total else 0,
        "submitted_at": datetime.now(timezone.utc),
        "answers": payload.answers,
    }
    await db.assessments.update_one({"_id": ObjectId(assessment_id), "user_id": user["id"]}, {"$set": result})
    return serialize(result)
