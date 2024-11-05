import torch
from torch.utils.data import DataLoader
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
from typing import Dict, List
import logging

class ModelTrainer:
    def __init__(self, config: Config, model: CrisisPredictor):
        self.config = config
        self.model = model
        self.logger = logging.getLogger(__name__)

    def train_model(self, train_data: Dict[str, torch.Tensor],
                    val_data: Dict[str, torch.Tensor],
                    epochs: int = 100) -> Dict[str, List[float]]:
        """Train the crisis prediction model."""
        optimizer = torch.optim.Adam(self.model.parameters())
        criterion = nn.MSELoss()

        history = {
            'train_loss': [],
            'val_loss': []
        }

        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0

            for batch in DataLoader(train_data, batch_size=32, shuffle=True):
                optimizer.zero_grad()
                outputs = self.model(batch)
                loss = criterion(outputs['final_predictions'], batch['targets'])
                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            # Validation
            self.model.eval()
            val_loss = 0

            with torch.no_grad():
                for batch in DataLoader(val_data, batch_size=32):
                    outputs = self.model(batch)
                    loss = criterion(outputs['final_predictions'], batch['targets'])
                    val_loss += loss.item()

            # Log metrics
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)

            if (epoch + 1) % 10 == 0:
                self.logger.info(f"Epoch {epoch+1}/{epochs}: "
                                 f"Train Loss = {train_loss:.4f}, "
                                 f"Val Loss = {val_loss:.4f}")

        return history