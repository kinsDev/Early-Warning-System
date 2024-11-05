# data_loader.py
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import logging

class DataLoader:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def load_data(self) -> pd.DataFrame:
        """Load the combined dataset."""
        try:
            df = pd.read_csv(self.config.data_path)
            self.logger.info(f"Successfully loaded data from {self.config.data_path}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def split_temporal(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data temporally for training and testing."""
        # Sort by date
        df['date'] = pd.to_datetime(df['YYYY_MM'], format='%Y_%m')
        df = df.sort_values('date')

        # Calculate split point
        split_idx = int(len(df) * (1 - self.config.test_size))

        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]

        return train_df, test_df