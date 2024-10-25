import streamlit as st
from modules.utils import load_header
from modules.constants import CONTRIBUTORS
from modules.cache_functions import cache_contributors, load_about_html


def about_us_page(contributors):
    load_header("Conozcan a los colaboradores del desafío")

    all_contributors = cache_contributors()

    # Padding with empty strings
    while len(all_contributors) % 3 != 0:
        all_contributors.append(["", None])

    # Split the list into chunks of 3
    chunks = [all_contributors[i:i + 3] for i in range(0, len(all_contributors), 3)]

    contributors_string = ""

    for chunk in chunks:
        cells = ""
        for contributor in chunk:
            if contributor[1] is None:
                cells += f"<td>{contributor[0]}</td>"
            else:
                cells += f"<td><a href='{contributor[1]}'>{contributor[0]}</a></td>"
        contributors_string += "<tr>" + cells + "</tr>"
   
    st.write(load_about_html().format(team=contributors_string), unsafe_allow_html=True)

