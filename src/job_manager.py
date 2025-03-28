import os
import json
import subprocess
import psutil
from datetime import datetime

JOB_FILE = "../logs/job_status.json"
def ensure_job_file():
# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(JOB_FILE), exist_ok=True)
# Then create the job_status.json if it doesn't exist
if not os.path.exists(JOB_FILE):
        with open(JOB_FILE, "w") as f:
            f.write("{}")

ensure_job_file()
def load_status():
    if not os.path.exists(JOB_FILE):
        return {}
    with open(JOB_FILE, "r") as f:
        return json.load(f)

def save_status(status):
    with open(JOB_FILE, "w") as f:
        json.dump(status, f, indent=2)

def start_job(name, command):
    status = load_status()
    if name in status and status[name].get("status") == "running":
        return False, "Job already running"

    process = subprocess.Popen(command, shell=True)
    status[name] = {
        "status": "running",
        "pid": process.pid,
        "last_run": datetime.now().isoformat()
    }
    save_status(status)
    return True, f"Started job {name} (PID {process.pid})"

def end_job(name):
    status = load_status()
    if name not in status or status[name].get("status") != "running":
        return False, "No running job found"

    pid = status[name].get("pid")
    try:
        p = psutil.Process(pid)
        p.terminate()
        status[name]["status"] = "terminated"
        status[name]["last_end"] = datetime.now().isoformat()
        save_status(status)
        return True, f"Job {name} terminated."
    except Exception as e:
        return False, str(e)

def get_job_info():
    return load_status()
