from __future__ import annotations

import json
from pathlib import Path

from features.feature_engineering import build_multi_hot_rows, global_topics
from models.clustering import run as run_clustering
from models.company_similarity import write_similarity_matrix
from preprocessing.clean_data import REQUIRED_COLUMNS, run as run_cleaning, write_csv
from profiling.company_profile import build_profiles
from visualization.plots import run as run_plots


ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / "data" / "company_questions.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUTS_DIR = ROOT / "outputs"


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    cleaned_rows = run_cleaning(INPUT_CSV, PROCESSED_DIR, OUTPUTS_DIR)

    topic_names = global_topics(cleaned_rows)
    multihot_rows = build_multi_hot_rows(cleaned_rows, topic_names)
    write_csv(
        PROCESSED_DIR / "question_topic_multihot.csv",
        multihot_rows,
        [*REQUIRED_COLUMNS, *topic_names],
    )

    question_to_cluster, clustering_metadata = run_clustering(cleaned_rows, OUTPUTS_DIR)
    profiles, company_keys, vectors, feature_config = build_profiles(
        cleaned_rows,
        question_to_cluster,
        OUTPUTS_DIR,
    )
    similarity_matrix = write_similarity_matrix(OUTPUTS_DIR, company_keys, vectors)
    run_plots(profiles, company_keys, similarity_matrix, OUTPUTS_DIR)

    pipeline_report = {
        "input_dataset": str(INPUT_CSV.relative_to(ROOT)),
        "processed_dataset": "data/processed/cleaned_questions.csv",
        "topic_multihot_dataset": "data/processed/question_topic_multihot.csv",
        "outputs_dir": "outputs",
        "company_count": len(company_keys),
        "profile_count": len(profiles),
        "clustering": {
            "method": clustering_metadata["method"],
            "selected_k": clustering_metadata["selected_k"],
            "selection_metric": clustering_metadata["selection_metric"],
        },
        "feature_config": feature_config,
        "constraints": {
            "llm_used": False,
            "manual_topic_rule_matching_used": False,
            "raw_question_data_modified": False,
        },
    }
    (OUTPUTS_DIR / "pipeline_report.json").write_text(
        json.dumps(pipeline_report, indent=2),
        encoding="utf-8",
    )

    print(f"Cleaned rows: {len(cleaned_rows)}")
    print(f"Companies profiled: {len(company_keys)}")
    print(f"Selected clusters: {clustering_metadata['selected_k']}")
    print("Wrote outputs/company_oa_profiles.json")
    print("Wrote outputs/company_oa_profiles.csv")
    print("Wrote outputs/company_similarity.csv")
    print("Wrote outputs/analysis_report.csv")
    print("Wrote outputs/visualizations/*.svg")


if __name__ == "__main__":
    main()
