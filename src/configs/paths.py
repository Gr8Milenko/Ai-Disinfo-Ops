from pathlib import Path

# Dynamically get the project root no matter where code is run from
PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOGS_DIR = PROJECT_ROOT / "logs"
LABELS_DIR = PROJECT_ROOT / "labels"
DATA_DIR = PROJECT_ROOT / "data"

INFER_LOG_PATH = LOGS_DIR / "inference_log.jsonl"
LABEL_LOG_PATH = LABELS_DIR / "manual_labels.jsonl"
REVIEW_QUEUE_PATH = LABELS_DIR / "review_queue.jsonl"
SCHED_PATH = LOGS_DIR / "scheduler_config.json"
PROCESSED_DIR = DATA_DIR / "processed"

print("[DEBUG] paths.py loaded")
