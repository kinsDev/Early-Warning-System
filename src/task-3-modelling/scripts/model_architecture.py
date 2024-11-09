from typing import Dict
from config import Config
import torch
import torch.nn as nn
from lightgbm import LGBMRegressor, LGBMClassifier
from catboost import CatBoostRegressor, CatBoostClassifier
from prophet import Prophet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class CrisisPredictor:
    def __init__(self, config: Config):
        self.config = config
        self.models = self._initialize_models()
        self.meta_model = self._create_meta_model()

    def _initialize_models(self) -> Dict:
        models = {}
        for target, specs in self.config.targets.items():
            if specs['type'] == 'regression':
                models[target] = {
                    'lightgbm': LGBMRegressor(n_estimators=1000, learning_rate=0.01),
                    'catboost': CatBoostRegressor(iterations=1000, verbose=False),
                    'prophet': Prophet(yearly_seasonality=True),
                    'lstm': self._create_lstm_model(len(specs['columns']))
                }
            else:  # multiclass
                models[target] = {
                    'lightgbm': LGBMClassifier(n_estimators=1000, learning_rate=0.01),
                    'catboost': CatBoostClassifier(iterations=1000, verbose=False)
                }
        return models

    def _create_lstm_model(self, output_dim):
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(30, len(self.config.feature_groups))),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(output_dim)
        ])
        model.compile(optimizer='adam',
                      loss='mse' if output_dim == 1 else 'categorical_crossentropy')
        return model

    def _create_meta_model(self):
        return nn.Sequential(
            nn.Linear(self._calculate_meta_input_size(), 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, self._calculate_meta_output_size())
        )

    def _calculate_meta_input_size(self):
        # Calculate based on number of base models and their outputs
        return sum(len(models) * len(self.config.targets[target]['columns'])
                   for target, models in self.models.items())

    def _calculate_meta_output_size(self):
        # Calculate total number of target variables
        return sum(len(specs['columns']) for specs in self.config.targets.values())

    def forward(self, x: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        base_predictions = {}
        for target, models in self.models.items():
            target_preds = []
            for model_name, model in models.items():
                if model_name == 'prophet':
                    # Special handling for Prophet
                    continue
                pred = model.predict(x[target])
                target_preds.append(torch.tensor(pred).float())
            base_predictions[target] = torch.stack(target_preds).mean(dim=0)

        # Combine predictions using meta-model
        combined_predictions = torch.cat([pred for pred in base_predictions.values()], dim=1)
        meta_output = self.meta_model(combined_predictions)

        return {
            'final_predictions': meta_output,
            'base_predictions': base_predictions
        }