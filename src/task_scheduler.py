import time
import json
from datetime import datetime, timedelta
from job_manager import start_job, load_status

CONFIG_PATH = "../logs/scheduler_config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

last_run_time = {}

def should_run(task, config):
    now = datetime.now()
    interval = timedelta(minutes=config.get("interval_minutes", 60))
    last_run = last_run_time.get(task, now - interval - timedelta(seconds=1))
    return (now - last_run) >= interval

while True:
    config = load_config()
    for task, details in config.items():
        if not details.get("enabled", False):
            continue
        if should_run(task, details):
            print(f"[SCHEDULER] Launching {task}")
            start_job(task, f"python ../src/{task}_loop.py")
            last_run_time[task] = datetime.now()
    time.sleep(60)
