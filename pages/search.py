import os
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
from src.config import *
from src.metrics import Metrics
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

import logging

# logdatetime = time.strftime("%m%d%Y_%H%M%S")
logdatetime = time.strftime("%m%d%Y")
logging.basicConfig(level=logging.INFO, 
		    format='%(asctime)s %(message)s', 
		    datefmt='%m/%d/%Y %I:%M:%S %p', 
		    filename= f"{LOG_DIR}/{LOG_PROP_DETAILS}_{logdatetime}.log", 
		    filemode='w',
		    force=True)


def cleanup_query_results(df, save_filename=None):
    cols = ['zpid', 'address', 'price', 'livingArea', 'lotAreaValue', 'bedrooms', 'bathrooms']
    df_ = df[cols]
    df_.columns = ['zpid', 'Address', 'Price', 'Living Area (sqft)', 'Lot Area (sqft)', 'Bedrooms', 'Bathrooms']
    df_["Living Area (sqft)"] = df_["Living Area (sqft)"].astype(int)
    df_["Lot Area (sqft)"] = df_["Lot Area (sqft)"].astype(int)
    if save_filename is not None:
        df_.to_csv(os.path.join(BASE_DIR, save_filename), index=False)
    else:
        df_.to_csv(os.path.join(BASE_DIR, PROP_SEARCH_REFINED), index=False) 
    return df_


def calc_metrics(df_, save_filename=None):
    df_out = df_.iloc[:20,].copy()  # limit to 20 rows for now
    # df_out = df_.copy()
    df_out["IRR (unleveraged)"] = 0
    df_out["IRR (leveraged)"] = 0
    df_out["Cap Rate"] = 0
    df_out["Cash On Cash Return"] = 0
    progress_bar = st.progress(0)
    for i, row in df_out.iterrows():
        try:
            zpid = int(row['zpid'])
            logging.info(f"Calculating metrics for zpid {zpid}")
            dp = DataPrep(zpid)
            cash_flow = dp.get_cashflow()
            cash_flow_unleveraged = cash_flow['cash_flow_unleveraged']
            cash_flow_leveraged = cash_flow['cash_flow_leveraged']
            dates = dp.get_cashflow()['dates']
            dates_xirr = Metrics.xirr_dates(dates)
            irr_unleveraged = np.round((Metrics.xirr(values=cash_flow_unleveraged, dates=dates_xirr))*100, 2)
            irr_leveraged = np.round((Metrics.xirr(values=cash_flow_leveraged, dates=dates_xirr))*100, 2)
            cap_rate = Metrics.cap_rate(cash_flow['net_rents'], row['Price'])
            coc = Metrics.cash_on_cash_return(cash_flow['net_rents'], cash_flow['less_taxes'], cash_flow['cash_invested'])
            logging.info("irr unleveraged: ", irr_unleveraged)
            logging.info("irr leveraged: ", irr_leveraged)
            logging.info("cap rate: ", cap_rate)
            logging.info("cash on cash return: ", coc)
            df_out.loc[i, 'IRR (unleveraged)'] = irr_unleveraged
            df_out.loc[i, 'IRR (leveraged)'] = irr_leveraged
            df_out.loc[i, 'Cap Rate'] = cap_rate
            df_out.loc[i, 'Cash On Cash Return'] = coc
            time.sleep(5)
            progress_bar.progress(i+1)
        except:
            pass
    # re-arranging the columns
    df_out = df_out[['zpid', 'Address', 'Price', 'IRR (unleveraged)', 'IRR (leveraged)', 'Cap Rate', 'Cash On Cash Return', 'Living Area (sqft)', 'Lot Area (sqft)', 'Bedrooms', 'Bathrooms']]
    df_out.to_csv(os.path.join(BASE_DIR, PROP_SEARCH_WITH_METRICS), index=False)
    return df_out


