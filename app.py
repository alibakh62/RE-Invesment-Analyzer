import pages.analysis
import pages.analysis_deprecated
import pages.analysis_multiple
import pages.default_assumptions
import pages.property_details
import pages.investment_criteria_deprecated
import pages.investment_criteria
import pages.search
import pages.search_deprecated
from streamlit_option_menu import option_menu

import streamlit as st

st.set_page_config(layout="wide", page_title="Real Estate Investment Analyzer", initial_sidebar_state="expanded")

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

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
        "Scenario Analysis 1+": pages.analysis_multiple.app,
        # "Scenario Analysis-deprecated": pages.analysis_deprecated.app,
        "Comparative Analysis": pages.analysis.app,
    }

    with st.sidebar:
        selected = option_menu(
            menu_title="Investoria",
            options=list(PAGES.keys()),
            icons=["sliders", "search", "house", "graph-up-arrow", "bar-chart"],
            default_index=0,
        )

    page = PAGES[selected]
    page()



# st.sidebar.title("Menu")
# selection = st.sidebar.selectbox("Pages", list(PAGES.keys()))
# page = PAGES[selection]
# page()