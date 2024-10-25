import streamlit as st
import os
import nltk
from huggingface_hub import login


from modules.sidebar import launch_sidebar

from modules.cache_functions import *


st.set_page_config(
    page_title='Sentiment Analysis Tool', 
    page_icon='static/img/favicon.png', layout='wide'
    )


def initialize_session_state():
    """
    Initialize session state variables if they don't exist.
    """

    if 'disable_button' not in st.session_state:
        st.session_state['disable_button'] = False

    if "selected_actor" not in st.session_state:
        st.session_state["selected_actor"] = None

    if "master_df" not in st.session_state:
        st.session_state["master_df"] = None

    if "original_tweet" not in st.session_state:
        st.session_state["original_tweet"] = None

    if "sentiment_over_date" not in st.session_state:
        st.session_state["sentiment_over_date"] = None

    if "display_target_count" not in st.session_state:
        st.session_state["display_target_count"] = None

    if "stacked_bar_fig" not in st.session_state:
        st.session_state["stacked_bar_fig"] = None

    if "most_common_trigrams" not in st.session_state:
        st.session_state["most_common_trigrams"] = None

    if "display_word_cloud" not in st.session_state:
        st.session_state["display_word_cloud"] = None

    if "graphs_created" not in st.session_state:
        st.session_state["graphs_created"] = False

    if "tweet_data" not in st.session_state:
        st.session_state["tweet_data"] = None

    if "display_target_count" not in st.session_state:
        st.session_state["display_target_count"] = None

    if "create_scatter_plot" not in st.session_state:
        st.session_state["create_scatter_plot"] = None

    if "locations_graphic" not in st.session_state:
        st.session_state["locations_graphic"] = None


def nltk_installs():
    NLTK_DATA =  "nltk_data"

    nltk.data.path.append(NLTK_DATA)
    # Ensure the stopwords are available
    try:
        nltk.data.find('corpora/stopwords.zip')
    except LookupError:
        nltk.download('stopwords', download_dir=NLTK_DATA)

    try:
        nltk.data.find("tokenizers/punkt.zip")
    except LookupError:
        nltk.download("punkt", download_dir=NLTK_DATA)


def main():
    """ Handles the application startup """

    # Initialize all needed keys at session_state dictionary
    initialize_session_state()

    # Checks/downloads nltk resources
    nltk_installs()

    # The huggingface login stays associated to the GitHub account
    login(token = st.secrets['MODEL_KEY'])

    # Cacheing Data/files
    cache_omdena_logo()
    cache_banner()
    cache_contributors()
    cache_pce_logo()
    cache_sample_dataset()
    cache_stopwords()


    # Cacheing resources
    sentiment_pipeline()
    apify_client()
    load_css()

    # Show the side bar
    launch_sidebar()   

if __name__ == "__main__":
    main()