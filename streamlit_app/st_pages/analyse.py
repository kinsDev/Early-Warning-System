import pandas as pd
import json
import streamlit as st
from modules.actors import run_apify_actors  # Import the scraper functions
from modules.scraper import fetch_main_tweet_dataframe, fetch_comments_dataframe
from modules.utils import (
    load_header,
    is_valid_twitter_url,
    apply_sentiment_pipeline
)
from modules.cache_functions import cache_sample_dataset
import pdb


def update_dataframes(df_comments, df_author):
    # Mapping dictionary
    sentiment_map = {
        1: 'Positiv',
        0: 'Neutral',
        -1: 'Negativ'
    }

    with st.spinner("Analyze tweets..."):
        df_comments['predictedSentiment'] = df_comments['cleaned_text'].apply(lambda x: apply_sentiment_pipeline(x))
        # Assigning sentiment labels based on predictedSentiment values
        df_comments['sentiment_label'] = df_comments['predictedSentiment'].map(sentiment_map)

    st.session_state["master_df"] = df_comments
    st.session_state["original_tweet"] = df_author



def display_results(selected_actor):
    with st.expander("Tweet Original", expanded=True):
        st.dataframe(
            st.session_state["original_tweet"], height=1, use_container_width=True, key=selected_actor,
        )

    with st.expander("Comments", expanded=True):
        st.dataframe(
            st.session_state["master_df"], height=450, use_container_width=True, key=f'Comments from tweet of {selected_actor}',
        )

    st.write("<br>", unsafe_allow_html=True)

    st.download_button(
        label="Download as CSV",
        data=st.session_state["master_df"].to_csv(index=False).encode("utf-8"),
        file_name="analysis.csv",
        use_container_width=True,
    )

# Function to process and display GDELT data
def display_gdelt_data(gdelt_news_data):
    #pdb.set_trace()
    if isinstance(gdelt_news_data, pd.DataFrame):
        # If gdelt_news_data is already a DataFrame, directly display it
        if not gdelt_news_data.empty:
            columns_to_display = ['title', 'url', 'sourcecountry']

            # Ensure all required columns are present before filtering
            if all(col in gdelt_news_data.columns for col in columns_to_display):
                gdelt_df_filtered = gdelt_news_data[columns_to_display]
                st.subheader("News Data (from GDELT)")
                st.dataframe(gdelt_df_filtered)
            else:
                st.warning("Some columns are missing in the GDELT data. Available columns: " + ", ".join(gdelt_news_data.columns))
        else:
            st.warning("No GDELT news data available for the selected criteria.")
    else:
        st.error("Unexpected data format for GDELT news data.")
def analyse_page():
    load_header("Analysis")

    # Dropdown for country selection

    col1, col2, col3, col4 = st.columns([0.3, 0.3, 0.1, 0.4])
    with col1:
        selected_country = st.selectbox(
            "Select a Country", 
            ["United States", "India", "Ukraine", "Sudan", "Mali", "Myanmar", "Burkina Faso"]
        ).strip()

        st.write(f"Country selected: {selected_country}")

    with col2:
        selected_keyword = st.selectbox(
            "Select a keyword", 
            ["protest", "demonstration", "war", "election", "drout", "earthquake", "inflation", "armed conflict", "military tension", "food shortage"]
        ).strip()

        st.write(f"Keyword selected: {selected_keyword}")

    with col3:
        st.write("<br>", unsafe_allow_html=True)
        analyze_button = st.button("Analyze", use_container_width=True)
    
    # Bind the "Analyze" button to run Apify actors
    if analyze_button:
        with st.spinner("Fetching data from API actors..."):
            # Run the Apify actors and fetch the data
            twitter_data, google_trends_data, gdelt_news_data = run_apify_actors(selected_country, selected_keyword)

            # Store the data in the session state
            st.session_state['twitter_data'] = twitter_data
            st.session_state['google_trends_data'] = google_trends_data
            st.session_state['gdelt_news_data'] = gdelt_news_data

        # Display the results
        st.subheader("Twitter Data")
        if not twitter_data.empty:
            st.dataframe(twitter_data)
        else:
            st.warning("No Twitter data available for the selected criteria.")

        st.subheader("Google Trends Data")
        if not google_trends_data.empty:
            columns_to_display = ['query', 'date', 'exploreLink']
            if all(col in google_trends_data.columns for col in columns_to_display):
                st.dataframe(google_trends_data[columns_to_display])
            else:
                st.dataframe(google_trends_data)
        else:
            st.warning(f"No trending searches available for {selected_country}.")

        # Display GDELT News Data
        display_gdelt_data(gdelt_news_data)

    # Display any previously fetched data
    if 'twitter_data' in st.session_state and not st.session_state['twitter_data'].empty:
        st.subheader("Previously Fetched Twitter Data")
        st.dataframe(st.session_state['twitter_data'])

    cols = st.columns([5, 1])

    # Initialize session state variables if not already defined
    if 'twitter_url' not in st.session_state:
        st.session_state['twitter_url'] = ''
    if 'df_comments' not in st.session_state:
        st.session_state['df_comments'] = None
    if 'df_author' not in st.session_state:
        st.session_state['df_author'] = None

    # User Input

    with cols[0]:
        twitter_url = st.text_input(
            "Tweet URL:",
            value=st.session_state['twitter_url'],  # Default value from session state
        ).strip()

    with cols[1]:
        st.write("<br>", unsafe_allow_html=True)
        submitted = st.button("Submit", use_container_width=True)

    valid_twitter = is_valid_twitter_url(twitter_url)

    # If the input field is enabled
    if submitted and not valid_twitter:
        st.toast("⚠️ Invalid URL. Please enter a valid Twitter URL", type="error")
    elif submitted and valid_twitter:
        with st.spinner("Obtaining data..."):
            df_author = fetch_main_tweet_dataframe(twitter_url)
            df_comments = fetch_comments_dataframe(twitter_url)

            # Save results in session state
            st.session_state['df_author'] = df_author
            st.session_state['df_comments'] = df_comments

            update_dataframes(df_comments, df_author)
            display_results('Actor Selected')

    # If we have results already in session state (i.e., switching back to this page)
    elif st.session_state['df_author'] is not None and st.session_state['df_comments'] is not None:
        display_results('Actor Selected')

    # Using default datasets
    else:
        st.markdown("<p style='font-size: small;'>The field is disabled for the demonstration, please use the menu to select a political actor</p>", unsafe_allow_html=True)

        datasets = cache_sample_dataset()

        options = list(datasets.keys())

        index = None if st.session_state["selected_actor"] is None else options.index(st.session_state["selected_actor"])

        selected_actor = st.selectbox(
            "Select a political actor", 
            options, 
            index=index, 
            placeholder="Select a political actor"
        )

        if selected_actor and selected_actor != st.session_state["selected_actor"]:
            df_author = [value for dictionary in datasets[selected_actor] for key, value in dictionary.items() if 'comments' not in key][0]
            df_comments = [value for dictionary in datasets[selected_actor] for key, value in dictionary.items() if 'comments' in key][0]
            
            # Save to session state
            st.session_state["selected_actor"] = selected_actor
            st.session_state['df_author'] = df_author
            st.session_state['df_comments'] = df_comments

            index = options.index(selected_actor)
            update_dataframes(df_comments, df_author)
            display_results(selected_actor)
            st.rerun()
        elif selected_actor and selected_actor == st.session_state["selected_actor"]:
            display_results(st.session_state["selected_actor"])