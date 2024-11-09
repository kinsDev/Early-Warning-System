from typing import List, Tuple, Dict
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from config import Config

class DataLoader:
    def __init__(self, config: Config):
        self.config = config

    def load_data(self) -> pd.DataFrame:
        """Load and perform initial data preparation."""
        df = pd.read_csv(self.config.data_path)
        df['date'] = pd.to_datetime(df['YYYY_MM'], format='%Y_%m')
        return df

    def split_temporal(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data temporally for time series prediction."""
        split_date = df['date'].max() - pd.DateOffset(months=self.config.test_size * len(df['date'].unique()))
        train_df = df[df['date'] <= split_date]
        test_df = df[df['date'] > split_date]
        return train_df, test_df

    def prepare_features_targets(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Prepare features and targets from the dataframe."""
        # Prepare targets
        targets = {}
        target_columns = []

        for target_name, target_info in self.config.targets.items():
            target_cols = target_info['columns']
            targets[target_name] = df[target_cols]
            target_columns.extend(target_cols)

        # Prepare features (excluding target columns)
        features = df.drop(columns=target_columns)

        return features, targets

    def create_sequences(self, df: pd.DataFrame, sequence_length: int = 30) -> np.ndarray:
        """Create sequences for LSTM processing."""
        data = df.values
        sequences = []

        for i in range(len(data) - sequence_length + 1):
            sequences.append(data[i:i + sequence_length])

        return np.array(sequences)

    def get_feature_groups(self) -> Dict[str, pd.DataFrame]:
        """Get features organized by feature groups defined in config."""
        df = self.load_data()
        feature_groups = {}

        for group_name, features in self.config.feature_groups.items():
            feature_groups[group_name] = df[features]

        return feature_groups

    def get_cv_splits(self, df: pd.DataFrame, n_splits: int = None) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Generate cross-validation splits respecting temporal order."""
        if n_splits is None:
            n_splits = self.config.cv_folds

        unique_dates = df['date'].unique()
        splits = []

        for i in range(n_splits):
            split_idx = int(len(unique_dates) * (1 - self.config.test_size))
            train_dates = unique_dates[:split_idx]
            test_dates = unique_dates[split_idx:]

            train_df = df[df['date'].isin(train_dates)]
            test_df = df[df['date'].isin(test_dates)]

            splits.append((train_df, test_df))
            unique_dates = unique_dates[len(unique_dates)//n_splits:]

        return splits