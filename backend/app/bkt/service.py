from datetime import datetime, timezone


DEFAULT_BKT = {
    "p_learn": 0.12,
    "p_guess": 0.2,
    "p_slip": 0.1,
}


def update_mastery(prior: float, correct: bool, params: dict[str, float] | None = None) -> float:
    params = params or DEFAULT_BKT
    p_learn = params["p_learn"]
    p_guess = params["p_guess"]
    p_slip = params["p_slip"]

    if correct:
        posterior = (prior * (1 - p_slip)) / ((prior * (1 - p_slip)) + ((1 - prior) * p_guess))
    else:
        posterior = (prior * p_slip) / ((prior * p_slip) + ((1 - prior) * (1 - p_guess)))
    updated = posterior + (1 - posterior) * p_learn
    return round(max(0.01, min(0.99, updated)), 4)


async def apply_attempt_update(db, user_id: str, topic: str, correct: bool) -> dict:
    existing = await db.skill_mastery.find_one({"user_id": user_id, "topic": topic})
    prior = float(existing.get("mastery_probability", 0.35)) if existing else 0.35
    updated_probability = update_mastery(prior, correct)
    now = datetime.now(timezone.utc)
    update = {
        "$set": {
            "mastery_probability": updated_probability,
            "updated_at": now,
        },
        "$inc": {
            "attempts": 1,
            "correct": 1 if correct else 0,
            "incorrect": 0 if correct else 1,
        },
        "$setOnInsert": {
            "user_id": user_id,
            "topic": topic,
            "created_at": now,
        },
    }
    await db.skill_mastery.update_one({"user_id": user_id, "topic": topic}, update, upsert=True)
    return await db.skill_mastery.find_one({"user_id": user_id, "topic": topic})
