from typing import Dict, Tuple, List
from pathlib import Path
import torch
import joblib
import json
import pandas as pd
from datetime import datetime
from .config import Config
from .model_architecture import CrisisPredictor
import logging
logging.basicConfig(level=logging.INFO)


class ModelPersistence:
    def __init__(self, config: Config):
        self.config = config
        self.model_dir = config.models_dir 
        self.model_dir.mkdir(exist_ok=True)

    def save_model(self, model: CrisisPredictor, metadata: Dict, version: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = self.model_dir / f"model_{version}_{timestamp}.joblib"
        
        logging.info(f"Saving model version {version} to {model_path}")

        # Save comprehensive model state
        model_state = {
            'model': model,
            'model_state': model.state_dict(),
            'base_models': {
                target: {name: model.serialize()
                         for name, model in models.items()}
                for target, models in model.models.items()
            },
            'meta_model': model.meta_model.state_dict(),
            'metadata': {
                'timestamp': timestamp,
                'name': version,
                'save_date': datetime.now().isoformat(),
                'model_version': version,
                'config': self.config.__dict__,
                **metadata
            }
        }
        
        try:
            joblib.dump(model_state, model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to save model: {str(e)}")

        logging.info(f"Successfully saved model version {version}")

        # Save using joblib for better compression
        joblib.dump(model_state, f"{model_path}.joblib")

        # Save feature importance
        if 'feature_importance' in metadata:
            self._save_feature_importance(metadata['feature_importance'], version)

        return model_path

    def load_model(self, version: str) -> Tuple[CrisisPredictor, Dict]:
        model_files = list(self.model_dir.glob(f"model_{version}*.joblib"))
        if not model_files:
            raise FileNotFoundError(f"No model found for version {version}")
        
        latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
        model_state = joblib.load(latest_model)

        model = CrisisPredictor(self.config)
        model.load_state_dict(model_state['model_state'])

        # Load base models
        for target, models in model_state['base_models'].items():
            for name, state in models.items():
                model.models[target][name].deserialize(state)

        # Load meta model
        model.meta_model.load_state_dict(model_state['meta_model'])

        return model, model_state['metadata']

    def _save_feature_importance(self, importance_data: Dict, version: str):
        importance_path = self.model_dir / f'feature_importance_{version}.csv'
        importance_df = pd.DataFrame(importance_data)
        importance_df.to_csv(importance_path, index=True)

    def list_available_models(self) -> List[str]:
        return sorted(list(set([
            f.stem.split('_')[1]  # Extract version from filename
            for f in self.model_dir.glob('model_*.joblib')
        ])))

    def get_model_metadata(self, version: str) -> Dict:
        model_files = list(self.model_dir.glob(f"model_{version}*.joblib"))
        if not model_files:
            raise FileNotFoundError(f"No model found for version {version}")
        
        latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
        model_state = joblib.load(latest_model)
        return model_state['metadata']

    def export_model_summary(self, version: str):
        metadata = self.get_model_metadata(version)
        summary_path = self.model_dir / f'model_summary_{version}.json'

        summary = {
            'version': version,
            'save_date': metadata['save_date'],
            'performance_metrics': metadata.get('performance_metrics', {}),
            'feature_importance': metadata.get('feature_importance', {}),
            'config_settings': metadata['config']
        }

        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=4)
