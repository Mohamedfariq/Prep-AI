from __future__ import annotations

import html
from pathlib import Path

import numpy as np


PALETTE = ["#2f6f73", "#c27d38", "#6c5b7b", "#3d7ea6", "#8a6f3d", "#9d4edd", "#247ba0"]


def svg_bar_chart(title: str, labels: list[str], values: list[float], path: Path, width: int = 1100, height: int = 620) -> None:
    margin_left, margin_right, margin_top, margin_bottom = 190, 40, 60, 70
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    max_value = max(values) if values else 1
    bar_height = max(12, plot_height / max(len(labels), 1) * 0.68)
    gap = max(4, plot_height / max(len(labels), 1) * 0.32)
    items = [
        f'<text x="{width/2}" y="32" text-anchor="middle" font-size="22" font-family="Arial">{html.escape(title)}</text>'
    ]
    for idx, (label, value) in enumerate(zip(labels, values)):
        y = margin_top + idx * (bar_height + gap)
        bar_width = (value / max_value) * plot_width if max_value else 0
        items.append(f'<text x="{margin_left-8}" y="{y+bar_height*0.72}" text-anchor="end" font-size="12" font-family="Arial">{html.escape(label[:28])}</text>')
        items.append(f'<rect x="{margin_left}" y="{y}" width="{bar_width:.2f}" height="{bar_height:.2f}" fill="{PALETTE[idx % len(PALETTE)]}"/>')
        items.append(f'<text x="{margin_left+bar_width+6}" y="{y+bar_height*0.72}" font-size="12" font-family="Arial">{value:.2f}</text>')
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{"".join(items)}</svg>', encoding="utf-8")


def svg_stacked_bar(
    title: str,
    labels: list[str],
    series: dict[str, list[float]],
    path: Path,
    width: int = 1100,
    height: int = 620,
) -> None:
    margin_left, margin_top = 170, 60
    plot_width, bar_height, gap = width - 230, 18, 10
    colors = {"Easy": "#2f9c95", "Medium": "#d89a3d", "Hard": "#b44d5d"}
    items = [f'<text x="{width/2}" y="32" text-anchor="middle" font-size="22" font-family="Arial">{html.escape(title)}</text>']
    for idx, label in enumerate(labels):
        y = margin_top + idx * (bar_height + gap)
        x = margin_left
        items.append(f'<text x="{margin_left-8}" y="{y+14}" text-anchor="end" font-size="12" font-family="Arial">{html.escape(label[:28])}</text>')
        for name, values in series.items():
            width_part = plot_width * values[idx]
            items.append(f'<rect x="{x:.2f}" y="{y}" width="{width_part:.2f}" height="{bar_height}" fill="{colors.get(name, "#777")}"/>')
            x += width_part
    legend_x = margin_left
    for name, color in colors.items():
        items.append(f'<rect x="{legend_x}" y="{height-38}" width="14" height="14" fill="{color}"/>')
        items.append(f'<text x="{legend_x+20}" y="{height-26}" font-size="13" font-family="Arial">{name}</text>')
        legend_x += 100
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{"".join(items)}</svg>', encoding="utf-8")


def svg_heatmap(title: str, labels: list[str], matrix: np.ndarray, path: Path, cell: int = 17) -> None:
    size = min(len(labels), 40)
    labels = labels[:size]
    matrix = matrix[:size, :size]
    width = 260 + size * cell
    height = 180 + size * cell
    items = [f'<text x="{width/2}" y="28" text-anchor="middle" font-size="20" font-family="Arial">{html.escape(title)}</text>']
    x0, y0 = 190, 70
    for i, label in enumerate(labels):
        items.append(f'<text x="{x0-8}" y="{y0+i*cell+12}" text-anchor="end" font-size="10" font-family="Arial">{html.escape(label[:22])}</text>')
        items.append(f'<text transform="translate({x0+i*cell+11},{y0-8}) rotate(-60)" font-size="9" font-family="Arial">{html.escape(label[:18])}</text>')
    for i in range(size):
        for j in range(size):
            value = float(matrix[i, j])
            shade = int(255 - 180 * value)
            color = f"rgb({shade},{shade},{255})"
            items.append(f'<rect x="{x0+j*cell}" y="{y0+i*cell}" width="{cell}" height="{cell}" fill="{color}"/>')
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{"".join(items)}</svg>', encoding="utf-8")


def run(
    profiles: dict[str, dict[str, object]],
    company_keys: list[str],
    similarity_matrix: np.ndarray,
    outputs_dir: Path,
) -> None:
    viz_dir = outputs_dir / "visualizations"
    viz_dir.mkdir(parents=True, exist_ok=True)

    top_companies = sorted(
        company_keys,
        key=lambda key: profiles[key]["data_summary"]["total_questions"],
        reverse=True,
    )[:20]
    svg_bar_chart(
        "Company-wise Question Count",
        [profiles[key]["company"] for key in top_companies],
        [profiles[key]["data_summary"]["total_questions"] for key in top_companies],
        viz_dir / "company_question_count.svg",
    )

    svg_stacked_bar(
        "Difficulty Distribution by Company",
        [profiles[key]["company"] for key in top_companies],
        {
            difficulty: [
                profiles[key]["difficulty_profile"][difficulty]["percentage"]
                for key in top_companies
            ]
            for difficulty in ["Easy", "Medium", "Hard"]
        },
        viz_dir / "difficulty_distribution_by_company.svg",
    )

    for key in top_companies[:5]:
        topic_items = sorted(
            profiles[key]["topic_profile"].items(),
            key=lambda item: item[1]["count"],
            reverse=True,
        )[:15]
        svg_bar_chart(
            f"Topic Distribution - {profiles[key]['company']}",
            [topic for topic, _data in topic_items],
            [data["count"] for _topic, data in topic_items],
            viz_dir / f"topic_distribution_{key}.svg",
        )

    frequency_values = [
        profiles[key]["frequency_profile"]["mean"] or 0
        for key in company_keys
    ]
    svg_bar_chart(
        "Mean Frequency by Company",
        [profiles[key]["company"] for key in top_companies],
        [profiles[key]["frequency_profile"]["mean"] or 0 for key in top_companies],
        viz_dir / "frequency_distribution.svg",
    )

    global_trends = {}
    for key in company_keys:
        for topic, data in profiles[key]["recent_topic_trends"].items():
            global_trends[topic] = global_trends.get(topic, 0) + data["weighted_score"]
    top_trends = sorted(global_trends.items(), key=lambda item: item[1], reverse=True)[:20]
    svg_bar_chart(
        "Recent Topic Trends",
        [topic for topic, _score in top_trends],
        [score for _topic, score in top_trends],
        viz_dir / "recent_topic_trends.svg",
    )

    cluster_counts = {}
    for key in company_keys:
        for cluster_id, data in profiles[key]["cluster_profile"].items():
            cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + data["count"]
    cluster_items = sorted(cluster_counts.items(), key=lambda item: int(item[0]))
    svg_bar_chart(
        "K-Means Cluster Distribution",
        [f"Cluster {cluster_id}" for cluster_id, _count in cluster_items],
        [count for _cluster_id, count in cluster_items],
        viz_dir / "kmeans_cluster_distribution.svg",
    )

    svg_heatmap(
        "Company Similarity Heatmap",
        [profiles[key]["company"] for key in company_keys[:40]],
        similarity_matrix[:40, :40],
        viz_dir / "company_similarity_heatmap.svg",
    )

    _ = frequency_values
