import re
import pandas as pd
import streamlit as st
from apify_client import ApifyClient
import requests  # For GDELT API requests
import time
import json
import pdb


# Constants for Apify Actors
APIFY_TWITTER_ACTOR_ID = '61RPP7dywgiy0JPD0'  # Replace with actual Twitter scraper actor ID
APIFY_GOOGLE_TRENDS_ACTOR_ID = '49HfNLFgg6B8YetTj'  # Google Trending Searches actor ID

# Columns to keep from the scraped data
TWEETS_COLUMNS_LIST = [
    "id",
    "url",
    "text",
    "createdAt",
    "retweetCount",
    "replyCount",
    "likeCount",
    "quoteCount",
    "bookmarkCount",
    "author_name",
    "author_followers",
    "author_isVerified",
    "author_userName",
    "author_profilePicture",
    "author_location",
    "author_createdAt",
    "author_statusesCount",
    "author_following",
    "author_favouritesCount",
    "author_isBlueVerified"
]

# Apify API Token
APIFY_TOKEN = st.secrets["APIFY_TOKEN"]

# Initialize the Apify client
client = ApifyClient(APIFY_TOKEN)


# Country coordinates mapping for geotargeting (latitude, longitude, radius)
COUNTRY_COORDINATES = {
    "Sudan": "15.5007,32.5599,500km",  # Sudan with a 500km radius
    "United States": "37.0902,-95.7129,1000km",
    "India": "20.5937,78.9629,1000km",
    "Mali": "17.5707,-3.9962,500km",
    "Myanmar": "21.9162,95.9560,500km",
    "Burkina Faso": "12.2383,-1.5616,500km"
}

# Function to clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r'#\w+', '', text)  # Remove hashtags and the words following them
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    text = re.sub(r'[\U00010000-\U0010FFFF]', '', text)  # Remove emojis
    return text if text else None  # Return None if the text is empty

# Flatten the response
def flatten_response(response):
    author_info = response.get("author", {})
    return {
        "id": response.get("id"),
        "url": response.get("url"),
        "text": response.get("text"),
        "createdAt": pd.to_datetime(response.get("createdAt")),
        "retweetCount": response.get("retweetCount"),
        "replyCount": response.get("replyCount"),
        "likeCount": response.get("likeCount"),
        "quoteCount": response.get("quoteCount"),
        "bookmarkCount": response.get("bookmarkCount"),
        "author_name": author_info.get("name"),
        "author_followers": author_info.get("followers"),
        "author_isVerified": author_info.get("isVerified"),
        "author_userName": author_info.get("userName"),
        "author_profilePicture": author_info.get("profilePicture"),
        "author_location": author_info.get("location"),
        "author_createdAt": pd.to_datetime(author_info.get("createdAt")),
        "author_statusesCount": author_info.get("statusesCount"),
        "author_following": author_info.get("following"),
        "author_favouritesCount": author_info.get("favouritesCount"),
        "author_isBlueVerified": author_info.get("isBlueVerified")
    }

# Function to fetch Twitter data using Apify
def fetch_twitter_data(keyword, country, conversation_id=None):
    #pdb.set_trace()
    
    # Prepare run input with geocode if country is found in the mapping
    geocode = COUNTRY_COORDINATES.get(country, None)

    # Update the input parameters as per your specified query
    run_input = {
        "maxItems": 10,
        "includeSearchTerms": False,
        "onlyImage": False,
        "onlyQuote": False,
        "onlyTwitterBlue": False,
        "onlyVerifiedUsers": False,
        "onlyVideo": False,
        "searchTerms": [
            f"({keyword}) ({country})"
        ],
        "sort": "Latest",
    }

    # Add geolocation data if available
    #if geocode:
        #run_input["geocode"] = geocode

    try:
        run = client.actor(APIFY_TWITTER_ACTOR_ID).call(run_input=run_input)
        
        # Log the run result to check for issues
        print("Twitter Run Response:", run)

        # Fetch the results from the dataset
        response = [
            dictionary
            for dictionary in client.dataset(run["defaultDatasetId"]).iterate_items()
        ]

        if not response:  # Check if the response is empty
            print("Twitter response is empty.")

        flattened_data = [flatten_response(tweet) for tweet in response]
        df = pd.DataFrame(flattened_data, columns=TWEETS_COLUMNS_LIST)
        df['cleaned_text'] = df['text'].apply(clean_text)
        return df
    
    except Exception as e:
        print(f"Error fetching Twitter data: {e}")
        return pd.DataFrame(columns=TWEETS_COLUMNS_LIST)  # Return an empty DataFrame in case of error


