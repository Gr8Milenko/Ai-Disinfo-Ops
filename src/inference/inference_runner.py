# src/inference/inference_runner.py

import json
from pathlib import Path
from typing import List, Union
from models.bert_model import BertDisinfoModel

class DisinfoModel:
    def __init__(self, model_type="bert"):
        self.model_type = model_type.lower()
        if self.model_type == "bert":
            self.model = BertDisinfoModel()
        else:
            raise NotImplementedError(f"Model type '{self.model_type}' not implemented in inference runner.")

    def predict(self, texts: List[str]) -> List[str]:
        return self.model.predict(texts)

    def predict_proba(self, texts: List[str]) -> List[List[float]]:
        return self.model.predict_proba(texts)

def load_texts_from_jsonl(file_path: Union[str, Path]) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line)["text"] for line in f if line.strip()]

def run_inference(input_data: Union[str, List[str]], model_type="bert") -> List[dict]:
    model = DisinfoModel(model_type=model_type)

    if isinstance(input_data, str) and input_data.endswith(".jsonl"):
        texts = load_texts_from_jsonl(input_data)
    elif isinstance(input_data, list):
        texts = input_data
    else:
        raise ValueError("Input must be a JSONL file path or a list of text strings.")

    predictions = model.predict(texts)
    probabilities = model.predict_proba(texts)

    results = []
    for text, label, prob in zip(texts, predictions, probabilities):
        results.append({
            "text": text,
            "predicted_label": label,
            "confidence": max(prob),
            "probabilities": prob
        })
    return results

if __name__ == "__main__":
    sample_input = "data/processed/test_inputs/sample1.json"
    results = run_inference(sample_input, model_type="bert")
    print(json.dumps(results, indent=2))
