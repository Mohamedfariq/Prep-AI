from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.recommendation.service import generate_recommendations
from app.routers.dependencies import get_current_user
from app.schemas.recommendations import RecommendationAction
from app.utils.serializers import serialize


router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("")
async def recommendations(user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase | None = Depends(get_database)):
    if db is None:
        return []
    try:
        rows = await db.recommendations.find({"user_id": user["id"], "status": {"$in": ["new", "saved"]}}).sort("generated_at", -1).limit(20).to_list(length=20)
        if not rows:
            rows = await generate_recommendations(db, user["id"])
        return serialize(rows)
    except Exception:
        return []


@router.post("/{recommendation_id}/dismiss")
async def dismiss(recommendation_id: str, payload: RecommendationAction | None = None, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    result = await db.recommendations.update_one({"_id": ObjectId(recommendation_id), "user_id": user["id"]}, {"$set": {"status": "dismissed"}})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"status": "dismissed"}


@router.post("/{recommendation_id}/save")
async def save(recommendation_id: str, payload: RecommendationAction | None = None, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    result = await db.recommendations.update_one({"_id": ObjectId(recommendation_id), "user_id": user["id"]}, {"$set": {"status": "saved"}})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"status": "saved"}
