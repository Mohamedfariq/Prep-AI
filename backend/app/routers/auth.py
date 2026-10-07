from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.routers.dependencies import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.utils.security import create_access_token, hash_password, verify_password
from app.utils.serializers import public_user


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    now = datetime.now(timezone.utc)
    user_id = str(ObjectId())
    user = {
        "_id": ObjectId(user_id),
        "id": user_id,
        "name": payload.name,
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "graduation_year": payload.graduation_year,
        "branch": payload.branch,
        "created_at": now,
        "updated_at": now,
    }
    await db.users.insert_one(user)
    await db.candidate_profiles.insert_one({
        "user_id": user_id,
        "target_company": None,
        "overall_mastery": 0,
        "accuracy": 0,
        "average_time": 0,
        "questions_attempted": 0,
        "questions_solved": 0,
        "current_streak": 0,
        "created_at": now,
        "updated_at": now,
    })
    token = create_access_token(user_id)
    return {"access_token": token, "token_type": "bearer", "user": public_user(user)}


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    minutes = 60 * 24 * 30 if payload.remember else None
    token = create_access_token(user["id"], expires_minutes=minutes)
    return {"access_token": token, "token_type": "bearer", "user": public_user(user)}


@router.post("/logout")
async def logout():
    return {"message": "Logged out"}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return public_user(user)
