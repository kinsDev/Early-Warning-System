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