import pages.analysis
import pages.default_assumptions
import pages.review_assumptions
import pages.user_assumptions
import pages.search

import streamlit as st

st.set_page_config(layout="wide")

PAGES = {
    "Default Assumptions": pages.default_assumptions.app,
    "User Assumptions": pages.user_assumptions.app,
    "Review Assumptions": pages.review_assumptions.app,
    "Search": pages.search.app,
    "Analysis": pages.analysis.app
}

st.sidebar.title("Menu")
selection = st.sidebar.radio("Pages", list(PAGES.keys()))
page = PAGES[selection]
page()