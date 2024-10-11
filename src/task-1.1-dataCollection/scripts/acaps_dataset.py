# Basic imports for API
import requests
import pandas as pd
from datetime import datetime
import time



# Step 1: Authentication - Get the token
def get_api_token(username, password):
    url = "https://api.acaps.org/api/v1/token-auth/"
    payload = {
        'username': username,
        'password': password
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        # Extract the token from the response
        print("Generating Token.....")
        token = response.json().get('token')
        return token
    elif response.status_code == 404:
        print("Error 404: URL not found. Check the URL.")
    elif response.status_code == 401:
        print("Error 401: Unauthorized. Check your credentials.")
    else:
        print(f"Error {response.status_code}: Unable to authenticate.")
        print(response.text)





# Step 2: Test API Access with token
def test_api_connection(token, url):
    headers = {
        'Authorization': f'Token {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("Successfully connected to the API.")
        return True
    elif response.status_code == 404:
        print("Error 404: URL not found. Check the endpoint.")
    elif response.status_code == 401:
        print("Error 401: Unauthorized. Token might be invalid.")
    else:
        print(f"Error {response.status_code}: Unable to access the API.")
        print(response.text)





# Step 3: Make a request using the token and handle pagination and save the data set in pandas data frame
def fetch_api_data(username, password, endpoint, params=None):
    token = get_api_token(username, password)
    if token:
        base_url = f"https://api.acaps.org/api/v1/{endpoint}"
        endpoint_exists = test_api_connection(token, base_url)
        
        if endpoint_exists:
            
            headers = {'Authorization': f'Token {token}'}
            all_results = []
            last_request_time = datetime.now()
            
            while base_url:
                
                # Wait to avoid throttling
                while (datetime.now()-last_request_time).total_seconds() < 1:
                    time.sleep(0.1)
                    
                response = requests.get(base_url, headers=headers, params=params)
                last_request_time = datetime.now()
                
                if response.status_code == 200:
                    data = response.json()
                    # Append the results from the current page
                    all_results.extend(data.get('results', []))
                    # Get the URL for the next page
                    base_url = data['next']
                else:
                    print(f"Error: Failed to fetch data. Status code {response.status_code}")
                    break
            
            # Convert the results to a DataFrame
            if all_results:
                return pd.DataFrame(all_results)
            else:
                print("No data found")
                return None