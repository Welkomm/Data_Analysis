import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
from PIL import Image
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
import json
import geopandas as gpd
import time  # For progress bar

# --- Page Configuration ---
st.set_page_config(
    page_title="Data Viz Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

# --- Utility Functions ---


def count_rows(rows):
    """Counts the number of rows in a DataFrame."""
    return len(rows)


def load_lottiefile(filepath: str):
    """Loads a Lottie animation from a local file."""
    with open(filepath, "r") as f:
        return json.load(f)


def load_lottieurl(url: str):
    """Loads a Lottie animation from a URL."""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def show_data_preview(df, title):
    """Displays a preview of the DataFrame with a title."""
    st.write(f"**Data Preview ({title}):**")
    st.dataframe(df.head())


# Load Lottie animations
lottie_taxi = load_lottiefile("taxi.json")
lottie_data = load_lottieurl(
    "https://assets8.lottiefiles.com/packages/lf20_ydo1amjm.json"
)

# --- Data Loading and Preprocessing ---

# Uber dataset
df_uber = pd.read_csv("uber.csv", delimiter=",")
df_uber["Date/Time"] = pd.to_datetime(
    df_uber["Date/Time"], format="%m/%d/%Y %H:%M:%S"
)
df_uber["day"] = df_uber["Date/Time"].dt.day
df_uber["weekday"] = df_uber["Date/Time"].dt.weekday
df_uber["hour"] = df_uber["Date/Time"].dt.hour
df_uber["month"] = df_uber["Date/Time"].dt.month

# Tips dataset
df_tips = pd.read_csv("tips.csv")
df_tips["day"] = df_tips["day"].astype("category")
df_tips["time"] = df_tips["time"].astype("category")

# Load GeoJSON file (with progress bar)
with st.spinner("Loading GeoJSON..."):
    @st.cache_data
    def load_geojson(filepath):
        """Loads a GeoJSON file from the specified path."""
        with open(filepath, "r") as f:
            return json.load(f)

    nyc_geojson = load_geojson("nyc.geojson")

# Load NYC boroughs shapefile or GeoJSON (with progress bar)
with st.spinner("Loading NYC Boroughs..."):
    nyc_boroughs = gpd.read_file("nyc.geojson")

# --- Images ---
uber_logo = Image.open("Uber.png")
my_pic = Image.open("CV.jpg")
efrei_logo = Image.open("efrei.png")

# --- Sidebar ---
with st.sidebar:
    # Logo and Title
    st.image(efrei_logo, width=200)
    st.title("Data Explorer")

    # About Section (using st.expander to collapse by default)
    with st.expander("About Samuel BIENVENU 👋"):
        st.image(my_pic, use_column_width=True)
        st.markdown(
            "Passionate about Data Science and creating interactive dashboards to reveal actionable insights."
        )
        st.write(
            "**Skills:** Python, Data Analysis, Machine Learning, Data Visualization (Streamlit, Plotly, etc.)"
        )

        st.markdown("---")  # Separator

        st.header("Contact Me 📞")  # Contact section
        st.write("Email: samuel.bienvenu@protonmail.com")
        st.write("Phone: +33 (0) 6 XX XX XX XX")  # Replace with your number
        st.markdown(
            "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/samuel-bienvenu)"
        )  # Replace with your LinkedIn profile link

    # --- Contact Form ---
    with st.expander("Contact Form 📧"):
        st.write("Want to collaborate? Send me a message!")
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        subject = st.text_input("Message Subject")
        message = st.text_area("Your Message")

        if st.button("Send"):
            # Handle message sending (see explanations below)
            st.success("Message sent successfully!")

    # Copyright at the bottom of the sidebar
    st.sidebar.markdown(
        """
        <div style="text-align: center; font-size: 12px; margin-top: 20px;">
            Copyright © 2024 Samuel BIENVENU. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Tabs ---
tab_home, tab_uber, tab_tips, tab_advanced = st.tabs(
    ["Home 🏠", "Uber Trip Analysis 🚕", "Tip Analysis 🍽️", "Advanced Visualizations ✨"]
)

# --- Home Page ---
with tab_home:
    st.title("Data Analysis Dashboard 📊")

    # Centered Uber logo with better presentation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st_lottie(lottie_data, height=200, key="data")

    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color:#00A0E9;font-family:Arial;font-size: 20px; font-weight: bold"> Exploring Uber and Restaurant Tip Data</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    This interactive dashboard allows you to explore Uber ride and restaurant tip data in depth.  
    Discover the visualizations and analyses below:
    """
    )

    st.markdown(
        """
    **Key Features:**
    * **Uber Trip Analysis:**
        * Visualization of ride frequency by day, hour, day of the week, and Uber base.
        * Interactive and animated map showing the evolution of Uber rides in New York by borough.
    * **Tip Analysis:**
        * Interactive visualizations of tips based on total bill, day of the week, gender, and smoking habit.
        * Exploration of relationships between these variables using a pivot table.
    """
    )

# --- Uber Trip Analysis Page ---
with tab_uber:
    st.title("Uber Trip Analysis 🚕")

    # Add Lottie animation at the top of the page
    col1, col2, col3 = st.columns([1, 2, 1])  # Create three columns for layout
    with col2:  # Center the animation in the middle column
        st_lottie(lottie_taxi, height=200, key="taxi") 

    show_data_preview(df_uber, "Uber")

    # --- Filters ---
    col1, col2, col3 = st.columns(3)
    with col1:
        day_filter = st.slider("Day of the Month:", 1, 30, (1, 30))
    with col2:
        hour_filter = st.slider("Hour of the Day:", 0, 23, (0, 23))
    with col3:
        base_filter = st.multiselect(
            "Uber Base:", df_uber["Base"].unique(), default=df_uber["Base"].unique()
        )

    # --- Apply Filters ---
    df_uber_filtered = df_uber[
        (df_uber["day"] >= day_filter[0])
        & (df_uber["day"] <= day_filter[1])
        & (df_uber["hour"] >= hour_filter[0])
        & (df_uber["hour"] <= hour_filter[1])
        & (df_uber["Base"].isin(base_filter))
    ]

    # --- Visualizations ---
    st.header("Uber Ride Visualizations")

    # --- Chart 1: Histogram of Rides per Hour ---
    fig_hour = px.histogram(
        df_uber_filtered, x="hour", title="Number of Rides per Hour"
    )
    st.plotly_chart(fig_hour)
    st.markdown(
        "**Insight:** This histogram reveals the peak hours for Uber rides, which can be valuable for demand forecasting and resource allocation."
    )

    # --- Chart 2: 3D Map of Dropoff Points ---
    st.subheader("3D Map of Dropoff Points")
    midpoint = (np.average(df_uber_filtered["Lat"]), np.average(df_uber_filtered["Lon"]))
    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10",
            initial_view_state=pdk.ViewState(
                latitude=midpoint[0], longitude=midpoint[1], zoom=11, pitch=50
            ),
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    df_uber_filtered[["Lon", "Lat"]].rename(
                        columns={"Lon": "lon", "Lat": "lat"}
                    ),
                    get_position=["lon", "lat"],
                    radius=200,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                )
            ],
        )
    )
    st.markdown(
        "**Insight:** The 3D hexbin map provides a visual representation of Uber dropoff hotspots, indicating areas with high ride demand."
    )

    # Chart 3: Heatmap of Uber Rides
    st.subheader("Heatmap of Uber Rides")
    fig_heatmap = px.density_mapbox(
        df_uber_filtered,
        lat="Lat",
        lon="Lon",
        radius=10,
        center=dict(lat=40.7128, lon=-74.0060),
        zoom=10,
        mapbox_style="carto-positron",
        title="Uber Ride Density",
    )
    st.plotly_chart(fig_heatmap)
    st.markdown(
        "**Insight:** The heatmap confirms the areas with the highest concentration of Uber rides, offering a more granular view of ride density compared to the 3D map."
    )

    # Chart 4: Pie Chart of Uber Bases
    st.subheader("Proportion of Rides by Uber Base")
    base_counts = df_uber_filtered["Base"].value_counts()
    fig_pie = px.pie(
        values=base_counts.values, names=base_counts.index, title="Proportion of Rides by Uber Base"
    )
    st.plotly_chart(fig_pie)
    st.markdown(
        "**Insight:** The pie chart shows the market share of different Uber bases, highlighting which bases are most active during the selected period."
    )

    # Chart 5: Pivot Table of Rides by Day and Hour
    st.subheader("Number of Rides by Day and Hour")
    df_pivot = df_uber_filtered.groupby(["weekday", "hour"]).size().unstack()
    st.dataframe(df_pivot)
    st.markdown(
        "**Insight:** The pivot table provides a detailed breakdown of ride frequency by day of the week and hour, revealing patterns in demand throughout the week."
    )

    # Chart 6: Histogram of Rides by Day of the Week
    st.subheader("Number of Rides by Day of the Week")
    fig_weekday = px.histogram(
        df_uber_filtered,
        x="weekday",
        title="Number of Rides by Day of the Week",
        nbins=7,
    )
    st.plotly_chart(fig_weekday)
    st.markdown(
        "**Insight:** This histogram illustrates the variation in Uber ride demand across different days of the week, potentially indicating weekend vs. weekday trends."
    )

    # --- Download Options ---
    csv = df_uber_filtered.to_csv(index=False)
    st.download_button(
        label="Download filtered Uber data as CSV",
        data=csv,
        file_name="uber_data.csv",
        mime="text/csv",
    )

