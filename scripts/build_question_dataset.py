from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data"

SOURCES = {
    "snehasishroy-leetcode-companywise-interview-questions": {
        "source_id": "snehasishroy_leetcode_companywise_interview_questions",
        "source_url": "https://github.com/snehasishroy/leetcode-companywise-interview-questions",
        "snapshot_note": "Repository README states data snapshot as of 22 November 2025.",
    },
    "liquidslr-leetcode-company-wise-problems": {
        "source_id": "liquidslr_leetcode_company_wise_problems",
        "source_url": "https://github.com/liquidslr/leetcode-company-wise-problems",
        "snapshot_note": "Repository README states data updated as of 1 June 2025.",
    },
}

RECENCY_ALIASES = {
    "thirty-days": "thirty_days",
    "1. thirty days": "thirty_days",
    "three-months": "three_months",
    "2. three months": "three_months",
    "six-months": "six_months",
    "3. six months": "six_months",
    "more-than-six-months": "more_than_six_months",
    "4. more than six months": "more_than_six_months",
    "all": "all",
    "5. all": "all",
}

RECENCY_ORDER = [
    "thirty_days",
    "three_months",
    "six_months",
    "more_than_six_months",
    "all",
]

OBSERVATION_COLUMNS = [
    "source_id",
    "source_url",
    "source_file",
    "company",
    "company_key",
    "recency_bucket",
    "question_id",
    "title",
    "question_key",
    "leetcode_url",
    "difficulty",
    "acceptance_rate_raw",
    "acceptance_rate_percent",
    "frequency_raw",
    "frequency_percent",
    "topics",
]

