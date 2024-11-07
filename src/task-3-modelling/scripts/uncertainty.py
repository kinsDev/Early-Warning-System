from typing import Dict, Tuple, List
import torch
import numpy as np
from collections import defaultdict

class UncertaintyEstimator:
    def __init__(self, config: Config):
        self.config = config

    def monte_carlo_dropout(self,
                            model: CrisisPredictor,
                            X: Dict[str, torch.Tensor],
                            n_iterations: int = 100) -> Tuple[Dict, Dict]:
        """Estimate prediction uncertainty using Monte Carlo Dropout."""
        predictions = defaultdict(list)
        model.train()  # Enable dropout

        with torch.no_grad():
            for _ in range(n_iterations):
                pred = model.forward(X)
                for target in pred:
                    predictions[target].append(pred[target].numpy())

        return self._calculate_uncertainty(predictions)

    def ensemble_uncertainty(self,
                             model: CrisisPredictor,
                             X: Dict[str, torch.Tensor]) -> Tuple[Dict, Dict]:
        """Estimate uncertainty using ensemble predictions."""
        predictions = defaultdict(list)
        model.eval()

        with torch.no_grad():
            for target, models in model.models.items():
                for base_model in models.values():
                    pred = base_model.predict(X[target])
                    predictions[target].append(pred)

        return self._calculate_uncertainty(predictions)

    def _calculate_uncertainty(self, predictions: Dict[str, List]) -> Tuple[Dict, Dict]:
        """Calculate mean predictions and uncertainty estimates."""
        mean_predictions = {}
        uncertainties = {}

        for target, preds in predictions.items():
            stacked_preds = np.stack(preds)
            mean_predictions[target] = np.mean(stacked_preds, axis=0)
            uncertainties[target] = {
                'std': np.std(stacked_preds, axis=0),
                'quantiles': np.percentile(stacked_preds, [2.5, 97.5], axis=0),
                'entropy': self._calculate_entropy(stacked_preds)
            }

        return mean_predictions, uncertainties

    def _calculate_entropy(self, predictions: np.ndarray) -> np.ndarray:
        """Calculate prediction entropy for classification tasks."""
        if len(predictions.shape) > 2:  # For classification tasks
            probs = np.mean(predictions, axis=0)
            return -np.sum(probs * np.log(probs + 1e-10), axis=-1)
        return np.zeros(predictions.shape[1])  # For regression tasks

    def calibration_metrics(self,
                            predictions: Dict[str, np.ndarray],
                            uncertainties: Dict[str, Dict],
                            y_true: Dict[str, np.ndarray]) -> Dict[str, Dict]:
        """Calculate uncertainty calibration metrics."""
        calibration = {}

        for target in predictions:
            pred = predictions[target]
            uncertainty = uncertainties[target]['std']
            true = y_true[target]

            calibration[target] = {
                'picp': self._calculate_picp(pred, uncertainty, true),
                'mpiw': self._calculate_mpiw(uncertainty),
                'confidence_correlation': np.corrcoef(uncertainty, np.abs(pred - true))[0, 1]
            }

        return calibration

    def _calculate_picp(self, pred: np.ndarray, uncertainty: np.ndarray,
                        true: np.ndarray) -> float:
        """Calculate Prediction Interval Coverage Probability."""
        lower = pred - 1.96 * uncertainty
        upper = pred + 1.96 * uncertainty
        return np.mean((true >= lower) & (true <= upper))

    def _calculate_mpiw(self, uncertainty: np.ndarray) -> float:
        """Calculate Mean Prediction Interval Width."""
        return np.mean(3.92 * uncertainty)  # 95% confidence interval width
