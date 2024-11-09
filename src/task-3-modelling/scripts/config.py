from pathlib import Path
import yaml

class Config:
    def __init__(self, config_path=None):
        # Base paths setup
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.models_dir = self.base_dir / 'models'
        self.results_dir = self.base_dir / 'results'

        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)

        # Load config file
        config_path = config_path or (self.base_dir / 'scripts' / 'config.yaml')
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Model parameters
        self.seed = 42
        self.test_size = 0.2
        self.cv_folds = 5
        self.max_sequence_length = 512

        # Model-specific parameters
        self.model_params = self.config['model_params']

        # Target variables
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

        # Feature groups
        self.feature_groups = {
            'temporal_context': self.config['features']['core_contextual'],
            'geographical_context': self.config['features']['core_contextual'],
            'socio_economic_indicators': self.config['features']['socio_economic'],
            'governance_indicators': self.config['features']['governance_indicators'],
            'crisis_impact_metrics': self.config['features']['crisis_impact'],
            'humanitarian_conditions': self.config['features']['humanitarian_conditions'],
            'access_constraints': self.config['features']['access_constraints']
        }

    @property
    def data_path(self):
        return self.data_dir / "combined_data.csv"

    @property
    def model_path(self):
        return self.models_dir

    @property
    def output_path(self):
        return self.results_dir
