# This code contains the Feature selection and Importance Calculations: To be used at a later time.

from scripts.feature_engineering import FeatureEngineering
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from lightgbm import LGBMRegressor, LGBMClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import pandas as pd
import numpy as np
import re

def clean_feature_names(X):
    """
    Clean feature names to be compatible with LightGBM and ensure uniqueness.
    Handles special characters, spaces, and adds numeric suffixes for duplicates.
    """
    X = X.copy()

    def clean_name(name):
        name = str(name)
        name = re.sub(r'[^A-Za-z0-9]+', '_', name)
        name = name.strip('_')
        if not name[0].isalpha():
            name = 'f_' + name
        return name

    clean_columns = [clean_name(col) for col in X.columns]

    seen = {}
    unique_names = []
    for name in clean_columns:
        if name in seen:
            seen[name] += 1
            unique_names.append(f"{name}_{seen[name]}")
        else:
            seen[name] = 0
            unique_names.append(name)

    X.columns = unique_names
    return X

class FeatureSelector:
    def __init__(self, config):
        self.config = config

    def select_features(self, X, y):
        """Select features based on importance scores across multiple targets"""
        all_importances = {}

        for target_name, target_values in y.items():
            specs = self.config.targets[target_name]
            target_type = specs['type']

            model_importances = self.calculate_importance_by_type(X, target_values, target_type)
            combined_importance = pd.DataFrame(model_importances).apply(lambda x: x.rank()).mean(axis=1)
            all_importances[target_name] = combined_importance

        final_importance = pd.DataFrame(all_importances).mean(axis=1)
        n_features = self.config.feature_selection.get('n_features', 50)
        selected_features = final_importance.nlargest(n_features).index.tolist()

        return selected_features

    def calculate_importance_by_type(self, X, y, target_type):
        """Calculate feature importance using multiple methods"""
        importances = {}
        importances.update(self._calculate_base_model_importance(X, y, target_type))
        importances['lstm'] = self._calculate_lstm_importance(X, y)
        return importances

    def _calculate_base_model_importance(self, X, y, target_type):
        """Calculate importance using traditional ML models"""
        importances = {}

        mi_func = mutual_info_regression if target_type == 'regression' else mutual_info_classif
        importances['mutual_info'] = pd.Series(mi_func(X, y), index=X.columns)

        lgb_model = LGBMRegressor(n_estimators=100) if target_type == 'regression' else LGBMClassifier(n_estimators=100)
        lgb_model.fit(X, y)
        importances['lightgbm'] = pd.Series(lgb_model.feature_importances_, index=X.columns)

        return importances

    def _calculate_lstm_importance(self, X, y):
        """Calculate feature importance using LSTM-based approach"""
        X_reshaped = X.values.reshape((X.shape[0], 1, X.shape[1]))

        model = Sequential([
            LSTM(50, input_shape=(1, X.shape[1])),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        model.fit(X_reshaped, y, epochs=5, verbose=0)

        importances = []
        baseline_pred = model.predict(X_reshaped, verbose=0)

        for i in range(X.shape[1]):
            X_temp = X.copy()
            X_temp.iloc[:, i] = X_temp.iloc[:, i].mean()
            X_temp_reshaped = X_temp.values.reshape((X_temp.shape[0], 1, X_temp.shape[1]))
            new_pred = model.predict(X_temp_reshaped, verbose=0)
            importance = np.mean(np.abs(baseline_pred - new_pred))
            importances.append(importance)

        return pd.Series(importances, index=X.columns)
class CustomFeatureEngineering(FeatureEngineering):
    def __init__(self, config):
        super().__init__(config)
        self.label_encoders = {}
        self.null_values = ['x', 'X', 'Missing', 'missing', 'False', 'false', '-', 'NA', 'na', 'N/A', 'n/a']
        self.categorical_cols = ['Country', 'Iso3', 'Region', 'Crisis Id', 'Crisis']
        self.identifier_cols = [col for col in df.columns if any(x in col for x in ['Total population', 'Helper'])]

    def process_features(self, df: pd.DataFrame):
        df = df.copy()
        processed_df = df.copy()

        for group_name, features in self.config.feature_groups.items():
            processed_df = self._process_feature_group(processed_df, features, group_name)

        temporal_features = self._create_temporal_features(processed_df)
        encoded_features = self._encode_categorical_features(temporal_features)

        return {
            'base': processed_df,
            'temporal': temporal_features,
            'encoded': encoded_features,
            'lstm': self._prepare_lstm_features(encoded_features),
            'prophet': self._prepare_prophet_features(temporal_features)
        }

    def _process_feature_group(self, df, features, group_name):
        df = df.copy()

        for col in features:
            if col not in df.columns:
                continue

            if col in self.categorical_cols or col in self.identifier_cols:
                continue
            elif 'Date' in col:
                df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            elif col == 'YYYY_MM':
                df[col] = pd.to_datetime(df[col], format='%Y_%m', errors='coerce')
            else:
                df[col] = df[col].replace(self.null_values, 0)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)

        return df

    def _create_temporal_features(self, df):
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['YYYY_MM'], format='%Y_%m')
        df['year'] = df['datetime'].dt.year
        df['month'] = df['datetime'].dt.month
        df['quarter'] = df['datetime'].dt.quarter
        return df

    def _encode_categorical_features(self, df):
        df = df.copy()
        categorical_cols = self.categorical_cols + self.identifier_cols

        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
        return df

    def _prepare_lstm_features(self, df):
        df_lstm = df.copy()
        numeric_cols = df_lstm.select_dtypes(include=['float64', 'int64']).columns
        df_lstm = df_lstm[numeric_cols]
        return df_lstm

    def _prepare_prophet_features(self, df):
        df_prophet = df.copy()
        df_prophet['ds'] = df_prophet['datetime']
        return df_prophet

