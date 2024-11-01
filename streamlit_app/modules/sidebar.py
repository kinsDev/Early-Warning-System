import streamlit as st
from st_on_hover_tabs import on_hover_tabs

from st_pages.home import home_page
from st_pages.analyse import analyse_page
from st_pages.dashboard import dashboard
from st_pages.about import about_us_page
from modules.constants import CONTRIBUTORS, DEFAULT_CHOICE
from modules.utils import load_header


def launch_sidebar():
    with st.sidebar:
        st.write("<br>" * 4, unsafe_allow_html=True)
        selected_task = on_hover_tabs(
            tabName=["Home Page", "Analyse Sentiment", "Dashboard", "About Us"],
            iconName=["home", "engineering", "equalizer", "contact_support"],
            styles={
                "navtab": {"background-color": "#fff"},
                "tabOptionsStyle": {
                    ":hover :hover": {"color": "#170034", "cursor": "pointer"}
                },
            },
            default_choice=DEFAULT_CHOICE,
        )

    if selected_task == "Home Page":
        with st.spinner("Loading main page..."):
            home_page()

    elif selected_task == "Analyse Sentiment":
        with st.spinner("Loading Analyze Tweet..."):
            analyse_page()

    elif selected_task == "Dashboard":
        if "master_df" in st.session_state and st.session_state["master_df"] is None:
            load_header("Dashboard")
            st.info("Please analyze a tweet before accessing the dashboard")
        else:
            with st.spinner("Loading dashboard..."):
                dashboard()

    elif selected_task == "About Us":
        about_us_page(CONTRIBUTORS)