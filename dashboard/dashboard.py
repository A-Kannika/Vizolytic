import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
import base64
import plotly.figure_factory as ff

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
        filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
    elif region and state:
        filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
    elif city:
        filtered_df = df3[df3["City"].isin(city)]
    else:
        filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

    # filter Categories column
    category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

    return filtered_df, category_df

# create bar chart for the category data
def create_barchart(category_df):
    st.subheader("Category Wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", 
                 text=[f"${x:,.2f}" for x in category_df["Sales"]],
                 template="seaborn"
                 )
    fig.update_layout(height=400)
    st.plotly_chart(fig, config={"responsive": True})

# create pie chart for the region data
def create_piechart(filtered_df):
    st.subheader("Region Wise Sales")
    fig = px.pie(filtered_df, values="Sales",names="Region", hole=0)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    fig.update_layout(height=400)
    st.plotly_chart(fig, config={"responsive": True})

# Category view/download data
def category_view_data(filtered_df, category_df):
    cl1, cl2 = st.columns(2)
    with cl1:
        with st.expander("Category View Data"):
            st.write(category_df.style.background_gradient(cmap="Blues"))
            csv = category_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                               help="Click here to download the data as a csv file")
    with cl2:
        with st.expander("Region View Data"):
            region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
            st.write(region.style.background_gradient(cmap="Blues"))
            csv = region.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                               help="Click here to download the data as a csv file")
    
# Time series analysis
def time_series_analysis1(filtered_df):
    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
    st.subheader('Time Series Analysis')
    line_chart = (filtered_df.groupby("month_year")["Sales"].sum().reset_index())
    line_chart["month_year_str"] = line_chart["month_year"].dt.strftime("%Y - %b")
    fig = px.line(
        line_chart,
        x="month_year_str",
        y="Sales",
        labels={"Sales": "Amount"},
        height=500,
        width=1000,
        template="gridon"
    )
    st.plotly_chart(fig, config={"responsive": True})
    time_series_view_data(line_chart)

def time_series_analysis(filtered_df):
    # Ensure Order Date is datetime
    filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"], errors="coerce")

    st.subheader('Time Series Analysis')

    filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
    line_chart = filtered_df.groupby("month_year")["Sales"].sum().reset_index()
    line_chart["month_year_str"] = line_chart["month_year"].dt.strftime("%Y - %b")

    fig = px.line(
        line_chart,
        x="month_year_str",
        y="Sales",
        labels={"Sales": "Amount"},
        height=500,
        width=1000,
        template="gridon"
    )
    st.plotly_chart(fig, config={"responsive": True})
    time_series_view_data(line_chart)

# Time series data download
def time_series_view_data(line_chart):
    with st.expander("View Data Time Series"):
        export_df = line_chart[["month_year", "Sales"]]
        st.write(export_df.T.style.background_gradient(cmap="Blues"))
        csv = export_df.sort_values(by="month_year", ascending=True).to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Timeseries.csv", mime="text/csv",
                               help="Click here to download the data as a csv file")

# Create tree map based on Region, category, sub-categories
def treemap_view(filtered_df):
    st.subheader("hierarchical view of Sales using TreeMap")
    fig = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales",
                     hover_data=["Sales"], color="Sub-Category", 
                     color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(width=800, height=650)
    st.plotly_chart(fig, use_container_width=True)

# Create the chart for the segment wise sales
def segmants_wise_data(filtered_df):
    st.subheader("Segments Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Create the chart for the sales wise data
def category_wise_data(filtered_df):
    st.subheader("Category Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Figure factory
def figure_factory_data(df, filtered_df):
    st.subheader(":point_right: Month wise Sub-Category Sales Summary")
    with st.expander("Summary Tables"):
        df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
        fig = ff.create_table(df_sample, colorscale="tropic")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("Month wise Sub-Category Table")
        filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
        sub_category_year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"],
                                           columns="month")
        st.write(sub_category_year.style.background_gradient(cmap="Blues"))

# Create Scatter plot
def create_scatter_plot(filtered_df):
    for col in ["Sales", "Profit", "Quantity"]:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce")
    filtered_df = filtered_df.dropna(subset=["Sales", "Profit", "Quantity"])

    fig = px.scatter(
        filtered_df,
        x="Sales",
        y="Profit",
        size="Quantity",
        title="Relationship between Sales and Profits using Scatter Plot"
    )
    
    fig.update_layout(
        title=dict(text="Relationship between Sales and Profits using Scatter Plot", font=dict(size=20)),
        xaxis_title="Sales",
        yaxis_title="Profit",
        height=500,
        width=900
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Data visualization
def viz_data(df):
    # Create Side Bar to filler the data
    filtered_df, category_df = create_sidebar(df)

    col1, col2 = st.columns(2)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    # Getting min and max date
    start_date = pd.to_datetime(df["Order Date"]).min()
    end_date = pd.to_datetime(df["Order Date"]).max()

    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", start_date))
        create_barchart(category_df)
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", end_date))
        create_piechart(filtered_df)

    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()
    
    # Download the data available
    category_view_data(filtered_df, category_df)

    # Time series analysis
    time_series_analysis(filtered_df)

    # TreeMap based on Region, category, sub-categories
    treemap_view(filtered_df)

    chart1, chart2 = st.columns((2))
    with chart1:
        segmants_wise_data(filtered_df)
    with chart2:
        category_wise_data(filtered_df)

    figure_factory_data(df, filtered_df)
    create_scatter_plot(filtered_df)
    return df

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

    # Data visualization
    viz_data(df)

if __name__== "__main__":
    main()