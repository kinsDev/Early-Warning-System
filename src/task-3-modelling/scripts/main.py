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