# src/utils/file_utils.py

import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from src.config.paths import INFER_LOG_PATH, REVIEW_QUEUE_PATH, PROCESSED_DIR


def extract_datetime_from_filename(filename):
    try:
        full_path = PROCESSED_DIR / Path(filename).name
        if full_path.exists():
            return datetime.fromtimestamp(full_path.stat().st_mtime)
        else:
            print(f"[WARN] File not found: {full_path}")
    except Exception as e:
        print(f"[ERROR] Failed to get datetime for {filename}: {e}")
    return datetime.min


def load_inference_log():
    if not os.path.exists(INFER_LOG_PATH):
        return pd.DataFrame()

    with open(INFER_LOG_PATH, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f.readlines()]
    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["confidence"] = df["result"].apply(lambda x: x.get("confidence", 0.0))
    df["flagged"] = df["result"].apply(lambda x: x.get("flagged", False))
    df["reason"] = df["result"].apply(lambda x: x.get("reason", ""))
    df["datetime"] = df["file"].apply(extract_datetime_from_filename)
    return df


def load_review_queue():
    if not os.path.exists(REVIEW_QUEUE_PATH):
        return []

    with open(REVIEW_QUEUE_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f.readlines()]
