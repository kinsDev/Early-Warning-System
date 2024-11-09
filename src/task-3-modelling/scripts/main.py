import logging
import argparse
from pathlib import Path
import pandas as pd
from .config import Config
from .feature_engineering import FeatureEngineering
from .preprocessing import DataPreprocessor
from .feature_importance import FeatureSelector
from .model_architecture import CrisisPredictor

def setup_logging(config: Config) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.output_path / 'training.log'),
            logging.StreamHandler()
        ]
    )

def prepare_model_specific_data(config: Config, logger: logging.Logger):
    data_loader = DataLoader(config)
    df = data_loader.load_data()
    train_df, test_df = data_loader.split_temporal(df)

    feature_engineer = FeatureEngineering(config)
    preprocessor = DataPreprocessor(config)

    # Process data for each model type
    train_processed = {
        'base': preprocessor.process_data(feature_engineer.process_features(train_df)['base']),
        'lstm': preprocessor._prepare_sequences(feature_engineer.process_features(train_df)['lstm']),
        'prophet': preprocessor._prepare_prophet_data(feature_engineer.process_features(train_df)['prophet'])
    }

    return train_processed, test_df

def select_model_features(processed_data: dict, config: Config):
    feature_selector = FeatureSelector(config)
    selected_features = {}

    for model_type, data in processed_data.items():
        X = data.drop(columns=[col for target in config.targets.values()
                               for col in target['columns']])
        y = {target: data[specs['columns']]
             for target, specs in config.targets.items()}

        selected_features[model_type] = feature_selector.select_features(X, y)

    return selected_features

def train_models(processed_data: dict, selected_features: dict, config: Config):
    models = {}
    trainer = ModelTrainer(config)

    for model_type, features in selected_features.items():
        model = CrisisPredictor(config)
        data = processed_data[model_type]

        for target, target_features in features.items():
            X = data[target_features]
            y = data[config.targets[target]['columns']]
            models[f"{model_type}_{target}"] = trainer.train_model(model, X, y)

    return models

def train_meta_model(models: dict, processed_data: dict, config: Config):
    meta_trainer = MetaModelTrainer(config)
    meta_model = meta_trainer.train(models, processed_data)
    return meta_model

def train_pipeline(config: Config, logger: logging.Logger):
    logger.info("Starting training pipeline")

    # Load and process data for all model types
    processed_data, test_df = prepare_model_specific_data(config, logger)

    # Feature selection for each model type
    selected_features = select_model_features(processed_data, config)

    # Train individual models
    models = train_models(processed_data, selected_features, config)

    # Train meta-model
    meta_model = train_meta_model(models, processed_data, config)

    # Save models and metadata
    persistence = ModelPersistence(config)
    metadata = {
        'selected_features': selected_features,
        'training_date': pd.Timestamp.now().isoformat(),
        'model_types': list(processed_data.keys())
    }
    persistence.save_models(models, meta_model, metadata, 'v1.0')

    return models, meta_model

def evaluate_pipeline(config: Config, logger: logging.Logger):
    logger.info("Starting evaluation pipeline")

    # Load models and metadata
    persistence = ModelPersistence(config)
    models, meta_model, metadata = persistence.load_models('v1.0')

    # Prepare test data
    _, test_df = prepare_model_specific_data(config, logger)

    # Evaluate models
    evaluator = ModelEvaluator(config)
    uncertainty_estimator = UncertaintyEstimator(config)

    results = evaluator.evaluate_ensemble(models, meta_model, test_df)
    uncertainties = uncertainty_estimator.estimate_ensemble_uncertainty(
        models, meta_model, test_df
    )

    # Visualize results
    visualizer = Visualizer(config)
    visualizer.plot_ensemble_results(test_df['date'], results, uncertainties)

    return results, uncertainties

def main():
    parser = argparse.ArgumentParser(description='Crisis Prediction System')
    parser.add_argument('--config', type=str, default='config.yaml')
    parser.add_argument('--mode', type=str, choices=['train', 'evaluate', 'predict'])
    args = parser.parse_args()

    config = Config(args.config)
    setup_logging(config)
    logger = logging.getLogger(__name__)

    if args.mode == 'train':
        models, meta_model = train_pipeline(config, logger)
    elif args.mode == 'evaluate':
        results, uncertainties = evaluate_pipeline(config, logger)
        logger.info(f"Evaluation results: {results}")
    elif args.mode == 'predict':
        # Implement prediction pipeline
        pass

if __name__ == "__main__":
    main()