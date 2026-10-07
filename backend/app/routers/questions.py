from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import cast, func, or_, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.question import Question
from app.routers.dependencies import get_current_user

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("")
async def get_questions(
    company: str | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    search: str | None = None,
    letter: str | None = None,
    sort_by: str = Query(default="title", pattern="^(title|frequency|difficulty)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Question)
    count_stmt = select(func.count(Question.id))

    if search:
        search_filter = or_(
            Question.title.ilike(f"%{search}%"),
            Question.question_key.ilike(f"%{search}%"),
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)

    if letter and letter.upper() != "ALL":
        if letter == "#":
            stmt = stmt.where(Question.title.regexp_match(r"^[0-9]"))
            count_stmt = count_stmt.where(Question.title.regexp_match(r"^[0-9]"))
        else:
            stmt = stmt.where(Question.title.ilike(f"{letter}%"))
            count_stmt = count_stmt.where(Question.title.ilike(f"{letter}%"))

    if difficulty and difficulty.lower() != "all":
        stmt = stmt.where(Question.difficulty.ilike(difficulty))
        count_stmt = count_stmt.where(Question.difficulty.ilike(difficulty))

    if company:
        comp_filter = cast(Question.companies, String).ilike(f"%{company.lower()}%")
        stmt = stmt.where(comp_filter)
        count_stmt = count_stmt.where(comp_filter)

    if topic:
        topic_filter = cast(Question.topics, String).ilike(f"%{topic}%")
        stmt = stmt.where(topic_filter)
        count_stmt = count_stmt.where(topic_filter)

    total = (await session.execute(count_stmt)).scalar() or 0
    skip = (page - 1) * limit

    if sort_by == "frequency":
        stmt = stmt.order_by(Question.frequency_percent.desc(), Question.title.asc())
    elif sort_by == "difficulty":
        stmt = stmt.order_by(Question.difficulty.asc(), Question.title.asc())
    else:  # title / alphabetical
        stmt = stmt.order_by(Question.title.asc())

    stmt = stmt.offset(skip).limit(limit)
    rows = (await session.execute(stmt)).scalars().all()

    items = [
        {
            "id": q.id,
            "question_id": q.question_id,
            "question_key": q.question_key,
            "title": q.title,
            "leetcode_url": q.leetcode_url,
            "difficulty": q.difficulty,
            "topics": q.topics or [],
            "frequency_percent": q.frequency_percent or 0.0,
            "acceptance_rate_percent": q.acceptance_rate_percent or 0.0,
            "companies": q.companies or [],
            "status": "new",
        }
        for q in rows
    ]

    return {"items": items, "page": page, "limit": limit, "total": total}


@router.get("/{question_id}")
async def get_question_detail(
    question_id: str,
    user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(Question).where(
        or_(
            Question.question_id == question_id,
            Question.question_key == question_id,
        )
    )
    q = (await session.execute(stmt)).scalars().first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return {
        "id": q.id,
        "question_id": q.question_id,
        "question_key": q.question_key,
        "title": q.title,
        "leetcode_url": q.leetcode_url,
        "difficulty": q.difficulty,
        "topics": q.topics or [],
        "frequency_percent": q.frequency_percent or 0.0,
        "acceptance_rate_percent": q.acceptance_rate_percent or 0.0,
        "companies": q.companies or [],
    }
