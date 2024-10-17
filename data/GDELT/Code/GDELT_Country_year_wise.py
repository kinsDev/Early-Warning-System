"""## GDELT Data Wrangler

One of the challenges of dealing with GDELT is that its size makes implementation in a SQL database challenging. It is easier (although slower) to extract a subset of the data that we wish to work with, and do our actual data investigation afterwards. If we're interested in data broken down by date, we have it easy: GDELT files are provided this way. If instead we want to look at a single country, we have some work to do. This notebook parses through each of the GDELT files, one at a time, extracts the relevant lines, and exports them again to a smaller set of csv files. It then gives the option to load these files into a Pandas DataFrame, pickle the result, and remove the intermediate files.

There are certainly more computationally efficient methods for doing this, but this one works well enough.

### Additional References

* To export a single set of data, use this exporter: http://analysis.gdeltproject.org/module-event-exporter.html

* Raw Data is available here: http://data.gdeltproject.org/events/index.html

* A description of the data fields is here: http://data.gdeltproject.org/documentation/GDELT-Data_Format_Codebook.pdf

* The event codes are described in this document: http://gdeltproject.org/data/documentation/CAMEO.Manual.1.1b3.pdf

* This condensed version of the codes is easier to browse: http://cameocodes.wikispaces.com/EventCodes

* CAMEO country codes are listed here: http://cameocodes.wikispaces.com/countrybyname

* FIPS country codes are listed here: http://en.wikipedia.org/wiki/List_of_FIPS_country_codes"""

"""### Build intermediary files into a Pandas Dataframe

We may be content to use the data we just sampled into csv files in its present state. However, if we are working in python, it is convenient to load them into a DataFrame, save that DataFrame to a pickle, and delete the temporary files. This can save space on the disk, and make our future analysis of the data more simple.

* Our algorithm here is simple - we build dataframes out of each of the temporary files, and then merge them into one big dataframe. We save that big dataframe, and delete the temporary files.

* We use a helper file here which lists the column names. You can download the file to your working directory with this link:

http://gdeltproject.org/data/lookups/CSV.header.fieldids.xlsx

    Returns:
        _type_: _description_
    """




import os
import requests
import zipfile
import glob
import pandas as pd
import concurrent.futures
from io import BytesIO
import lxml.html as lh
import time

# GDELT base URL for event data
gdelt_base_url = 'http://data.gdeltproject.org/events/'

# Directory paths
local_path = 'path/to/local/directory/'
tmp_path = os.path.join(local_path, 'tmp/')
country_output_path = os.path.join(local_path, 'country/')
processed_files_log = os.path.join(local_path, 'processed_files.txt')

# Create directories if they don't exist
os.makedirs(tmp_path, exist_ok=True)
os.makedirs(country_output_path, exist_ok=True)

# FIPS country code
# fips_country_code = 'UP'  # Replace with the country code you're interested in, here I use UP for Ukraine
fips_country_code = 'SY'  # Replace with the country code you're interested in

# Function to download and extract GDELT files
def download_and_extract(compressed_file):
    try:
        print(f"Processing {compressed_file}...")
        # Download the file
        file_url = gdelt_base_url + compressed_file
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            # Unzip the file to the temporary directory
            with zipfile.ZipFile(BytesIO(response.content)) as z:
                z.extractall(path=tmp_path)
            print(f"Extracted {compressed_file}")
            return True
        else:
            print(f"Failed to download {compressed_file}")
            return False
    except Exception as e:
        print(f"Error downloading {compressed_file}: {e}")
        return False

# Get the list of GDELT files to process
def get_file_list(start_year=None, end_year=None, limit=None):
    page = requests.get(gdelt_base_url + 'index.html')
    doc = lh.fromstring(page.content)
    link_list = doc.xpath("//*/ul/li/a/@href")
    
    # Extract files that start with digits (representing dates)
    file_list = [x for x in link_list if x[:4].isdigit()]
    
    # Filter by year range if specified
    if start_year is not None:
        file_list = [f for f in file_list if int(f[:4]) >= start_year]
    if end_year is not None:
        file_list = [f for f in file_list if int(f[:4]) <= end_year]

    # Sort files in descending order to start with the most recent
    file_list = sorted(file_list, reverse=True)
    
    # Limit the number of files to process
    if limit:
        file_list = file_list[:limit]
    
    return file_list

# Function to filter GDELT files by country code
def filter_by_country_code(infile_name, outfilecounter):
    outfile_name = f"{country_output_path}{fips_country_code}_{outfilecounter:04}.tsv"
    
    with open(infile_name, 'r', encoding='utf-8', errors='replace') as infile, open(outfile_name, 'w', encoding='utf-8') as outfile:
        for line in infile:
            columns = line.split('\t')
            # Check if the country code is in relevant fields
            if fips_country_code in (columns[51], columns[37], columns[44]):
                outfile.write(line)

# Parallel processing for downloading and extracting files
def process_files_concurrently(file_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(download_and_extract, file_list))
    return results

# Process all GDELT files to extract rows based on country code
def extract_country_data(file_list):
    outfilecounter = 0
    for infile_name in glob.glob(tmp_path + '*'):
        filter_by_country_code(infile_name, outfilecounter)
        outfilecounter += 1
        os.remove(infile_name)  # Remove temp file after processing
    print("Country-specific data extracted.")

# Build a single Pandas DataFrame from the processed files
def build_dataframe():
    colnames = pd.read_excel('CSV.header.fieldids.xlsx', sheet_name='Sheet1', 
                             index_col='Column ID', usecols=[0, 1])['Field Name']
    
    # Get all country-specific files
    files = glob.glob(f"{country_output_path}{fips_country_code}_*.tsv")
    DFlist = [pd.read_csv(file, sep='\t', header=None, names=colnames, dtype=str, encoding='utf-8') for file in files]
    
    # Concatenate all the dataframes
    full_df = pd.concat(DFlist, ignore_index=True)
    
    # Save the dataframe to a pickle file for efficient storage
    full_df.to_pickle(f"{local_path}{fips_country_code}_data.pkl")
    
    # Optionally, delete temporary CSV files
    for file in files:
        os.remove(file)
    print(f"DataFrame built and saved as {fips_country_code}_data.pkl")

# Track processed files
def log_processed_file(file_name):
    with open(processed_files_log, 'a') as log_file:
        log_file.write(f"{file_name}\n")

def is_file_processed(file_name):
    if os.path.exists(processed_files_log):
        with open(processed_files_log, 'r', encoding='utf-8') as log_file:
            processed_files = log_file.read().splitlines()
        return file_name in processed_files
    return False

# Main workflow
if __name__ == "__main__":

    start_year = 2024  # Replace with your desired start year
    end_year = 2024    # Replace with your desired end year
    limit = 300         # Limit the number of files processed at a time

    # Step 1: Get the list of GDELT files
    file_list = get_file_list(start_year=start_year, end_year=end_year, limit=limit)
    
    # Step 2: Filter out already processed files
    file_list = [f for f in file_list if not is_file_processed(f)]
    
    # Step 3: Download and extract the relevant GDELT files
    if file_list:
        results = process_files_concurrently(file_list)
    
        # Step 4: Extract the country-specific data
        extract_country_data(file_list)
    
        # Step 5: Build the DataFrame and save it
        build_dataframe()
    
        # Log the processed files
        for file in file_list:
            log_processed_file(file)
    else:
        print("No new files to process.")
        
        
        
        
        
'''
##  How to access pkl files?
import pandas as pd

file_path = r'path\to\local\directory\AF_data.pkl'  
df = pd.read_pickle(file_path)

print(df.head())
'''        
