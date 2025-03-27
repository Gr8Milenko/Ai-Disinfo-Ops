import os
import json
import numpy as np
import pandas as pd
from preprocess import preprocess_and_vectorize
from models.bert_model import BertDisinfoModel

REVIEW_QUEUE_PATH = "../labels/review_queue.jsonl"
NUM_QUERY_SAMPLES = 10  # number of uncertain samples to queue

def entropy(probabilities):
    return -np.sum(probabilities * np.log(probabilities + 1e-9), axis=1)

def run_active_learning_round():
    X, y, df = preprocess_and_vectorize()

    if X.empty or len(y.unique()) < 2:
        print("[ACTIVE] Not enough labeled data to train.")
        return

    model = BertDisinfoModel()
    print("[ACTIVE] Training BERT model on labeled data...")
    model.fit(df["text"], y)

    all_df = df.copy()
    all_df["is_labeled"] = all_df["label"].notnull()
    unlabeled_df = all_df[~all_df["is_labeled"]].copy()

    if len(unlabeled_df) == 0:
        print("[ACTIVE] No unlabeled samples available.")
        return

    print(f"[ACTIVE] Predicting on {len(unlabeled_df)} unlabeled samples...")
    probs = model.predict_proba(unlabeled_df["text"].tolist())
    unlabeled_df["uncertainty"] = entropy(probs)

    top_uncertain = unlabeled_df.sort_values("uncertainty", ascending=False).head(NUM_QUERY_SAMPLES)

    with open(REVIEW_QUEUE_PATH, "a", encoding="utf-8") as f:
        for _, row in top_uncertain.iterrows():
            queue_item = {
                "file": row["source_file"],
                "uncertainty": row["uncertainty"],
                "text": row["text"][:1000]
            }
            f.write(json.dumps(queue_item) + "\n")

    print(f"[ACTIVE] Pushed {len(top_uncertain)} uncertain samples to review queue.")

if __name__ == "__main__":
    run_active_learning_round()
