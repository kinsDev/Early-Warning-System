import pandas as pd
import requests
import io
import os
from datetime import datetime


# Function to combine 22 CSV files per month into one monthly file
def combine_monthly_data(base_url, start_date, end_date, files_per_month, output_dir):
    month_names = ["january", "february", "march", "april", "may", "june",
                   "july", "august", "september", "october", "november", "december"]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 13):
            month_name = month_names[month - 1]
            current_date = datetime(year, month, 1)

            # Only process months within the specified date range
            if current_date < start_date or current_date > end_date:
                continue

            monthly_data = []
            ref_columns = None
            inconsistent_files = []

            # Loop through all 22 files in the month
            for file_num in range(1, files_per_month + 1):
                file_name = f"{year}_{month_name}_{file_num}.csv"  # Adjust naming pattern if necessary
                file_url = f"{base_url}/{year} {month_name}/{file_name}"

                try:
                    response = requests.get(file_url)
                    response.raise_for_status()
                    file_df = pd.read_csv(io.StringIO(response.text))

                    # Set the first file's columns as reference for consistency
                    if ref_columns is None:
                        ref_columns = set(file_df.columns)

                    # Check for column consistency within the month
                    if set(file_df.columns) != ref_columns:
                        inconsistent_files.append(file_name)
                    else:
                        monthly_data.append(file_df)  # Append consistent file

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching {file_name}: {e}")
                    continue

            # Log inconsistent files for reference
            if inconsistent_files:
                print(f"Inconsistent columns in {year} {month_name}: {inconsistent_files}")

            # Combine monthly data if files are consistent, otherwise skip or handle adjustments here
            if monthly_data:
                combined_month_df = pd.concat(monthly_data, ignore_index=True)

                # Save each month's combined file as a single CSV
                output_file = f"{output_dir}/{year}_{month_name}.csv"
                combined_month_df.to_csv(output_file, index=False)
                print(f"Saved combined data for {year} {month_name} to {output_file}")


# Configuration for file paths and parameters
base_url = "https://raw.githubusercontent.com/username/repo/branch/data/INFORM Suite/INFORM Severity/EuroCom_INFORM_Severity_Data"
output_dir = "combined_monthly_data"  # Local directory to save combined monthly files
start_date = datetime(2020, 9, 1)  # Start date: September 2020
end_date = datetime.now()  # Dynamic end date (latest available month)
files_per_month = 22  # Adjust if necessary

# Run the function to combine data by month
combine_monthly_data(base_url, start_date, end_date, files_per_month, output_dir)