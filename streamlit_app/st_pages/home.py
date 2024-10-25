import streamlit as st
from streamlit_lottie import st_lottie
from modules.cache_functions import cache_banner


def home_page():
    with st.columns([1, 2, 1])[1]:
        st.image(cache_banner(), use_column_width="auto")

    st.write(
        """
    <center>
        <h1 class="top">Omdena's Social Media Sentiment Analysis Tool for ACAPS Project</h1>
        <p class="caption">
            This project aims to develop a custom workflow that leverages AI-powered tools to gather real-time data on crisis triggers. By utilizing data from multiple sources such as Twitter, Google Trends, and news websites, we categorize public sentiment and provide actionable insights for data analysts and policymakers in various countries. Our goal is to offer precise, real-time information to support informed decision-making to predict crisis situations.
            <hr>
        </p>
    </center>
    """,
        unsafe_allow_html=True,
    )

    cols1 = st.columns([0.2, 1, 0.05, 1, 0.2])
    padding_row = "<br>"

    with cols1[1]:
        st.write(
            """
            <h3>Impact on Analysis and Decision Making</h3>
            <p>The slow pace and potential inaccuracies of manual sentiment analysis have significant implications for political analysis and decision-making in regions experiencing political, economic, and social unrest. Delays in obtaining real-time information hinder analysts and policymakers from proactively responding to public sentiment, leading to missed opportunities for engagement or intervention. Furthermore, inaccuracies in manual analysis can result in poorly informed strategies that not only fail to achieve objectives but also exacerbate public dissatisfaction and distrust, affecting political stability and undermining the democratic process.</p>
        """,
            unsafe_allow_html=True,
        )
        st.write(padding_row, unsafe_allow_html=True)

        st_lottie(
            "https://lottie.host/4bbcd636-eece-482f-8613-0e3ed93dafec/4ezAdnro3W.json",
            height=325,
        )
        st.write(padding_row, unsafe_allow_html=True)

        st.write(
            """
            <h3>Empowering Analysts with Real-Time Insights</h3>
            <p>The goal of this initiative is to provide analysts and policymakers in regions experiencing political, economic, and social unrest with real-time and accurate insights on public sentiment. By utilizing an advanced web interface to gather and visualize data from sources like Twitter, Google Trends, and news websites, the project enhances the ability to quickly respond to crises and improve the effectiveness of strategies and policies.</p>
        """, 
            unsafe_allow_html=True)

    with cols1[3]:
        st_lottie(
            "https://lottie.host/a786afd8-9903-4bed-8952-12b21b8016bd/PBO8x4JBEQ.json",
            height=325,
        )
        st.write(padding_row, unsafe_allow_html=True)

        st.write(
            f"""
            <br>
            <h3>The Need for an Automated Solution</h3>
            <p>The development of an AI-powered sentiment analysis tool is essential to overcoming the challenges of manual analysis. By applying advanced Natural Language Processing (NLP) techniques to various data sources, this tool provides a faster and more accurate process, enabling timely insights in response to emerging crises.</p>
            {'<br>'*5}
        """,
            unsafe_allow_html=True,
        )
        st.write(padding_row, unsafe_allow_html=True)

        st_lottie(
            "https://lottie.host/9c945dc7-e5d7-4148-b7f6-dfd748e1eb38/q0oJidkFyf.json",
            height=325,
        )

