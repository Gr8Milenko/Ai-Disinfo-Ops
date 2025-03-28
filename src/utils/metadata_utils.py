# src/utils/metadata_utils.py

import json


def load_metadata_from_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
