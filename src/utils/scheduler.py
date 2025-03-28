# src/utils/scheduler.py

import json
from pathlib import Path
from typing import Dict

class SchedulerManager:
    def __init__(self, sched_path: Path):
        self.sched_path = sched_path
        self._ensure_file()

    def _ensure_file(self):
        if not self.sched_path.exists():
            self.sched_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.sched_path, "w") as f:
                json.dump({}, f)

    def load(self) -> Dict:
        with open(self.sched_path, "r") as f:
            return json.load(f)

    def save(self, config: Dict) -> None:
        with open(self.sched_path, "w") as f:
            json.dump(config, f, indent=2)

    def get_task_config(self, task_name: str, default: Dict = None) -> Dict:
        config = self.load()
        return config.get(task_name, default or {})

    def set_task_config(self, task_name: str, task_config: Dict) -> None:
        config = self.load()
        config[task_name] = task_config
        self.save(config)
