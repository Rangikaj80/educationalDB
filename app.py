import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import plotly.express as px

# Set page config
st.set_page_config(page_title="Education Data Dashboard", layout="wide")

# Helper functions
@st.cache_data
def load_data():
    data = pd.read_csv("cleaned_world_education_data.csv")
    data['year'] = pd.to_datetime(data['year'], format='%Y')
    return data

def calculate_delta(df, column):
    if len(df) < 2:
        return 0, 0
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-2]
    delta = current_value - previous_value 
    delta_percent = (delta / previous_value) * 100 if previous_value != 0 else 0
    return delta, delta_percent
    
def display_metric(col, title, value, df, column, color):
    with col:
        delta, delta_percent = calculate_delta(df, column)
        delta_str = f"{delta:+,.0f} ({delta_percent:+.2f}%)"
        st.metric(title, f"{value:,.2f}", delta= delta_str)

# Load data
data = load_data()

# Sidebar for user input
st.sidebar.title("Filters")
countries = st.sidebar.multiselect("Select Countries", options=sorted(data['country'].unique()), default=['United States'])
years = st.sidebar.slider("Select Year Range",
                          min_value=int(data['year'].dt.year.min()),
                          max_value=int(data['year'].dt.year.max()),
                          value=(2010, 2020))
metrics = st.sidebar.multiselect(
    "Select Metrics to Desplay",
    options=["gov_exp_pct_gdp", "school_enrol_primary_pct", "school_enrol_secondary_pct", "school_enrol_tertiary_pct", "pupil_teacher_primary", "pupil_teacher_secondary"],
    default=["gov_exp_pct_gdp", "school_enrol_primary_pct"]
)

# Filter the data
filtered_data = data[(data['country'].isin(countries)) &
                     (data['year'].dt.year.between(years[0], years[1]))]

# Main dashboard
st.title("Education Data Dashboard")
st.subheader("Comparative Analysis of Selected Countries")

# Metrics section
metrics_cols = st.columns(len(metrics))
for col, metric in zip(metrics_cols, metrics):
    value = filtered_data[metric].mean()
    display_metric(col, metric.replace('_', ' ').title(), value, filtered_data, metric, '#29b5e8')

# Visualizations
st.subheader("Visualizations")

# Compare countries
st.markdown("### Country Comparision")
chart1 = alt.Chart(filtered_data).mark_bar().encode(
    x=alt.X('country:N', title="Country"),
    y=alt.Y('gov_exp_pct_gdp:Q', title="Government Expenditure (% of GDP)"),
    color='country:N'
).properties(width=800, height=400)
st.altair_chart(chart1, use_container_width=True)

# Enrollment trends over years
st.markdown("### Enrollment Trends Over Time")
chart2 = alt.Chart(filtered_data).mark_line(point=True).encode(
    x=alt.X('year:T', title='Year'),
    y=alt.Y('school_enrol_primary_pct:Q', title="Primary Enrollment (%)"),
    color='country:N'
).properties(width=800, height=400)
st.altair_chart(chart2, use_container_width=True)


# Teacher-pupil ratio trends
st.markdown('### Teacher-Pupil Ratios')
chart3 = alt.Chart(filtered_data).mark_line(point=True).encode(
    x=alt.X('year:T', title='Year'),
    y=alt.Y('pupil_teacher_primary:Q', title='Pupil-Teacher Ratio (Primary)'),
    color='country:N'
).properties(width=800, height=400)
st.altair_chart(chart3, use_container_width=True)

# Display filtered dataset
with st.expander('View Filtered Data'):
    st.dataframe(filtered_data)


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


# Calculate Composite Metric for Education Levels
indicators = [
    'pri_comp_rate_pct', 
    'school_enrol_primary_pct', 
    'school_enrol_secondary_pct', 
    'school_enrol_tertiary_pct'
]

# Ensure these columns exist in the filtered data
if all(indicator in filtered_data.columns for indicator in indicators):
    filtered_data['composite_metric'] = filtered_data[indicators].mean(axis=1)

    # Aggregate data by country
    country_composite_scores = (
        filtered_data.groupby('country')['composite_metric']
        .mean()
        .reset_index()
        .sort_values(by='composite_metric', ascending=False)
    )
else:
    st.error("Required indicators for composite metric are missing in the dataset.")


# Top 10 Countries with the Best Education Levels
st.markdown("### Top 10 Countries by Composite Education Metric")

# Filter top 10 countries
top_10_countries = country_composite_scores.head(10)

# Create a bar chart
chart_top_countries = alt.Chart(top_10_countries).mark_bar().encode(
    x=alt.X('composite_metric:Q', title="Composite Education Metric"),
    y=alt.Y('country:N', sort='-x', title="Country"),
    color=alt.Color('country:N', legend=None)
).properties(
    width=800,
    height=400,
    title="Top 10 Countries by Composite Education Metric"
)

# Display the chart
st.altair_chart(chart_top_countries, use_container_width=True)