# --- Tip Analysis Page ---
with tab_tips:
    st.title("Tip Analysis 🍽️")
    show_data_preview(df_tips, "Tips")

    # --- Filters ---
    col1, col2, col3 = st.columns(3)
    with col1:
        day_filter_tips = st.multiselect(
            "Day of the Week:", df_tips["day"].unique(), default=df_tips["day"].unique()
        )
    with col2:
        smoker_filter = st.radio("Smoker:", ["All", "Yes", "No"], index=0)
    with col3:
        gender_filter = st.radio("Gender:", ["All", "Male", "Female"], index=0)

    # --- Apply Filters ---
    df_tips_filtered = df_tips[df_tips["day"].isin(day_filter_tips)]
    if gender_filter != "All":
        df_tips_filtered = df_tips_filtered[df_tips_filtered["sex"] == gender_filter]
    if smoker_filter != "All":
        df_tips_filtered = df_tips_filtered[df_tips_filtered["smoker"] == smoker_filter]

    # --- Visualizations ---
    st.header("Tip Data Visualizations")

    # --- Chart 1: Scatter Plot for Total Bill vs. Tip ---
    fig_scatter = px.scatter(
        df_tips_filtered,
        x="total_bill",
        y="tip",
        color="day",
        size="size",
        title="Total Bill vs. Tip Relationship",
    )
    st.plotly_chart(fig_scatter)
    st.markdown(
        "**Insight:** This scatter plot explores the relationship between the total bill amount and the tip amount, revealing potential correlations and trends based on different days."
    )

    # --- Chart 2: Violin Plot ---
    fig_violin = px.violin(
        df_tips_filtered,
        x="day",
        y="tip",
        color="sex",
        box=True,
        points="all",
        title="Tip Distribution by Day and Gender",
    )
    st.plotly_chart(fig_violin)
    st.markdown(
        "**Insight:** The violin plot provides insights into the distribution of tips by day and gender, showing the density and range of tips for each category."
    )

    # Chart 3: Boxplot of Tips by Day of the Week and Gender
    st.subheader("Tip Distribution by Day and Gender (Boxplot)")
    fig_boxplot_tips, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x="day", y="tip", hue="sex", data=df_tips_filtered, ax=ax)
    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Tip")
    ax.set_title("Tip Distribution by Day and Gender")
    st.pyplot(fig_boxplot_tips)
    st.markdown(
        "**Insight:** The boxplot offers a concise visualization of the tip distribution, highlighting the median, quartiles, and potential outliers for each day and gender combination."
    )

    # Chart 4: Histogram of Tips
    st.subheader("Tip Distribution (Histogram)")
    fig_hist_tips = px.histogram(
        df_tips_filtered, x="tip", nbins=20, title="Tip Distribution"
    )
    st.plotly_chart(fig_hist_tips)
    st.markdown(
        "**Insight:** This histogram visualizes the overall distribution of tip amounts, showing the frequency of different tip ranges."
    )

    # Chart 5: Scatter Plot with Regression
    st.subheader("Relationship between Tip and Total Bill (Regression)")
    fig_regplot, ax = plt.subplots(figsize=(10, 6))
    sns.regplot(x="total_bill", y="tip", data=df_tips_filtered, ax=ax)
    ax.set_xlabel("Total Bill Amount")
    ax.set_ylabel("Tip")
    ax.set_title("Relationship between Tip and Total Bill")
    st.pyplot(fig_regplot)
    st.markdown(
        "**Insight:** The scatter plot with regression line quantifies the relationship between the total bill and tip, indicating a positive correlation and allowing for predictions."
    )

    # Chart 6: Boxplot of Tips by Group Size
    st.subheader("Tip Distribution by Group Size (Boxplot)")
    fig_boxplot_size, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x="size", y="tip", data=df_tips_filtered, ax=ax)
    ax.set_xlabel("Group Size")
    ax.set_ylabel("Tip")
    ax.set_title("Tip Distribution by Group Size")
    st.pyplot(fig_boxplot_size)
    st.markdown(
        "**Insight:** The boxplot examines the impact of group size on tip amounts, revealing how tip distributions vary for different party sizes."
    )

    # Chart 7: Pivot Table (Average Tips)
    st.subheader("Pivot Table (Average Tips)")
    df_pivot_tips = pd.pivot_table(
        df_tips_filtered, values="tip", index=["day"], columns=["sex"], aggfunc=np.mean
    )

    # Remove the separate 'sex' row and set 'day' as the index name
    df_pivot_tips.columns.name = None  # Remove the 'sex' label
    df_pivot_tips = df_pivot_tips.rename_axis(index=None)  # Remove the index name

    # Insert 'day' as the first column header
    df_pivot_tips.insert(0, "day", df_pivot_tips.index)
    df_pivot_tips = df_pivot_tips.reset_index(drop=True)  # Reset the index

    # Style the first row (including 'day') in bold
    styled_df = df_pivot_tips.style.set_properties(
        **{"font-weight": "bold"}, subset=pd.IndexSlice[[0], :]
    )

    st.markdown(styled_df.to_html(), unsafe_allow_html=True)

    st.markdown(
        "**Insight:** The pivot table summarizes the average tip amounts based on day and gender, providing a concise overview of tipping patterns across different categories."
    )
    
    # Chart 8: Histogram of Tip Percentage
    st.subheader("Distribution of Tip Percentage of Total")
    df_tips_filtered["tip_percentage"] = (
        df_tips_filtered["tip"] / df_tips_filtered["total_bill"]
    ) * 100
    fig_hist_percentage, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df_tips_filtered["tip_percentage"], kde=True, ax=ax)
    ax.set_xlabel("Tip Percentage")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Tip Percentage")
    st.pyplot(fig_hist_percentage)
    st.markdown(
        "**Insight:** This histogram shows the distribution of tip percentages, revealing the most common tipping rates and identifying any outliers or unusual patterns."
    )

    # --- Download Options ---
    csv = df_tips_filtered.to_csv(index=False)
    st.download_button(
        label="Download filtered tips data as CSV",
        data=csv,
        file_name="tips_data.csv",
        mime="text/csv",
    )


