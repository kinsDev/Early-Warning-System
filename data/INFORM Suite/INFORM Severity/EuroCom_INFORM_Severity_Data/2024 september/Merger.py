#!/usr/bin/env python
# coding: utf-8

# In[118]:


import os
import pandas as pd
import re
from datetime import datetime
import gc
import numpy as np

# In[119]:


# Path to the current folder containing
folder_path = os.getcwd() 

# Get a list of all CSV files in the folder
file_list = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')], key=str.casefold)
print("\n".join(file_list))


# In[120]:


# Initialize the variables
current_file_index = -1
release_date = None
month = None
year = None
year_month = None


# Functions:

# In[121]:


import os
import pandas as pd

def load_next_csv(file_list, folder_path, current_file_index):
    """
    Loads the next CSV file from the file list into a DataFrame.
    
    Parameters:
    file_list (list): List of CSV filenames to load.
    folder_path (str): Path to the folder containing the CSV files.
    current_file_index (int): Index of the current file to load.
    
    Returns:
    tuple: DataFrame loaded from the next CSV file, updated file index
    """
    # Check if there are more files to process
    if current_file_index >= len(file_list) - 1:
        print("No more CSV files left to load.")
        return None, current_file_index
    
    # Increment the file index to load the next file
    current_file_index += 1
    
    # Get the next file in the list
    current_file = file_list[current_file_index]
    file_path = os.path.join(folder_path, current_file)
    print(f"Opening file: {current_file}")
    
    # Load the CSV file into a DataFrame without headers for initial inspection
    df = pd.read_csv(file_path, header=None)
    
    return df, current_file_index


# In[122]:


def drop_nan(df, column_name):
    """
    Cleans the DataFrame by removing rows where the specified column has NaN,
    removing columns with NaN in the header, and renaming unnamed columns.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to clean.
    column_name (str): The name of the column to check for NaN values in rows.
    
    Returns:
    pd.DataFrame: The cleaned DataFrame.
    """
    # Track rows with NaN in the specified column
    rows_to_delete = df[df[column_name].isna()].index.tolist()

    # Drop rows with NaN in the specified column
    df = df.dropna(subset=[column_name])

    # Track columns with NaN in the header
    columns_to_delete = [col for col in df.columns if pd.isna(col)]
    
    # Replace NaN headers with placeholders (e.g., "Unnamed")
    df.columns = [col if pd.notna(col) else f"Unnamed_{i}" for i, col in enumerate(df.columns)]
    
    # Optionally drop columns that were NaN if not needed
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    # Print deleted rows and columns
    print("Deleted rows (indices):", rows_to_delete)
    print("Deleted columns:", columns_to_delete)

    return df


# In[123]:


def clean_dataframe(df, crisis_id_col):
    """
    Cleans the DataFrame by dropping rows where the Crisis ID column has NaN,
    resetting the index, and setting row 0 as the header.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to clean.
    crisis_id_col (str): The name of the Crisis ID column to check for NaN values.
    
    Returns:
    pd.DataFrame: The cleaned DataFrame with updated headers.
    """
    # List to collect rows to drop
    rows_to_drop = []
    cols_to_drop = []
    
    # Identify rows where the Crisis ID column has NaN
    for row in range(len(df)):
        if pd.isna(df.iloc[row, crisis_id_col]):
            rows_to_drop.append(row)
    
    # Drop rows with NaN in the Crisis ID column
    print(f"Dropping NaN rows: {rows_to_drop}")
    df = df.drop(index=rows_to_drop)

    # Reset the index
    df = df.reset_index(drop=True)

    # Identify columns where header is NaN
    for col in range(0, len(df.columns)):
        if pd.isna(df.iloc[0, col]):
            cols_to_drop.append(df.columns[col])

    # Drop columns with NaN in the header
    print(f"Dropping NaN columns: {cols_to_drop}")
    df = df.drop(columns=cols_to_drop)

    # Make row 0 the header
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])

    # Rename columns for consistency
    column_mappings = {
        'Crisis Id': 'Crisis Id',
        'Crisisid': 'Crisis Id',
        'CrisisID': 'Crisis Id',
        'ISO3 code': 'ISO3',
        'Iso3 Code': 'ISO3',
        'Iso3': 'ISO3',
        'Iso 3': 'ISO3',
        # Add any other variations that need standardization
    }
    df = df.rename(columns=column_mappings)

    # Standardize target columns to titlecase strings and strip whitespace
    target_columns = ['Crisis', 'Drivers', 'Crisis Id', 'Country', 'ISO3']
    for col in target_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.title().str.strip()

    df.columns = df.columns.str.title()

    return df


