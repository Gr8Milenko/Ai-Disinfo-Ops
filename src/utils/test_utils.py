# src/utils/test_utils.py

import os
import json
import random
from pathlib import Path
from datetime import datetime

SAMPLE_TEXTS = [
    "Breaking: Officials confirm new cyber campaign targeting elections.",
    "Experts warn of AI-generated content used to sway voters.",
    "Local news: community event draws record turnout.",
    "Viral tweet claims vaccine contains microchips—fact-checkers disagree.",
    "Transcript shows misleading edits in viral interview clip."
]

ENTITY_LIST = [
    ["Russia", "elections"],
    ["AI", "disinformation"],
    ["community", "event"],
    ["vaccine", "microchips"],
    ["interview", "clip"]
]

SOURCE_TYPES = ["article", "tweet", "video_transcript"]

def generate_sample(i):
    text = SAMPLE_TEXTS[i % len(SAMPLE_TEXTS)]
    return {
        "text": text,
        "named_entities": ENTITY_LIST[i % len(ENTITY_LIST)],
        "type": SOURCE_TYPES[i % len(SOURCE_TYPES)],
        "url": f"https://example.com/item/{i}"
    }

def write_synthetic_samples(n, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    files = []
    for i in range(n):
        sample = generate_sample(i)
        fname = f"sample_{i}_{timestamp}.json"
        fpath = os.path.join(output_dir, fname)
        sample["source_file"] = fpath
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2)
        files.append(fpath)
    return output_dir
