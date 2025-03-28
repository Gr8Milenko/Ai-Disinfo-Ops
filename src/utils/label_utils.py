# src/utils/label_utils.py

import json
from datetime import datetime
from pathlib import Path
from src.config.paths import LABEL_LOG_PATH


def save_manual_label(metadata_id, label):
    label_entry = {
        "id": metadata_id,
        "label": label,
        "timestamp": datetime.now().isoformat()
    }

    Path(LABEL_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(LABEL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(label_entry) + "\n")

def append_to_review_queue(entries, queue_path):
    Path(queue_path).parent.mkdir(parents=True, exist_ok=True)
    with open(queue_path, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
