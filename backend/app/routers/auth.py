from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.candidate import CandidateProfile
from app.models.user import User
from app.routers.dependencies import current_user_response, get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.taxonomy_service import sync_user_taxonomy_skills
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db)):
    # Check existing user by email
    existing_result = await session.execute(select(User).where(User.email == payload.email.lower()))
    if existing_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        graduation_year=payload.graduation_year,
        branch=payload.branch,
    )
    session.add(user)
    await session.flush()

    # Create associated CandidateProfile
    candidate_profile = CandidateProfile(
        user_id=user.id,
        bio="",
        target_company=None,
    )
    session.add(candidate_profile)
    await session.flush()

    # Seed initial SkillProfile for taxonomy topics
    await sync_user_taxonomy_skills(session, user.id)

    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": current_user_response(user),
    }


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalars().first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    minutes = 60 * 24 * 30 if payload.remember else None
    token = create_access_token(user.id, expires_minutes=minutes)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": current_user_response(user),
    }


@router.post("/logout")
async def logout():
    return {"message": "Logged out"}


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return current_user_response(user)
