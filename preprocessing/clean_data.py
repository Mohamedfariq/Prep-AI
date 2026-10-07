from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = [
    "company",
    "company_key",
    "title",
    "question_key",
    "leetcode_url",
    "difficulty",
    "topics",
    "question_id",
    "frequency_percent",
    "acceptance_rate_percent",
    "recency_buckets",
    "has_thirty_days",
    "has_three_months",
    "has_six_months",
    "has_more_than_six_months",
    "has_all",
    "sources",
    "source_file_count",
]

DIFFICULTY_MAP = {
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
}

RECENCY_COLUMNS = [
    "has_thirty_days",
    "has_three_months",
    "has_six_months",
    "has_more_than_six_months",
    "has_all",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def numeric_or_none(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def normalize_topics(value: str) -> str:
    seen: set[str] = set()
    topics: list[str] = []
    for topic in (value or "").split(","):
        cleaned = " ".join(topic.strip().split())
        if not cleaned:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            topics.append(cleaned)
    return ", ".join(topics)


def topic_list(value: str) -> list[str]:
    return [topic.strip() for topic in (value or "").split(",") if topic.strip()]


def row_signature(row: dict[str, str]) -> tuple[str, ...]:
    return tuple((row.get(column) or "").strip() for column in REQUIRED_COLUMNS)


def validate_dataset(rows: list[dict[str, str]], columns: list[str]) -> dict[str, object]:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    missing_values = {
        column: sum(1 for row in rows if not (row.get(column) or "").strip())
        for column in columns
    }

    duplicate_exact = len(rows) - len({row_signature(row) for row in rows})
    duplicate_keys = {}
    for key in ["question_key", "question_id", "leetcode_url"]:
        values = [row.get(key, "").strip() for row in rows if row.get(key, "").strip()]
        counts = Counter(values)
        duplicate_keys[key] = sum(1 for value in counts.values() if value > 1)

    topic_counts = [len(topic_list(row.get("topics", ""))) for row in rows]
    numeric_checks = {
        "frequency_percent": {
            "numeric": sum(1 for row in rows if numeric_or_none(row.get("frequency_percent", "")) is not None),
            "non_numeric": sum(
                1
                for row in rows
                if row.get("frequency_percent", "").strip()
                and numeric_or_none(row.get("frequency_percent", "")) is None
            ),
        },
        "acceptance_rate_percent": {
            "numeric": sum(
                1 for row in rows if numeric_or_none(row.get("acceptance_rate_percent", "")) is not None
            ),
            "non_numeric": sum(
                1
                for row in rows
                if row.get("acceptance_rate_percent", "").strip()
                and numeric_or_none(row.get("acceptance_rate_percent", "")) is None
            ),
        },
    }

    recency_values = {
        column: dict(Counter(row.get(column, "").strip() for row in rows))
        for column in RECENCY_COLUMNS
    }

    duplicate_company_questions: dict[str, int] = defaultdict(int)
    company_question_counts = Counter((row.get("company_key", ""), row.get("question_key", "")) for row in rows)
    for (company, _question), count in company_question_counts.items():
        if count > 1:
            duplicate_company_questions[company] += 1

    return {
        "shape": {"rows": len(rows), "columns": len(columns)},
        "columns": columns,
        "dtypes": {column: "string_from_csv" for column in columns},
        "missing_required_columns": missing_columns,
        "missing_values": missing_values,
        "exact_duplicate_rows": duplicate_exact,
        "duplicate_questions_by_identifier": duplicate_keys,
        "duplicate_company_question_pairs": dict(duplicate_company_questions),
        "difficulty_unique_values": sorted({row.get("difficulty", "").strip() for row in rows}),
        "topics_structure": {
            "rows_with_empty_topics": sum(1 for count in topic_counts if count == 0),
            "min_topics_per_question": min(topic_counts) if topic_counts else 0,
            "max_topics_per_question": max(topic_counts) if topic_counts else 0,
            "avg_topics_per_question": round(sum(topic_counts) / len(topic_counts), 4) if topic_counts else 0,
            "unique_topics": len({topic.lower() for row in rows for topic in topic_list(row.get("topics", ""))}),
        },
        "numeric_checks": numeric_checks,
        "recency_field_values": recency_values,
    }


def clean_dataset(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, object]]:
    cleaned: list[dict[str, str]] = []
    exact_seen: set[tuple[str, ...]] = set()
    exact_duplicate_count = 0
    duplicate_sources: dict[str, int] = defaultdict(int)

    for row in rows:
        new_row = {column: (row.get(column, "") or "").strip() for column in REQUIRED_COLUMNS}
        new_row["difficulty"] = DIFFICULTY_MAP.get(new_row["difficulty"].lower(), new_row["difficulty"])
        new_row["topics"] = normalize_topics(new_row["topics"])

        for column in RECENCY_COLUMNS:
            new_row[column] = "1" if new_row[column] == "1" else "0"

        signature = row_signature(new_row)
        if signature in exact_seen:
            exact_duplicate_count += 1
            continue
        exact_seen.add(signature)
        cleaned.append(new_row)

    by_company_question = Counter((row["company_key"], row["question_key"]) for row in cleaned)
    for (company_key, _question_key), count in by_company_question.items():
        if count > 1:
            duplicate_sources[company_key] += count

    report = {
        "input_rows": len(rows),
        "output_rows": len(cleaned),
        "removed_exact_duplicate_records": exact_duplicate_count,
        "duplicate_company_question_rows_preserved_for_review": dict(duplicate_sources),
        "note": "Question rows are preserved across companies; only exact duplicate records are removed.",
    }
    return cleaned, report


def run(input_csv: Path, processed_dir: Path, outputs_dir: Path) -> list[dict[str, str]]:
    rows = read_csv(input_csv)
    with input_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        columns = list(csv.DictReader(handle).fieldnames or [])

    quality_report = validate_dataset(rows, columns)
    cleaned, cleaning_report = clean_dataset(rows)

    processed_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    write_csv(processed_dir / "cleaned_questions.csv", cleaned, REQUIRED_COLUMNS)
    write_csv(outputs_dir / "cleaned_questions.csv", cleaned, REQUIRED_COLUMNS)

    (outputs_dir / "data_quality_report.json").write_text(
        json.dumps({"validation": quality_report, "cleaning": cleaning_report}, indent=2),
        encoding="utf-8",
    )

    quality_rows = [
        {"metric": "rows", "value": quality_report["shape"]["rows"]},
        {"metric": "columns", "value": quality_report["shape"]["columns"]},
        {"metric": "exact_duplicate_rows", "value": quality_report["exact_duplicate_rows"]},
        {"metric": "rows_with_empty_topics", "value": quality_report["topics_structure"]["rows_with_empty_topics"]},
        {"metric": "unique_topics", "value": quality_report["topics_structure"]["unique_topics"]},
        {"metric": "cleaned_rows", "value": cleaning_report["output_rows"]},
    ]
    write_csv(outputs_dir / "data_quality_report.csv", quality_rows, ["metric", "value"])

    return cleaned
