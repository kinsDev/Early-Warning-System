from run_notebooks import run_main
from copy_merged_files import copy_main
from copy_merged_files import copy_file
from vertical_integration import integrate_main
import sys

sys.path.append('src\task-1.1-dataCollection\scripts')

# from EuroCom_Data_Scraper import fetch_eurocom_data

def final_pipeline():
    # fetch_new_eurocom_data() -- In the final realtime pipeline, it will only fetch the latest monthly data.
    # Once the latest data is fetched, it will move the merger notebook file from the folder of previous month to the folder of the latest month. This assumes that the monthly merger file for the previous month will work for the latest monthly data as well. If any structural changes in the monthly  releases are made then this might create problems while merging the monthly data.
    # copy_file()
    years = [i for i in range(2020,2023)]
    for year in years:

        run_main(year)
        copy_main(year)
        integrate_main()
        
final_pipeline()