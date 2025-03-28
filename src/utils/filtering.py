# src/utils/filtering.py

import pandas as pd
from datetime import datetime, timedelta, time as dtime

class InferenceFilter:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def filter_by_date(self, days_back: int) -> 'InferenceFilter':
        time_threshold = pd.Timestamp.combine(
            pd.Timestamp.now().date() - pd.Timedelta(days=days_back),
            dtime.min
        )
        self.df = self.df[self.df["datetime"] >= time_threshold]
        return self

    def filter_by_type(self, content_type: str) -> 'InferenceFilter':
        if content_type != "All":
            self.df = self.df[self.df["type"] == content_type]
        return self

    def filter_by_flagged(self, flagged_only: bool) -> 'InferenceFilter':
        if flagged_only:
            self.df = self.df[self.df["flagged"] == True]
        return self

    def filter_by_confidence(self, min_confidence: float) -> 'InferenceFilter':
        self.df = self.df[self.df["confidence"] >= min_confidence]
        return self

    def get_filtered(self) -> pd.DataFrame:
        return self.df
