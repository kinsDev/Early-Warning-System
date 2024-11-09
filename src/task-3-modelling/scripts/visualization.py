from typing import Dict, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from config import Config
from .evaluation import ModelEvaluator

class Visualizer:
    def __init__(self, config: Config):
        self.config = config
        self.output_path = Path(config.output_path) / 'visualizations'
        self.output_path.mkdir(parents=True, exist_ok=True)
        plt.style.use('seaborn')

    def plot_results(self, dates: pd.Series,
                     predictions: Dict[str, Dict],
                     metrics: Dict[str, Dict]):
        """Generate comprehensive visualization of results."""
        for target in predictions:
            self._plot_target_predictions(dates, predictions[target], target)
            self._plot_uncertainty_analysis(dates, predictions[target], target)
            self._plot_feature_importance(target)
            self._plot_performance_metrics(metrics[target], target)

    def _plot_target_predictions(self, dates: pd.Series,
                                 prediction_data: Dict, target: str):
        """Plot predictions with uncertainty bands."""
        plt.figure(figsize=(15, 8))

        # Plot actual values
        plt.plot(dates, prediction_data['actual'],
                 label='Actual', color='blue', alpha=0.7)

        # Plot predictions with uncertainty
        plt.plot(dates, prediction_data['predictions'],
                 label='Predicted', color='red', alpha=0.7)

        # Add uncertainty bands
        lower = prediction_data['predictions'] - prediction_data['uncertainty']['std']
        upper = prediction_data['predictions'] + prediction_data['uncertainty']['std']
        plt.fill_between(dates, lower, upper, color='red', alpha=0.2,
                         label='Uncertainty (±1 std)')

        plt.title(f'Predictions for {target}')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_path / f'{target}_predictions.png')
        plt.close()

    def _plot_uncertainty_analysis(self, dates: pd.Series,
                                   prediction_data: Dict, target: str):
        """Plot uncertainty analysis."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))

        # Uncertainty over time
        ax1.plot(dates, prediction_data['uncertainty']['std'],
                 label='Uncertainty', color='purple')
        ax1.set_title(f'Uncertainty Evolution for {target}')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Uncertainty (std)')

        # Uncertainty distribution
        sns.histplot(prediction_data['uncertainty']['std'], ax=ax2,
                     bins=50, color='purple')
        ax2.set_title('Uncertainty Distribution')
        ax2.set_xlabel('Uncertainty Value')

        plt.tight_layout()
        plt.savefig(self.output_path / f'{target}_uncertainty.png')
        plt.close()

    def _plot_feature_importance(self, target: str):
        """Plot feature importance analysis."""
        importance_data = pd.read_csv(
            self.config.model_path / f'feature_importance_{target}.csv'
        )

        plt.figure(figsize=(12, 8))
        sns.barplot(data=importance_data.head(20),
                    x='importance', y='feature', palette='viridis')
        plt.title(f'Top 20 Important Features for {target}')
        plt.tight_layout()
        plt.savefig(self.output_path / f'{target}_feature_importance.png')
        plt.close()

    def _plot_performance_metrics(self, metrics: Dict, target: str):
        """Plot performance metrics."""
        plt.figure(figsize=(10, 6))

        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())

        plt.bar(metric_names, metric_values, color='teal')
        plt.title(f'Performance Metrics for {target}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_path / f'{target}_metrics.png')
        plt.close()

    def plot_training_history(self, history: Dict):
        """Plot training history."""
        plt.figure(figsize=(15, 8))

        for metric in history:
            if metric.startswith('train_'):
                val_metric = f'val_{metric[6:]}'
                plt.plot(history[metric], label=f'Training {metric[6:]}')
                plt.plot(history[val_metric], label=f'Validation {metric[6:]}')

        plt.title('Training History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.output_path / 'training_history.png')
        plt.close()