DATASET_COLUMNS = [
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


def normalize_key(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def display_company_from_path(company_dir: str) -> str:
    if " " in company_dir or company_dir.upper() == company_dir:
        return company_dir.strip()
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", company_dir.strip()))


def recency_from_filename(path: Path) -> str:
    stem = path.stem.strip().lower()
    return RECENCY_ALIASES.get(stem, normalize_key(stem))


def normalize_difficulty(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    return value.lower().capitalize()


def parse_percent(value: str, *, source_id: str, column: str) -> float | None:
    raw = (value or "").strip()
    if not raw:
        return None

    has_percent = raw.endswith("%")
    cleaned = raw.rstrip("%").replace(",", "")
    try:
        number = float(cleaned)
    except ValueError:
        return None

    if column == "acceptance_rate" and source_id.startswith("liquidslr") and not has_percent:
        # This source stores LeetCode acceptance values as tiny decimals
        # (for example, Two Sum appears around 0.0058 for about 58%).
        return round(number * 10000, 4)

    return round(number, 4)


def question_key_from_url_or_title(url: str, title: str) -> str:
    url = (url or "").strip().rstrip("/")
    match = re.search(r"leetcode\.com/problems/([^/?#]+)", url)
    if match:
        return match.group(1).strip().lower()
    return normalize_key(title)


def split_topics(value: str) -> list[str]:
    topics = []
    seen = set()
    for topic in (value or "").split(","):
        cleaned = topic.strip()
        key = cleaned.lower()
        if cleaned and key not in seen:
            topics.append(cleaned)
            seen.add(key)
    return topics


def read_csv(path: Path) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return list(csv.DictReader(handle))
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("csv", b"", 0, 1, f"Unable to decode {path}")


def normalize_row(row: dict[str, str], csv_path: Path, repo_root: Path, source: dict[str, str]) -> dict[str, str] | None:
    company_dir = csv_path.parent.name
    company = display_company_from_path(company_dir)
    company_key = normalize_key(company_dir)
    source_id = source["source_id"]

    if source_id.startswith("snehasishroy"):
        title = row.get("Title", "").strip()
        url = row.get("URL", "").strip()
        question_id = row.get("ID", "").strip()
        difficulty = row.get("Difficulty", "")
        acceptance_raw = row.get("Acceptance %", "")
        frequency_raw = row.get("Frequency %", "")
        topics = ""
    else:
        title = row.get("Title", "").strip()
        url = row.get("Link", "").strip()
        question_id = ""
        difficulty = row.get("Difficulty", "")
        acceptance_raw = row.get("Acceptance Rate", "")
        frequency_raw = row.get("Frequency", "")
        topics = row.get("Topics", "")

    if not title:
        return None

    question_key = question_key_from_url_or_title(url, title)
    relative_file = csv_path.relative_to(ROOT).as_posix()
    acceptance_percent = parse_percent(
        acceptance_raw,
        source_id=source_id,
        column="acceptance_rate",
    )
    frequency_percent = parse_percent(
        frequency_raw,
        source_id=source_id,
        column="frequency",
    )

    return {
        "source_id": source_id,
        "source_url": source["source_url"],
        "source_file": relative_file,
        "company": company,
        "company_key": company_key,
        "recency_bucket": recency_from_filename(csv_path),
        "question_id": question_id,
        "title": title,
        "question_key": question_key,
        "leetcode_url": url,
        "difficulty": normalize_difficulty(difficulty),
        "acceptance_rate_raw": acceptance_raw.strip(),
        "acceptance_rate_percent": "" if acceptance_percent is None else f"{acceptance_percent:.4f}".rstrip("0").rstrip("."),
        "frequency_raw": frequency_raw.strip(),
        "frequency_percent": "" if frequency_percent is None else f"{frequency_percent:.4f}".rstrip("0").rstrip("."),
        "topics": ", ".join(split_topics(topics)),
    }


def load_observations() -> list[dict[str, str]]:
    observations: list[dict[str, str]] = []

    for repo_name, source in SOURCES.items():
        repo_root = RAW_DIR / repo_name
        if not repo_root.exists():
            raise FileNotFoundError(f"Missing source repository: {repo_root}")

        for csv_path in sorted(repo_root.rglob("*.csv")):
            if ".git" in csv_path.parts:
                continue
            for row in read_csv(csv_path):
                normalized = normalize_row(row, csv_path, repo_root, source)
                if normalized:
                    observations.append(normalized)

    return observations


def first_non_empty(values: list[str]) -> str:
    for value in values:
        if value:
            return value
    return ""


def most_common_non_empty(values: list[str]) -> str:
    counts = Counter(value for value in values if value)
    if not counts:
        return ""
    return counts.most_common(1)[0][0]


def median_non_empty(values: list[str]) -> str:
    numbers = []
    for value in values:
        if not value:
            continue
        try:
            numbers.append(float(value))
        except ValueError:
            continue
    if not numbers:
        return ""
    value = round(median(numbers), 4)
    return f"{value:.4f}".rstrip("0").rstrip(".")


def max_non_empty(values: list[str]) -> str:
    numbers = []
    for value in values:
        if not value:
            continue
        try:
            numbers.append(float(value))
        except ValueError:
            continue
    if not numbers:
        return ""
    value = round(max(numbers), 4)
    return f"{value:.4f}".rstrip("0").rstrip(".")


def merge_topics(rows: list[dict[str, str]]) -> str:
    merged = []
    seen = set()
    for row in rows:
        for topic in split_topics(row["topics"]):
            key = topic.lower()
            if key not in seen:
                merged.append(topic)
                seen.add(key)
    return ", ".join(merged)


def sort_recencies(recencies: set[str]) -> list[str]:
    order = {name: index for index, name in enumerate(RECENCY_ORDER)}
    return sorted(recencies, key=lambda item: (order.get(item, len(order)), item))


def build_dataset(observations: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in observations:
        grouped[(row["company_key"], row["question_key"])].append(row)

    dataset = []
    for (_company_key, _question_key), rows in grouped.items():
        recencies = set(row["recency_bucket"] for row in rows if row["recency_bucket"])
        sources = sorted(set(row["source_id"] for row in rows if row["source_id"]))
        source_files = sorted(set(row["source_file"] for row in rows if row["source_file"]))

        output = {
            "company": most_common_non_empty([row["company"] for row in rows]),
            "company_key": rows[0]["company_key"],
            "title": most_common_non_empty([row["title"] for row in rows]),
            "question_key": rows[0]["question_key"],
            "leetcode_url": first_non_empty([row["leetcode_url"] for row in rows]),
            "difficulty": most_common_non_empty([row["difficulty"] for row in rows]),
            "topics": merge_topics(rows),
            "question_id": first_non_empty([row["question_id"] for row in rows]),
            "frequency_percent": max_non_empty([row["frequency_percent"] for row in rows]),
            "acceptance_rate_percent": median_non_empty([row["acceptance_rate_percent"] for row in rows]),
            "recency_buckets": ";".join(sort_recencies(recencies)),
            "sources": ";".join(sources),
            "source_file_count": str(len(source_files)),
        }

        for recency in RECENCY_ORDER:
            output[f"has_{recency}"] = "1" if recency in recencies else "0"

        dataset.append(output)

    return sorted(dataset, key=lambda row: (row["company_key"], row["title"].lower(), row["question_key"]))


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_metadata(observations: list[dict[str, str]], dataset: list[dict[str, str]]) -> None:
    company_counts = Counter(row["company_key"] for row in dataset)
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": "Question_Links.txt",
        "sources": SOURCES,
        "observation_rows": len(observations),
        "deduplicated_question_rows": len(dataset),
        "company_count": len(company_counts),
        "top_companies_by_question_count": [
            {"company_key": company, "question_count": count}
            for company, count in company_counts.most_common(20)
        ],
        "outputs": {
            "observations_csv": "data/company_question_observations.csv",
            "deduplicated_csv": "data/company_questions.csv",
        },
    }

    path = OUTPUT_DIR / "dataset_metadata.json"
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main() -> None:
    observations = load_observations()
    dataset = build_dataset(observations)

    write_csv(OUTPUT_DIR / "company_question_observations.csv", observations, OBSERVATION_COLUMNS)
    write_csv(OUTPUT_DIR / "company_questions.csv", dataset, DATASET_COLUMNS)
    write_metadata(observations, dataset)

    print(f"Observation rows: {len(observations)}")
    print(f"Deduplicated question rows: {len(dataset)}")
    print(f"Companies: {len(set(row['company_key'] for row in dataset))}")
    print("Wrote data/company_question_observations.csv")
    print("Wrote data/company_questions.csv")
    print("Wrote data/dataset_metadata.json")


if __name__ == "__main__":
    main()
