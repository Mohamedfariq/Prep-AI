from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


def min_max_scale(matrix: np.ndarray) -> np.ndarray:
    mins = matrix.min(axis=0)
    maxs = matrix.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1
    return (matrix - mins) / ranges


def cosine_similarity(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = matrix / norms
    return normalized @ normalized.T


def write_similarity_matrix(
    outputs_dir: Path,
    company_keys: list[str],
    vectors: list[list[float]],
) -> np.ndarray:
    matrix = np.array(vectors, dtype=np.float64)
    scaled = min_max_scale(matrix)
    similarities = cosine_similarity(scaled)

    with (outputs_dir / "company_similarity.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["company_key", *company_keys])
        for company_key, row in zip(company_keys, similarities):
            writer.writerow([company_key, *[round(float(value), 6) for value in row]])

    return similarities
