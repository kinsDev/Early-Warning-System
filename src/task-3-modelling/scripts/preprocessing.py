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