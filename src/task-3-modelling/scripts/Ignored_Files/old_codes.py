# model_architecture.py
from typing import Dict
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputClassifier

class CrisisPredictor(nn.Module):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

        # Base models for different targets
        self.models = {
            'severity_level': GradientBoostingRegressor(),
            'crisis_probability': RandomForestClassifier(),
            'humanitarian_conditions': MultiOutputClassifier(RandomForestClassifier()),
            'escalation_risk': RandomForestClassifier()
        }

        # Meta-model combining predictions
        self.meta_model = nn.Sequential(
            nn.Linear(len(self.models) * 4, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 4)  # Final output dimension
        )

    def forward(self, x: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        # Get predictions from base models
        base_predictions = {}
        for target, model in self.models.items():
            base_predictions[target] = model.predict(x[target])

        # Combine predictions using meta-model
        combined_predictions = torch.cat([
            torch.tensor(pred).float() for pred in base_predictions.values()
        ], dim=1)

        meta_output = self.meta_model(combined_predictions)

        return {
            'final_predictions': meta_output,
            'base_predictions': base_predictions
        }

# feature_engineering.py
from typing import List, Dict
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoModel
import torch

class FeatureEngineer:
    def __init__(self, config: Config):
        self.config = config
        self.text_model = AutoModel.from_pretrained('bert-base-uncased')
        self.tfidf = TfidfVectorizer(max_features=100)

    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create temporal features from date information."""
        df = df.copy()

        # Extract temporal components
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter

        # Create rolling features
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        windows = [3, 6, 12]

        for col in numerical_cols:
            for window in windows:
                df[f'{col}_rolling_mean_{window}m'] = df.groupby('Crisis Id')[col].rolling(window=window).mean().reset_index(0, drop=True)
                df[f'{col}_rolling_std_{window}m'] = df.groupby('Crisis Id')[col].rolling(window=window).std().reset_index(0, drop=True)

        return df

    def extract_text_features(self, texts: pd.Series) -> np.ndarray:
        """Extract features from text using BERT embeddings and TF-IDF."""
        # BERT embeddings
        encodings = self.preprocessor.preprocess_text(texts)
        with torch.no_grad():
            outputs = self.text_model(**encodings)
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()

        # TF-IDF features
        tfidf_features = self.tfidf.fit_transform(texts).toarray()

        # Combine features
        return np.hstack([embeddings, tfidf_features])

# preprocessing.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from transformers import AutoTokenizer
import torch

class Preprocessor:
    def __init__(self, config: Config):
        self.config = config
        self.scalers = {}
        self.label_encoders = {}
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

    def preprocess_numerical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess numerical features."""
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns

        for col in numerical_cols:
            if col not in self.scalers:
                self.scalers[col] = StandardScaler()

            df[col] = self.scalers[col].fit_transform(df[[col]])

        return df

    def preprocess_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess categorical features."""
        categorical_cols = df.select_dtypes(include=['object']).columns

        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()

            df[col] = self.label_encoders[col].fit_transform(df[col])

        return df

    def preprocess_text(self, texts: pd.Series) -> torch.Tensor:
        """Preprocess text data using BERT tokenizer."""
        encodings = self.tokenizer(
            texts.tolist(),
            truncation=True,
            padding=True,
            max_length=self.config.max_sequence_length,
            return_tensors='pt'
        )

        return encodings

# feature_importance.py
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


# main.py
import logging
import argparse
from pathlib import Path

def setup_logging(config: Config) -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.output_path / 'training.log'),
            logging.StreamHandler()
        ]
    )

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Crisis Prediction System')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--mode', type=str, choices=['train', 'evaluate', 'predict'],
                        required=True, help='Operation mode')
    args = parser.parse_args()

    # Initialize configuration
    config = Config(args.config)
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # Initialize components
    data_loader = DataLoader(config)
    preprocessor = Preprocessor(config)
    feature_engineer = FeatureEngineer(config)
    model = CrisisPredictor(config)
    trainer = ModelTrainer(config, model)
    evaluator = ModelEvaluator(config)

    if args.mode == 'train':
        # Training workflow
        logger.info("Starting training workflow")

        # Load and preprocess data
        df = data_loader.load_data()
        train_df, test_df = data_loader.split_temporal(df)

        # Preprocess and engineer features
        train_data = preprocessor.preprocess_all(train_df)
        train_data = feature_engineer.engineer_features(train_data)

        # Train model
        history = trainer.train_model(train_data)

        # Save model
        persistence = ModelPersistence(config)
        metadata = {
            'training_history': history,
            'feature_columns': train_data.columns.tolist(),
            'training_date': pd.Timestamp.now().isoformat()
        }
        persistence.save_model(model, metadata, 'v1.0')

    elif args.mode == 'evaluate':
        # Evaluation workflow
        logger.info("Starting evaluation workflow")

        # Load test data and model
        persistence = ModelPersistence(config)
        model, metadata = persistence.load_model('v1.0')

        df = data_loader.load_data()
        _, test_df = data_loader.split_temporal(df)

        # Preprocess test data
        test_data = preprocessor.preprocess_all(test_df)
        test_data = feature_engineer.engineer_features(test_data)

        # Evaluate model
        metrics = evaluator.evaluate_model(model, test_data)
        logger.info(f"Evaluation metrics: {metrics}")

        # Generate visualizations
        visualizer = Visualizer(config)
        for target in config.targets:
            visualizer.plot_predictions_over_time(
                test_df['date'],
                metrics[target]['predictions'],
                metrics[target]['uncertainties'],
                test_data[target],
                target
            )

    elif args.mode == 'predict':
        # Prediction workflow
        logger.info("Starting prediction workflow")

        # Load model and make predictions
        persistence = ModelPersistence(config)
        model, _ = persistence.load_model('v1.0')

        # Load and preprocess new data
        df = data_loader.load_data()
        data = preprocessor.preprocess_all(df)
        data = feature_engineer.engineer_features(data)

        # Generate predictions with uncertainty
        uncertainty_estimator = UncertaintyEstimator(config)
        predictions, uncertainties = uncertainty_estimator.monte_carlo_dropout(
            model, data
        )

        # Save predictions
        results = pd.DataFrame({
            'date': df['date'],
            'predictions': predictions,
            'uncertainty': uncertainties
        })
        results.to_csv(config.output_path / 'predictions.csv', index=False)
        logger.info("Predictions saved to predictions.csv")

if __name__ == "__main__":
    main()