class CustomDataPreprocessor:
    def __init__(self, config):
        self.config = config
        self.numerical_imputer = SimpleImputer(strategy='constant', fill_value=0)
        self.categorical_imputer = SimpleImputer(strategy='constant', fill_value='missing')

    def process_data(self, data_dict):
        processed = {}
        for key, df in data_dict.items():
            if isinstance(df, pd.DataFrame):
                processed[key] = self.handle_missing_values(df)
        return processed

    def handle_missing_values(self, df):
        df = df.copy()

        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numerical_cols) > 0:
            df[numerical_cols] = self.numerical_imputer.fit_transform(df[numerical_cols])

        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            df[categorical_cols] = self.categorical_imputer.fit_transform(df[categorical_cols])

        return df
def process_features(df, config):
    feature_engineer = CustomFeatureEngineering(config)
    preprocessor = CustomDataPreprocessor(config)

    engineered_features = feature_engineer.process_features(df)
    processed_data = preprocessor.process_data(engineered_features)

    X = processed_data['encoded']

    datetime_cols = X.select_dtypes(include=['datetime64[ns]']).columns
    identifier_cols = feature_engineer.identifier_cols
    categorical_cols = feature_engineer.categorical_cols

    cols_to_exclude = list(datetime_cols) + identifier_cols + categorical_cols
    X_numeric = X.drop(columns=cols_to_exclude, errors='ignore')

    X_numeric = X_numeric.replace(['x', 'X', 'Missing', 'missing', 'False', 'false'], 0)
    X_numeric = X_numeric.apply(pd.to_numeric, errors='coerce')
    X_numeric = X_numeric.fillna(0)

    X_numeric = clean_feature_names(X_numeric)

    targets = {}
    for target_name, target_info in config.targets.items():
        target_cols = target_info['columns']
        target_values = processed_data['encoded'][target_cols[0]]
        targets[target_name] = pd.to_numeric(target_values.replace(['x', 'X'], 0), errors='coerce').fillna(0)

    feature_selector = FeatureSelector(config)
    selected_features = feature_selector.select_features(X_numeric, targets)

    return processed_data, selected_features

def detailed_inspection(processed_data):
    print("\nDetailed Data Processing Results:")
    print("-" * 50)

    for key, df in processed_data.items():
        print(f"\nDataset Type: {key}")
        print(f"Shape: {df.shape}")

        print("\nColumn Data Types:")
        for col in df.columns:
            print(f"{col}: {df[col].dtype}")

        null_counts = df.isnull().sum()
        if null_counts.any():
            print("\nColumns with null values:")
            print(null_counts[null_counts > 0])
        else:
            print("\nNo null values found")

        print("\nSample Data:")
        print(df.head())
        print("-" * 50)

# Run processing and inspection
train_processed, selected_features = process_features(train_df, config)
detailed_inspection(train_processed)
