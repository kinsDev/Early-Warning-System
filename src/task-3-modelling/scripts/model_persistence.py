from typing import Dict, Tuple, List
import torch
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class ModelPersistence:
    def __init__(self, config: Config):
        self.config = config
        self.model_path = Path(self.config.model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)

    def save_model(self, model: CrisisPredictor, metadata: Dict, version: str):
        """Save model state and metadata."""
        save_path = self.model_path / f'model_{version}'

        # Save model state
        torch.save({
            'model_state': model.state_dict(),
            'base_models': {
                target: {name: model.serialize()
                         for name, model in models.items()}
                for target, models in model.models.items()
            },
            'meta_model': model.meta_model.state_dict(),
            'metadata': {
                **metadata,
                'save_date': datetime.now().isoformat(),
                'model_version': version,
                'config': self.config.__dict__
            }
        }, save_path)

        # Save feature importance
        if 'feature_importance' in metadata:
            self._save_feature_importance(metadata['feature_importance'], version)

    def load_model(self, version: str) -> Tuple[CrisisPredictor, Dict]:
        """Load model state and metadata."""
        load_path = self.model_path / f'model_{version}'
        checkpoint = torch.load(load_path)

        model = CrisisPredictor(self.config)
        model.load_state_dict(checkpoint['model_state'])

        # Load base models
        for target, models in checkpoint['base_models'].items():
            for name, state in models.items():
                model.models[target][name].deserialize(state)

        # Load meta model
        model.meta_model.load_state_dict(checkpoint['meta_model'])

        return model, checkpoint['metadata']

    def _save_feature_importance(self, importance_data: Dict, version: str):
        """Save feature importance data."""
        importance_path = self.model_path / f'feature_importance_{version}.csv'
        importance_df = pd.DataFrame(importance_data)
        importance_df.to_csv(importance_path, index=True)

    def list_available_models(self) -> List[str]:
        """List all available model versions."""
        return [f.stem.replace('model_', '')
                for f in self.model_path.glob('model_*')]

    def get_model_metadata(self, version: str) -> Dict:
        """Get metadata for specific model version."""
        load_path = self.model_path / f'model_{version}'
        checkpoint = torch.load(load_path, map_location='cpu')
        return checkpoint['metadata']

    def export_model_summary(self, version: str):
        """Export model summary including architecture and performance."""
        metadata = self.get_model_metadata(version)
        summary_path = self.model_path / f'model_summary_{version}.json'

        summary = {
            'version': version,
            'save_date': metadata['save_date'],
            'performance_metrics': metadata.get('performance_metrics', {}),
            'feature_importance': metadata.get('feature_importance', {}),
            'config_settings': metadata['config']
        }

        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=4)
