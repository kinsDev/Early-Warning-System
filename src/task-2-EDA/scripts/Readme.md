# Scripts

- Please add all the scripts/notebook that is used for Data Analysis here only.

# edaDisplacement.py
- This script performs exploratory data analysis (EDA) on humanitarian crisis data provided in a CSV file. It generates visualizations and prepares the data for further modeling.

## Requirements

- Python 3.7+
- Required packages are listed in the `requirementsEdaDisplacement.txt` file. Install them using:
  ```bash
  pip install -r requirementsEdaDisplacement.txt
  ```

## Usage
- Place your CSV data file in the data/raw/ directory
- Run the script:
    ```bash
    python3 edaDisplacement.py 
    ```
- You will be prompted to enter the path to your CSV file.

## Data Storage
- The script creates an `output` directory (if it doesn't exist) where it stores the generated outputs:

### Output Directory Structure:
- **`output/`**
  - `cleaned_data.csv`:  The cleaned dataset after preprocessing.
  - `model_ready_data.csv`: Data prepared for machine learning modeling, including feature engineering and encoding.
  - `weekly_displacement_trends.png`:  Plot showing weekly trends of displacement.
  - `spatial_distribution.png`:  Map visualizing the spatial distribution of displacement events.
  - `displacement_causes.png`:  Bar chart displaying the counts of different displacement causes. 
  - `correlation_heatmap.png`: Heatmap showing correlations between numeric features.
  - `word_cloud.png`: Word cloud generated from the 'description' column (if available) to highlight common themes.
  - `pca_analysis.png`: Scatter plot showing the results of Principal Component Analysis (PCA) on the numeric features.

## Notes

- The script automatically attempts to identify relevant columns based on common column names. You might need to adjust the code if your column names are different.
- Make sure your data file is properly formatted as a CSV with appropriate headers.
- The script assumes that the data is related to humanitarian crises and displacement events. You may need to modify it for different types of data.
