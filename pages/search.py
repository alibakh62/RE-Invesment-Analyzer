from re import sub
import requests
import streamlit as st
import numpy as np
import pandas as pd
import json
import plotly.express as px
import src.api as api
import time
import pickle
from src.utils import DataPrep, InvestmentAssumptions
from src.metrics import Metrics
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')


def app():
    """
    This is where user searches for properties
    """
    st.markdown("<h1 style='text-align: center; color: black;'>Search</h1>", unsafe_allow_html=True)

    # st text input
    address = st.text_input("Enter an address, neighborhood, city, or zip code", key="search_address", placeholder="Dallas, TX")
    st.markdown("#")
    with st.container():
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            status_type = st.selectbox("Status", ["For Sale", "Recently Sold"], index=0)
            status_type = "ForSale" if status_type == "For Sale" else "RecentlySold"
        with c2:
            property_type = st.selectbox("Property Type", ["Multi-family", "Apartments", "Houses", "Manufactured", "Condos", "LotsLand", "Townhomes"], index=2)
        with c3:
            sort_by = st.selectbox("Sort By", ["Homes_for_You", "Price_High_Low", "Price_Low_High", "Newest", "Bedrooms", "Bathrooms", "Square_Feet"])
    
    st.markdown("#")
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1])
        with c1:
            price = st.slider("Price", min_value=20_000, max_value=1_000_000, value=[50_000, 350_000], step=1000)
        with c2:
            bedrooms = st.slider("Bedrooms", min_value=0, max_value=10, value=[1, 3], step=1)
        with c3:
            bathrooms = st.slider("Bathrooms", min_value=0, max_value=10, value=[1, 3], step=1)
        with c4:
            square_feet = st.slider("Square Feet", min_value=0, max_value=10_000, value=[100, 1_500], step=100)
        with c5:
            build_year = st.slider("Build Year", min_value=1970, max_value=2020, value=[2000, 2020], step=1)

    st.markdown("#")
    with st.container():
        days_on_zillow = st.selectbox("Days on Zillow", ["1", "7", "14", "30", "90", "6m", "12m", "24m", "36m", "All"], index=3)
        # is_basement = st.checkbox("Is basement finished?")
        # is_pending = st.checkbox("Is the property pending under contract?")
        # is_coming_soon = st.checkbox("Is the property coming soon?")

    # with st.form("Search"):
        st.markdown("#")
        with st.container():
            c1, c2, c3 = st.columns([4,1,4])
            with c1:
                st.write('')
            with c2:
                search_button = st.button("Search") #st.form_submit_button("Search")
                st.markdown("#")
            with c3:
                st.write('')

            if search_button:
                query = {}
                query['address'] = address
                query['status_type'] = status_type
                query['property_type'] = property_type
                query['sort_by'] = sort_by
                query['price'] = price
                query['bedrooms'] = bedrooms
                query['bathrooms'] = bathrooms
                query['square_feet'] = square_feet
                query['build_year'] = build_year
                query['days_on_zillow'] = days_on_zillow

                # query API
                # response = api.property_search(query)
                # storing the response for further use
                # with open('data/search_data.json', 'w') as f:
                #     json.dump(response.json(), f)
                # df = pd.json_normalize(response.json()['props'])
                # df.to_csv("data/search_data.csv", index=False)
                df = pd.read_csv("data/search_data.csv")

                # clean up response
                cols = ['zpid', 'address', 'price', 'livingArea', 'lotAreaValue', 'bedrooms', 'bathrooms', 'listingSubType.is_FSBA', 'listingSubType.is_newHome', 'listingSubType.is_openHouse']
                df_ = df[cols]
                df_.columns = ['zpid', 'Address', 'Price', 'Living Area (sqft)', 'Lot Area (sqft)', 'Bedrooms', 'Bathrooms', 'is_FSBA', 'is_newHome', 'is_openHouse']
                df_["Living Area (sqft)"] = df_["Living Area (sqft)"].astype(int)
                df_["Lot Area (sqft)"] = df_["Lot Area (sqft)"].astype(int)
                df_.to_csv("data/search_data_refined.csv", index=False)
                # # ================================================================
                # df = pd.read_csv("data/search_data.csv")

                # df = pd.read_csv("data/output.csv")
                # # rearranage columns
                # df = df[['zpid', 'Cash Required', 'Cap Rate', 'Mortgage Payment', 'Total Payments', 'Total Interest', 'Minimum Monthly Expenses', 'Monthly Cash Flow', 'Annual Yield (CoC ROI)']]
                # # df = df.fillna('null')
                # df = df.sort_values(by=['Cap Rate'], ascending=False)

                # st.markdown("#")
                # st.markdown("---")
                # st.markdown("#")
                # st.markdown("<h2 style='text-align: center; color: black;'>Search Results</h2>", unsafe_allow_html=True)
                # st.markdown("#")
                # st.markdown("---")
                # st.dataframe(df_)


    with st.expander("Show the results in a table"):
        if st.checkbox("Show the results in a table"):
            # df_ = pd.read_csv("data/search_data_refined.csv")
            # df_out = df_.iloc[:10,].copy()  # limit to 10 rows for now
            # df_out["IRR (unleveraged)"] = 0
            # df_out["IRR (leveraged)"] = 0
            # df_out["Cap Rate"] = 0
            # df_out["Cash On Cash Return"] = 0
            # for i, row in df_out.iterrows():
            #     try:
            #         zpid = int(row['zpid'])
            #         print(zpid)
            #         dp = DataPrep(zpid)
            #         cash_flow = dp.get_cashflow()
            #         cash_flow_unleveraged = cash_flow['cash_flow_unleveraged']
            #         cash_flow_leveraged = cash_flow['cash_flow_leveraged']
            #         dates = dp.get_cashflow()['dates']
            #         dates_xirr = Metrics.xirr_dates(dates)
            #         irr_unleveraged = np.round((Metrics.xirr(values=cash_flow_unleveraged, dates=dates_xirr))*100, 2)
            #         irr_leveraged = np.round((Metrics.xirr(values=cash_flow_leveraged, dates=dates_xirr))*100, 2)
            #         cap_rate = Metrics.cap_rate(cash_flow['net_rents'], row['Price'])
            #         coc = Metrics.cash_on_cash_return(cash_flow['net_rents'], cash_flow['less_taxes'], cash_flow['cash_invested'])
            #         print("irr unleveraged: ", irr_unleveraged)
            #         print("irr leveraged: ", irr_leveraged)
            #         print("cap rate: ", cap_rate)
            #         print("cash on cash return: ", coc)
            #         df_out.loc[i, 'IRR (unleveraged)'] = irr_unleveraged
            #         df_out.loc[i, 'IRR (leveraged)'] = irr_leveraged
            #         df_out.loc[i, 'Cap Rate'] = cap_rate
            #         df_out.loc[i, 'Cash On Cash Return'] = coc
            #         time.sleep(5)
            #     except:
            #         pass
            # # re-arranging the columns
            # df_out = df_out[['zpid', 'Address', 'Price', 'IRR (unleveraged)', 'IRR (leveraged)', 'Cap Rate', 'Cash On Cash Return', 'Living Area (sqft)', 'Lot Area (sqft)', 'Bedrooms', 'Bathrooms', 'is_FSBA', 'is_newHome', 'is_openHouse']]
            # df_out.to_csv("data/search_data_with_metrics.csv", index=False)
            df_out = pd.read_csv("data/search_data_with_metrics.csv")
            st.markdown("#")
            st.markdown("---")
            st.markdown("#")
            st.markdown("<h2 style='text-align: center; color: black;'>Results</h2>", unsafe_allow_html=True)
            st.markdown("#")
            st.dataframe(df_out)


    with st.expander("Show the results in a map"):
        if st.checkbox("Show the results in a map"):
            df = pd.read_csv("data/search_data_with_metrics.csv")
            search = pd.read_csv("data/search_data.csv")
            df["latitude"] = search["latitude"]
            df["longitude"] = search["longitude"]
            px.set_mapbox_access_token(open("notebook/.mapbox_token").read())
            fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="Price", size="Price", hover_name="zpid", hover_data=["Address", "Price", 'IRR (unleveraged)', 'IRR (leveraged)', 'Cap Rate', 'Cash On Cash Return'], zoom=10, labels="zpid", height=600, color_continuous_scale=px.colors.cyclical.IceFire, size_max=15)
            st.markdown("#")
            st.markdown("---")
            st.markdown("#")
            st.markdown("<h2 style='text-align: center; color: black;'>Map</h2>", unsafe_allow_html=True)
            st.markdown("#")
            # this has to be done through st.plotly --> plotly.express.scatter_mapbox
            # st.map(df, zoom=10, use_container_width=True)
            st.plotly_chart(fig, use_container_width=True)

    # get property details
    # if True: #st.session_state.get('FormSubmitter:Search-Search'):
    with st.expander("Select a property for analysis"):
        with st.form("Select Property"):
            df = pd.read_csv("data/search_data.csv")
            # st.write(f"search state: {st.session_state}")
            # st.markdown("#")
            # st.markdown("---")
            # st.markdown("#")
            # st.markdown("<h1 style='text-align: center; color: black;'>Select a property for analysis</h1>", unsafe_allow_html=True)
            # st.markdown("#")
            selected_properties = st.selectbox("Select zpid of the properties you want to analyze", df['zpid'], key="selected_properties")
            submit_selected_properties = st.form_submit_button("Submit")
            if submit_selected_properties:
                with open("data/selected_properties.pkl", "wb") as f:
                    pickle.dump(selected_properties, f)
                st.success(f"You selected {selected_properties} properties")
    # else:
    #     st.write("No properties selected")
    # print(st.session_state.selected_properties)

    # print(response.text)