from typing import List, Dict
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoModel
import torch

class FeatureEngineer:
    def __init__(self, config: Config):
        self.config = config
        self.text_model = AutoModel.from_pretrained('bert-base-uncased')
        self.tfidf = TfidfVectorizer(max_features=100)

    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create temporal features from date information."""
        df = df.copy()

        # Extract temporal components
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter

        # Create rolling features
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        windows = [3, 6, 12]

        for col in numerical_cols:
            for window in windows:
                df[f'{col}_rolling_mean_{window}m'] = df.groupby('Crisis Id')[col].rolling(window=window).mean().reset_index(0, drop=True)
                df[f'{col}_rolling_std_{window}m'] = df.groupby('Crisis Id')[col].rolling(window=window).std().reset_index(0, drop=True)

        return df

    def extract_text_features(self, texts: pd.Series) -> np.ndarray:
        """Extract features from text using BERT embeddings and TF-IDF."""
        # BERT embeddings
        encodings = self.preprocessor.preprocess_text(texts)
        with torch.no_grad():
            outputs = self.text_model(**encodings)
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()

        # TF-IDF features
        tfidf_features = self.tfidf.fit_transform(texts).toarray()

        # Combine features
        return np.hstack([embeddings, tfidf_features])