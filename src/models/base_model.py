from abc import ABC, abstractmethod

class BaseDisinfoModel(ABC):
    @abstractmethod
    def fit(self, X, y):
        """Train the model."""
        pass

    @abstractmethod
    def predict(self, X):
        """Predict labels."""
        pass

    @abstractmethod
    def predict_proba(self, X):
        """Return confidence scores or probabilities."""
        pass
