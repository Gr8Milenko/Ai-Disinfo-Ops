import json
import logging

# Dummy inference logic (replace with real model later)
def run_inference_on_metadata(metadata: dict) -> dict:
    """
    Fake disinfo classifier — flags texts with over 5 named entities.
    """
    entities = metadata.get("named_entities", [])
    flag = len(entities) > 5

    return {
        "flagged": flag,
        "reason": "High named entity density" if flag else "Normal content",
        "confidence": 0.85 if flag else 0.10
    }

def auto_infer_from_saved_metadata(metadata: dict, filepath: str):
    result = run_inference_on_metadata(metadata)
    output = {
        "file": filepath,
        "type": metadata.get("type", "unknown"),
        "result": result
    }

    log_path = "logs/inference_log.jsonl"
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(json.dumps(output) + "\n")

    print(f"[INFER] {filepath} flagged={result['flagged']} confidence={result['confidence']}")
