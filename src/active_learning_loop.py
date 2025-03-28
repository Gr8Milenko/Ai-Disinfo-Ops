import os
import json
from datetime import datetime

from src.utils.data_loader import load_all_metadata_files
from src.utils.label_utils import load_manual_labels
from src.utils.file_utils import safe_write_json

from src.config.paths import (
    REVIEW_QUEUE_PATH,
    PROCESSED_DIR,
    LABEL_LOG_PATH,
)

# --- Config ---
UNCERTAINTY_THRESHOLD = 0.15
SAMPLE_LIMIT = 25


def calculate_uncertainty(result):
    confidence = result.get("confidence", 0.0)
    return 1.0 - confidence


def build_review_queue(interactive=False):
    """
    Returns a list of uncertain samples for review.
    If interactive=False, also writes the queue to disk.
    """
    all_metadata = load_all_metadata_files(PROCESSED_DIR)
    manual_labels = load_manual_labels(LABEL_LOG_PATH)

    review_items = []

    for path, metadata in all_metadata.items():
        if path in manual_labels:
            continue

        result = metadata.get("result", {})
        uncertainty = calculate_uncertainty(result)

        if uncertainty >= UNCERTAINTY_THRESHOLD:
            item = {
                "file": path,
                "uncertainty": round(uncertainty, 4),
                "text": metadata.get("text", "")[:1000],
                "type": metadata.get("type", "unknown"),
                "url": metadata.get("url"),
            }
            review_items.append(item)

    review_items.sort(key=lambda x: x["uncertainty"], reverse=True)
    top_items = review_items[:SAMPLE_LIMIT]

    if not interactive:
        with open(REVIEW_QUEUE_PATH, "w", encoding="utf-8") as f:
            for item in top_items:
                f.write(json.dumps(item) + "\n")
        print(f"[INFO] Wrote {len(top_items)} uncertain samples to queue")

    return top_items


def main():
    print("[INFO] Starting Active Learning Loop")
    build_review_queue(interactive=False)


if __name__ == "__main__":
    main()
