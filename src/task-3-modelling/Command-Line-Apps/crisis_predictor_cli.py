# Main imports for the CLI application
import click
import torch
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add project root to Python path for module imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from lstm_predictor import LSTMPredictor

class CrisisPredictorCLI:
    """Main class for Crisis Prediction Command Line Interface"""
    def __init__(self):
        # Initialize paths for model and data
        self.model_path = Path(__file__).parent.parent / "models" / "lstm_crisis_severity_predictor_20241116_092126.pt"
        self.data_path = Path(__file__).parent.parent / "scripts" / "Combined_Dataset_Experimentation" / "combined_data.csv"

        print(f"Loading model from: {self.model_path}")
        self.model_state = torch.load(self.model_path)
        self.model = self._load_model()
        self.feature_names = self.model_state['feature_names']
        self.scaler = self.model_state['scaler']
        self.historical_data = pd.read_csv(self.data_path)

        # Define severity level classifications with corresponding colors
        self.severity_levels = {
            1: {"label": "Minimal", "color": "green"},
            2: {"label": "Moderate", "color": "yellow"},
            3: {"label": "Severe", "color": "orange"},
            4: {"label": "Critical", "color": "red"},
            5: {"label": "Catastrophic", "color": "bright_red"}
        }

    def _load_model(self):
        """Load and initialize the LSTM model with saved weights and architecture"""
        model = LSTMPredictor(
            input_dim=self.model_state['model_architecture']['input_dim'],
            hidden_dim=self.model_state['model_architecture']['hidden_dim'],
            output_dim=self.model_state['model_architecture']['output_dim'],
            forecast_horizon=3,
            n_layers=2,
            dropout=0.2
        )
        model.load_state_dict(self.model_state['model_state_dict'])
        model.eval()
        return model

    def get_country_crises(self, country):
        """Retrieve and analyze historical crisis data for a specific country
        Returns aggregated statistics including severity metrics and frequency"""
        country_data = self.historical_data[self.historical_data['Country'] == country]
        crises = country_data.groupby('Crisis').agg({
            'Inform Severity Index': ['mean', 'max', 'min'],
            'YYYY_MM': 'count'
        }).reset_index()
        crises.columns = ['Crisis', 'Avg Severity', 'Max Severity', 'Min Severity', 'Frequency']
        return crises

    def predict_crisis_severity(self, country, crisis_type, date=None):
        """Generate 3-month crisis severity predictions for a specific country and crisis type"""
        sequence = self._prepare_sequence(country, crisis_type, date)
        with torch.no_grad():
            prediction = self.model(sequence)
        return self._format_prediction(prediction)

    def _prepare_sequence(self, country, crisis_type, date):
        """Prepare input sequence for the LSTM model using historical data
        Processes and scales the features for prediction"""
        if date is None:
            date = datetime.now()

        historical = self.historical_data[
            (self.historical_data['Country'] == country) &
            (self.historical_data['Crisis'] == crisis_type)
            ].sort_values('YYYY_MM').tail(30)

        feature_vector = historical[self.feature_names].values
        scaled_features = self.scaler.transform(feature_vector)
        return torch.FloatTensor(scaled_features).unsqueeze(0)

    def _format_prediction(self, prediction):
        """Format model predictions into human-readable results
        Includes severity indices, confidence scores, and risk levels"""
        prediction = prediction.numpy().squeeze()
        results = {}
        for i in range(3):
            severity_index = prediction[i, 0]
            confidence = 1 - np.std(prediction[i]) / (np.mean(prediction[i]) + 1e-6)
            risk_level = self._get_risk_level(severity_index)

            month = (datetime.now() + timedelta(days=30*(i+1))).strftime('%Y-%m')
            results[month] = {
                'severity_index': float(severity_index),
                'confidence': float(confidence),
                'risk_level': risk_level,
                'color': self.severity_levels[risk_level]['color'],
                'label': self.severity_levels[risk_level]['label']
            }
        return results

    def _get_risk_level(self, severity_index):
        """Map severity index to corresponding risk level using predefined thresholds"""
        thresholds = [1.5, 2.5, 3.5, 4.5]
        for level, threshold in enumerate(thresholds, 1):
            if severity_index < threshold:
                return level
        return 5

