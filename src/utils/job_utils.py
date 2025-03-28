# src/utils/job_utils.py

import os
import json
from datetime import datetime
from src.job_manager import start_job, end_job, get_job_info


def trigger_job_start(job_name: str, command: str):
    success, msg = start_job(job_name, command)
    return success, msg


def trigger_job_end(job_name: str):
    success, msg = end_job(job_name)
    return success, msg


def fetch_job_status():
    return get_job_info()


def render_job_status(st):
    st.markdown("## Job Monitor")
    job_info = fetch_job_status()
    
    if not job_info:
        st.info("No jobs found.")
        return

    for job, details in job_info.items():
        st.markdown(f"**{job}** - Status: `{details['status']}`")
        st.code(f"Last Run: {details.get('last_run', 'N/A')}")
        st.code(f"PID: {details.get('pid', 'N/A')}")
