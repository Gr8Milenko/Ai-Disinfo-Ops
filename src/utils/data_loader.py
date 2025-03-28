# utils/data_loader.py

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import streamlit as st
from src.config.paths import INFER_LOG_PATH, LABEL_LOG_PATH, PROCESSED_DIR

@st.cache_data(ttl=30)
def load_inference_log():
    if not os.path.exists(INFER_LOG_PATH):
        return pd.DataFrame()

    with open(INFER_LOG_PATH, "r") as f:
        records = [json.loads(line) for line in f if line.strip()]
    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["confidence"] = df["result"].apply(lambda x: x.get("confidence", 0.0))
    df["flagged"] = df["result"].apply(lambda x: x.get("flagged", False))
    df["reason"] = df["result"].apply(lambda x: x.get("reason", ""))
    df["datetime"] = df["file"].apply(lambda f: extract_datetime_from_filename(f))
    return df

def extract_datetime_from_filename(filename):
    try:
        full_path = PROCESSED_DIR / Path(filename).name
        if full_path.exists():
            return datetime.fromtimestamp(full_path.stat().st_mtime)
    except Exception:
        pass
    return datetime.min

def load_metadata_from_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def save_manual_label(metadata_id, label):
    Path(LABEL_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(LABEL_LOG_PATH, "a", encoding="utf-8") as f:
        json.dump({
            "id": metadata_id,
            "label": label,
            "timestamp": datetime.now().isoformat()
        }, f)
        f.write("\n")

def export_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")
