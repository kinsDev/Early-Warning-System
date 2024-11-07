from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import pandas as pd

class DataPreprocessor:
    def __init__(self, config: Config):
        self.config = config
        self.numerical_scaler = StandardScaler()
        self.robust_scaler = RobustScaler()
        self.label_encoder = LabelEncoder()
        self.imputer = SimpleImputer(strategy='median')

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

    def process_data(self, df):
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