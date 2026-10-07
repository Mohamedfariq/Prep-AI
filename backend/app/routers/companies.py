from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.routers.dependencies import get_current_user
from app.utils.serializers import serialize


router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("")
async def companies(search: str | None = None, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    query = {"name": {"$regex": search, "$options": "i"}} if search else {}
    rows = await db.companies.find(query).sort("name", 1).limit(200).to_list(length=200)
    profile = await db.candidate_profiles.find_one({"user_id": user["id"]}) or {}
    return serialize({"target_company": profile.get("target_company"), "companies": rows})


@router.get("/{company_id}")
async def company_detail(company_id: str, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    company = await db.companies.find_one({"company_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    profile = await db.company_oa_profiles.find_one({"company_id": company_id})
    candidate = await db.candidate_profiles.find_one({"user_id": user["id"]}) or {}
    return serialize({"company": company, "oa_profile": profile, "candidate_profile": candidate})


@router.get("/{company_id}/profile")
async def company_profile(company_id: str, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    profile = await db.company_oa_profiles.find_one({"company_id": company_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Company OA profile not found")
    return serialize(profile)
