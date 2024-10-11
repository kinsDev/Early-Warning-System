import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import load_workbook
from io import BytesIO
from urllib.parse import urljoin
import shutil
import re
import time

# Setting up directories
base_dir = "INFORM_Severity_CSVs"
os.makedirs(base_dir, exist_ok=True)

base_url = "https://drmkc.jrc.ec.europa.eu"
page_url = "https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Severity/Results-and-data"

response = requests.get(page_url)
if response.status_code != 200:
    raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

soup = BeautifulSoup(response.content, "html.parser")

# Finding Excel file download links
excel_links = soup.find_all("a", href=lambda href: href and href.endswith(".xlsx"))

if not excel_links:
    print("No Excel links found.")
    exit()

print(f"Found {len(excel_links)} Excel files to download.")

# Loop through Excel files
for idx, link in enumerate(excel_links, start=1):
    relative_url = link.get('href')
    file_url = urljoin(base_url, relative_url)
    file_name = os.path.basename(relative_url)
    
    print(f"[{idx}/{len(excel_links)}] Downloading {file_name} from {file_url}...")
    
    try:
        # Downloading the file
        excel_response = requests.get(file_url)
        if excel_response.status_code != 200:
            print(f"Failed to download {file_name}. Status code: {excel_response.status_code}")
            continue
        excel_data = BytesIO(excel_response.content)
        
        # Looping through sheets in the workbook
        workbook = load_workbook(excel_data, data_only=True)
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            data = sheet.values
            
            try:
                columns = next(data)
            except StopIteration:
                print(f"Sheet '{sheet_name}' in {file_name} is empty. Skipping.")
                continue
            df = pd.DataFrame(data, columns=columns)
            
            # Cleaning sheet_name and file_name
            clean_sheet_name = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in sheet_name).strip().replace(" ", "_")
            csv_filename = f"{os.path.splitext(file_name)[0]}_{clean_sheet_name}.csv"
            csv_path = os.path.join(base_dir, csv_filename)
            df.to_csv(csv_path, index=False)
            print(f"  Saved: {csv_path}")
        
        # Extracting month and year from the filename
        match = re.search(r"_(\w+)_(\d{4})", file_name)
        if match:
            month_name = match.group(1)  # Get the month from the name
            year = match.group(2)  # Get the year from the name

            folder_name = f"{year} {month_name}"
            folder_path = os.path.join(base_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Moving the file to the new folder
            for csv_file in os.listdir(base_dir):
                if csv_file.endswith(".csv") and csv_file.startswith(file_name.replace(".xlsx", "")):
                    shutil.move(os.path.join(base_dir, csv_file), folder_path)
                    print(f"  Moved {csv_file} to {folder_name}")

        time.sleep(1)
    
    except Exception as e:
        print(f"Error processing {file_name}: {e}")

print("All files downloaded.")
