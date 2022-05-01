import pages.analysis
import pages.default_assumptions
import pages.investment_criteria_tmp
import pages.investment_criteria
import pages.search

import streamlit as st

st.set_page_config(layout="wide", page_title="Real Estate Investment Analyzer", initial_sidebar_state="expanded")

PAGES = {
    # "Default Assumptions": pages.default_assumptions.app,
    "Investment Criteria": pages.investment_criteria.app,
    # "Review Assumptions": pages.investment_criteria_tmp.app,
    "Search": pages.search.app,
    "Property Details": pages.search.app,
    "Property Investment Worksheet": pages.search.app,
    "Scenario Analysis": pages.analysis.app,
    "Comparative Analysis": pages.analysis.app,
}

st.sidebar.title("Menu")
selection = st.sidebar.radio("Pages", list(PAGES.keys()))
page = PAGES[selection]
page()