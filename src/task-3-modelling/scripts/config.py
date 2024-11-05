from pathlib import Path
import yaml

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.base_path = Path("D:/ACAPS/ACAPS/src/task-3-modelling/scripts/Combined_Dataset_Experimentation")
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

        # Target variables
        self.targets = {
            'severity_level': 'regression',
            'crisis_probability': 'binary',
            'humanitarian_conditions': 'ordinal',
            'escalation_risk': 'multiclass'
        }

        # Feature groups
        self.feature_groups = {
            'contextual': ['Country', 'Iso3', 'Region', 'Crisis Id', 'Crisis'],
            'socio_economic': ['Empowerment', 'Bti - Democracy Status', 'Trust In Society',
                               'Ethnic Fractionalisation', 'Gender Inequality', 'Income Gini Coefficient'],
            'crisis_impact': ['Conflict Intensity', 'Total Killed In All Crisis', 'Safety And Security'],
            'humanitarian': ['People In Need', 'People Displaced', 'People Affected'],
            'access': ['Humanitarian Access', 'Access Of Humanitarian Actors To Affected Populations']
        }