import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Dict, List
from config import Config

class FeatureEngineering:
    def __init__(self, config: Config):
        self.config = config
        self.scaler = StandardScaler()

    def _process_base_features(self, df: pd.DataFrame) -> pd.DataFrame:
        self.df = df.copy()
        self.df = self.create_temporal_features()
        self.df = self.create_geographical_features()
        self.df = self.create_socioeconomic_features()
        self.df = self.create_governance_features()
        self.df = self.create_crisis_impact_features()
        self.df = self.create_humanitarian_features()
        self.df = self.create_access_constraint_features()

        important_indicators = [
            'crisis_severity_index',
            'humanitarian_severity_index',
            'access_constraint_index'
        ]
        self.df = self.create_lag_features(important_indicators)

        return self.df

    def _create_temporal_sequences(self, df: pd.DataFrame) -> pd.DataFrame:
        sequence_length = self.config.model_params['lstm']['sequence_length']
        sequences = {}

        for col in df.select_dtypes(include=[np.number]).columns:
            sequences[col] = self._create_sliding_window(df[col], sequence_length)

        return pd.DataFrame(sequences)

    def _create_sliding_window(self, series: pd.Series, window_size: int) -> np.ndarray:
        data = series.values
        windows = []
        for i in range(len(data) - window_size + 1):
            windows.append(data[i:i + window_size])
        return np.array(windows)

    def _format_temporal_data(self, df: pd.DataFrame) -> pd.DataFrame:
        prophet_df = df.copy()
        prophet_df['ds'] = pd.to_datetime(df['YYYY_MM'], format='%Y_%m')

        # Additional Prophet-specific formatting
        for col in df.select_dtypes(include=[np.number]).columns:
            prophet_df[f'regressor_{col}'] = df[col]

        return prophet_df

    # Existing feature creation methods remain unchanged
    def create_temporal_features(self):
        self.df['date'] = pd.to_datetime(self.df['YYYY_MM'], format='%Y_%m')
        self.df['year'] = self.df['date'].dt.year
        self.df['month'] = self.df['date'].dt.month
        self.df['quarter'] = self.df['date'].dt.quarter
        self.df['month_sin'] = np.sin(2 * np.pi * self.df['month']/12)
        self.df['month_cos'] = np.cos(2 * np.pi * self.df['month']/12)
        return self.df

    def create_geographical_features(self):
        self.df['region_encoded'] = pd.Categorical(self.df['Region']).codes
        self.df['country_encoded'] = pd.Categorical(self.df['Country']).codes
        return self.df

    def create_socioeconomic_features(self):
        socio_columns = self.config.feature_groups['socio_economic_indicators']
        self.df['socio_economic_index'] = self.df[socio_columns].mean(axis=1)
        self.df['inequality_index'] = self.df[['Gender Inequality', 'Income Gini Coefficient']].mean(axis=1)
        return self.df

    def create_governance_features(self):
        gov_columns = self.config.feature_groups['governance_indicators']
        self.df['governance_index'] = self.df[gov_columns].mean(axis=1)
        self.df['rule_of_law_composite'] = self.df[['Rule Of Law (Wgi)', 'Rule Of Law (Bti)']].mean(axis=1)
        return self.df

    def create_crisis_impact_features(self):
        impact_columns = self.config.feature_groups['crisis_impact_metrics']
        self.df['crisis_severity_index'] = self.df[impact_columns].mean(axis=1)
        self.df['economic_impact_ratio'] = self.df['Economic Losses [Figure]'] / self.df['People Affected']
        return self.df

    def create_humanitarian_features(self):
        humanitarian_columns = self.config.feature_groups['humanitarian_conditions']
        self.df['humanitarian_severity_index'] = self.df[humanitarian_columns].mean(axis=1)
        self.df['displacement_ratio'] = self.df['People Displaced'] / self.df['People Affected']
        return self.df

    def create_access_constraint_features(self):
        access_columns = self.config.feature_groups['access_constraints']
        self.df['access_constraint_index'] = self.df[access_columns].mean(axis=1)
        self.df['physical_security_constraint'] = self.df[['Physical And Security Constraints',
                                                           'Ongoing Insecurity/Hostilities Affecting Humanitarian Assistance']].mean(axis=1)
        return self.df

    def create_lag_features(self, columns_to_lag, lag_periods=[1, 2, 3]):
        for col in columns_to_lag:
            for lag in lag_periods:
                self.df[f'{col}_lag_{lag}'] = self.df.groupby('Iso3')[col].shift(lag)
        return self.df

    def process_features(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        base_features = self._process_base_features(df)

        return {
            'base': base_features,
            'lstm': self._prepare_lstm_features(base_features),
            'prophet': self._prepare_prophet_features(base_features)
        }