def filter_by_user_metrics(df_out, user_metrics, save_filename=None):
    if user_metrics["metric_selected"] == "Cap Rate":
        df_out = df_out.loc[df_out['Cap Rate'] > user_metrics["metric_min"],]
        df_out = df_out.sort_values(by=['Cap Rate'], ascending=False)
    elif user_metrics["metric_selected"] == "IRR Unleveraged":
        df_out = df_out.loc[df_out['IRR (unleveraged)'] > user_metrics["metric_min"],]
        df_out = df_out.sort_values(by=['Cap Rate'], ascending=False)
    elif user_metrics["metric_selected"] == "IRR Leveraged":
        df_out = df_out.loc[df_out['IRR (leveraged)'] > user_metrics["metric_min"],]
        df_out = df_out.sort_values(by=['Cap Rate'], ascending=False)
    elif user_metrics["metric_selected"] == "Cash On Cash Return":
        df_out = df_out.loc[df_out['Cash On Cash Return'] > user_metrics["metric_min"],]
        df_out = df_out.sort_values(by=['Cap Rate'], ascending=False)
    if save_filename is not None:
        df_out.to_csv(os.path.join(BASE_DIR, save_filename), index=False)
    else:
        df_out.to_csv(os.path.join(BASE_DIR, PROP_SEARCH_WITH_METRICS_FILTERED), index=False)
    return df_out



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
            status_type = st.selectbox("Status", ["For Sale", "Recently Sold"], index=0, key="status_type")
            st.session_state.status_type_refined = "ForSale" if status_type == "For Sale" else "RecentlySold"
        with c2:
            property_type = st.selectbox("Property Type", ["Multi-family", "Apartments", "Houses", "Manufactured", "Condos", "LotsLand", "Townhomes"], index=2, key="property_type")
        with c3:
            sort_by = st.selectbox("Sort By", ["Homes_for_You", "Price_High_Low", "Price_Low_High", "Newest", "Bedrooms", "Bathrooms", "Square_Feet"], index=0, key="sort_by")
    
    st.markdown("#")
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1])
        with c1:
            price = st.slider("Price", min_value=20_000, max_value=1_000_000, value=[50_000, 350_000], step=1000, key="price")
        with c2:
            bedrooms = st.slider("Bedrooms", min_value=0, max_value=10, value=[1, 3], step=1, key="bedrooms")
        with c3:
            bathrooms = st.slider("Bathrooms", min_value=0, max_value=10, value=[1, 3], step=1, key="bathrooms")
        with c4:
            square_feet = st.slider("Square Feet", min_value=0, max_value=10_000, value=[100, 1_500], step=100, key="square_feet")
        with c5:
            build_year = st.slider("Build Year", min_value=1970, max_value=2020, value=[2000, 2020], step=1, key="build_year")

    st.markdown("#")
    with st.container():
        c1, c2, c3 = st.columns([2,1,2])
        with c1:
            st.write("")
        with c2:
            days_on_zillow = st.selectbox("Days on Zillow", ["1", "7", "14", "30", "90", "6m", "12m", "24m", "36m", "All"], index=3, key="days_on_zillow")
        with c3:
            st.write("")

    # with st.form("Search"):
    st.markdown("#")
    with st.container():
        c1, c2, c3 = st.columns([4,1,4])
        with c1:
            st.write('')
        with c2:
            search_button = st.button("Search", key="search_button")
            st.markdown("#")
        with c3:
            st.write('')

    if st.session_state.search_button:
        query = {}
        query['address'] = st.session_state.search_address
        query['status_type'] = st.session_state.status_type_refined
        query['property_type'] = st.session_state.property_type
        query['sort_by'] = st.session_state.sort_by
        query['price'] = st.session_state.price
        query['bedrooms'] = st.session_state.bedrooms
        query['bathrooms'] = st.session_state.bathrooms
        query['square_feet'] = st.session_state.square_feet
        query['build_year'] = st.session_state.build_year
        query['days_on_zillow'] = st.session_state.days_on_zillow

        # query API
        if GET_FROM_API:
            response = api.property_search(query)
            # storing the response for further use
            with open(f'{BASE_DIR}/{PROP_SEARCH_RESPONSE}', 'w') as f:
                json.dump(response.json(), f)
            df = pd.json_normalize(response.json()['props'])
            df.to_csv(os.path.join(BASE_DIR, PROP_SEARCH), index=False)
        else:
            df = pd.read_csv(os.path.join(BASE_DIR, PROP_SEARCH))

        # clean up response
        df_ = cleanup_query_results(df)
        df_out = calc_metrics(df_)

    # show results in a table
    try:
        with st.expander("Show the results in a table"):
            df_out = pd.read_csv(os.path.join(BASE_DIR, PROP_SEARCH_WITH_METRICS))
            with open(os.path.join(BASE_DIR, USER_METRICS), 'r') as f:
                user_metrics = json.load(f)
            df_out_ = filter_by_user_metrics(df_out, user_metrics)
            st.markdown("#")
            st.markdown("---")
            st.markdown("#")
            st.markdown("<h2 style='text-align: center; color: black;'>Results</h2>", unsafe_allow_html=True)
            if len(df_out_) > 0:
                st.markdown("#")
                st.dataframe(df_out_)
                st.markdown("#")
                # st.table(df_out_)
            elif len(df_out) == 0:
                st.markdown("#")
                st.error("No results found matching your search criteria")
            elif (len(df_out) > 0) & (len(df_out_) == 0):
                st.markdown("#")
                st.error("No results found matching your investment criteria")
    except FileNotFoundError:
        with st.expander("Show the results in a table"):
            st.markdown("#")
            st.error("No results found! Make sure you have entered a valid address.")

    # show the results in a map
    try:
        with st.expander("Show the results in a map"):
            if st.checkbox("Show the results in a map"):
                df = pd.read_csv(os.path.join(BASE_DIR, PROP_SEARCH_WITH_METRICS_FILTERED))
                if len(df) > 0:
                    search = pd.read_csv(os.path.join(BASE_DIR, PROP_SEARCH))
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
                else:
                    st.markdown("#")
                    st.error("No results found matching your investment criteria")
    except FileNotFoundError:
        with st.expander("Show the results in a map"):
            st.markdown("#")
            st.error("No results found! Make sure you have entered a valid address.")

    # select a list of properties for further analysis
    try:
        with st.expander("Select a property for analysis"):
            df = pd.read_csv(os.path.join(BASE_DIR, PROP_SEARCH_WITH_METRICS_FILTERED))
            if len(df) > 0:
                selected_properties = st.selectbox("Select zpid of the properties you want to analyze", df['zpid'], key="selected_properties")
                submit_selected_properties = st.button("Submit")
                if submit_selected_properties:
                    with open(f"{BASE_DIR}/{SELECTED_PROPERTY}", "wb") as f:
                        pickle.dump(selected_properties, f)
                    st.success(f"You selected {selected_properties} properties")
            else:
                st.markdown("#")
                st.error("No results found matching your investment criteria")
    except FileNotFoundError:
        with st.expander("Select a property for analysis"):
            st.markdown("#")
            st.error("No results found! Make sure you have entered a valid address.")