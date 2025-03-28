# src/models/bert_model.py

import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax

class BertDisinfoModel:
    def __init__(self, model_name="bert-base-uncased", checkpoint_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(model_name)

        if checkpoint_path:
            self.model = BertForSequenceClassification.from_pretrained(checkpoint_path)
        else:
            # Start with a base model for demo/testing purposes
            self.model = BertForSequenceClassification.from_pretrained(
                model_name, num_labels=2
            )

        self.model.to(self.device)
        self.model.eval()

    def _tokenize(self, texts):
        return self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

    def predict(self, texts):
        inputs = self._tokenize(texts)
        with torch.no_grad():
            outputs = self.model(**inputs)
            preds = torch.argmax(outputs.logits, dim=1).tolist()
        return ["disinfo" if p == 1 else "real" for p in preds]

    def predict_proba(self, texts):
        inputs = self._tokenize(texts)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = softmax(outputs.logits, dim=1)
        return probs.cpu().tolist()
