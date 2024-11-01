import streamlit as st
import requests
from datetime import datetime

def fetch_reliefweb_data(limit):
    url = "https://api.reliefweb.int/v1/reports"
    params = {
        "appname": "apidoc",
        "limit": limit,
        "profile": "full",
        "sort[]": "date:desc"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data from Reliefweb API")
        return None

def reliefweb_page():
    st.title("ReliefWeb Reports")

    # slider for the user to select the number of reports
    num_reports = st.slider("Select number of reports to fetch", min_value=1, max_value=50, value=10)

    data = fetch_reliefweb_data(num_reports)
    if data:
        reports = data.get("data", [])
        st.write(f"Number of reports fetched: {len(reports)}")
        for report in reports:
            title = report["fields"].get("title", "No Title")
            date_str = report["fields"].get("date", {}).get("created", "No Date")
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z") if date_str != "No Date" else None
            formatted_date = date.strftime("%B %d, %Y %H:%M:%S %Z") if date else "No Date"
            summary = report["fields"].get("body-html", "No Summary Available")
            st.subheader(title)
            st.write(f"Date: {formatted_date}")
            st.markdown(summary, unsafe_allow_html=True)
            st.markdown("---")

if __name__ == "__main__":
    reliefweb_page()