from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from features.feature_engineering import (
    DIFFICULTIES,
    RECENCY_COLUMNS,
    acceptance_profile,
    company_groups,
    difficulty_profile,
    frequency_profile,
    global_topics,
    recent_topic_trends,
    recency_profile,
    stat_summary,
    to_float,
    topic_profile,
    topics,
)


DIFFICULTY_SCORE = {"Easy": 1.0, "Medium": 2.0, "Hard": 3.0}


def cluster_profile(
    rows: list[dict[str, str]],
    question_to_cluster: dict[str, int],
) -> dict[str, dict[str, object]]:
    total = len(rows)
    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[question_to_cluster[row["question_key"]]].append(row)

    profile = {}
    for cluster_id, cluster_rows in sorted(grouped.items()):
        frequencies = [value for value in (to_float(row["frequency_percent"]) for row in cluster_rows) if value is not None]
        difficulty_scores = [
            DIFFICULTY_SCORE[row["difficulty"]]
            for row in cluster_rows
            if row["difficulty"] in DIFFICULTY_SCORE
        ]
        topic_counts = Counter(topic for row in cluster_rows for topic in topics(row))
        difficulty_counts = Counter(row["difficulty"] for row in cluster_rows)
        profile[str(cluster_id)] = {
            "count": len(cluster_rows),
            "percentage": round(len(cluster_rows) / total, 6) if total else 0,
            "avg_difficulty_score": round(mean(difficulty_scores), 4) if difficulty_scores else None,
            "difficulty_distribution": dict(difficulty_counts),
            "avg_frequency": round(mean(frequencies), 4) if frequencies else None,
            "dominant_existing_topics": [
                {"topic": topic, "count": count}
                for topic, count in topic_counts.most_common(10)
            ],
        }
    return profile


def difficulty_counts_and_percentages(rows: list[dict[str, str]]) -> dict[str, dict[str, float | int]]:
    total = len(rows)
    counts = Counter(row["difficulty"] for row in rows)
    return {
        difficulty: {
            "count": counts.get(difficulty, 0),
            "percentage": round(counts.get(difficulty, 0) / total, 6) if total else 0,
        }
        for difficulty in DIFFICULTIES
    }


def recency_counts_and_percentages(rows: list[dict[str, str]]) -> dict[str, dict[str, float | int]]:
    return recency_profile(rows)


def top_question_count(rows: list[dict[str, str]]) -> int:
    return len({row["question_key"] for row in rows})


def make_feature_config(rows: list[dict[str, str]], question_to_cluster: dict[str, int]) -> dict[str, object]:
    topic_counts = Counter(topic for row in rows for topic in topics(row))
    top_topics = [topic for topic, _count in topic_counts.most_common(75)]
    clusters = sorted({question_to_cluster[row["question_key"]] for row in rows})
    return {
        "top_topics": top_topics,
        "clusters": clusters,
        "recency_trend_weights": {
            "has_thirty_days": 1.0,
            "has_three_months": 0.7,
            "has_six_months": 0.4,
            "has_more_than_six_months": 0.1,
        },
        "difficulty_score_mapping_for_cluster_summary_only": DIFFICULTY_SCORE,
    }


def company_feature_vector(
    rows: list[dict[str, str]],
    question_to_cluster: dict[str, int],
    config: dict[str, object],
) -> tuple[list[float], list[str]]:
    total = len(rows) or 1
    labels: list[str] = []
    vector: list[float] = []

    row_topics = [topics(row) for row in rows]
    for topic in config["top_topics"]:
        labels.append(f"topic_share__{topic}")
        vector.append(sum(1 for values in row_topics if topic in values) / total)

    difficulty_counts = Counter(row["difficulty"] for row in rows)
    for difficulty in DIFFICULTIES:
        labels.append(f"difficulty_share__{difficulty}")
        vector.append(difficulty_counts.get(difficulty, 0) / total)

    frequency_values = [value for value in (to_float(row["frequency_percent"]) for row in rows) if value is not None]
    acceptance_values = [value for value in (to_float(row["acceptance_rate_percent"]) for row in rows) if value is not None]
    frequency_stats = stat_summary(frequency_values)
    acceptance_stats = stat_summary(acceptance_values)
    for key in ["mean", "median"]:
        labels.append(f"frequency_{key}")
        vector.append(float(frequency_stats[key] or 0))
    labels.append("acceptance_mean")
    vector.append(float(acceptance_stats["mean"] or 0))

    for label, column in RECENCY_COLUMNS.items():
        labels.append(f"recency_share__{label}")
        vector.append(sum(1 for row in rows if row.get(column) == "1") / total)

    cluster_counts = Counter(question_to_cluster[row["question_key"]] for row in rows)
    for cluster_id in config["clusters"]:
        labels.append(f"cluster_share__{cluster_id}")
        vector.append(cluster_counts.get(cluster_id, 0) / total)

    trends = recent_topic_trends(rows, config["recency_trend_weights"])
    for topic in config["top_topics"]:
        labels.append(f"recent_topic_score__{topic}")
        vector.append(float(trends.get(topic, {}).get("normalized_score", 0)))

    return vector, labels


