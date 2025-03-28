import os
import json
import pandas as pd
import spacy
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
from functools import lru_cache
from src.config.paths import PROCESSED_DIR, LABEL_LOG_PATH

nlp = spacy.load("en_core_web_sm")
logger = logging.getLogger(__name__)

# Central location for folder types
SUPPORTED_FOLDERS = ["articles", "tweets", "transcripts"]

def load_metadata_files(folders=SUPPORTED_FOLDERS):
    all_data = []
    for folder in folders:
        dir_path = Path(PROCESSED_DIR) / folder
        if not dir_path.exists():
            logger.warning(f"[PREPROCESS] Skipping missing folder: {dir_path}")
            continue
        for file in dir_path.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    data["source_file"] = str(file)
                    all_data.append(data)
            except Exception as e:
                logger.error(f"[PREPROCESS] Failed to load {file}: {e}")
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
    if not os.path.exists(LABEL_LOG_PATH):
        return {}
    with open(LABEL_LOG_PATH, "r") as f:
        entries = [json.loads(line) for line in f.readlines()]
    return {e["id"]: e["label"] for e in entries}

def apply_labels(df):
    label_map = load_manual_labels()
    df["label"] = df["source_file"].map(label_map)
    df = df[df["label"].notnull()]
    return df

def preprocess_and_vectorize(use_cache=False, folders=SUPPORTED_FOLDERS):
    def _run():
        df = load_metadata_files(folders)
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

    if use_cache:
        return _cached_run(folders=tuple(folders))  # lru_cache needs hashable args
    else:
        return _run()

@lru_cache(maxsize=2)
def _cached_run(folders=("articles", "tweets", "transcripts")):
    return preprocess_and_vectorize(use_cache=False, folders=list(folders))
