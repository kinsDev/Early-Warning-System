import pandas as pd
import requests
import io
from datetime import datetime


# Updated function to check column consistency based on folder structure
def check_column_consistency(base_url, years, months, files_per_month):
    ref_columns = None
    inconsistent_files = []
    consistent_data = []
    month_names = ["january", "february", "march", "april", "may", "june",
                   "july", "august", "september", "october", "november", "december"]

    for year in years:
        for month in range(1, 13):
            month_name = month_names[month - 1]  # Convert month number to name
            for file_num in range(1, files_per_month + 1):
                file_name = f"{year}{month_name}{file_num}.csv"  # Adjust this as per actual naming format
                file_url = f"{base_url}/{year} {month_name}/{file_name}"

                try:
                    response = requests.get(file_url)
                    response.raise_for_status()
                    file_df = pd.read_csv(io.StringIO(response.text))

                    # Set the first file's columns as the reference
                    if ref_columns is None:
                        ref_columns = set(file_df.columns)

                    # Check for column consistency
                    if set(file_df.columns) != ref_columns:
                        inconsistent_files.append((year, month_name, file_name, list(file_df.columns)))
                    else:
                        consistent_data.append(file_df)  # Add to list if columns match

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching {file_name}: {e}")
                    continue

    return ref_columns, inconsistent_files, consistent_data


# URL and file configuration
base_url = "https://raw.githubusercontent.com/username/repo/branch/data/INFORM Suite/INFORM Severity/EuroCom_INFORM_Severity_Data"
years = range(2020, datetime.now().year + 1)
files_per_month = 22  # Adjust if necessary

# Check for column consistency
ref_columns, inconsistent_files, consistent_data = check_column_consistency(base_url, years, range(1, 13),
                                                                            files_per_month)

# Option to exclude or adjust files with different columns
adjust_to_match = True  # Set to False if you want to exclude inconsistent files

if adjust_to_match:
    # Adjust inconsistent files to match ref_columns
    adjusted_data = []
    for year, month_name, file_name, columns in inconsistent_files:
        file_url = f"{base_url}/{year} {month_name}/{file_name}"

        try:
            response = requests.get(file_url)
            response.raise_for_status()
            file_df = pd.read_csv(io.StringIO(response.text))

            # Align columns: add missing columns, drop extras
            for col in ref_columns:
                if col not in file_df.columns:
                    file_df[col] = None  # Fill missing columns with None
            file_df = file_df[list(ref_columns)]  # Ensure correct column order
            adjusted_data.append(file_df)

        except requests.exceptions.RequestException as e:
            print(f"Error adjusting {file_name}: {e}")

    # Concatenate consistent and adjusted data
    all_data = pd.concat(consistent_data + adjusted_data, ignore_index=True)
else:
    # Concatenate only consistent data
    all_data = pd.concat(consistent_data, ignore_index=True)

# Save or analyze the final combined dataset
all_data.to_csv("common_dataset.csv", index=False)

# Log inconsistent files for reference
print("Files with inconsistent columns:", inconsistent_files)