# In[124]:


def get_dataframe_stats(df):
    """
    Prints the number of rows and columns in the DataFrame.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to analyze.
    """
    num_rows, num_columns = df.shape
    return f"{num_rows} rows x {num_columns} columns"


# In[125]:


#####-MERGE-#####


def merge_df(df_1, df_2, on_col, merge_type='outer'):
    # Add suffixes to all columns except the key column
    df_1 = df_1.rename(columns={col: f"{col}[df1]" for col in df_1.columns if col != on_col})
    df_2 = df_2.rename(columns={col: f"{col}[df2]" for col in df_2.columns if col != on_col})
    
    # Merge the DataFrames
    merged_df = pd.merge(df_1, df_2, on=on_col, how=merge_type)

    # Remove suffixes by renaming columns
    merged_df.columns = [col.replace('[df1]', '').replace('[df2]', '') for col in merged_df.columns]
    
    # Identify duplicated columns (keeping only the first occurrence)
    duplicate_columns = [col for col in merged_df.columns if merged_df.columns.tolist().count(col) > 1]

    # Remove duplicate columns, keeping only the first occurrence
    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

    # Identify rows where all values are duplicates
    duplicate_rows = merged_df.duplicated(keep=False)  # Marks all rows that are full duplicates

    # Get the indices of duplicate rows
    duplicate_indices = merged_df[duplicate_rows].index.tolist()

    # Count the number of duplicate rows
    num_deleted_rows = len(duplicate_indices)

    # Drop these duplicate rows from the DataFrame
    merged_df_cleaned = merged_df[~duplicate_rows].reset_index(drop=True)

    # Print the number of deleted rows and the row indices
    print(f"Number of rows deleted: {num_deleted_rows}")
    print("Indices of deleted duplicate rows:", duplicate_indices)
    print("DataFrame after removing fully duplicate rows:")
    print(merged_df_cleaned)

    return merged_df_cleaned



# About.csv

# In[126]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[127]:


# Function to check if a string is a date
def is_date(string, date_format="%d/%m/%Y"):
    try:
        datetime.strptime(string, date_format)
        return True
    except ValueError:
        return False


# In[128]:


current_file = file_list[current_file_index]
print(f"Current file: {current_file}")
if current_file.endswith("About.csv"):
    # Identify the first column by its index position
    first_column = df.columns[0]
    
    # Search for the word 'release' in the first column
    for i, row in df.iterrows():
        if str(row[first_column]).strip().lower() == "release:":
            # Check if the next row exists and if it contains a date
            next_row_value = df.at[i + 1, first_column] if i + 1 < len(df) else None
            if next_row_value and is_date(str(next_row_value)):
                release_date = next_row_value
                day, month, year = release_date.split("/")  # Split the date into parts
                month = int(month)
                year = int(year)
                year_month = f"{year}{month:02d}"
            break


# In[129]:


# Display the extracted release date, month, year, and year_month
if release_date:
    print(f"Release date for {current_file}: {release_date}")
    print(f"Month: {month}")
    print(f"Year: {year}")
    print(f"Year-Month: {year_month}")
else:
    print("\n" + f"No release date found in {current_file}.")


# In[130]:


pd.set_option('display.max_columns', None)


# df1. Complexity_of_the_crisis.csv

# In[131]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")


# In[132]:

# Case-Specific
current_file = file_list[current_file_index]
if current_file.endswith("Complexity_of_the_crisis.csv"):
    if df.iloc[1, 5] == "Empowerment" and pd.isna(df.iloc[4, 5]):
        # Copy the content from row 1 (columns 5-39) down into row 4 (columns 5-39)
        df.iloc[4, 5:df.shape[1]] = df.iloc[1, 5:df.shape[1]]
    # Delete empty rows
    df = clean_dataframe(df, crisis_id_col = 2)
    df1 = df
else: print("Wrong file")


# In[133]:


# Display the updated DataFrame
df1


# df2. Conditions_of_people_affected.csv

# In[134]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[135]:


