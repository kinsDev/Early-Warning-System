import re
import streamlit as st

from sklearn.feature_extraction.text import CountVectorizer
from modules.cache_functions import sentiment_pipeline, cache_pce_logo, cache_omdena_logo
from modules.constants import SENTIMENT_TAGS


def load_header(title):
    cols = st.columns([4, 1, 0.7, 1.5])
    with cols[0]:
        st.write(
            """<h2 class='custom' style='color:#00000099'>{}</h2>""".format(title),
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.image(cache_pce_logo(), use_column_width=True)
    with cols[3]:
        st.image(cache_omdena_logo(), use_column_width=True)

def get_top_ngram(corpus, n=None):
    vec = CountVectorizer(
        ngram_range=(n, n), 
        max_df=0.9
    ).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return words_freq[:15]

def is_valid_twitter_url(url):
    pattern = r"^https://(www\.)?(twitter|x)\.com/.+/status/\d+$"
    return re.match(pattern, url) is not None

def tokenize(text):  # noqa: F811
    """basic tokenize method with word character, non word character and digits"""
    text = re.sub(r" +", " ", str(text))
    text = re.split(r"(\d+|[a-zA-ZğüşıöçĞÜŞİÖÇ]+|\W)", text)
    text = list(filter(lambda x: x != "" and x != " ", text))
    sent_tokenized = " ".join(text)
    return sent_tokenized

def add_columns_for_graphs():
    master_df = st.session_state["master_df"]
    original_tweet = st.session_state["original_tweet"]

    data = {
        "viewCount": original_tweet.viewCount.iloc[0],
        "likeCount": original_tweet.likeCount.iloc[0],
        "retweetCount": original_tweet.retweetCount.iloc[0],
        "replyCount": original_tweet.replyCount.iloc[0],
        "author__followers": original_tweet.author__followers.iloc[0],
        "is_author_verified": original_tweet.author__verified.iloc[0],
        "text": original_tweet.text.iloc[0],
        "url": original_tweet.url.iloc[0],
    }

    pos_sum = master_df.loc[master_df['predictedSentiment'] == 1].shape[0]
    neu_sum = master_df.loc[master_df['predictedSentiment'] == 0].shape[0]
    neg_sum = master_df.loc[master_df['predictedSentiment'] == -1].shape[0]

    sums = {"Positivo": pos_sum, "Neutral": neu_sum, "Negativo": neg_sum}
    overall_sentiment = max(sums, key=sums.get)

    data.update(
        {
            "overall_sentiment": overall_sentiment,
            "positive": pos_sum,
            "neutral": neu_sum,
            "negative": neg_sum,
        }
    )

    master_df["account_creation_time"] = (
        (master_df["createdAt"].dt.year - master_df["author__createdAt"].dt.year) * 12 + 
        (master_df["createdAt"].dt.month - master_df["author__createdAt"].dt.month)
        )

    return data, master_df

def apply_sentiment_pipeline(text):
    pipeline = sentiment_pipeline()

    return SENTIMENT_TAGS[pipeline(text)[0]['label']]
