import torch
from pathlib import Path
import json
from typing import Dict, Any

class ModelPersistence:
    def __init__(self, config: Config):
        self.config = config

    def save_model(self, model: CrisisPredictor,
                   metadata: Dict[str, Any],
                   version: str) -> None:
        """Save model and associated metadata."""
        # Create version directory
        version_dir = self.config.model_path / version
        version_dir.mkdir(parents=True, exist_ok=True)

        # Save model state
        torch.save(model.state_dict(),
                   version_dir / 'model_state.pth')

        # Save metadata
        with open(version_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)

        # Save preprocessor states
        torch.save({
            'scalers': self.preprocessor.scalers,
            'label_encoders': self.preprocessor.label_encoders,
            'tokenizer': self.preprocessor.tokenizer
        }, version_dir / 'preprocessor_state.pth')

    def load_model(self, version: str) -> Tuple[CrisisPredictor, Dict[str, Any]]:
        """Load model and associated metadata."""
        version_dir = self.config.model_path / version

        # Load model
        model = CrisisPredictor(self.config)
        model.load_state_dict(torch.load(version_dir / 'model_state.pth'))

        # Load metadata
        with open(version_dir / 'metadata.json', 'r') as f:
            metadata = json.load(f)

        # Load preprocessor states
        preprocessor_state = torch.load(version_dir / 'preprocessor_state.pth')
        self.preprocessor.scalers = preprocessor_state['scalers']
        self.preprocessor.label_encoders = preprocessor_state['label_encoders']
        self.preprocessor.tokenizer = preprocessor_state['tokenizer']

        return model, metadata