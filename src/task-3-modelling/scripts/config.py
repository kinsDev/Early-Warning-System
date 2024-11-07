from pathlib import Path
import yaml

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        # Base paths
        self.base_path = Path("scripts/Combined_Dataset_Experimentation")
        self.data_path = self.base_path / "combined_data.csv"
        self.model_path = self.base_path / "models"
        self.output_path = self.base_path / "outputs"

        # Create directories if they don't exist
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Model parameters
        self.seed = 42
        self.test_size = 0.2
        self.cv_folds = 5
        self.max_sequence_length = 512  # For text processing

        # Model-specific parameters
        self.model_params = {
            'lstm': {
                'sequence_length': 30,
                'hidden_size': 50,
                'num_layers': 2
            },
            'prophet': {
                'seasonality_mode': 'multiplicative',
                'yearly_seasonality': True
            },
            'lightgbm': {
                'n_estimators': 1000,
                'learning_rate': 0.01
            },
            'catboost': {
                'iterations': 1000,
                'verbose': False
            }
        }

        # Target variables with their corresponding columns
        self.targets = {
            'severity_level': {
                'columns': ['Inform Severity Index', 'Inform Severity Category'],
                'type': 'regression'
            },
            'crisis_probability': {
                'columns': ['Concentration Of Conditions', 'Complexity Of The Crisis', 'Updated_Score'],
                'type': 'multiclass'
            },
            'escalation_risk': {
                'columns': ['Trend (Last 3 Months)', 'Impact Of The Crisis'],
                'type': 'multiclass'
            }
        }

        # Feature groups - organized by category
        self.feature_groups = {
            'temporal_context': [
                'YYYY_MM'
            ],
            'geographical_context': [
                'Country',
                'Iso3',
                'Region',
                'Crisis Id',
                'Crisis'
            ],
            'socio_economic_indicators': [
                'Empowerment',
                'Bti - Democracy Status',
                'Trust In Society',
                'Ethnic Fractionalisation',
                'Gender Inequality',
                'Income Gini Coefficient',
                'Corruption Perception'
            ],
            'governance_indicators': [
                'Rule Of Law (Wgi)',
                'Rule Of Law (Bti)',
                'Rule Of Law',
                'Freedom In The World'
            ],
            'crisis_impact_metrics': [
                'Conflict Intensity',
                'Total Killed In All Crisis',
                'Safety And Security',
                'People In Need',
                'Buildings Damaged [Helper 8]',
                'Buildings Damaged [Figure]',
                'Buildings Damaged [Date]',
                'Economic Losses [Helper 11]',
                'Economic Losses [Figure]',
                'Economic Losses [Date]'
            ],
            'humanitarian_conditions': [
                '# Of People Facing Minimal Humanitarian Needs (Level 1)',
                '# Of People Facing Stressed Humanitarian Conditions And Needs (Level 2)',
                '# Of People Facing Moderate Humanitarian Conditions And Needs (Level 3)',
                '# Of People Facing Severe Humanitarian Conditions And Needs (Level 4)',
                '# Of People Facing Extreme Humanitarian Conditions And Needs (Level 5)',
                '% Of People In None/Minimal Conditions - Level 1',
                '% Of People In Stressed Conditions - Level 2',
                '% Of People In Moderate Conditions - Level 3',
                '% Of People Severe Conditions - Level 4',
                '% Of People Extreme Conditions - Level 5',
                'People Displaced',
                'People Affected'
            ],
            'access_constraints': [
                'Humanitarian Access',
                'Access Of Humanitarian Actors To Affected Populations',
                'Ongoing Insecurity/Hostilities Affecting Humanitarian Assistance',
                'Physical And Security Constraints',
                'Access Of People In Need To Aid'
            ]
        }
