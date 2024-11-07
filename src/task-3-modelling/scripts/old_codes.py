# model_architecture.py
from typing import Dict
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputClassifier

class CrisisPredictor(nn.Module):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

        # Base models for different targets
        self.models = {
            'severity_level': GradientBoostingRegressor(),
            'crisis_probability': RandomForestClassifier(),
            'humanitarian_conditions': MultiOutputClassifier(RandomForestClassifier()),
            'escalation_risk': RandomForestClassifier()
        }

        # Meta-model combining predictions
        self.meta_model = nn.Sequential(
            nn.Linear(len(self.models) * 4, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 4)  # Final output dimension
        )

    def forward(self, x: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        # Get predictions from base models
        base_predictions = {}
        for target, model in self.models.items():
            base_predictions[target] = model.predict(x[target])

        # Combine predictions using meta-model
        combined_predictions = torch.cat([
            torch.tensor(pred).float() for pred in base_predictions.values()
        ], dim=1)

        meta_output = self.meta_model(combined_predictions)

        return {
            'final_predictions': meta_output,
            'base_predictions': base_predictions
        }

# feature_engineering.py
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

# preprocessing.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from transformers import AutoTokenizer
import torch

class Preprocessor:
    def __init__(self, config: Config):
        self.config = config
        self.scalers = {}
        self.label_encoders = {}
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

    def preprocess_numerical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess numerical features."""
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns

        for col in numerical_cols:
            if col not in self.scalers:
                self.scalers[col] = StandardScaler()

            df[col] = self.scalers[col].fit_transform(df[[col]])

        return df

    def preprocess_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess categorical features."""
        categorical_cols = df.select_dtypes(include=['object']).columns

        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()

            df[col] = self.label_encoders[col].fit_transform(df[col])

        return df

    def preprocess_text(self, texts: pd.Series) -> torch.Tensor:
        """Preprocess text data using BERT tokenizer."""
        encodings = self.tokenizer(
            texts.tolist(),
            truncation=True,
            padding=True,
            max_length=self.config.max_sequence_length,
            return_tensors='pt'
        )

        return encodings