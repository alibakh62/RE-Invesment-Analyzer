import requests
import streamlit as st
import pandas as pd
import json
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')

@st.cache
def get_data(query):
    # get property details
    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

    querystring = {f"location": str(query['address']),
                    "page":"2",
                    "status_type":str(query['status_type']),
                    "home_type":str(query['property_type']),
                    "sort":str(query['sort_by']),
                    "minPrice":str(query['price'][0]),
                    "maxPrice":str(query['price'][1]),
                    "bathsMin":str(query['bathrooms'][0]),
                    "bathsMax":str(query['bathrooms'][1]),
                    "bedsMin":str(query['bedrooms'][0]),
                    "bedsMax":str(query['bedrooms'][1]),
                    "sqftMin":str(query['square_feet'][0]),
                    "sqftMax":str(query['square_feet'][1]),
                    "buildYearMin":str(query['build_year'][0]),
                    "buildYearMax":str(query['build_year'][1]),
                    "daysOn":str(query['days_on_zillow']),}

    headers = {
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com",
        "X-RapidAPI-Key": "a271625fdbmsh9c07327c04cb02bp1314d1jsn9ac44145b089"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response

def app():
    """
    This is where user searches for properties
    """
    st.markdown("<h1 style='text-align: center; color: black;'>Search</h1>", unsafe_allow_html=True)
    # st.markdown("<p style='text-align: center; color: grey;'>Enter an address, neighborhood, city, or zip code.</p>", unsafe_allow_html=True)

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

    st.markdown("#")
    with st.container():
        c1, c2, c3 = st.columns([4,1,4])
        with c1:
            st.write('')
        with c2:
            search_button = st.button("Search", key="search_button")
        with c3:
            st.write('')

    if st.session_state.search_button:
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
        # response = get_data(query)
        # with open('data/search_data.json', 'w') as f:
        #     json.dump(response.json(), f)
        # df = pd.json_normalize(response.json()['props'])
        # df.to_csv("data/search_data.csv", index=False)
        df = pd.read_csv("data/search_data.csv")

        # clean up response
        cols = ['zpid', 'address', 'price', 'listingDateTime', 'livingArea', 'lotAreaValue', 'bedrooms', 'bathrooms', 'listingSubType.is_FSBA', 'listingSubType.is_newHome', 'listingSubType.is_openHouse']
        df_ = df[cols]
        df_.columns = ['zpid', 'Address', 'Price', 'Listing DateTime', 'Living Area (sqft)', 'Lot Area (sqft)', 'Bedrooms', 'Bathrooms', 'is_FSBA', 'is_newHome', 'is_openHouse']
        df_["Living Area (sqft)"] = df_["Living Area (sqft)"].astype(int)
        df_["Lot Area (sqft)"] = df_["Lot Area (sqft)"].astype(int)
        # # ================================================================
        # df = pd.read_csv("data/search_data.csv")

        # df = pd.read_csv("data/output.csv")
        # # rearranage columns
        # df = df[['zpid', 'Cash Required', 'Cap Rate', 'Mortgage Payment', 'Total Payments', 'Total Interest', 'Minimum Monthly Expenses', 'Monthly Cash Flow', 'Annual Yield (CoC ROI)']]
        # # df = df.fillna('null')
        # df = df.sort_values(by=['Cap Rate'], ascending=False)

        st.markdown("#")
        st.markdown("---")
        st.markdown("#")
        st.markdown("<h2 style='text-align: center; color: black;'>Search Results</h2>", unsafe_allow_html=True)
        st.markdown("#")
        st.dataframe(df_)
        # st.json(query)
        # st.json(querystring)
        # st.json(response.json())

        # get property details
        # selected_properties = st.multiselect("Select properties you want to analyze", df['address'], key="selected_properties")
        # print(st.session_state.selected_properties)

    # print(response.text)