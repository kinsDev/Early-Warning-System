import os
import pandas as pd

def vertical_integration(folder_path, output_file):
    # List to hold DataFrames
    dataframes = []

    # Loop through all files in the specified folder
    for file_name in os.listdir(folder_path):
        if (file_name.endswith('.csv') and ~(file_name=='final_data.csv')):  # Check if the file is a CSV and not the final dataset file.
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_path}")

            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Append the DataFrame to the list
            dataframes.append(df)
            
            # Delete the file after it's read
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

    # Vertically concatenate all DataFrames in the list
    if dataframes:  # Check if the list is not empty
        combined_df = pd.concat(dataframes, ignore_index=True)

        # Save the combined DataFrame to a new CSV file
        combined_df.to_csv(output_file, index=False)
        print(f"Integrated data saved to: {output_file}")
    else:
        print("No CSV files found in the specified folder.")

def integrate_main():
    
    # Get the directory of the current Python file
    final_directory = "Data\INFORM Suite\INFORM Severity\EuroCom_INFORM_Severity_Data\Monthly_merged_data"

    vertical_integration(final_directory,os.path.join('final_data.csv'))
    