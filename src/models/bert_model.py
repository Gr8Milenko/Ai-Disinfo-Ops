import torch
import numpy as np
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset
from .base_model import BaseDisinfoModel

class BertDisinfoModel(BaseDisinfoModel):
    def __init__(self, model_name="distilbert-base-uncased", num_labels=3):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
        self.label_encoder = LabelEncoder()
        self.trainer = None

    def _tokenize(self, texts):
        return self.tokenizer(texts, truncation=True, padding=True, return_tensors="pt")

    def fit(self, texts, labels):
        encoded_labels = self.label_encoder.fit_transform(labels)

        class DisinfoDataset(Dataset):
            def __init__(self, texts, labels):
                self.encodings = self.tokenizer(texts, truncation=True, padding=True)
                self.labels = labels

            def __getitem__(self, idx):
                item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
                item["labels"] = torch.tensor(self.labels[idx])
                return item

            def __len__(self):
                return len(self.labels)

        dataset = DisinfoDataset(texts, encoded_labels)

        args = TrainingArguments(
            output_dir="./models/bert-checkpoints",
            per_device_train_batch_size=8,
            num_train_epochs=3,
            logging_dir="./logs/bert",
            logging_steps=10,
            disable_tqdm=True,
            save_strategy="no"
        )

        self.trainer = Trainer(model=self.model, args=args, train_dataset=dataset)
        self.trainer.train()

    def predict(self, texts):
        self.model.eval()
        inputs = self._tokenize(texts)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=1).numpy()
        return self.label_encoder.inverse_transform(preds)

    def predict_proba(self, texts):
        self.model.eval()
        inputs = self._tokenize(texts)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1).numpy()
        return probs
