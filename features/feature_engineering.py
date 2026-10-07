from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, median, stdev


DIFFICULTIES = ["Easy", "Medium", "Hard"]
RECENCY_COLUMNS = {
    "last_30_days": "has_thirty_days",
    "last_3_months": "has_three_months",
    "last_6_months": "has_six_months",
    "older": "has_more_than_six_months",
    "all": "has_all",
}


def to_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def topics(row: dict[str, str]) -> list[str]:
    return [topic.strip() for topic in row.get("topics", "").split(",") if topic.strip()]


def stat_summary(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"mean": None, "median": None, "min": None, "max": None, "std": None}
    return {
        "mean": round(mean(values), 4),
        "median": round(median(values), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "std": round(stdev(values), 4) if len(values) > 1 else 0.0,
    }


def company_groups(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["company_key"]].append(row)
    return dict(grouped)


def global_topics(rows: list[dict[str, str]]) -> list[str]:
    return sorted({topic for row in rows for topic in topics(row)})


def topic_profile(rows: list[dict[str, str]]) -> dict[str, dict[str, float | int | None]]:
    total_questions = len(rows)
    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        for topic in topics(row):
            by_topic[topic].append(row)

    profile = {}
    for topic, topic_rows in sorted(by_topic.items()):
        frequencies = [value for value in (to_float(row["frequency_percent"]) for row in topic_rows) if value is not None]
        acceptances = [
            value for value in (to_float(row["acceptance_rate_percent"]) for row in topic_rows) if value is not None
        ]
        recent_count = sum(1 for row in topic_rows if row.get("has_thirty_days") == "1")
        profile[topic] = {
            "count": len(topic_rows),
            "percentage": round(len(topic_rows) / total_questions, 6) if total_questions else 0,
            "avg_frequency": round(mean(frequencies), 4) if frequencies else None,
            "median_frequency": round(median(frequencies), 4) if frequencies else None,
            "avg_acceptance_rate": round(mean(acceptances), 4) if acceptances else None,
            "recent_question_count": recent_count,
        }
    return profile


def difficulty_profile(rows: list[dict[str, str]]) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    total = len(rows)
    counts = Counter(row["difficulty"] for row in rows)
    distribution = {
        difficulty: round(counts.get(difficulty, 0) / total, 6) if total else 0
        for difficulty in DIFFICULTIES
    }

    topic_difficulty: dict[str, dict[str, float]] = {}
    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        for topic in topics(row):
            by_topic[topic].append(row)

    for topic, topic_rows in by_topic.items():
        topic_total = len(topic_rows)
        topic_counts = Counter(row["difficulty"] for row in topic_rows)
        topic_difficulty[topic] = {
            difficulty: round(topic_counts.get(difficulty, 0) / topic_total, 6)
            for difficulty in DIFFICULTIES
        }
    return distribution, topic_difficulty


def frequency_profile(rows: list[dict[str, str]]) -> dict[str, object]:
    values = [value for value in (to_float(row["frequency_percent"]) for row in rows) if value is not None]
    highest = sorted(
        [
            {
                "title": row["title"],
                "question_key": row["question_key"],
                "frequency_percent": to_float(row["frequency_percent"]),
            }
            for row in rows
            if to_float(row["frequency_percent"]) is not None
        ],
        key=lambda item: item["frequency_percent"],
        reverse=True,
    )[:10]
    by_topic = topic_profile(rows)
    return {
        **stat_summary(values),
        "topic_avg_frequency": {
            topic: data["avg_frequency"] for topic, data in by_topic.items()
        },
        "topic_median_frequency": {
            topic: data["median_frequency"] for topic, data in by_topic.items()
        },
        "highest_frequency_questions": highest,
    }


def acceptance_profile(rows: list[dict[str, str]]) -> dict[str, object]:
    values = [value for value in (to_float(row["acceptance_rate_percent"]) for row in rows) if value is not None]
    by_topic = topic_profile(rows)
    by_difficulty: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        value = to_float(row["acceptance_rate_percent"])
        if value is not None:
            by_difficulty[row["difficulty"]].append(value)

    return {
        **stat_summary(values),
        "topic_avg_acceptance_rate": {
            topic: data["avg_acceptance_rate"] for topic, data in by_topic.items()
        },
        "difficulty_avg_acceptance_rate": {
            difficulty: round(mean(vals), 4) if vals else None
            for difficulty, vals in by_difficulty.items()
        },
    }


def recency_profile(rows: list[dict[str, str]]) -> dict[str, dict[str, float | int]]:
    total = len(rows)
    profile = {}
    for label, column in RECENCY_COLUMNS.items():
        count = sum(1 for row in rows if row.get(column) == "1")
        profile[label] = {
            "count": count,
            "percentage": round(count / total, 6) if total else 0,
        }
    return profile


def recent_topic_trends(
    rows: list[dict[str, str]],
    weights: dict[str, float] | None = None,
) -> dict[str, dict[str, float | int]]:
    weights = weights or {
        "has_thirty_days": 1.0,
        "has_three_months": 0.7,
        "has_six_months": 0.4,
        "has_more_than_six_months": 0.1,
    }
    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        for topic in topics(row):
            by_topic[topic].append(row)

    trends = {}
    for topic, topic_rows in sorted(by_topic.items()):
        score = 0.0
        activity = {}
        for column, weight in weights.items():
            count = sum(1 for row in topic_rows if row.get(column) == "1")
            activity[column] = count
            score += count * weight
        trends[topic] = {
            "weighted_score": round(score, 6),
            "normalized_score": round(score / len(topic_rows), 6) if topic_rows else 0,
            "question_count": len(topic_rows),
            **activity,
        }
    return dict(sorted(trends.items(), key=lambda item: item[1]["weighted_score"], reverse=True))


def build_multi_hot_rows(rows: list[dict[str, str]], topic_names: list[str]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        row_topics = set(topics(row))
        output.append(
            {
                **row,
                **{topic: 1 if topic in row_topics else 0 for topic in topic_names},
            }
        )
    return output
