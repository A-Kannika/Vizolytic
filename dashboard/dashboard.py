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

# upload file
def uploaded_file():
    fl = st.file_uploader("📁 Upload your CSV file.", type=["csv", "txt", "xlsx", "xls"])
    if fl is not None:
        filename = fl.name
        df = pd.read_csv(filename, encoding="ISO-8859-1")
        st.success(f"✅ {filename} uploaded successfully!!")
        st.write("📄 Data Preview")
        st.write(df.head())
    else:
        df = pd.read_csv("data/Superstore.csv", encoding="ISO-8859-1")

    return df

# read the data
def read_data(df):
    col1, col2 = st.columns((2))
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    # Getting min and max date
    start_date = pd.to_datetime(df["Order Date"]).min()
    end_date = pd.to_datetime(df["Order Date"]).max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", start_date))
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", end_date))

    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

    return df

# Create Side Bar
def create_sidebar(df):
    st.sidebar.header("Select Your Filter:")

    # Region filtering
    region = st.sidebar.multiselect("Select the Region", sorted(df["Region"].unique()))
    if not region:
        df2 = df.copy()
    else:
        df2 = df[df["Region"].isin(region)]

    # State filtering
    state = st.sidebar.multiselect("Select the State", sorted(df2["State"].unique()))
    if not state:
        df3 = df2.copy()
    else:
        df3 = df2[df2["State"].isin(state)]

    # City filtering
    city = st.sidebar.multiselect("Select the City", sorted(df3["City"].unique()))

    # filter data based on Region, State, and City
    if not region and not state and not city:
        filtered_df = df
    elif not state and not city:
        filtered_df = df[df["Region"].isin(region)]
    elif not region and not city:
        filtered_df = df[df["State"].isin(state)]
    elif state and city:
        filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
    elif region and city:
        filtered_df = df3[df["State"].isin(region) & df3["City"].isin(city)]
    elif region and state:
        filtered_df = df3[df["State"].isin(region) & df3["City"].isin(state)]
    elif city:
        filtered_df = df3[df3["City"].isin(city)]
    else:
        filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]


def main():
    st.set_page_config(
        page_title="Vizolytic – Turning Data Into Decisions",
        page_icon="assets/icon1.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Create the page title
    page_title()

    # Uoload file
    df = uploaded_file()

    # Read the data
    read_data(df)

    # Create Side Bar
    create_sidebar(df)

    

    

if __name__== "__main__":
    main()