# Case-Specific
current_file = file_list[current_file_index]
if current_file.endswith("Conditions_of_people_affected.csv"):
    if df.iloc[1, 5] == "# of people in none/minimal conditions - Level 1" and pd.isna(df.iloc[4, 5]):
        # Copy the content from row 1 (columns 5-39) down into row 4 (columns 5-39)
        df.iloc[4, 5:df.shape[1]] = df.iloc[1, 5:df.shape[1]]
    # Delete empty rows
    df = clean_dataframe(df, crisis_id_col = 2)
    df2 = df
else: print("Wrong file")


# In[136]:


# Display the updated DataFrame
df2


# In[137]:


#####-MERGE-#####

merged_df = merge_df(df1, df2, on_col="Crisis Id")
merged_df


# df3. Core_Indicators.csv

# In[138]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[139]:


def find_column_name(df, row, col):
    # Start one row up from the "Helper" cell
    current_row = row - 1
    current_col = col  # Starting column

    # Iterate to the right until a non-empty cell is found
    while current_col < df.shape[1]:  # Ensure we don't go beyond the last column
        if pd.notna(df.iloc[current_row, current_col]):
            return df.iloc[current_row, current_col]
        current_col += 1  # Move to the next column

    # If no column name is found, return a placeholder or None
    return None

# Case-Specific
current_file = file_list[current_file_index]
if current_file.endswith("Core_Indicators.csv"):
    for col in range(5, len(df.columns)):
        if pd.notna(df.loc[1, col]) and re.match(r"^Helper.*", str(df.loc[1, col])):
        # Try to find the column name by searching upwards
            col_name = find_column_name(df, 1, col)
        df.loc[0, col] =f"{col_name} [{str(df.loc[1, col])}]"
    df = clean_dataframe(df, crisis_id_col = 3)
    
    df3 = df
else: print("Wrong file")


# In[140]:


df3


# In[141]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df3, on_col="Crisis Id")
merged_df


# df4. Country_Indicator_Data.csv

# In[142]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[143]:


# Case-Specific
current_file = file_list[current_file_index]
if current_file.endswith("Country_Indicator_Data.csv"):
    cols_to_drop = []
    for col in range(2, len(df.columns)):
        if pd.isna(df.iloc[0, col]):
            cols_to_drop.append(df.columns[col])
            df[col] = df[col].astype(object)  # Convert the entire column to object type
        df.iloc[0, col] =f"{df.iloc[0, col]} [{str(df.iloc[1, col])}] [{df.iloc[2, col]}]"

    print(f"Columns to drop: {cols_to_drop}")
    df = df.drop(columns=cols_to_drop)

    df = clean_dataframe(df, crisis_id_col = 1)
    df4 = df
else: print("Wrong file")


# In[144]:


df4


# In[145]:


#####-MERGE-#####
merged_df = merge_df(merged_df, df4, on_col="Country")
merged_df


# df5. Crisis_Indicator_Data.csv

# In[146]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[147]:


# Case-Specific
current_file = file_list[current_file_index]
if current_file.endswith("Crisis_Indicator_Data.csv"):
    for col in range(5, len(df.columns)):
        if pd.notna(df.loc[1, col]):
            df.loc[0, col] =f"{df.loc[0, col]} [{df.loc[1, col]}]" 
    df = clean_dataframe(df, crisis_id_col = 2)
    df5 = df
else: print("Wrong file")


# In[148]:


df5


# In[149]:


merged_df = merge_df(merged_df, df5, on_col="Crisis Id")
merged_df


# df6. Crisis_info.csv

# In[150]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[151]:


# Case-Specific
current_file = file_list[current_file_index]
if current_file.endswith("Crisis_info.csv"):
    df = clean_dataframe(df, crisis_id_col = 0)
    df6 = df
else: print("Wrong file")


# In[152]:


df6


# In[153]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df6, on_col="Crisis Id")
merged_df


# df7. Data_Reliability.csv

# In[154]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[155]:


# Case-Specific
current_file = file_list[current_file_index]
if current_file.endswith("Data_Reliability.csv"):
    df = clean_dataframe(df, crisis_id_col = 0)
    df7 = df
else: print("Wrong file")


# In[156]:


df7


# In[157]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df7, on_col="Crisis Id")
merged_df


# df8. Impact_of_the_crisis.csv

