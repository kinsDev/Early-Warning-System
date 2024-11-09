from typing import Dict, List
import pandas as pd
import numpy as np
from config import Config
import matplotlib.pyplot as plt
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from catboost import CatBoostRegressor, CatBoostClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from sklearn.inspection import permutation_importance
import torch

class FeatureSelector:
    def __init__(self, config: Config):
        self.config = config
        self.feature_importance = {}
        self.selected_features = {}

    def _calculate_base_model_importance(self, X: pd.DataFrame, y: pd.Series, target_type: str) -> Dict[str, pd.Series]:
        importances = {}

        # Mutual Information
        mi_func = mutual_info_regression if target_type == 'regression' else mutual_info_classif
        importances['mutual_info'] = pd.Series(mi_func(X, y), index=X.columns)

        # LightGBM
        lgb_model = LGBMRegressor(n_estimators=1000) if target_type == 'regression' else LGBMClassifier(n_estimators=1000)
        lgb_model.fit(X, y)
        importances['lightgbm'] = pd.Series(lgb_model.feature_importances_, index=X.columns)

        # CatBoost
        cat_model = CatBoostRegressor(iterations=1000) if target_type == 'regression' else CatBoostClassifier(iterations=1000)
        cat_model.fit(X, y, verbose=False)
        importances['catboost'] = pd.Series(cat_model.feature_importances_, index=X.columns)

        return importances

    def calculate_importance_by_type(self, X: pd.DataFrame, y: pd.Series, target_type: str) -> Dict[str, pd.Series]:
        importances = {}

        # Base models importance
        importances.update(self._calculate_base_model_importance(X, y, target_type))

        # Prophet-specific importance
        if target_type == 'regression':
            importances['prophet'] = self._calculate_prophet_importance(X, y)
            importances['lstm'] = self._calculate_lstm_importance(X, y)

        return importances

    def _calculate_prophet_importance(self, X: pd.DataFrame, y: pd.Series) -> pd.Series:
        temporal_importance = X.apply(lambda x: self._temporal_correlation(x, y))
        return temporal_importance

    def _temporal_correlation(self, series: pd.Series, target: pd.Series) -> float:
        return np.abs(np.corrcoef(series, target)[0, 1])

    def calculate_lstm_importance(self, X: pd.DataFrame, y: pd.Series) -> pd.Series:
        correlations = X.apply(lambda x: abs(x.corr(y)))
        return correlations

    def select_features(self, X: pd.DataFrame, y: Dict[str, pd.Series]) -> Dict[str, List[str]]:
        for target_name, specs in self.config.targets.items():
            target_values = y[target_name]
            target_type = specs['type']

            # Calculate importance for each model type
            model_importances = self.calculate_importance_by_type(X, target_values, target_type)

            # Combine importance scores with weighted ranking
            combined_importance = pd.DataFrame(model_importances).apply(lambda x: x.rank()).mean(axis=1)

            self.feature_importance[target_name] = {
                **model_importances,
                'combined': combined_importance
            }

            # Select top features based on combined importance
            self.selected_features[target_name] = combined_importance.nlargest(
                n=min(50, len(X.columns))
            ).index.tolist()

        return self.selected_features

    def plot_importance_analysis(self, target_name: str, top_n: int = 20):
        plt.figure(figsize=(20, 15))
        importance_data = self.feature_importance[target_name]

        n_plots = len(importance_data)
        fig, axes = plt.subplots(n_plots, 1, figsize=(15, 5*n_plots))
        fig.suptitle(f'Feature Importance Analysis for {target_name}')

        for (method, scores), ax in zip(importance_data.items(), axes):
            scores.nlargest(top_n).plot(kind='barh', ax=ax, title=f'{method.title()} Importance')
            ax.set_xlabel('Importance Score')

        plt.tight_layout()
        plt.savefig(self.config.output_path / f'feature_importance_{target_name}.png')
        plt.close()

    def generate_comprehensive_report(self):
        report_data = []
        for target_name, importances in self.feature_importance.items():
            target_type = self.config.targets[target_name]['type']
            self.plot_importance_analysis(target_name)

            for feature in self.selected_features[target_name]:
                feature_scores = {method: scores[feature]
                                  for method, scores in importances.items()}
                report_data.append({
                    'target': target_name,
                    'target_type': target_type,
                    'feature': feature,
                    **feature_scores
                })

        report = pd.DataFrame(report_data)
        report.to_csv(self.config.output_path / 'feature_importance_report.csv')
        return report