# Function to fetch Google Trends data using pytrends
def fetch_google_trends_data(country):
    # Country codes mapping for Apify Google Trending Searches
    #pdb.set_trace()
    COUNTRY_CODES = {
        "United States": "US",
        "India": "IN",
        "Ukraine": "UA",
        "Bangladesh": "BD",
        "Sudan": "SD",
        "Mali": "ML",
        "Myanmar": "MM",
        "Burkina Faso": "BF"
    }

    # Get the country code
    country_code = COUNTRY_CODES.get(country)

    if not country_code:
        print(f"Country code not found for {country}.")
        return pd.DataFrame()

    # Prepare the run input
    run_input = {
        "extendOutputFunction": "async ({ data, item, request, customData, fromDate, toDate, Apify }) => { return item; }",
        "extendScraperFunction": "async ({ data, item, request, addUrl, customData, fromDate, toDate, extendOutputFunction, Apify }) => {}",
        "fromDate": "today",
        "toDate": "3 days",
        "geo": country_code,
        "maxItems": 20,
        "proxy": {
            "useApifyProxy": True
        },
        "outputMode": "complete",
        "customData": {}
    }

    try:
        run = client.actor(APIFY_GOOGLE_TRENDS_ACTOR_ID).call(run_input=run_input)

        # Fetch the results from the dataset
        response = [
            item
            for item in client.dataset(run["defaultDatasetId"]).iterate_items()
        ]

        if not response:
            print("Google Trends response is empty.")
            return pd.DataFrame()

        # Process the data and return as DataFrame
        df = pd.DataFrame(response)
        df['date'] = pd.to_datetime(df['date'])
        return df

    except Exception as e:
        print(f"Error fetching Google Trends data: {e}")
        return pd.DataFrame()


   
# Function to fetch news data using GDELT API
def fetch_gdelt_news(keyword, country):
    base_url = "http://api.gdeltproject.org/api/v2/doc/doc"
    
    params = {
        'query': f'{keyword} {country}',
        'mode': 'artlist',
        'maxrecords': 50,  # Limit the number of results
        'format': 'json'
    }
    
    try:
        response = requests.get(base_url, params=params)
        raw_response = response.text
        print("GDELT API Raw Response:", raw_response)

        # Try to parse the JSON response
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if the JSON is invalid

        # Check if the 'articles' key exists in the response
        if 'articles' in data:
            articles = pd.DataFrame(data['articles'])
            
            # Check if required columns are present
            columns_to_display = ['title', 'url', 'sourcecountry']
            if all(col in articles.columns for col in columns_to_display):
                return articles[columns_to_display]
            else:
                print(f"Expected columns not found. Available columns: {', '.join(articles.columns)}")
                return pd.DataFrame()  # Return an empty DataFrame if columns are missing
        else:
            print("No 'articles' key found in GDELT response.")
            return pd.DataFrame()  # Return an empty DataFrame if no articles are found
    
    except Exception as e:
        print(f"Error fetching news from GDELT: {e}")
        return pd.DataFrame()



# Function to run all the scrapers
def run_apify_actors(selected_country, selected_keyword):
    twitter_data = fetch_twitter_data(selected_keyword, selected_country)
    google_trends_data = fetch_google_trends_data(selected_country)
    gdelt_news_data = fetch_gdelt_news(selected_keyword, selected_country)
    
    return twitter_data, google_trends_data, gdelt_news_data

