import os
import shutil



def copy_file(source_folder, destination_folder, condition):
    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        return

    # Ensure the destination folder exists, create it if it doesn’t.
    os.makedirs(destination_folder, exist_ok=True)

    # Loop through files in the source folder
    for file_name in os.listdir(source_folder):
        # Construct the full file path
        file_path = os.path.join(source_folder, file_name)

        # Check if it's a file and meets the condition
        if os.path.isfile(file_path) and condition(file_name):
            # Copy the file to the destination folder
            shutil.copy2(file_path, destination_folder)
            print(f"Copied '{file_name}' to '{destination_folder}'")

def copy_main(year):
    base_dir = 'Data/INFORM Suite/INFORM Severity/EuroCom_INFORM_Severity_Data'
    sources = [os.path.join(base_dir, f) for f in os.listdir(base_dir) if f != 'Monthly_merged_data' and os.path.isdir(os.path.join(base_dir, f)) and f.startswith(str(year))]
    
    for source in sources:
        destination = os.path.join(base_dir, "Monthly_merged_data")
        copy_file(source, destination, lambda filename: filename.endswith('merged.csv'))
        



