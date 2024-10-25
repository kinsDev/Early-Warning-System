import streamlit as st
from modules.generate_pdf import construct_pdf
from modules.utils import load_header, add_columns_for_graphs
from modules.graph_functions import (
    metrics_bar,
    most_common_trigrams,
    display_word_cloud,
    create_scatter_plot,
    display_target_count,
    sentiment_over_date,
    stacked_bar_fig,
    clean_and_plot_locations,
)


def dashboard():
    # Update master_df and calculate tweet data
    st.session_state["tweet_data"], st.session_state["master_df"] = add_columns_for_graphs()
    master_df = st.session_state["master_df"]
    tweet_data = st.session_state["tweet_data"]

    load_header("Tablero de Comando")
    metrics_bar(tweet_data, master_df)

    st.session_state["sentiment_over_date"] = sentiment_over_date(master_df)
    st.session_state["display_target_count"] = display_target_count(master_df)
    st.session_state["display_word_cloud"] = display_word_cloud(master_df)
    st.session_state["most_common_trigrams"] = most_common_trigrams(master_df)
    st.session_state["create_scatter_plot"] = create_scatter_plot(master_df)
    st.session_state["stacked_bar_fig"] = stacked_bar_fig(master_df)
    st.session_state["locations_graphic"] = clean_and_plot_locations(master_df)

    row2 = st.columns([2.25, 1.75])

    with row2[0]:
        with st.container(border=True):
            st.write("Nube de Palabras - Términos más comunes")
            st.plotly_chart(
                st.session_state["display_word_cloud"], use_container_width=True
            )

    with row2[1]:
        with st.container(border=True):
            st.write("Tweet Original")
            pdf_data = construct_pdf()
            cols = st.columns(2)
            with cols[0]:
                st.metric(label="Views 👁️", value=tweet_data["viewCount"])
                st.metric(label="Likes ❤️", value=tweet_data["likeCount"])
                st.metric(label="Retweets 🔁", value=tweet_data["retweetCount"])
                if pdf_data:
                    st.download_button(
                        label="Create PDF",
                        data=pdf_data,
                        file_name="report_sentimient_analisis.pdf",
                        use_container_width=True,
                    )
            with cols[1]:
                st.metric(label="Followers 👥", value=tweet_data["author__followers"])
                st.metric(label="Replies 💬", value=tweet_data["replyCount"])
                verified_status = "Verified" if tweet_data["is_author_verified"] else "False"
                st.metric(label="Autor Verified 🔐", value=verified_status)
                st.link_button(
                    "Go to Tweet", url=tweet_data["url"], use_container_width=True
                )

    row3 = st.columns([2, 2])

    with row3[0]:
        for graph in [
            st.session_state["sentiment_over_date"],
            st.session_state["display_target_count"]
        ]:
            with st.container(border=True):
                st.plotly_chart(graph, use_container_width=True)

    with row3[1]:
        for graph in [
            st.session_state["most_common_trigrams"],
            st.session_state["create_scatter_plot"],
        ]:
            with st.container(border=True):
                st.plotly_chart(graph, use_container_width=True)

    row4 = st.columns([2, 2])

    with row4[0]:
        for graph in [
            st.session_state["stacked_bar_fig"]
        ]:
            with st.container(border=True):
                st.plotly_chart(graph, use_container_width=True)

    with row4[1]:
        for graph in [
            st.session_state["locations_graphic"]
        ]:
            with st.container(border=True):
                st.plotly_chart(graph, use_container_width=True)

