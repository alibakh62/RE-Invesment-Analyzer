import streamlit as st
from streamlit_option_menu import option_menu
import json
import requests
import shutil
import os
import pandas as pd
import numpy as np
import src.api as api
import pickle
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')


def download_images(image_url, zpid):
    """
    Download images from Zillow API.
    """
    filename = image_url.split("/")[-1]
    if not os.path.exists(f"data/images/{str(zpid)}"):
        os.mkdir(f"data/images/{str(zpid)}")
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream=True)
    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        
        # Open a local file with wb ( write binary ) permission.
        with open(f"data/images/{str(zpid)}/{filename}",'wb') as f:
            shutil.copyfileobj(r.raw, f)
            
        print('Image sucessfully Downloaded: ',filename)
    else:
        print('Image Couldn\'t be retreived')

def app():
    """
    This page will show property details info
    """
    selected = option_menu(
        menu_title=None,
        options=["Property Information", "Neighborhood Information", "Tax Information", "Property Images"],
        icons=["house", "geo", "bank", "image"],
        default_index=0,
        orientation="horizontal",
        # for more styling refer to: https://github.com/victoryhb/streamlit-option-menu
    )
    if selected == "Property Information":
        st.title("Property Information")
    elif selected == "Neighborhood Information":
        st.title("Neighborhood Information")
    elif selected == "Tax Information":
        st.title("Tax Information")
    elif selected == "Property Images":
        with open('data/selected_properties.pkl', 'rb') as f:
            zpid = pickle.load(f)
        prop_det = api.property_detail(zpid).json()
        if not os.path.exists(f"data/images/{str(zpid)}"):
            images = api.property_image(zpid).json()
            for image_url in images['images']:
                download_images(image_url, zpid)
        st.markdown("<h1 style='text-align: center; color: black;'>Images</h1>", unsafe_allow_html=True)
        list_of_images = os.listdir(f"data/images/{str(zpid)}")
        for image in list_of_images:
            st.image(f"data/images/{str(zpid)}/{image}")
        pass