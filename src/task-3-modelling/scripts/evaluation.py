from sklearn.metrics import (
    mean_squared_error,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)
import numpy as np
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns

class ModelEvaluator:
    def __init__(self, config: Config):
        self.config = config

    def evaluate_model(self, model: CrisisPredictor,
                       test_data: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """Evaluate model performance on test data."""
        model.eval()
        metrics = {}

        with torch.no_grad():
            predictions = model(test_data)

            # Evaluate each target separately
            for target in self.config.targets:
                target_preds = predictions['base_predictions'][target]
                target_true = test_data[target]

                if self.config.targets[target] == 'regression':
                    metrics[target] = {
                        'mse': mean_squared_error(target_true, target_preds),
                        'rmse': np.sqrt(mean_squared_error(target_true, target_preds))
                    }
                else:
                    metrics[target] = {
                        'accuracy': accuracy_score(target_true, target_preds),
                        'precision_recall_f1': precision_recall_fscore_support(
                            target_true, target_preds, average='weighted'
                        )
                    }

        return metrics

    def plot_confusion_matrices(self, predictions: Dict[str, np.ndarray],
                                true_values: Dict[str, np.ndarray]) -> None:
        """Plot confusion matrices for classification targets."""
        for target in self.config.targets:
            if self.config.targets[target] != 'regression':
                plt.figure(figsize=(8, 6))
                cm = confusion_matrix(true_values[target], predictions[target])
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                plt.title(f'Confusion Matrix - {target}')
                plt.ylabel('True Label')
                plt.xlabel('Predicted Label')
                plt.savefig(self.config.output_path / f'confusion_matrix_{target}.png')
                plt.close()