def build_profiles(
    rows: list[dict[str, str]],
    question_to_cluster: dict[str, int],
    outputs_dir: Path,
) -> tuple[dict[str, dict[str, object]], list[str], list[list[float]], dict[str, object]]:
    grouped = company_groups(rows)
    config = make_feature_config(rows, question_to_cluster)
    profiles: dict[str, dict[str, object]] = {}
    vector_labels: list[str] = []
    vectors_by_company: dict[str, list[float]] = {}

    for company_key, company_rows in sorted(grouped.items()):
        company_name = company_rows[0]["company"]
        topic_data = topic_profile(company_rows)
        difficulty_distribution, topic_difficulty = difficulty_profile(company_rows)
        trends = recent_topic_trends(company_rows, config["recency_trend_weights"])
        clusters = cluster_profile(company_rows, question_to_cluster)
        vector, labels = company_feature_vector(company_rows, question_to_cluster, config)
        vector_labels = labels
        vectors_by_company[company_key] = vector

        profiles[company_key] = {
            "company": company_name,
            "company_key": company_key,
            "data_summary": {
                "total_questions": len(company_rows),
                "unique_questions": top_question_count(company_rows),
            },
            "topic_profile": topic_data,
            "difficulty_profile": difficulty_counts_and_percentages(company_rows),
            "difficulty_distribution": difficulty_distribution,
            "difficulty_distribution_by_topic": topic_difficulty,
            "frequency_profile": frequency_profile(company_rows),
            "acceptance_profile": acceptance_profile(company_rows),
            "recency_profile": recency_counts_and_percentages(company_rows),
            "recent_topic_trends": trends,
            "cluster_profile": clusters,
            "company_feature_vector": vector,
            "feature_vector_labels": labels,
        }

    company_keys = sorted(profiles)
    vectors = [vectors_by_company[company_key] for company_key in company_keys]
    write_profiles(outputs_dir, profiles, company_keys, vector_labels)
    write_analysis_report(outputs_dir, profiles, company_keys)
    return profiles, company_keys, vectors, config


def write_profiles(
    outputs_dir: Path,
    profiles: dict[str, dict[str, object]],
    company_keys: list[str],
    vector_labels: list[str],
) -> None:
    (outputs_dir / "company_oa_profiles.json").write_text(
        json.dumps(
            {
                "profile_generation_method": {
                    "uses_llm": False,
                    "uses_manual_topic_rules": False,
                    "raw_question_data_kept_separate": True,
                    "feature_vector_labels": vector_labels,
                },
                "companies": profiles,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    flattened_rows = []
    for company_key in company_keys:
        profile = profiles[company_key]
        row = {
            "company": profile["company"],
            "company_key": company_key,
            "total_questions": profile["data_summary"]["total_questions"],
            "unique_questions": profile["data_summary"]["unique_questions"],
            "frequency_mean": profile["frequency_profile"]["mean"],
            "frequency_median": profile["frequency_profile"]["median"],
            "frequency_min": profile["frequency_profile"]["min"],
            "frequency_max": profile["frequency_profile"]["max"],
            "frequency_std": profile["frequency_profile"]["std"],
            "acceptance_mean": profile["acceptance_profile"]["mean"],
            "acceptance_median": profile["acceptance_profile"]["median"],
            "acceptance_std": profile["acceptance_profile"]["std"],
            "recency_last_30_days": profile["recency_profile"]["last_30_days"]["count"],
            "recency_last_3_months": profile["recency_profile"]["last_3_months"]["count"],
            "recency_last_6_months": profile["recency_profile"]["last_6_months"]["count"],
            "recency_older": profile["recency_profile"]["older"]["count"],
        }
        for difficulty in DIFFICULTIES:
            row[f"{difficulty.lower()}_count"] = profile["difficulty_profile"][difficulty]["count"]
            row[f"{difficulty.lower()}_percentage"] = profile["difficulty_profile"][difficulty]["percentage"]
        flattened_rows.append(row)

    columns = list(flattened_rows[0].keys()) if flattened_rows else []
    with (outputs_dir / "company_oa_profiles.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(flattened_rows)


def write_analysis_report(
    outputs_dir: Path,
    profiles: dict[str, dict[str, object]],
    company_keys: list[str],
) -> None:
    rows = []
    for company_key in company_keys:
        profile = profiles[company_key]
        topic_profile_data = profile["topic_profile"]
        top_topics = sorted(
            topic_profile_data.items(),
            key=lambda item: item[1]["count"],
            reverse=True,
        )[:10]
        rows.append(
            {
                "company": profile["company"],
                "company_key": company_key,
                "total_questions": profile["data_summary"]["total_questions"],
                "unique_questions": profile["data_summary"]["unique_questions"],
                "top_topics": "; ".join(f"{topic}:{data['count']}" for topic, data in top_topics),
                "frequency_mean": profile["frequency_profile"]["mean"],
                "acceptance_mean": profile["acceptance_profile"]["mean"],
                "last_30_days_count": profile["recency_profile"]["last_30_days"]["count"],
                "largest_cluster": max(
                    profile["cluster_profile"].items(),
                    key=lambda item: item[1]["count"],
                )[0]
                if profile["cluster_profile"]
                else "",
            }
        )

    columns = list(rows[0].keys()) if rows else []
    with (outputs_dir / "analysis_report.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
