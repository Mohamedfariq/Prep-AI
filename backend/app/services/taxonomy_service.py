from pathlib import Path
from typing import Any
import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import SkillProfile

_TAXONOMY_CACHE: list[dict[str, Any]] | None = None


def load_taxonomy() -> list[dict[str, Any]]:
    global _TAXONOMY_CACHE
    if _TAXONOMY_CACHE is None:
        yaml_path = Path(__file__).resolve().parent.parent / "config" / "taxonomy.yaml"
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                _TAXONOMY_CACHE = data.get("topics", [])
        else:
            _TAXONOMY_CACHE = []
    return _TAXONOMY_CACHE


async def sync_user_taxonomy_skills(session: AsyncSession, user_id: str) -> list[SkillProfile]:
    """
    Ensures that a user has a SkillProfile entry for all ~40 taxonomy topics.
    Returns the user's complete list of skill profiles.
    """
    topics = load_taxonomy()
    existing_result = await session.execute(
        select(SkillProfile).where(SkillProfile.user_id == user_id)
    )
    existing_skills = {s.topic_id: s for s in existing_result.scalars().all()}

    new_profiles = []
    for topic in topics:
        tid = topic["id"]
        if tid not in existing_skills:
            sp = SkillProfile(
                user_id=user_id,
                topic_id=tid,
                topic_name=topic["name"],
                category=topic.get("category", "DSA"),
                self_rating=2.5,
                diagnostic_score=0.0,
                mastery_probability=0.25,
                attempts=0,
            )
            session.add(sp)
            new_profiles.append(sp)

    if new_profiles:
        await session.flush()

    # Re-query all to return sorted list
    all_res = await session.execute(
        select(SkillProfile).where(SkillProfile.user_id == user_id).order_by(SkillProfile.category, SkillProfile.topic_name)
    )
    return list(all_res.scalars().all())


def calculate_bkt_prior(diagnostic_score: float, self_rating: float) -> float:
    """
    Computes the initial Bayesian Knowledge Tracing prior P(L0)
    as specified in Module 1: blend 70% diagnostic score and 30% self-rating (scaled 1-5 to 0-1).
    """
    normalized_self = max(1.0, min(5.0, self_rating)) / 5.0
    diag = max(0.0, min(1.0, diagnostic_score))
    p0 = (0.70 * diag) + (0.30 * normalized_self)
    return round(p0, 4)
