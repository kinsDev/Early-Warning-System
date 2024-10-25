import streamlit as st 
import os
import pandas as pd
from apify_client import ApifyClient
from transformers import pipeline
from nltk.corpus import stopwords

from modules.constants import CONTRIBUTORS, CUSTOM_STOP_WORDS, SPANISH_STOP_WORDS


@st.cache_data
def cache_omdena_logo():
    return r'static/img/omdena_logo.png'

@st.cache_data
def cache_pce_logo():
    return r'static/img/pce.png'

@st.cache_data
def cache_banner():
    return r'static/img/banner.png'
 
@st.cache_data
def cache_contributors():
    return CONTRIBUTORS

@st.cache_data
def cache_stopwords():
    stop_words = set(stopwords.words('spanish'))
    
    # Add other custom options
    stop_words.update(set(stopwords.words("english")))
    stop_words.update(CUSTOM_STOP_WORDS)
    stop_words.update(SPANISH_STOP_WORDS)

    return stop_words

@st.cache_data
def load_about_html():
    path = r'static/html/about.html'

    with open(path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    return html_content

@st.cache_data
def load_css():
   path = r'static/css/styles.css'

   with open(path) as f:
      st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


@st.cache_data
def cache_sample_dataset():
    """
    Returns a dictionary where the political actor's name is the key and the value
    is a list of dictionaries, where the key is the file's name, and the value is 
    the pandas dataframe that corresponds to the file name.
    """

    path =  r'static/dataset/sample_datasets'
    df_dict = dict()

    with os.scandir(path) as sample_datasets_dir:
        for file in sample_datasets_dir:
            file_name = os.path.splitext(file.name)[0]
            actor = file_name.replace('_tweet_comments', '').replace('_tweet', '')
            actor = actor.replace('_', ' ').title()
            df = pd.read_parquet(file.path)

            if actor not in df_dict:
                df_dict[actor] = []
            
            df_dict[actor].append({file_name: df})

    return df_dict


@st.cache_resource
def apify_client():
    return ApifyClient(st.secrets['APIFY_TOKEN'])

@st.cache_resource
def sentiment_pipeline():
    """
    Loads the pre trained model from Hugging Face platform,
    returning a pipeline object.
    """

    return pipeline("text-classification", model="sagar213/bert-base-spanish-wwm-uncased-finetuned-political_elsalvadore")
