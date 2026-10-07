from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.routers.dependencies import get_current_user
from app.utils.serializers import serialize


router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("")
async def questions(
    company: str | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100),
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    query = {}
    if company:
        query["companies"] = company
    if topic:
        query["topics"] = topic
    if difficulty:
        query["difficulty"] = difficulty
    if search:
        query["title"] = {"$regex": search, "$options": "i"}
    skip = (page - 1) * limit
    rows = await db.questions.find(query).skip(skip).limit(limit).to_list(length=limit)
    total = await db.questions.count_documents(query)
    attempts = await db.candidate_attempts.find({"user_id": user["id"]}).to_list(length=5000)
    attempted = {attempt["question_id"] for attempt in attempts}
    for row in rows:
        row["status"] = "attempted" if row.get("question_id") in attempted else "new"
    return serialize({"items": rows, "page": page, "limit": limit, "total": total})


@router.get("/{question_id}")
async def question_detail(question_id: str, user: dict = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    question = await db.questions.find_one({"question_id": question_id}) or await db.questions.find_one({"question_key": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return serialize(question)
