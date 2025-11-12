import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Marine Biodiversity Dashboard",
    page_icon="🐠",
    layout="wide",
)

# --- 2. Data Loading Function ---
@st.cache_data
def load_data(file_path):
    """Loads and prepares the biodiversity data from your CSV."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please check the file path.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    if 'eventDate' not in df.columns:
        st.error("Error: Your dataset does not have an 'eventDate' column.")
        st.stop()
        
    # --- Create Time Columns ---
    # errors='coerce' will turn bad dates into NaT (Not a Time)
    df['eventDate'] = pd.to_datetime(df['eventDate'], errors='coerce')
    
    # This will now ONLY drop the rows with bad dates, not all rows
    df = df.dropna(subset=['eventDate']) 
    
    df['year'] = df['eventDate'].dt.year
    df['month'] = df['eventDate'].dt.month_name()
    df['year'] = df['year'].astype(int)
    
    return df

# --- 3. Load Your Data ---
FILE_PATH = "indOBIS_cleaned.csv" 
df = load_data(FILE_PATH)



# --- 5. Main Page Layout ---
st.title("🐠 Marine Biodiversity Dashboard")
st.markdown("*(Displaying ALL data from the file)*")

# --- 5a. Key Performance Indicators (KPIs) ---
st.subheader("Top-Level Statistics (All Data)")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Occurrences", f"{df.shape[0]:,}")
kpi2.metric("Unique Species", f"{df['scientificName'].nunique():,}")

if 'individualCount' in df.columns:
    kpi3.metric("Total Individuals Recorded", f"{df['individualCount'].sum():,}")
else:
    kpi3.metric("Total Individuals Recorded", "N/A")

if 'country' in df.columns:
    kpi4.metric("Countries Surveyed", f"{df['country'].nunique():,}")
else:
    kpi4.metric("Countries Surveyed", "N/A")

st.markdown("---")

# --- 5b. Interactive Map (from image 3) ---
st.subheader("Species Distribution by Latitude and Longitude")
if 'decimalLatitude' in df.columns and 'decimalLongitude' in df.columns:
    fig_map = px.scatter_mapbox(
        df,  # Using main df
        lat="decimalLatitude",
        lon="decimalLongitude",
        color="scientificName",
        hover_name="scientificName",
        hover_data={"locality": True, "eventDate": True},
        zoom=4,
        height=500,
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Dataset must contain 'decimalLatitude' and 'decimalLongitude' to display map.")

st.markdown("---")

# --- 5c. Time, Species, and Depth Charts (from image 2) ---
col1, col2 = st.columns(2)

with col1:
    # Occurrences over Time (Area Chart)
    st.markdown("#### Occurrences over Time")
    occurrences_by_year = df.groupby('year').size().reset_index(name='Count')
    fig_area = px.area(
        occurrences_by_year,
        x='year',
        y='Count',
    )
    st.plotly_chart(fig_area, use_container_width=True)

    # Species Occurrence by Depth (Scatter)
    st.markdown("#### Species Occurrence by Depth")
    if 'depth' in df.columns and 'individualCount' in df.columns:
        fig_depth_scatter = px.scatter(
            df,  # Using main df
            x='individualCount',
            y='depth',
            hover_name='scientificName',
            labels={'individualCount': 'Individual Count', 'depth': 'Depth (m)'}
        )
        st.plotly_chart(fig_depth_scatter, use_container_width=True)
    else:
        st.info("Requires 'depth' and 'individualCount' columns.")

with col2:
    # Top 10 Species (Bar Chart)
    st.markdown("#### Top 10 Species")
    species_counts = df['scientificName'].value_counts().nlargest(10).reset_index()
    species_counts.columns = ['Scientific Name', 'Count']
    fig_bar = px.bar(
        species_counts, 
        x='Count', 
        y='Scientific Name', 
        orientation='h',
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

    # Conservation Status (Donut Chart)
    st.markdown("#### Conservation Status")
    if 'redlist_category' in df.columns:
        redlist_counts = df['redlist_category'].value_counts().reset_index()
        redlist_counts.columns = ['Category', 'Count']
        fig_pie = px.pie(
            redlist_counts,
            names='Category',
            values='Count',
            hole=0.4 # Donut chart
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Requires 'redlist_category' column.")

st.markdown("---")

# --- 5d. Taxonomic & Water Body Analysis (from images 1 & 3) ---
col3, col4 = st.columns(2)

with col3:
    # Taxonomic Breakdown (Sunburst Chart)
    st.markdown("#### Taxonomic Breakdown")
    taxo_cols = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus']
    if all(col in df.columns for col in taxo_cols):
        taxo_data = df.dropna(subset=taxo_cols)
        fig_sunburst = px.sunburst(
            taxo_data,
            path=taxo_cols,
            values='individualCount' if 'individualCount' in df.columns else None,
            hover_name="class"
        )
        fig_sunburst.update_layout(margin = dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig_sunburst, use_container_width=True)
    else:
        st.info("Requires 'kingdom', 'phylum', 'class', 'order', 'family', 'genus' columns.")

with col4:
    # Species by Water Body (Bar Chart)
    st.markdown("#### Occurrences by Water Body")
    if 'waterBody' in df.columns:
        water_counts = df['waterBody'].value_counts().nlargest(10).reset_index()
        water_counts.columns = ['Water Body', 'Count']
        fig_water_bar = px.bar(
            water_counts,
            x='Count',
            y='Water Body',
            orientation='h'
        )
        fig_water_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_water_bar, use_container_width=True)
    else:
        st.info("Requires 'waterBody' column.")

st.markdown("---")

# --- 5e. Advanced Temporal & Environmental (from image 4) ---
st.subheader("Advanced Analysis")
col5, col6 = st.columns(2)

with col5:
    # Changing Occurrence of Species (Stacked Bar)
    st.markdown("#### Changing Occurrence of Species (by Year)")
    species_over_time = df.groupby(['year', 'scientificName']).size().reset_index(name='Count')
    top_10_species = df['scientificName'].value_counts().nlargest(10).index
    species_over_time_top10 = species_over_time[species_over_time['scientificName'].isin(top_10_species)]

    fig_stacked_bar = px.bar(
        species_over_time_top10,
        x='year',
        y='Count',
        color='scientificName',
        title="Annual Occurrences of Top 10 Species"
    )
    st.plotly_chart(fig_stacked_bar, use_container_width=True)

    # Temp vs Salinity (Scatter)
    st.markdown("#### Temperature vs. Salinity")
    if 'sst' in df.columns and 'sss' in df.columns:
        fig_temp_sal = px.scatter(
            df,  # Using main df
            x='sst',
            y='sss',
            color='scientificName',
            hover_name='scientificName',
            labels={'sst': 'Sea Surface Temperature (°C)', 'sss': 'Sea Surface Salinity'}
        )
        st.plotly_chart(fig_temp_sal, use_container_width=True)
    else:
        st.info("Requires 'sst' and 'sss' columns.")
        
with col6:
    # Month-Year Heatmap
    st.markdown("#### Month-Year Occurrence Heatmap")
    heatmap_data = pd.crosstab(df['month'], df['year'])
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
                   'August', 'September', 'October', 'November', 'December']
    heatmap_data = heatmap_data.reindex(month_order)
    
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="Year", y="Month", color="Occurrences"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        text_auto=True,
        aspect="auto"
    )
    fig_heatmap.update_xaxes(side="bottom")
    st.plotly_chart(fig_heatmap, use_container_width=True)


# --- 5f. Raw Data Table (from image 3) ---
st.subheader("Raw Data")
st.dataframe(df)