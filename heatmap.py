import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Heatmap & Bubble Map", layout="wide")

@st.cache_data
def load_data():
    data = pd.read_csv("cleaned_world_education_data.csv")
    data['year'] = pd.to_datetime(data['year'], format='%Y')
    return data

# Load data
data = load_data()

# Sidebar for user input
st.sidebar.title("Filters")
years = st.sidebar.slider("Select Year", 
                           min_value=int(data['year'].dt.year.min()), 
                           max_value=int(data['year'].dt.year.max()), 
                           value=(2015, 2020))
metric = st.sidebar.selectbox(
    "Select Metric for Visualization", 
    ["gov_exp_pct_gdp", "school_enrol_primary_pct", "school_enrol_secondary_pct", "school_enrol_tertiary_pct"]
)

# Filter data
filtered_data = data[data['year'].dt.year.between(years[0], years[1])]

# Main page
st.title("Heatmap & Bubble Map")
st.subheader("Visualizing Global Education Levels")

# Heatmap
st.markdown("### Heatmap of Education Metric by Country")
heatmap_data = filtered_data.groupby('country')[metric].mean().reset_index()
fig_heatmap = px.choropleth(
    heatmap_data,
    locations="country",
    locationmode="country names",
    color=metric,
    title=f"Heatmap of {metric.replace('_', ' ').title()}",
    color_continuous_scale="Viridis",
    labels={metric: metric.replace('_', ' ').title()}
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Bubble Map
st.markdown("### Bubble Map Indicating Education Levels")
bubble_data = filtered_data.groupby(['country', 'latitude', 'longitude'])[metric].mean().reset_index()
fig_bubble = px.scatter_geo(
    bubble_data,
    lat="latitude",
    lon="longitude",
    size=metric,
    color=metric,
    hover_name="country",
    title=f"Bubble Map of {metric.replace('_', ' ').title()}",
    projection="natural earth",
    labels={metric: metric.replace('_', ' ').title()}
)
st.plotly_chart(fig_bubble, use_container_width=True)
