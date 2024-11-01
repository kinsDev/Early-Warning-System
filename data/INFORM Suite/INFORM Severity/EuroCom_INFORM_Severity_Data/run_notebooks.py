import subprocess
import os

def run_notebook(notebook_path):
    # Check if the notebook file exists
    if not os.path.isfile(notebook_path):
        print(f"The specified notebook '{notebook_path}' does not exist.")
        return

    # Execute the notebook using nbconvert
    try:
        subprocess.run([
            "jupyter", "nbconvert", 
            "--to", "notebook", 
            "--execute", 
            "--inplace", 
            notebook_path
        ], check=True)
        print(f"Executed the notebook: {notebook_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the notebook: {e}")

def run_main():
    
    base_dir = 'Data\INFORM Suite\INFORM Severity\EuroCom_INFORM_Severity_Data'
    sources = [os.path.join(base_dir, f) for f in os.listdir(base_dir) if f != 'Monthly_merged_data' and os.path.isdir(os.path.join(base_dir, f))]
    
    print(sources)
    for source in sources:
        print(os.path.join(source,'Merger.ipynb'))
        run_notebook(os.path.join(source,'Merger.ipynb'))