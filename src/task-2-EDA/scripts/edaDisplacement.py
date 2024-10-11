import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import geopandas as gpd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import os
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class HumanitarianCrisisAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.df_cleaned = None
        self.file_name = os.path.splitext(os.path.basename(file_path))[0]
        self.output_dir = os.path.join('output', self.file_name)
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        try:
            self.df = pd.read_csv(self.file_path, parse_dates=False)
            print(f"Data loaded successfully. Shape: {self.df.shape}")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def identify_columns(self):
        self.date_columns = [col for col in self.df.columns if 'date' in col.lower()]
        self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = self.df.select_dtypes(include=['object']).columns.tolist()

        self.displacement_column = next((col for col in self.df.columns if 'figure' in col.lower() or 'displaced' in col.lower()), None)
        self.lat_column = next((col for col in self.df.columns if 'latitude' in col.lower() or 'lat' in col.lower()), None)
        self.lon_column = next((col for col in self.df.columns if 'longitude' in col.lower() or 'lon' in col.lower()), None)
        self.country_column = next((col for col in self.df.columns if 'country' in col.lower()), None)
        self.description_column = next((col for col in self.df.columns if 'description' in col.lower()), None)

        print(f"Identified columns:\nDate columns: {self.date_columns}\nNumeric columns: {self.numeric_columns}\n"
              f"Categorical columns: {self.categorical_columns}\nDisplacement column: {self.displacement_column}\n"
              f"Latitude column: {self.lat_column}\nLongitude column: {self.lon_column}\n"
              f"Country column: {self.country_column}\nDescription column: {self.description_column}")

    def clean_data(self):
        df = self.df.copy()

        # Convert date columns
        for col in self.date_columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                print(f"Converted {col} to datetime. Null values: {df[col].isnull().sum()}")
            except Exception as e:
                print(f"Error converting {col} to datetime: {e}")
                if col in self.date_columns:
                    self.date_columns.remove(col)

        # Handle numeric columns
        for col in self.numeric_columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"Converted {col} to numeric. Null values: {df[col].isnull().sum()}")
            except Exception as e:
                print(f"Error converting {col} to numeric: {e}")
                if col in self.numeric_columns:
                    self.numeric_columns.remove(col)

        # Handle categorical columns
        for col in self.categorical_columns:
            df[col] = df[col].fillna('Unknown')
            print(f"Filled null values in {col} with 'Unknown'")

        # Remove entirely empty columns
        empty_cols = df.columns[df.isnull().all()].tolist()
        df = df.drop(columns=empty_cols)
        print(f"Removed empty columns: {empty_cols}")

        # Update column lists after removing empty columns
        self.numeric_columns = [col for col in self.numeric_columns if col not in empty_cols]
        self.categorical_columns = [col for col in self.categorical_columns if col not in empty_cols]

        # Impute missing numeric values
        if self.numeric_columns:
            imputer = SimpleImputer(strategy='mean')
            df[self.numeric_columns] = imputer.fit_transform(df[self.numeric_columns])
            print("Imputed missing numeric values with mean")

        # Remove rows with missing critical information
        if self.country_column and self.date_columns:
            before_drop = len(df)
            df.dropna(subset=[self.country_column] + self.date_columns, inplace=True)
            print(f"Removed {before_drop - len(df)} rows with missing critical information")

        self.df_cleaned = df
        print(f"Data cleaning completed. Final shape: {self.df_cleaned.shape}")
        
    def plot_displacement_trends(self):
        if not self.displacement_column or not self.date_columns:
            print("Unable to plot displacement trends: missing required columns.")
            return

        plt.figure(figsize=(15, 8))
        for date_col in self.date_columns:
            try:
                if self.df_cleaned[date_col].dtype != 'datetime64[ns]':
                    print(f"Skipping {date_col} as it's not a datetime column.")
                    continue
                df_temp = self.df_cleaned.set_index(date_col)[self.displacement_column].resample('W').sum()
                plt.plot(df_temp.index, df_temp.values, label=date_col)
                print(f"Plotted displacement trend for {date_col}")
            except Exception as e:
                print(f"Error plotting {date_col}: {e}")

        plt.title('Weekly Displacement Trends')
        plt.xlabel('Date')
        plt.ylabel('Number of Displaced People')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'weekly_displacement_trends.png'))
        plt.close()
        print("Displacement trends plot saved")

    def analyze_spatial_patterns(self):
        if not self.lat_column or not self.lon_column or not self.displacement_column:
            print("Unable to analyze spatial patterns: missing required columns.")
            return

        try:
            # Convert latitude and longitude to numeric
            self.df_cleaned[self.lat_column] = pd.to_numeric(self.df_cleaned[self.lat_column], errors='coerce')
            self.df_cleaned[self.lon_column] = pd.to_numeric(self.df_cleaned[self.lon_column], errors='coerce')
            
            # Remove rows with invalid lat/lon
            valid_coords = self.df_cleaned[self.lat_column].notna() & self.df_cleaned[self.lon_column].notna()
            df_spatial = self.df_cleaned[valid_coords]
            
            if len(df_spatial) == 0:
                print("No valid coordinates for spatial analysis.")
                return

            gdf = gpd.GeoDataFrame(
                df_spatial,
                geometry=gpd.points_from_xy(df_spatial[self.lon_column], df_spatial[self.lat_column])
            )
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

            fig, ax = plt.subplots(figsize=(15, 10))
            world.plot(ax=ax, alpha=0.4, color='grey')
            gdf.plot(ax=ax, markersize=gdf[self.displacement_column]/gdf[self.displacement_column].max()*100,
                    alpha=0.5, color='red')
            plt.title('Spatial Distribution of Displacement Events')
            plt.savefig(os.path.join(self.output_dir, 'spatial_distribution.png'))
            plt.close()
            print("Spatial distribution plot saved")
        except Exception as e:
            print(f"Error in spatial analysis: {e}")

    def analyze_displacement_causes(self):
        cause_column = next((col for col in ['type', 'category', 'subcategory'] if col in self.df_cleaned.columns), None)
        if not cause_column:
            print("Unable to analyze displacement causes: missing cause column.")
            return

        cause_counts = self.df_cleaned[cause_column].value_counts()
        plt.figure(figsize=(12, 6))
        cause_counts.plot(kind='bar')
        plt.title('Displacement Causes')
        plt.xlabel('Cause')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'displacement_causes.png'))
        plt.close()
        print("Displacement causes plot saved")

    def perform_correlation_analysis(self):
        if len(self.numeric_columns) < 2:
            print("Unable to perform correlation analysis: not enough numeric columns.")
            return

        corr_matrix = self.df_cleaned[self.numeric_columns].corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
        plt.title('Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'correlation_heatmap.png'))
        plt.close()
        print("Correlation heatmap saved")

    def analyze_text_data(self):
        if not self.description_column:
            print("Unable to analyze text data: missing description column.")
            return

        text = ' '.join(self.df_cleaned[self.description_column].dropna().astype(str))
        words = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_words))
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud of Displacement Descriptions')
        plt.savefig(os.path.join(self.output_dir, 'word_cloud.png'))
        plt.close()
        print("Word cloud saved")

    def perform_pca_analysis(self):
        if len(self.numeric_columns) < 2:
            print("Unable to perform PCA: not enough numeric columns.")
            return

        try:
            # Remove rows with NaN values specifically for PCA
            df_pca = self.df_cleaned[self.numeric_columns].dropna()
            
            if len(df_pca) == 0:
                print("No data remaining after removing NaNs. Unable to perform PCA.")
                return

            X = StandardScaler().fit_transform(df_pca)
            pca = PCA(n_components=2)
            principal_components = pca.fit_transform(X)

            plt.figure(figsize=(10, 8))
            plt.scatter(principal_components[:, 0], principal_components[:, 1], alpha=0.5)
            plt.title('PCA of Numeric Features')
            plt.xlabel('First Principal Component')
            plt.ylabel('Second Principal Component')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'pca_analysis.png'))
            plt.close()
            print("PCA analysis plot saved")
        except Exception as e:
            print(f"Error in PCA analysis: {e}")

    def prepare_for_modeling(self):
        df = self.df_cleaned.copy()

        # Create time-based features
        if self.date_columns:
            for date_col in self.date_columns:
                if df[date_col].dtype == 'datetime64[ns]':
                    df[f'{date_col}_month'] = df[date_col].dt.month
                    df[f'{date_col}_day_of_week'] = df[date_col].dt.dayofweek
                    df[f'{date_col}_is_weekend'] = df[f'{date_col}_day_of_week'].isin([5, 6]).astype(int)
                    print(f"Time-based features created for {date_col}")
                else:
                    print(f"Skipping time-based feature creation for {date_col} as it's not a datetime column")

        # Encode categorical variables
        df_encoded = pd.get_dummies(df, columns=self.categorical_columns)
        print("Categorical variables encoded")

        # Scale numeric features
        scaler = StandardScaler()
        df_encoded[self.numeric_columns] = scaler.fit_transform(df_encoded[self.numeric_columns])
        print("Numeric features scaled")

        return df_encoded

    def run_analysis(self):
        if not self.load_data():
            return

        self.identify_columns()
        self.clean_data()

        print("\nBasic Statistics:")
        print(self.df_cleaned[self.numeric_columns].describe())

        print("\nMissing Values After Cleaning:")
        print(self.df_cleaned.isnull().sum())

        self.plot_displacement_trends()
        self.analyze_spatial_patterns()
        self.analyze_displacement_causes()
        self.perform_correlation_analysis()
        self.analyze_text_data()
        self.perform_pca_analysis()

        self.df_cleaned.to_csv(os.path.join(self.output_dir, 'cleaned_data.csv'), index=False)
        print(f"Cleaned data saved to {os.path.join(self.output_dir, 'cleaned_data.csv')}")

        df_model_ready = self.prepare_for_modeling()
        df_model_ready.to_csv(os.path.join(self.output_dir, 'model_ready_data.csv'), index=False)
        print(f"Data prepared for modeling and saved to {os.path.join(self.output_dir, 'model_ready_data.csv')}")

        print("Analysis completed. Check the 'output' directory for results.")

if __name__ == "__main__":
    file_path = input("Enter the path to your CSV file: ")
    analysis = HumanitarianCrisisAnalysis(file_path)
    analysis.run_analysis()
