import pages.analysis
import pages.analysis_deprecated
import pages.default_assumptions
import pages.property_details
import pages.investment_criteria_deprecated
import pages.investment_criteria
import pages.search
import pages.search_deprecated
from streamlit_option_menu import option_menu

import streamlit as st

st.set_page_config(layout="wide", page_title="Real Estate Investment Analyzer", initial_sidebar_state="expanded")

PAGES = {
    # "Default Assumptions": pages.default_assumptions.app,
    "Investment Criteria": pages.investment_criteria.app,
    # "Investment Criteria_deprecated": pages.investment_criteria_deprecated.app,
    # "Review Assumptions": pages.investment_criteria_tmp.app,
    "Search": pages.search.app,
    # "Search_deprecated": pages.search_deprecated.app,
    "Property Details": pages.property_details.app,
    # "Property Investment Worksheet": pages.search.app,
    "Scenario Analysis": pages.analysis.app,
    # "Scenario Analysis-deprecated": pages.analysis_deprecated.app,
    "Comparative Analysis": pages.analysis.app,
}

with st.sidebar:
    selected = option_menu(
        menu_title="Investoria",
        options=list(PAGES.keys()),
        icons=["sliders", "search", "house", "graph-up-arrow", "bar-chart"],
        default_index=1,
    )

page = PAGES[selected]
page()



# st.sidebar.title("Menu")
# selection = st.sidebar.selectbox("Pages", list(PAGES.keys()))
# page = PAGES[selection]
# page()