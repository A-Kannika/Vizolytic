import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')


def main():
    st.set_page_config(
        page_title="VIZOLYTIC Application ",
        page_icon="assets/icon1.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )

if __name__== "__main__":
    main()