# common_dataset.py Script

## Data Consistency Checker

This scripts processes data files for column consistency from a structured dataset. It fetches CSV files from a specified directory path, identifies files with inconsistent columns, and can adjust inconsistent files to align with a reference column structure for seamless data concatenation.

## Explanation of Key Functions

### `check_column_consistency(base_url, years, months, files_per_month)`

This function:
- Builds paths for each file based on `year`, `month_name`, and `file_num`.
- Fetches each file, reads it as a DataFrame, and compares its columns with a reference column set.
- Records files with inconsistent columns and returns consistent data as a list of DataFrames.

### Main Script Logic
- **Adjust Columns**: If `adjust_to_match=True`, the script modifies inconsistent files by adding missing columns and removing extras, ensuring alignment with the reference column structure.
- **Data Concatenation**: Consistent and adjusted data are concatenated and saved as `common_dataset.csv`.

## Output
- **`common_dataset.csv`**: The final, concatenated dataset.
- **`inconsistent_files.log`**: List of files with inconsistent columns.

---


# one-file-per-month.py script

## Code Explanation
To achieve this, we will modify the previous script to combine each month’s 22 CSV files into a single file. The modified script will work as follows:
- Iterate through each month (directory).
- Load all 22 CSV files.
- Check for column consistency within that month.
- Merge the consistent files into a single DataFrame.
- Save the combined DataFrame as a single CSV file for that month, creating a structure of "one month = one file."

## Explanation 
- **Loop through Monthly Files**: For each month, it loads the 22 files, checks for column consistency, and appends consistent files to `monthly_data`.
- **Inconsistent Files Logging**: If any files have inconsistent columns, their names are logged for reference. Adjustments can be added if needed (similar to previous code).
- **Saving Monthly Combined File**: After processing each month, it concatenates `monthly_data` and saves it to a new CSV file for that specific month in the `output_dir`.

## Handling Date Ranges
We will iterate through the calendar years, currently running from September 2020 to September 2024. As new months are added, the code will continue to process available months without requiring updates.

### Enhancements for Dynamic Adaptability
- **Start and End Dates**: We define the start as September 2020 and the end date dynamically based on available data. When more data is added, the script will handle additional months automatically.
- **Filtering Months Within Range**: The script loops through each year and month but processes only those months from the start date onward.
