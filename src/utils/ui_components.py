# src/utils/ui_components.py

import streamlit as st
import pandas as pd
from datetime import time as dtime
from src.utils.label_utils import save_manual_label
from src.utils.metadata_utils import load_metadata_from_file


def render_filters(df):
    st.sidebar.header("Filters")

    filter_type = st.sidebar.selectbox("Type", options=["All", "article", "tweet", "video_transcript"])
    filter_flagged = st.sidebar.checkbox("Flagged only", value=False)
    min_conf = st.sidebar.slider("Min Confidence", 0.0, 1.0, 0.5, step=0.01)
    days_back = st.sidebar.slider("Days Back", 0, 30, 7)

    time_threshold = pd.Timestamp.combine(
        pd.Timestamp.now().date() - pd.Timedelta(days=days_back),
        dtime.min
    )

    filtered_df = df[df["datetime"] >= time_threshold]
    if filter_type != "All":
        filtered_df = filtered_df[filtered_df["type"] == filter_type]
    if filter_flagged:
        filtered_df = filtered_df[filtered_df["flagged"] == True]
    filtered_df = filtered_df[filtered_df["confidence"] >= min_conf]

    return filtered_df


def render_export_button(df, label="Export Filtered Results to CSV"):
    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(label, data=csv, file_name="disinfo_results.csv")


def render_entry_card(row):
    with st.expander(f"{row['type'].capitalize()} | Confidence: {row['confidence']:.2f}", expanded=False):
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


def render_review_queue(queue):
    if not queue:
        st.success("No items in review queue.")
        return

    st.markdown("### Review Queue")
    for item in queue:
        with st.expander(f"Sample | Uncertainty: {item['uncertainty']:.4f}"):
            st.text_area("Text", item["text"], height=200)
            label = st.radio(
                "Assign label",
                ["None", "Disinformation", "Uncertain", "Legit"],
                key=item["file"] + "_queue"
            )
            if label != "None":
                save_manual_label(item["file"], label)
                st.success(f"Labeled as {label}")
