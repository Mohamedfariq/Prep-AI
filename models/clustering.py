from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def unique_questions(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row["question_key"]
        if key not in seen:
            seen[key] = {
                "question_key": row["question_key"],
                "question_id": row["question_id"],
                "title": row["title"],
                "difficulty": row["difficulty"],
                "frequency_percent": row["frequency_percent"],
                "topics": row["topics"],
            }
    return list(seen.values())


def build_tfidf(documents: list[str], max_features: int = 1000) -> tuple[np.ndarray, list[str]]:
    tokenized = [tokenize(document) for document in documents]
    doc_count = len(tokenized)
    df = Counter()
    tf_rows = []
    for tokens in tokenized:
        counts = Counter(tokens)
        tf_rows.append(counts)
        df.update(counts.keys())

    vocab = [
        token
        for token, _count in sorted(
            df.items(),
            key=lambda item: (item[1], item[0]),
            reverse=True,
        )[:max_features]
    ]
    index = {token: idx for idx, token in enumerate(vocab)}
    matrix = np.zeros((doc_count, len(vocab)), dtype=np.float32)

    for row_index, counts in enumerate(tf_rows):
        total = sum(counts.values()) or 1
        for token, count in counts.items():
            column = index.get(token)
            if column is None:
                continue
            tf = count / total
            idf = math.log((1 + doc_count) / (1 + df[token])) + 1
            matrix[row_index, column] = tf * idf

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    matrix = matrix / norms
    return matrix, vocab


def kmeans(matrix: np.ndarray, k: int, seed: int = 42, max_iter: int = 80) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed + k)
    n_rows = matrix.shape[0]
    initial = rng.choice(n_rows, size=k, replace=False)
    centroids = matrix[initial].copy()
    labels = np.zeros(n_rows, dtype=np.int32)

    for _ in range(max_iter):
        distances = np.linalg.norm(matrix[:, None, :] - centroids[None, :, :], axis=2)
        new_labels = np.argmin(distances, axis=1)
        if np.array_equal(labels, new_labels):
            break
        labels = new_labels
        for cluster_id in range(k):
            members = matrix[labels == cluster_id]
            if len(members):
                centroids[cluster_id] = members.mean(axis=0)
            else:
                centroids[cluster_id] = matrix[rng.integers(0, n_rows)]

    return labels, centroids


def davies_bouldin(matrix: np.ndarray, labels: np.ndarray, centroids: np.ndarray) -> float:
    k = len(centroids)
    scatter = np.zeros(k, dtype=np.float64)
    for cluster_id in range(k):
        members = matrix[labels == cluster_id]
        if len(members):
            scatter[cluster_id] = np.mean(np.linalg.norm(members - centroids[cluster_id], axis=1))

    centroid_distances = np.linalg.norm(centroids[:, None, :] - centroids[None, :, :], axis=2)
    centroid_distances[centroid_distances == 0] = np.inf
    scores = []
    for i in range(k):
        ratios = (scatter[i] + scatter) / centroid_distances[i]
        ratios[i] = -np.inf
        scores.append(np.max(ratios))
    return float(np.mean(scores))


def sample_silhouette(matrix: np.ndarray, labels: np.ndarray, sample_size: int = 1000, seed: int = 42) -> float | None:
    unique_labels = np.unique(labels)
    if len(unique_labels) < 2:
        return None
    rng = np.random.default_rng(seed)
    sample_indices = rng.choice(len(matrix), size=min(sample_size, len(matrix)), replace=False)
    sample_matrix = matrix[sample_indices]
    sample_labels = labels[sample_indices]
    cosine = np.clip(sample_matrix @ sample_matrix.T, -1.0, 1.0)
    distances = np.sqrt(np.maximum(0.0, 2.0 - 2.0 * cosine))
    scores = []
    for i, label in enumerate(sample_labels):
        same = sample_labels == label
        other_labels = [other for other in np.unique(sample_labels) if other != label]
        if np.sum(same) <= 1 or not other_labels:
            continue
        a = float(np.mean(distances[i, same][distances[i, same] > 0]))
        b = min(float(np.mean(distances[i, sample_labels == other])) for other in other_labels)
        scores.append((b - a) / max(a, b) if max(a, b) else 0)
    return round(float(np.mean(scores)), 6) if scores else None


def choose_k(matrix: np.ndarray, candidate_ks: list[int]) -> tuple[int, np.ndarray, np.ndarray, list[dict[str, float | int | None]]]:
    results = []
    best = None
    for k in candidate_ks:
        labels, centroids = kmeans(matrix, k)
        dbi = davies_bouldin(matrix, labels, centroids)
        silhouette = sample_silhouette(matrix, labels)
        result = {"k": k, "davies_bouldin": round(dbi, 6), "sample_silhouette": silhouette}
        results.append(result)
        if best is None or dbi < best[0]:
            best = (dbi, k, labels, centroids)
    assert best is not None
    return best[1], best[2], best[3], results


def cluster_summaries(
    rows: list[dict[str, str]],
    question_to_cluster: dict[str, int],
) -> dict[str, dict[str, object]]:
    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[question_to_cluster[row["question_key"]]].append(row)

    summaries = {}
    for cluster_id, cluster_rows in sorted(grouped.items()):
        difficulties = Counter(row["difficulty"] for row in cluster_rows)
        topics = Counter(
            topic.strip()
            for row in cluster_rows
            for topic in row.get("topics", "").split(",")
            if topic.strip()
        )
        frequencies = []
        for row in cluster_rows:
            try:
                frequencies.append(float(row["frequency_percent"]))
            except ValueError:
                pass
        summaries[str(cluster_id)] = {
            "question_count": len({row["question_key"] for row in cluster_rows}),
            "company_question_rows": len(cluster_rows),
            "difficulty_distribution": dict(difficulties),
            "avg_frequency": round(float(np.mean(frequencies)), 4) if frequencies else None,
            "dominant_existing_topics": [
                {"topic": topic, "count": count}
                for topic, count in topics.most_common(10)
            ],
            "sample_titles": [row["title"] for row in cluster_rows[:8]],
        }
    return summaries


def run(rows: list[dict[str, str]], outputs_dir: Path) -> tuple[dict[str, int], dict[str, object]]:
    questions = unique_questions(rows)
    titles = [question["title"] for question in questions]
    matrix, vocab = build_tfidf(titles)
    max_k = min(14, max(4, int(math.sqrt(len(questions)) // 2)))
    candidate_ks = list(range(4, max_k + 1))
    best_k, labels, _centroids, evaluation = choose_k(matrix, candidate_ks)

    question_to_cluster = {
        question["question_key"]: int(labels[index])
        for index, question in enumerate(questions)
    }

    cluster_rows = [
        {
            "question_id": row["question_id"],
            "company": row["company"],
            "title": row["title"],
            "question_key": row["question_key"],
            "cluster_id": question_to_cluster[row["question_key"]],
        }
        for row in rows
    ]

    with (outputs_dir / "question_clusters.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["question_id", "company", "title", "question_key", "cluster_id"],
        )
        writer.writeheader()
        writer.writerows(cluster_rows)

    metadata = {
        "method": "TF-IDF on question titles followed by K-Means clustering",
        "manual_cluster_names_used": False,
        "unique_questions_clustered": len(questions),
        "tfidf_vocabulary_size": len(vocab),
        "candidate_k_values": candidate_ks,
        "selected_k": best_k,
        "selection_metric": "minimum Davies-Bouldin Index",
        "evaluation": evaluation,
        "cluster_summaries": cluster_summaries(rows, question_to_cluster),
    }
    (outputs_dir / "clustering_report.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return question_to_cluster, metadata
