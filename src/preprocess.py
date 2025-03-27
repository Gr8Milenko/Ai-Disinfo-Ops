import os
import json
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load("en_core_web_sm")

# Paths
PROCESSED_DIR = "../data/processed"
LABELS_FILE = "../labels/manual_labels.jsonl"

def load_metadata_files():
    all_data = []
    for folder in ["articles", "tweets", "transcripts"]:
        dir_path = os.path.join(PROCESSED_DIR, folder)
        if not os.path.exists(dir_path):
            continue
        for file in os.listdir(dir_path):
            if file.endswith(".json"):
                path = os.path.join(dir_path, file)
                with open(path, "r") as f:
                    data = json.load(f)
                    data["source_file"] = path
                    all_data.append(data)
    return pd.DataFrame(all_data)

def clean_text(text):
    doc = nlp(text)
    tokens = [t.lemma_.lower() for t in doc if not t.is_stop and not t.is_punct]
    return " ".join(tokens)

def add_metadata_features(df):
    df["word_count"] = df["text"].apply(lambda x: len(x.split()))
    df["sentence_count"] = df["text"].apply(lambda x: len(list(nlp(x).sents)))
    df["ner_count"] = df["named_entities"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    return df
def load_manual_labels():
    if not os.path.exists(LABELS_FILE):
        return {}
    with open(LABELS_FILE, "r") as f:
        entries = [json.loads(line) for line in f.readlines()]
    return {e["id"]: e["label"] for e in entries}

def apply_labels(df):
    label_map = load_manual_labels()
    df["label"] = df["source_file"].map(label_map)
    df = df[df["label"].notnull()]
    return df

def preprocess_and_vectorize():
    df = load_metadata_files()
    df = df[df["text"].notnull()]
    df["clean_text"] = df["text"].apply(clean_text)
    df = add_metadata_features(df)
    df = apply_labels(df)

    vectorizer = TfidfVectorizer(max_features=1000)
    X_text = vectorizer.fit_transform(df["clean_text"])

    metadata_features = df[["word_count", "sentence_count", "ner_count"]].reset_index(drop=True)
    X = pd.concat([pd.DataFrame(X_text.toarray()), metadata_features], axis=1)
    y = df["label"].reset_index(drop=True)

    return X, y, df

if __name__ == "__main__":
    X, y, df = preprocess_and_vectorize()
    print(f"Processed {len(df)} labeled records. Feature shape: {X.shape}")
