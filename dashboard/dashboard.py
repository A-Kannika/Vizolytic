import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
import base64
import plotly.figure_factory as ff
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt
import io

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

    generate_analytic_report(filtered_df, category_df)

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

# View the data
def view_data(filtered_df):
    with st.expander("View Data"):
        st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

# Showing the heat map
# Dictionary mapping full state names to abbreviations
us_state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}

def heat_map(filtered_df):
    st.subheader("Sales in the U.S. by State")

    # Aggregate sales by state
    state_sales = filtered_df.groupby("State", as_index=False)["Sales"].sum()

    # Map full state names to abbreviations
    state_sales["State_Abbrev"] = state_sales["State"].map(us_state_abbrev)

    # Remove any states that couldn't be mapped
    state_sales = state_sales.dropna(subset=["State_Abbrev"])

    # Create choropleth
    fig = px.choropleth(
        state_sales,
        locations="State_Abbrev",
        locationmode="USA-states",
        color="Sales",
        hover_name="State",
        hover_data={"Sales": True, "State_Abbrev": False},  # show state name and sales
        color_continuous_scale="Blues",
        range_color=(0, state_sales["Sales"].max()),
        scope="usa",
        labels={"Sales": "Total Sales"}
    )

    fig.update_layout(
        template='plotly_white',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        title=dict(text="State-wise Sales in the U.S.", font=dict(size=20))
    )

    st.plotly_chart(fig, use_container_width=True)

# Download original dataset
def download_dataset(df):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data = csv, file_name="Data.csv", mime="text/csv")

# generate the report and export as pdf
def generate_analytic_report(filtered_df, category_df):
    # Create the download button in sidebar
    st.sidebar.subheader("📄 Export Report")

    if st.sidebar.button("Generate PDF Report"):
        if filtered_df is None or category_df is None:
            st.warning("⚠️ Please apply filters before generating the report.")
            return

        # Create a BytesIO buffer for the PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # --- Report Title ---
        story.append(Paragraph("📊 Vizolytic - Sales Dashboard Report", styles["Title"]))
        story.append(Spacer(1, 12))

        # --- Summary Section ---
        total_sales = filtered_df["Sales"].sum()
        avg_profit = filtered_df["Profit"].mean()
        total_orders = len(filtered_df)

        summary_text = f"""
        <b>Total Sales:</b> ${total_sales:,.2f}<br/>
        <b>Average Profit:</b> ${avg_profit:,.2f}<br/>
        <b>Total Orders:</b> {total_orders}<br/>
        """
        story.append(Paragraph(summary_text, styles["BodyText"]))
        story.append(Spacer(1, 12))

        # --- Bar Chart: Category Sales ---
        fig, ax = plt.subplots()
        ax.bar(category_df["Category"], category_df["Sales"], color="teal")
        ax.set_title("Category-wise Sales")
        ax.set_ylabel("Sales")
        ax.set_xlabel("Category")
        plt.tight_layout()

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        plt.close(fig)
        img_buf.seek(0)
        story.append(Image(img_buf, width=400, height=250))
        story.append(Spacer(1, 12))

        # --- Pie Chart: Region Sales ---
        region_sales = filtered_df.groupby("Region")["Sales"].sum().reset_index()
        fig, ax = plt.subplots()
        ax.pie(region_sales["Sales"], labels=region_sales["Region"], autopct="%1.1f%%", startangle=90)
        ax.set_title("Region-wise Sales")
        plt.tight_layout()

        img_buf2 = io.BytesIO()
        plt.savefig(img_buf2, format='png')
        plt.close(fig)
        img_buf2.seek(0)
        story.append(Image(img_buf2, width=400, height=250))
        story.append(Spacer(1, 12))

        # --- Table Summary ---
        top_cities = filtered_df.groupby("City")["Sales"].sum().nlargest(5).reset_index()
        top_cities_html = "<br/>".join(
            [f"{row.City}: ${row.Sales:,.2f}" for _, row in top_cities.iterrows()]
        )
        story.append(Paragraph("<b>Top 5 Cities by Sales:</b><br/>" + top_cities_html, styles["BodyText"]))
        story.append(Spacer(1, 12))

        # Build the PDF
        doc.build(story)
        buffer.seek(0)

        # Download button
        st.sidebar.download_button(
            label="📥 Download PDF",
            data=buffer,
            file_name="Vizolytic_Report.pdf",
            mime="application/pdf"
        )

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
    view_data(filtered_df)
    heat_map(filtered_df)
    download_dataset(df)
    generate_analytic_report()
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