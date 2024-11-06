import torch
import numpy as np
from typing import Dict, Tuple

class UncertaintyEstimator:
    def __init__(self, config: Config):
        self.config = config

    def monte_carlo_dropout(self, model: CrisisPredictor,
                            input_data: Dict[str, torch.Tensor],
                            n_iterations: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Estimate prediction uncertainty using MC Dropout."""
        model.train()  # Enable dropout
        predictions = []

        with torch.no_grad():
            for _ in range(n_iterations):
                output = model(input_data)
                predictions.append(output['final_predictions'].numpy())

        # Calculate mean and standard deviation
        predictions = np.stack(predictions)
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)

        return mean_pred, std_pred