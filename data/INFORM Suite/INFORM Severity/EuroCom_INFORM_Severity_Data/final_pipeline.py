from run_notebooks import run_main
from copy_merged_files import copy_main
from vertical_integration import integrate_main
import sys

sys.path.append('src\task-1.1-dataCollection\scripts')

from EuroCom_Data_Scraper import fetch_eurocom_data

def final_pipeline():
    
    fetch_eurocom_data()
    run_main()
    copy_main()
    integrate_main()