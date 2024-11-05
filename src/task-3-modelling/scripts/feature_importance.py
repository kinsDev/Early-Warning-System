import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance

class FeatureImportanceAnalyzer:
    def __init__(self, config: Config):
        self.config = config

    def calculate_feature_importance(self, model: CrisisPredictor,
                                     X: np.ndarray, y: np.ndarray,
                                     feature_names: List[str]) -> pd.DataFrame:
        """Calculate feature importance using permutation importance."""
        result = permutation_importance(
            model, X, y,
            n_repeats=10,
            random_state=self.config.seed
        )

        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance_mean': result.importances_mean,
            'importance_std': result.importances_std
        })

        return importance_df.sort_values('importance_mean', ascending=False)

    def plot_feature_importance(self, importance_df: pd.DataFrame,
                                top_n: int = 20) -> None:
        """Plot feature importance."""
        plt.figure(figsize=(12, 8))
        importance_df.head(top_n).plot(
            x='feature',
            y='importance_mean',
            kind='bar',
            yerr='importance_std',
            capsize=5
        )
        plt.title('Top Feature Importance')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(self.config.output_path / 'feature_importance.png')
        plt.close()