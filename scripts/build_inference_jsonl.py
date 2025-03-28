# scripts/build_inference_jsonl.py

import json
from pathlib import Path

INPUT_DIR = Path("data/processed/test_inputs")
OUTPUT_FILE = Path("data/processed/test_inference.jsonl")

def build_jsonl():
    files = list(INPUT_DIR.glob("*.json"))
    if not files:
        raise RuntimeError("[ERROR] No input files found in test_inputs.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for file in files:
            with open(file, "r", encoding="utf-8") as in_f:
                data = json.load(in_f)
                out_f.write(json.dumps({"text": data["text"]}) + "\n")

    print(f"[DONE] Wrote {len(files)} samples to {OUTPUT_FILE}")

if __name__ == "__main__":
    build_jsonl()
