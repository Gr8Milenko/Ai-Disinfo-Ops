import sys
import os
import json
import time

import streamlit as st

import pandas as pd


# Add the project root to the path so "src" can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Paths ---
from src.config.paths import (
    INFER_LOG_PATH,
    LABEL_LOG_PATH,
    REVIEW_QUEUE_PATH,
    SCHED_PATH,
    PROCESSED_DIR,
)

from datetime import datetime, timedelta
from src.job_manager import start_job, end_job, get_job_info

print("cwd:", os.getcwd())
print("sys.path:", sys.path)

# --- Auto-refresh ---
AUTO_REFRESH_SECONDS = st.sidebar.slider("Auto-Refresh Interval (sec)", 15, 300, 60, step=15)
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > AUTO_REFRESH_SECONDS:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# --- Loaders ---
@st.cache_data(ttl=30)
def load_inference_log():
    if not os.path.exists(INFER_LOG_PATH):
        return pd.DataFrame()
    with open(INFER_LOG_PATH, "r") as f:
        records = [json.loads(line) for line in f.readlines()]
    df = pd.DataFrame(records)

    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("No valid entries in inference log.")
        st.stop()

    df["confidence"] = df["result"].apply(lambda x: x.get("confidence", 0.0))
    df["flagged"] = df["result"].apply(lambda x: x.get("flagged", False))
    df["reason"] = df["result"].apply(lambda x: x.get("reason", ""))
    df["datetime"] = df["file"].apply(lambda f: extract_datetime_from_filename(f))
    st.write("[DEBUG] Sample resolved datetimes:", df["datetime"].tolist())

    print("[DEBUG] Log loaded:", len(df))
    print("[DEBUG] Columns:", df.columns)
    print(df.head())
    
    return df

from pathlib import Path
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

def load_metadata_from_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def save_manual_label(metadata_id, label):
    label_entry = {
        "id": metadata_id,
        "label": label,
        "timestamp": datetime.now().isoformat()
    }

    # Ensure labels directory exists
    Path(LABEL_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

    with open(LABEL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(label_entry) + "\n")

def export_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# --- Sidebar: Job Controls ---
st.sidebar.header("Automation")

if st.sidebar.button("Start Active Learning Round"):
    success, msg = start_job("active_learning", "python ../src/active_learning_loop.py")
    st.sidebar.success(msg if success else f"Failed: {msg}")

if st.sidebar.button("End Active Learning"):
    success, msg = end_job("active_learning")
    st.sidebar.info(msg)

# --- Sidebar: Scheduler Toggle ---
st.sidebar.markdown("### Scheduled Tasks")

def load_sched():
    if not os.path.exists(SCHED_PATH):
        return {}
    with open(SCHED_PATH, "r") as f:
        return json.load(f)

def save_sched(cfg):
    with open(SCHED_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

sched_cfg = load_sched()
al_cfg = sched_cfg.get("active_learning", {"enabled": False, "interval_minutes": 360})

enabled = st.sidebar.checkbox("Auto-Schedule Active Learning", value=al_cfg["enabled"])
interval = st.sidebar.number_input("Interval (minutes)", 30, 1440, al_cfg["interval_minutes"], step=30)

al_cfg["enabled"] = enabled
al_cfg["interval_minutes"] = interval
sched_cfg["active_learning"] = al_cfg
save_sched(sched_cfg)

# --- Main Dashboard ---
st.title("Disinformation Detection Dashboard")

df = load_inference_log()
st.write("[DEBUG] Loaded log data:")
st.write(df)

if not df.empty:
    st.write("[DEBUG] Sample confidence values:", df["confidence"].tolist())
    st.write("[DEBUG] Sample datetime values:", df["datetime"].tolist())
if df.empty:
    st.warning("No inference logs found.")
    st.stop()

# --- Filters ---
st.sidebar.header("Filters")
filter_type = st.sidebar.selectbox("Type", options=["All", "article", "tweet", "video_transcript"])
filter_flagged = st.sidebar.checkbox("Flagged only", value=False)
min_conf = st.sidebar.slider("Min Confidence", 0.0, 1.0, 0.5, step=0.01)
days_back = st.sidebar.slider("Days Back", 0, 30, 7)
time_threshold = pd.Timestamp.now() - pd.Timedelta(days=days_back)

df = df[df["datetime"] >= time_threshold]
if filter_type != "All":
    df = df[df["type"] == filter_type]
if filter_flagged:
    df = df[df["flagged"] == True]
df = df[df["confidence"] >= min_conf]

st.markdown(f"### {len(df)} entries found")

# --- Export ---
if not df.empty:
    csv = export_to_csv(df)
    st.download_button("Export Filtered Results to CSV", data=csv, file_name="disinfo_results.csv")

# --- Show Results ---
for idx, row in df.iterrows():
    st.subheader(f"{row['type'].capitalize()} | Confidence: {row['confidence']:.2f}")
    st.write(f"**Flagged**: {'Yes' if row['flagged'] else 'No'}")
    st.write(f"**Reason**: {row['reason']}")
    st.write(f"**File**: `{row['file']}`")

    metadata = load_metadata_from_file(row["file"])
    preview = metadata.get("text", "")[:1000]
    st.text_area("Preview", preview, height=200)

    if metadata.get("named_entities"):
        st.markdown("**Named Entities:**")
        st.write(", ".join(metadata["named_entities"][:10]))

    if metadata.get("url"):
        st.markdown(f"[Source Link]({metadata['url']})")

    label = st.radio(
        f"Label this item (ID: {row['file']})",
        options=["None", "Disinformation", "Uncertain", "Legit"],
        key=row["file"]
    )
    if label != "None":
        save_manual_label(row["file"], label)
        st.success(f"Labeled as: {label}")

    st.markdown("---")

# --- Job Monitor ---
st.markdown("## Job Monitor")
job_info = get_job_info()
if not job_info:
    st.info("No jobs found.")
else:
    for job, details in job_info.items():
        st.markdown(f"**{job}** - Status: `{details['status']}`")
        st.code(f"Last Run: {details.get('last_run', 'N/A')}")
        st.code(f"PID: {details.get('pid', 'N/A')}")

# --- Review Queue ---
st.markdown("### Review Queue")

if os.path.exists(REVIEW_QUEUE_PATH):
    with open(REVIEW_QUEUE_PATH, "r") as f:
        queue = [json.loads(line) for line in f.readlines()]
else:
    queue = []

if not queue:
    st.success("No items in review queue.")
else:
    for item in queue:
        st.subheader(f"Sample | Uncertainty: {item['uncertainty']:.4f}")
        st.text_area("Text", item["text"], height=200)
        label = st.radio(
            "Assign label",
            ["None", "Disinformation", "Uncertain", "Legit"],
            key=item["file"] + "_queue"
        )
        if label != "None":
            save_manual_label(item["file"], label)
            st.success(f"Labeled as {label}")
