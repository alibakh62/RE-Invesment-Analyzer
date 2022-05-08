import streamlit as st
from streamlit_option_menu import option_menu
import json
import requests
import shutil
import os
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import src.api as api
import pickle
from src.config import *
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


def download_image_from_api(image_url, zpid, filename):
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream=True)
    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        # Open a local file with wb ( write binary ) permission.
        with open(f"{BASE_DIR}/{PROP_IMAGES}/{str(zpid)}/{filename}",'wb') as f:
            shutil.copyfileobj(r.raw, f)
        logging.info(f'Image {filename} sucessfully Downloaded: ')
    else:
        logging.warning(f'Image {filename} Couldn\'t be retreived')


def save_image(image_url, zpid, save_dir):
    """
    Download images from Zillow API.
    """
    filename = image_url.split("/")[-1]
    logging.info(f'Downloading images for {zpid}')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    download_image_from_api(image_url, zpid, filename)


def get_tax_history(prop_det):
    tax_paid = []
    prop_value = []
    tax_rate_hist = []
    tax_year = []
    for i in range(len(prop_det["taxHistory"])):
        if prop_det["taxHistory"][i]["taxPaid"] is not None:
            tax_paid.append(prop_det["taxHistory"][i]["taxPaid"])
            prop_value.append(prop_det["taxHistory"][i]["value"])
            tax_rate_hist.append(np.round(prop_det["taxHistory"][i]["taxPaid"]/prop_det["taxHistory"][i]["value"]*100, 2))
            tax_year.append(datetime.fromtimestamp(prop_det["taxHistory"][i]["time"] / 1e3).strftime('%Y-%m-%d'))
    return tax_paid, prop_value, tax_rate_hist, tax_year


def app():
    """
    This page will show property details info
    """
    # Setting up the navigation bar
    selected = option_menu(
        menu_title=None,
        options=["Property Details", "Neighborhood", "Tax History", "Property Images"],
        icons=["house", "geo", "bank", "image"],
        default_index=0,
        orientation="horizontal",
        # for more styling refer to: https://github.com/victoryhb/streamlit-option-menu
    )
    # Getting property details info
    with open(f'{BASE_DIR}/{SELECTED_PROPERTY}', 'rb') as f:
        zpid = pickle.load(f)
    try:
        with open(f"{BASE_DIR}/{PROP_DETAIL_RESPONSE}_{str(zpid)}.json", "r") as f:
                prop_det = json.load(f)
    except:
        prop_det = api.property_detail(zpid).json()
    
    # Different pages of property details
    if selected == "Property Details":
        st.markdown("<h1 style='text-align: center; color: black;'>Property Info</h1>", unsafe_allow_html=True)
    elif selected == "Neighborhood":
        st.markdown("<h1 style='text-align: center; color: black;'>Neighborhood</h1>", unsafe_allow_html=True)
    elif selected == "Tax History":
        st.markdown("<h1 style='text-align: center; color: black;'>Tax</h1>", unsafe_allow_html=True)
        tax_paid, prop_value, tax_rate_hist, tax_year = get_tax_history(prop_det)

        st.markdown("#")
        st.markdown("<h3 style='text-align: center; color: black;'>Tax Paid</h1>", unsafe_allow_html=True)
        fig = px.line(x=tax_year[::-1], y=tax_paid[::-1], labels={"x": "Year", "y": "Tax ($)"}, text=tax_paid[::-1])
        fig.update_traces(textposition='top center')
        # fig.update_layout(title_text='Tax Rate History', title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#")
        st.markdown("<h3 style='text-align: center; color: black;'>Tax Rate</h1>", unsafe_allow_html=True)
        fig = px.line(x=tax_year[::-1], y=tax_rate_hist[::-1], labels={"x": "Year", "y": "Tax Rate"}, text=tax_rate_hist[::-1])
        fig.update_traces(textposition='top center')
        # fig.update_layout(title_text='Tax Rate History', title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#")
        st.markdown("<h3 style='text-align: center; color: black;'>Property Value</h1>", unsafe_allow_html=True)
        fig = px.line(x=tax_year[::-1], y=prop_value[::-1], labels={"x": "Year", "y": "Value ($)"}, text=prop_value[::-1])
        fig.update_traces(textposition='top center')
        # fig.update_layout(title_text='Tax Rate History', title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

    elif selected == "Property Images":
        image_dir = f"{BASE_DIR}/{PROP_IMAGES}/{str(zpid)}"
        if not os.path.exists(image_dir):
            logging.info(f"Initializing image download for {zpid}")
            images = api.property_image(zpid).json()
            if len(images["images"]) > 0:
                for image_url in images['images']:
                    save_image(image_url, zpid, image_dir)
            else:
                logging.info(f"No images for {zpid}")
                st.error(f"No images for {zpid}")
        elif os.listdir(image_dir) == []:
            logging.info(f"Initializing image download for {zpid}")
            images = api.property_image(zpid).json()
            for image_url in images['images']:
                save_image(image_url, zpid, image_dir)
        else:
            logging.info(f"Images for {zpid} already downloaded")
        st.markdown("<h1 style='text-align: center; color: black;'>Images</h1>", unsafe_allow_html=True)
        list_of_images = os.listdir(image_dir)
        for image in list_of_images:
            st.image(f"{image_dir}/{image}")
        pass