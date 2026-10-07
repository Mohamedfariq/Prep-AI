from fastapi import Depends, Header, HTTPException, status
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.utils.security import decode_access_token
from app.utils.serializers import public_user


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication token")
    token = authorization.split(" ", 1)[1]
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    user = await db.users.find_one({"id": user_id})
    if not user and ObjectId.is_valid(user_id):
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def current_user_response(user: dict) -> dict:
    return public_user(user)
