from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import pandas as pd
from typing import Dict

class DataPreprocessor:
    def __init__(self, config: Config):
        self.config = config
        self.numerical_scaler = StandardScaler()
        self.robust_scaler = RobustScaler()
        self.label_encoder = LabelEncoder()
        self.imputer = SimpleImputer(strategy='median')

    def _process_base_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.handle_missing_values(df)

        for group, features in self.config.feature_groups.items():
            if group == 'temporal_context':
                df = self.process_temporal_features(df, features)
            elif group == 'geographical_context':
                df = self.process_geographical_features(df, features)
            elif group in ['socio_economic_indicators', 'governance_indicators']:
                df = self.process_indicator_features(df, features)
            else:
                df = self.process_numerical_features(df, features)

        return df

    def process_temporal_features(self, df, features):
        for feature in features:
            if feature == 'YYYY_MM':
                df[feature] = pd.to_datetime(df[feature], format='%Y_%m')
        return df

    def process_geographical_features(self, df, features):
        for feature in features:
            if df[feature].dtype == 'object':
                df[f'{feature}_encoded'] = self.label_encoder.fit_transform(df[feature])
        return df

    def process_numerical_features(self, df, features):
        numerical_features = df[features].select_dtypes(include=['float64', 'int64']).columns
        if len(numerical_features) > 0:
            df[numerical_features] = self.numerical_scaler.fit_transform(df[numerical_features])
        return df

    def process_indicator_features(self, df, features):
        if len(features) > 0:
            df[features] = self.robust_scaler.fit_transform(df[features].fillna(0))
        return df

    def handle_missing_values(self, df):
        numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns
        df[numerical_columns] = self.imputer.fit_transform(df[numerical_columns])

        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col] = df[col].fillna(df[col].mode().iloc[0])
        return df

    def _create_sliding_windows(self, df: pd.DataFrame, sequence_length: int) -> pd.DataFrame:
        sequences = []
        for group in df.groupby('Iso3'):
            country_data = group[1].sort_values('YYYY_MM')
            for i in range(len(country_data) - sequence_length + 1):
                sequence = country_data.iloc[i:i + sequence_length]
                sequences.append(sequence)
        return pd.concat(sequences, axis=0)

    def _prepare_sequences(self, df: pd.DataFrame) -> pd.DataFrame:
        sequence_length = self.config.model_params['lstm']['sequence_length']
        sequences = self._create_sliding_windows(df, sequence_length)
        return sequences

    def _prepare_prophet_data(self, df: pd.DataFrame) -> pd.DataFrame:
        prophet_df = df.copy()
        prophet_df['ds'] = pd.to_datetime(df['YYYY_MM'], format='%Y_%m')
        return prophet_df

    def process_data(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        base_processed = self._process_base_features(df)

        processed = {
            'base': base_processed,
            'lstm': self._prepare_sequences(base_processed),
            'prophet': self._prepare_prophet_data(base_processed)
        }
        return processed