# In[158]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[159]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("Impact_of_the_crisis.csv"):
    if df.iloc[1, 5] == "Area affected - absolute" and pd.isna(df.iloc[4, 5]):
        # Copy the content from row 1 (columns 5-...) down into row 4 (columns 5-...)
        df.iloc[4, 5:df.shape[1]] = df.iloc[1, 5:df.shape[1]]
    df = clean_dataframe(df, crisis_id_col = 0)
    df8 = df
else: print("Wrong file")


# In[160]:


df8


# In[161]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df8, on_col="Crisis Id")
merged_df


# Imputed_and_missing_data_hidden.csv -- No data

# In[162]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")


# Indicator_Date_hidden.csv -- No data

# In[163]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")


# Indicator_Date_hidden2.csv -- No data

# In[164]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")


# Indicator_Metadata.csv -- No data, just description of features

# In[165]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")


# In[166]:


df = clean_dataframe(df, crisis_id_col = 0)
df.head()


# df9. INFORM_Severity___all_crises.csv

# In[167]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[168]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("INFORM_Severity_all_crises.csv"):
    df = clean_dataframe(df, crisis_id_col = 1)
    df9 = df
else: print("Wrong file")


# In[169]:


df9


# In[170]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df9, on_col="Crisis Id")
merged_df


# df10. INFORM_Severity___country.csv

# In[171]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[172]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("INFORM_Severity_country.csv"):
    df = clean_dataframe(df, crisis_id_col = 1)
    df10 = df
else: print("Wrong file")


# In[173]:


df10


# In[174]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df10, on_col="Crisis Id")
merged_df


# INFORM_Severity___hidden.csv -- Was hidden. No Data to be used

# In[175]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# df11. Lists.csv

# In[176]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[177]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("Lists.csv"):
    df = clean_dataframe(df, crisis_id_col = 2)
    df11 = df
else: print("Wrong file")


# In[178]:


df11


# In[179]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df11, on_col="Crisis Id")
merged_df


# df12. Log.csv

# In[180]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[181]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("Log.csv"):
    df = clean_dataframe(df, crisis_id_col = 1)
    df12 = df
else: print("Wrong file")


# In[182]:


df12


# In[183]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df12, on_col="Crisis Id")
merged_df


# df13. Regional_Crises.csv

# In[184]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[185]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("Regional_Crises.csv"):
    for col in range(5, len(df.columns)):
        if pd.notna(df.loc[1, col]):
            df.loc[0, col] =f"{df.loc[0, col]} [{df.loc[1, col]}]" 
    df = clean_dataframe(df, crisis_id_col = 1)
    df13 = df
else: print("Wrong file")


# In[186]:


df13


# In[187]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df13, on_col="Crisis Id")
merged_df


# df14. Reliability.csv

# In[188]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[189]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("Reliability.csv"):
    df = clean_dataframe(df, crisis_id_col = 0)
    df14 = df
else: print("Wrong file")


# In[190]:


df14


# In[191]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df14, on_col="Crisis Id")
merged_df


# df15. Reliability_updated.csv.csv

# In[192]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[193]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("Reliability_updated.csv"):
    df = clean_dataframe(df, crisis_id_col = 0)
    df15 = df
else: print("Wrong file")


# In[194]:


df15


# In[195]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df15, on_col="Crisis Id")
merged_df


# df16. Trends.csv

# In[196]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[197]:


# Case-Specific

current_file = file_list[current_file_index]
if current_file.endswith("Trends.csv"):
    df = clean_dataframe(df, crisis_id_col = 2)
    df16 = df
else: print("Wrong file")


# In[198]:


df16


# In[199]:


#####-MERGE-#####

merged_df = merge_df(merged_df, df16, on_col="Crisis Id")
merged_df


# In[200]:


# Remove rows where there are NaNs in the Crisis Id column and headers with NaNs or Unnamed
merged_df =  drop_nan(merged_df, column_name="Crisis Id")


# In[201]:


# Add the year_month column as the first column
merged_df.insert(0, 'YYYY_MM', year_month)

# Reorder columns to have Crisis ID as the second column
columns = ['YYYY_MM', 'Crisis Id'] + [col for col in merged_df.columns if col not in ['YYYY_MM', 'Crisis Id']]
merged_df = merged_df[columns]

merged_df


# In[202]:


merged_df.to_csv(f"{year_month}_merged.csv", index=False)


# In[1]:


df, current_file_index = load_next_csv(file_list, folder_path, current_file_index)
print(f"Current file index is: {current_file_index}")
df


# In[ ]:




