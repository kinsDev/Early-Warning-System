from pathlib import Path
import yaml

class Config:
    def __init__(self, config_path=None):
        # Base paths setup
        self.base_dir = Path(__file__).parent.parent

        # Set up directories
        self.data_dir = self.base_dir / 'scripts' / 'Combined_Dataset_Experimentation'
        self.models_dir = self.base_dir / 'models'
        self.results_dir = self.base_dir / 'results'

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
        
        self.validate_paths()

    @property
    def learning_rate(self):
        return self.config['model_params']['learning_rate']

    def validate_paths(self):
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        if not Path(self.data_path).exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

    @property
    def data_path(self):
        return self.base_dir / 'scripts' / 'Combined_Dataset_Experimentation' / 'combined_data.csv'

    @property
    def model_path(self):
        return self.models_dir

    @property
    def output_path(self):
        return self.results_dir