# --- Advanced Visualizations Page ---
with tab_advanced:
    st.title("Let's Dive into Stunning Visualizations! 🚀")

    # --- Example 1: Interactive 3D Scatter Plot with Plotly ---
    st.header("1. 3D Scatter Plot: Bill-Tip-Day Relationship")

    fig = px.scatter_3d(
        df_tips,
        x="total_bill",
        y="tip",
        z="day",
        color="sex",
        size="size",
        title="3D Relationship between Bill, Tip, and Day",
        labels={"total_bill": "Total Bill", "tip": "Tip", "day": "Day", "sex": "Gender"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "**Insight:** This interactive 3D scatter plot provides a multi-dimensional view of the data, allowing you to explore the relationship between bill amount, tip amount, day of the week, and gender simultaneously. You can rotate and zoom the plot to gain different perspectives."
    )

    # --- Example 2: Animated Choropleth Map (New York) ---
    st.header("2. Animated Choropleth Map: Evolution of Uber Rides in New York by Borough")

    # Prepare data for the map
    df_uber_geo = gpd.GeoDataFrame(
        df_uber, geometry=gpd.points_from_xy(df_uber.Lon, df_uber.Lat), crs="EPSG:4326"
    )

    # Spatial join (with progress bar)
    with st.spinner("Performing spatial join..."):
        df_joined = gpd.sjoin(df_uber_geo, nyc_boroughs, how="left", predicate="intersects")

    # Group the data
    df_joined["Date"] = pd.to_datetime(df_joined["Date/Time"]).dt.date
    df_grouped = df_joined.groupby(["Date", "name"]).size().reset_index(name="Number of Rides")

    # Create the choropleth map
    fig_choro_ny = px.choropleth(
        df_grouped,
        geojson=nyc_geojson,
        locations="name",  # Use 'name' as it's the name in the GeoJSON
        featureidkey="properties.name",
        color="Number of Rides",
        animation_frame="Date",
        color_continuous_scale="Viridis",
        range_color=(0, df_grouped["Number of Rides"].max()),
        title="Evolution of Uber Rides in New York by Borough",
        hover_data=["Number of Rides"],
        scope="north america",
    )

    # Improve appearance and projection
    fig_choro_ny.update_geos(
        center=dict(lon=-74.0060, lat=40.7128),
        fitbounds="locations",
        projection=dict(type="albers usa", parallels=[30, 40]),
    )
    fig_choro_ny.update_layout(
        geo=dict(showland=True, landcolor="rgb(217, 217, 217)", countrycolor="white"),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    # Add a slider to select the date
    unique_dates = df_grouped["Date"].unique()
    fig_choro_ny.update_layout(
        sliders=[
            {
                "steps": [
                    {
                        "args": [["Date", date]],
                        "label": date.strftime("%Y-%m-%d"),
                        "method": "animate",
                    }
                    for date in unique_dates
                ]
            }
        ]
    )

    st.plotly_chart(fig_choro_ny, use_container_width=True)
    st.markdown(
        "**Insight:** This animated choropleth map visually represents the evolution of Uber rides across different boroughs of New York City over time. Observe how ride patterns change throughout the month, providing valuable insights into spatial and temporal trends."
    )

    # --- Example 3: Interactive Sunburst Chart ---
    st.header("3. Sunburst Chart: Tip Breakdown")

    fig_sunburst = px.sunburst(
        df_tips,
        path=["day", "sex", "time"],
        values="tip",
        title="Tip Breakdown by Day, Gender, and Time",
    )
    st.plotly_chart(fig_sunburst)
    st.markdown(
        "**Insight:** The sunburst chart provides a hierarchical breakdown of tip amounts based on day of the week, gender, and meal time. Explore the interactive segments to understand how these factors contribute to overall tip patterns. For example, you can see which combinations of day, gender, and time lead to the highest average tips."
    )