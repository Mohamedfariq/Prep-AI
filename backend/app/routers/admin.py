from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.services.seed_data import import_company_profiles, import_questions


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/seed")
async def seed(db: AsyncIOMotorDatabase = Depends(get_database)):
    questions = await import_questions(db)
    profiles = await import_company_profiles(db)
    return {"questions": questions, "profiles": profiles}
