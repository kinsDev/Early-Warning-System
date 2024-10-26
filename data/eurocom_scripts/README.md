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

