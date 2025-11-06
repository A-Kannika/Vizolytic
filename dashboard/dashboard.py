import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import base64
warnings.filterwarnings('ignore')

# create the page title
def page_title():
    LOGO_IMAGE = "assets/icon1.png"
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1rem !important;
        }

        .container {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 15px;
            padding: 10px 0;
        }
        .logo-text {
            font-weight: 600 !important;
            font-size: 30px !important;
            color: #008080 !important;
            margin: 0;
        }
        .logo-img {
            width: 80px; 
            height: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Convert image to base64
    with open(LOGO_IMAGE, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <div class="container">
            <img class="logo-img" src="data:image/png;base64,{encoded}">
            <p class="logo-text">Vizolytic – Turning Data Into Decisions</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    st.set_page_config(
        page_title="VIZOLYTIC Application ",
        page_icon="assets/icon1.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Create the page title
    page_title()

if __name__== "__main__":
    main()