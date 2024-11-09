from typing import Dict, List
import numpy as np
import pandas as pd
import torch
from config import Config
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)

class ModelEvaluator:
    def __init__(self, config: Config):
        self.config = config

    def evaluate_predictions(self, y_true: Dict[str, pd.DataFrame],
                             y_pred: Dict[str, torch.Tensor]) -> Dict[str, Dict]:
        """Evaluate predictions for all targets."""
        metrics = {}
        for target, specs in self.config.targets.items():
            if specs['type'] == 'regression':
                metrics[target] = self._evaluate_regression(y_true[target], y_pred[target])
            else:
                metrics[target] = self._evaluate_classification(y_true[target], y_pred[target])
        return metrics

    def _evaluate_regression(self, y_true: pd.DataFrame, y_pred: torch.Tensor) -> Dict:
        """Calculate regression metrics."""
        y_pred_np = y_pred.numpy() if isinstance(y_pred, torch.Tensor) else y_pred
        return {
            'mse': mean_squared_error(y_true, y_pred_np),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred_np)),
            'mae': mean_absolute_error(y_true, y_pred_np),
            'r2': r2_score(y_true, y_pred_np)
        }

    def _evaluate_classification(self, y_true: pd.DataFrame, y_pred: torch.Tensor) -> Dict:
        """Calculate classification metrics."""
        y_pred_np = y_pred.numpy() if isinstance(y_pred, torch.Tensor) else y_pred
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred_np, average='weighted')

        return {
            'accuracy': accuracy_score(y_true, y_pred_np),
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': confusion_matrix(y_true, y_pred_np).tolist()
        }

    def evaluate_feature_importance(self, feature_importance: Dict[str, pd.Series]) -> Dict:
        """Evaluate feature importance metrics."""
        importance_metrics = {}
        for target, importance in feature_importance.items():
            importance_metrics[target] = {
                'top_features': importance.nlargest(10).index.tolist(),
                'importance_scores': importance.nlargest(10).tolist(),
                'feature_stability': self._calculate_feature_stability(importance)
            }
        return importance_metrics

    def _calculate_feature_stability(self, importance: pd.Series) -> float:
        """Calculate stability score for feature importance."""
        normalized_scores = importance / importance.sum()
        return -np.sum(normalized_scores * np.log(normalized_scores + 1e-10))

    def evaluate_uncertainty(self, predictions: Dict[str, np.ndarray]) -> Dict:
        """Evaluate uncertainty estimates."""
        uncertainty_metrics = {}
        for target, preds in predictions.items():
            uncertainty_metrics[target] = {
                'mean_uncertainty': np.mean(np.std(preds, axis=0)),
                'max_uncertainty': np.max(np.std(preds, axis=0)),
                'uncertainty_distribution': np.percentile(np.std(preds, axis=0),
                                                          [25, 50, 75]).tolist()
            }
        return uncertainty_metrics

    def generate_evaluation_report(self, metrics: Dict,
                                   feature_metrics: Dict,
                                   uncertainty_metrics: Dict) -> pd.DataFrame:
        """Generate comprehensive evaluation report."""
        report_data = []
        for target in metrics.keys():
            report_data.append({
                'target': target,
                'model_metrics': metrics[target],
                'feature_importance': feature_metrics[target],
                'uncertainty_metrics': uncertainty_metrics[target]
            })
        return pd.DataFrame(report_data)
