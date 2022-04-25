import requests
import streamlit as st
import pandas as pd
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

def app():
    """
    This is where user searches for properties
    """
    st.title("Real Estate Investment Analyzer")

    # st text input
    st.text_input("Enter an address, neighborhood, city, or zip code", key="search_address")
    st.button("Analyze", key="search_button")

    if st.session_state.search_button:
        # get property details
        # url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

        # querystring = {"location":f"{st.session_state.search_address}","home_type":"Houses"}

        # headers = {
        # 	"X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
        # 	"X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
        # }

        # response = requests.request("GET", url, headers=headers, params=querystring)
        # data_json = response.json()
        # df = pd.json_normalize(data_json['props'])
        # df.to_csv("data.csv", index=False)
        # df = pd.read_csv("data.csv")
        df = pd.read_csv("data/output.csv")
        # rearranage columns
        df = df[['zpid', 'Cash Required', 'Cap Rate', 'Mortgage Payment', 'Total Payments', 'Total Interest', 'Minimum Monthly Expenses', 'Monthly Cash Flow', 'Annual Yield (CoC ROI)']]
        # df = df.fillna('null')
        df = df.sort_values(by=['Cap Rate'], ascending=False)
        st.dataframe(df)

        # get property details
        # selected_properties = st.multiselect("Select properties you want to analyze", df['address'], key="selected_properties")
        # print(st.session_state.selected_properties)

    # print(response.text)