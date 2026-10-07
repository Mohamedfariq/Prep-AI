from datetime import datetime, timezone
from typing import Any


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def primary_topic(question: dict) -> str:
    topics = question.get("topics") or []
    if isinstance(topics, str):
        topics = [topic.strip() for topic in topics.split(",") if topic.strip()]
    return topics[0] if topics else "General"


def company_relevance(question: dict, topic_importance: dict[str, float]) -> float:
    topics = question.get("topics") or []
    if isinstance(topics, str):
        topics = [topic.strip() for topic in topics.split(",") if topic.strip()]
    if not topics:
        return 0.2
    return max(topic_importance.get(topic, 0.15) for topic in topics)


async def generate_recommendations(db, user_id: str, limit: int = 20) -> list[dict]:
    profile = await db.candidate_profiles.find_one({"user_id": user_id}) or {}
    target_company = profile.get("target_company")
    attempts = await db.candidate_attempts.find({"user_id": user_id}).to_list(length=5000)
    attempted_question_ids = {attempt.get("question_id") for attempt in attempts if attempt.get("question_id")}

    mastery_rows = await db.skill_mastery.find({"user_id": user_id}).to_list(length=500)
    mastery = {row["topic"]: safe_float(row.get("mastery_probability"), 0.35) for row in mastery_rows}

    company_profile = {}
    topic_importance = {}
    if target_company:
        company_profile = await db.company_oa_profiles.find_one({"company_id": target_company}) or {}
        topic_profile = company_profile.get("topic_profile", {})
        topic_importance = {
            topic: safe_float(data.get("percentage"), 0.0)
            for topic, data in topic_profile.items()
            if isinstance(data, dict)
        }

    query: dict[str, Any] = {}
    if target_company:
        query["companies"] = target_company
    if attempted_question_ids:
        query["question_id"] = {"$nin": list(attempted_question_ids)}

    questions = await db.questions.find(query).limit(800).to_list(length=800)
    if not questions and target_company:
        questions = await db.questions.find({"question_id": {"$nin": list(attempted_question_ids)}}).limit(800).to_list(length=800)

    ranked = []
    for question in questions:
        topic = primary_topic(question)
        weakness = 1.0 - mastery.get(topic, 0.35)
        relevance = company_relevance(question, topic_importance)
        frequency = safe_float(question.get("frequency_percent")) / 100.0
        recency = 1.0 if question.get("has_thirty_days") else 0.5 if question.get("has_three_months") else 0.25
        difficulty_bonus = {"Easy": 0.08, "Medium": 0.12, "Hard": 0.06}.get(question.get("difficulty"), 0.08)
        score = (0.42 * weakness) + (0.32 * relevance) + (0.16 * frequency) + (0.10 * recency) + difficulty_bonus
        score = round(min(score, 1.0), 4)
        reason = f"High company relevance and low candidate mastery in {topic}"
        ranked.append({
            "user_id": user_id,
            "question_id": question.get("question_id") or question.get("question_key"),
            "question_key": question.get("question_key"),
            "title": question.get("title"),
            "topic": topic,
            "difficulty": question.get("difficulty"),
            "company": target_company or (question.get("companies") or [""])[0],
            "company_relevance": round(relevance, 4),
            "score": score,
            "reason": reason,
            "generated_at": datetime.now(timezone.utc),
            "status": "new",
        })

    ranked.sort(key=lambda item: item["score"], reverse=True)
    selected = ranked[:limit]
    if selected:
        await db.recommendations.insert_many(selected)
    return selected