@click.group()
def cli():
    """ACAPS Crisis Severity Prediction Tool"""
    pass

@cli.command()
@click.option('--country', prompt='Enter country name')
def list_crises(country):
    """Command to list and analyze historical crises for a specified country"""
    predictor = CrisisPredictorCLI()
    crises = predictor.get_country_crises(country)

    click.echo(f"\nHistorical Crisis Analysis for {country}")
    click.echo("-" * 50)
    for _, crisis in crises.iterrows():
        click.echo(f"\nCrisis: {crisis['Crisis']}")
        click.echo(f"Average Severity: {crisis['Avg Severity']:.2f}")
        click.echo(f"Severity Range: {crisis['Min Severity']:.2f} - {crisis['Max Severity']:.2f}")
        click.echo(f"Frequency: {crisis['Frequency']} occurrences")

@cli.command()
@click.option('--country', prompt='Enter country name')
@click.option('--crisis', prompt='Enter crisis type')
@click.option('--date', default=None, help='Start date (YYYY-MM-DD)')
def predict(country, crisis, date):
    """Command to generate and display 3-month crisis severity predictions"""
    predictor = CrisisPredictorCLI()
    predictions = predictor.predict_crisis_severity(country, crisis, date)

    click.echo(f"\nCrisis Severity Predictions for {country} - {crisis}")
    click.echo("-" * 50)
    for month, pred in predictions.items():
        click.secho(f"\n{month}:", fg=pred['color'])
        click.secho(
            f"Severity Index: {pred['severity_index']:.2f} ({pred['label']})",
            fg=pred['color']
        )
        click.echo(f"Confidence: {pred['confidence']:.2%}")

@cli.command()
@click.option('--region', default=None, help='Specific region to analyze')
@click.option('--min-severity', default=None, type=float, help='Filter by minimum severity index')
@click.option('--sort-by', type=click.Choice(['severity', 'crises']), default='severity', help='Sort regions by severity or number of crises')
@click.option('--detailed', is_flag=True, help='Show detailed crisis breakdown for each region')
def analyze_regions(region, min_severity, sort_by, detailed):
    """Command to analyze and display crisis patterns by region"""
    predictor = CrisisPredictorCLI()
    regions = [region] if region else predictor.historical_data['Region'].unique()

    click.echo("\nRegional Crisis Analysis")
    click.echo("-" * 50)

    region_stats = []
    for region in regions:
        region_data = predictor.historical_data[predictor.historical_data['Region'] == region]
        avg_severity = region_data['Inform Severity Index'].mean()
        active_crises = len(region_data['Crisis'].unique())

        if min_severity and avg_severity < min_severity:
            continue

        region_stats.append({
            'region': region,
            'avg_severity': avg_severity,
            'active_crises': active_crises,
            'data': region_data if detailed else None
        })

    # Sort results based on user preference
    region_stats.sort(key=lambda x: x['avg_severity' if sort_by == 'severity' else 'active_crises'], reverse=True)

    # Display results
    for stat in region_stats:
        click.echo(f"\nRegion: {stat['region']}")
        click.echo(f"Average Severity: {stat['avg_severity']:.2f}")
        click.echo(f"Active Crises: {stat['active_crises']}")

        if detailed:
            click.echo("\nCrisis Breakdown:")
            for crisis in stat['data']['Crisis'].unique():
                crisis_severity = stat['data'][stat['data']['Crisis'] == crisis]['Inform Severity Index'].mean()
                click.echo(f"- {crisis}: {crisis_severity:.2f}")

if __name__ == '__main__':
    cli()
