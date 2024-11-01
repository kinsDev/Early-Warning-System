import requests
from bs4 import BeautifulSoup

# URL for the FEWS NET page
url = "https://fews.net/search?sort_by=date&f%5B0%5D=language%3Aen&f%5B1%5D=page_type%3Areport&f%5B2%5D=report_type%3A17&f%5B3%5D=report_type%3A39"

# Set up a headers dictionary to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}

# Send a GET request to the URL
response = requests.get(url, headers=headers)
response.raise_for_status()  # Raise an error for bad responses

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, "html.parser")