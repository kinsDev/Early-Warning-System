LSTM-based Crisis Severity Prediction Model
===========================================

Please Note
-------------------
1. The latest model's Jupyter Notebook is this one here ```task-3-modelling/notebooks/lstm_crisis_prediction_model.ipynb```
2. On the models folder, this is the most preferred model path: ```lstm_crisis_severity_predictor_20241116_092126.pt```
3. You can simply find the scripts that power or suppport the Jupyter Notebook specified above on the scripts folder ```src/task-3-modelling/scripts```
4. The command line apps directory on this part here:```src/task-3-modelling/Command-Line-Apps``` is still under development!

Table of Contents
-----------------

- [LSTM-based Crisis Severity Prediction Model](#lstm-based-crisis-severity-prediction-model)
  - [Please Note](#please-note)
  - [Table of Contents](#table-of-contents)
  - [Project Description](#project-description)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Scripts Overview](#scripts-overview)
  - [Model Storage Guidelines](#model-storage-guidelines)
  - [Project Structure](#project-structure)
  - [License](#license)
  - [Acknowledgements](#acknowledgements)


Project Description
-------------------

This project implements an LSTM-based model for predicting crisis severity levels over a 3-month horizon. The model leverages 166 features, including humanitarian indicators, socio-economic factors, and crisis metrics, to forecast both the **Inform Severity Index** and **Severity Category**.

There are some unused classes in the scripts, kindly ignore them as they were used for experimentation purposes when building the initial ensemble models.

The current model path under this notebook: ```task-3-modelling/notebooks/lstm_crisis_prediction_model.ipynb```

Installation
------------
Clone the repository. git clone [repository-url]  

Usage
-----

1. Run the Jupyter Notebook called "lstm_crisis_prediction.ipynb", it has the model trained to make 3 months future crisis predictions
   - Run the Notebook Cells Sequentially for:
     - Data Preparation 
     - Model Training 
     - Evaluation 
     - Results Visualization
2. Ensure you have all the necessary libraries installed. All that info is on the Notebook for easier usage.
3. Ensure you have all the necessary scripts in the "scripts" folder, they have classes and functions that are used in the Notebook.

Scripts Overview
----------------

*   **\_\_init\_\_.py** - Project initialization and setup.

*   **config.py** - Configuration management.

    *   Config class: Handles model parameters and paths.

*   **data\_loader.py** - Data loading and preprocessing.

    *   DataLoader class: Handles data loading and temporal splitting.

*   **feature\_engineering.py** - Feature creation and transformation.

    *   FeatureEngineering class: Creates temporal, geographical, and crisis-specific features.

*   **model\_architecture.py** - LSTM model definition.

    *   CrisisPredictor class: Implements the LSTM architecture.

*   **training.py** - Model training functionality.

    *   ModelTrainer class: Handles training loops and optimization.

*   **evaluation.py** - Model evaluation.

    *   ModelEvaluator class: Implements evaluation metrics and analysis.

*   **visualization.py** - Results visualization.

    *   Visualizer class: Creates performance plots and prediction visualizations.

*   **main.py** - Main execution flow.


Model Storage Guidelines
------------------------

> **Important**: When saving models and results, prefix filenames with your initials:
```
models/
├── KK_lstm_model_YYYYMMDD.pt
└── KK_evaluation_results.png

results/
├── KK_metrics_summary.csv
└── KK_predictions.csv

```

Project Structure
----------------
```
task-3-modelling/
├── .gitignore
├── README.md
├── requirements.txt
|
├── models/
│   ├── lstm_crisis_severity_predictor_YYYYMMDD_HHMMSS.pt
│   └── lstm_model_YYYYMMDD_HHMMSS.pt
|
├── notebooks/
│   ├── lstm_crisis_prediction_model.ipynb
│   ├── model_training_pipeline.ipynb
|
├── results/
│   └── visualizations/
│       ├── 3months_crisisseverity_predictor_eval.png
│       └── evaluation_results.png
|
├── scripts/
│   ├── __init__.py
│   ├── config.py
│   ├── config.yaml
│   ├── data_loader.py
│   ├── evaluation.py
│   ├── feature_engineering.py
│   ├── feature_importance.py
│   ├── main.py
│   ├── model_architecture.py
│   ├── model_persistence.py
│   ├── preprocessing.py
│   ├── training.py
│   ├── uncertainty.py
│   └── visualization.py
|
└── Combined_Dataset_Experimentation/
    ├── combined_data.csv
    └── combined_data_exploration.ipynb


```


License
-------

\[License information\]

Author
Kinsley Kaimenyi Gitonga


Acknowledgements
----------------

*   ACAPS for providing the humanitarian data.

*   European Commission for providing structured humanitarian data.

