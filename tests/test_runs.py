# tests/test_runs.py

import os
import json
from pathlib import Path

TEST_INPUT_DIR = Path("data/processed/test_inputs")
REQUIRED_FIELDS = ["text", "named_entities", "type", "url"]

class DisinfoModel:
    def __init__(self, model_type="mock"):
        self.model_type = model_type.lower()

        if self.model_type == "mock":
            self.model = self._mock_model()
        else:
            raise NotImplementedError(f"Model type '{self.model_type}' is not supported in tests yet.")

    def _mock_model(self):
        class MockModel:
            def predict(self, texts):
                return ["real" if "community" in t else "disinfo" for t in texts]

            def predict_proba(self, texts):
                return [[0.2, 0.8] if "community" not in t else [0.9, 0.1] for t in texts]
        return MockModel()

    def predict(self, texts):
        return self.model.predict(texts)

    def predict_proba(self, texts):
        return self.model.predict_proba(texts)

def validate_sample(sample, idx):
    for field in REQUIRED_FIELDS:
        if field not in sample:
            raise ValueError(f"[ERROR] Sample {idx} is missing required field: '{field}'")

    if not isinstance(sample["text"], str) or len(sample["text"]) < 20:
        raise ValueError(f"[ERROR] Sample {idx} has invalid or too-short 'text' field")

    if not isinstance(sample["named_entities"], list):
        raise ValueError(f"[ERROR] Sample {idx} has invalid 'named_entities' format")

    if sample["type"] not in ["article", "tweet", "video_transcript"]:
        raise ValueError(f"[ERROR] Sample {idx} has unknown type: '{sample['type']}'")

def test_samples():
    files = list(TEST_INPUT_DIR.glob("*.json"))
    if not files:
        raise RuntimeError("[ERROR] No test input files found.")

    print(f"[INFO] Validating and running inference on {len(files)} test samples...")
    texts = []
    for i, file in enumerate(files, 1):
        with open(file, "r", encoding="utf-8") as f:
            sample = json.load(f)
            validate_sample(sample, i)
            texts.append(sample["text"])

    model = DisinfoModel(model_type="mock")  # Easily swap to 'bert' later
    preds = model.predict(texts)
    probs = model.predict_proba(texts)

    assert len(preds) == len(texts), "[ERROR] Prediction count mismatch"
    assert all(isinstance(p, str) for p in preds), "[ERROR] Predictions must be strings"
    assert all(len(p) == 2 for p in probs), "[ERROR] Each probability vector must be length 2"

    print("[PASS] Test samples passed structure and inference validation.")

if __name__ == "__main__":
    test_samples()
