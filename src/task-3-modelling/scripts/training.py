from typing import Dict, List
import torch
import numpy as np
from collections import defaultdict
from tqdm import tqdm
import logging
from .config import Config

class ModelTrainer:
    def __init__(self, config: Config, model: CrisisPredictor):
        self.config = config
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )
        self.logger = logging.getLogger(__name__)

    def train_model(self, X: Dict[str, torch.Tensor], y: Dict[str, torch.Tensor]) -> Dict:
        """Train the model using the provided data."""
        history = defaultdict(list)
        best_loss = float('inf')

        for epoch in range(self.config.epochs):
            self.model.train()
            epoch_losses = self._train_epoch(X, y)

            # Validation step
            val_losses = self._validate(X, y)

            # Update learning rate
            self.scheduler.step(val_losses['total_loss'])

            # Log progress
            self._log_progress(epoch, epoch_losses, val_losses)

            # Save best model
            if val_losses['total_loss'] < best_loss:
                best_loss = val_losses['total_loss']
                self._save_checkpoint(epoch, best_loss)

            # Update history
            history = self._update_history(history, epoch_losses, val_losses)

        return history

    def _train_epoch(self, X: Dict[str, torch.Tensor], y: Dict[str, torch.Tensor]) -> Dict:
        """Train for one epoch."""
        self.optimizer.zero_grad()
        outputs = self.model.forward(X)
        losses = self._calculate_losses(outputs, y)

        losses['total_loss'].backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.grad_clip)
        self.optimizer.step()

        return {k: v.item() for k, v in losses.items()}

    def _validate(self, X: Dict[str, torch.Tensor], y: Dict[str, torch.Tensor]) -> Dict:
        """Perform validation."""
        self.model.eval()
        with torch.no_grad():
            outputs = self.model.forward(X)
            losses = self._calculate_losses(outputs, y)
        return {k: v.item() for k, v in losses.items()}

    def _calculate_losses(self, outputs: Dict[str, torch.Tensor],
                          targets: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Calculate losses for all targets."""
        losses = {}
        total_loss = 0

        for target_name, target_spec in self.config.targets.items():
            if target_spec['type'] == 'regression':
                loss = torch.nn.MSELoss()(outputs[target_name], targets[target_name])
            else:
                loss = torch.nn.CrossEntropyLoss()(outputs[target_name], targets[target_name])

            losses[f'{target_name}_loss'] = loss
            total_loss += target_spec.get('weight', 1.0) * loss

        losses['total_loss'] = total_loss
        return losses

    def _save_checkpoint(self, epoch: int, loss: float):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'loss': loss
        }
        torch.save(checkpoint, self.config.model_path / f'checkpoint_epoch_{epoch}.pt')

    def _log_progress(self, epoch: int, train_losses: Dict, val_losses: Dict):
        """Log training progress."""
        self.logger.info(
            f"Epoch {epoch}: Train Loss = {train_losses['total_loss']:.4f}, "
            f"Val Loss = {val_losses['total_loss']:.4f}"
        )

    def _update_history(self, history: Dict, train_losses: Dict, val_losses: Dict) -> Dict:
        """Update training history."""
        for k, v in train_losses.items():
            history[f'train_{k}'].append(v)
        for k, v in val_losses.items():
            history[f'val_{k}'].append(v)
        return history
