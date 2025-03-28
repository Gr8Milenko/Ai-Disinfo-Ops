import sys
import os
import json
import time
from datetime import datetime, timedelta, time as dtime
from pathlib import Path

import streamlit as st
import pandas as pd

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Imports ---
from src.config.paths import (
    INFER_LOG_PATH,
    LABEL_LOG_PATH,
    REVIEW_QUEUE_PATH,
    SCHED_PATH,
    PROCESSED_DIR,
)

from src.utils import (
    data_loader,
    file_utils,
    job_utils,
    label_utils,
    metadata_utils,
    scheduler_utils,
    filter_utils,
)

# --- Auto-refresh ---
AUTO_REFRESH_SECONDS = st.sidebar.slider("Auto-Refresh Interval (sec)", 15, 300, 60, step=15)
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if time.time() - st.session_state.last_refresh > AUTO_REFRESH_SECONDS:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# --- Sidebar: Automation Controls ---
st.sidebar.header("Automation")

if st.sidebar.button("Start Active Learning Round"):
    success, msg = job_utils.start_job("active_learning", "python ../src/active_learning_loop.py")
    st.sidebar.success(msg if success else f"Failed: {msg}")

if st.sidebar.button("End Active Learning"):
    success, msg = job_utils.end_job("active_learning")
    st.sidebar.info(msg)

# --- Sidebar: Scheduler Controls ---
st.sidebar.markdown("### Scheduled Tasks")
sched_cfg = scheduler_utils.load_sched()
al_cfg = sched_cfg.get("active_learning", {"enabled": False, "interval_minutes": 360})

al_cfg["enabled"] = st.sidebar.checkbox("Auto-Schedule Active Learning", value=al_cfg["enabled"])
al_cfg["interval_minutes"] = st.sidebar.number_input(
    "Interval (minutes)", min_value=30, max_value=1440, value=al_cfg["interval_minutes"], step=30
)
sched_cfg["active_learning"] = al_cfg
scheduler_utils.save_sched(sched_cfg)

# --- Main App ---
st.title("Disinformation Detection Dashboard")

df = data_loader.load_inference_log()
if df.empty:
    st.warning("No inference logs found.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
filter_type = st.sidebar.selectbox("Type", options=["All", "article", "tweet", "video_transcript"])
filter_flagged = st.sidebar.checkbox("Flagged only", value=False)
min_conf = st.sidebar.slider("Min Confidence", 0.0, 1.0, 0.5, step=0.01)
days_back = st.sidebar.slider("Days Back", 0, 30, 7)

# Apply filters
df = filter_utils.filter_data(df, filter_type, filter_flagged, min_conf, days_back)
st.markdown(f"### {len(df)} entries found")

# --- Export to CSV ---
if not df.empty:
    csv = file_utils.export_to_csv(df)
    st.download_button("Export Filtered Results to CSV", data=csv, file_name="disinfo_results.csv")

# --- Display Results ---
for idx, row in df.iterrows():
    st.subheader(f"{row['type'].capitalize()} | Confidence: {row['confidence']:.2f}")
    st.write(f"**Flagged**: {'Yes' if row['flagged'] else 'No'}")
    st.write(f"**Reason**: {row['reason']}")
    st.write(f"**File**: `{row['file']}`")

    metadata = metadata_utils.load_metadata_from_file(row["file"])
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
        label_utils.save_manual_label(row["file"], label)
        st.success(f"Labeled as: {label}")

    st.markdown("---")

# --- Job Monitor ---
st.markdown("## Job Monitor")
job_info = job_utils.get_job_info()
if not job_info:
    st.info("No jobs found.")
else:
    for job, details in job_info.items():
        st.markdown(f"**{job}** - Status: `{details['status']}`")
        st.code(f"Last Run: {details.get('last_run', 'N/A')}")
        st.code(f"PID: {details.get('pid', 'N/A')}")

# --- Review Queue ---
st.markdown("### Review Queue")
queue = file_utils.load_review_queue()

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
            label_utils.save_manual_label(item["file"], label)
            st.success(f"Labeled as {label}")
