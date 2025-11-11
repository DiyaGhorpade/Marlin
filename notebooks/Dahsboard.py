import os
import streamlit as st
import psycopg2
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Use 'Agg' backend for non-interactive plotting
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from dotenv import load_dotenv

# --- Page Setup ---
# This should be the first Streamlit command
st.set_page_config(layout="wide", page_title="Copernicus Dashboard")

# --- Database Config ---
load_dotenv()
POSTGRES_HOST = 'postgres'
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

@st.cache_data(ttl=600) # Cache data for 10 minutes (600 seconds)
def fetch_data():
    """
    Fetches the most recent data from Postgres.
    This function is cached by Streamlit.
    """
    print("CACHE MISS: Fetching new data from PostgreSQL...")
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST
        )
    except psycopg2.OperationalError as e:
        st.error(f"Error connecting to PostgreSQL: {e}")
        return None, None

    try:
        # --- Step 1: Find the single most recent timestamp ---
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(time) FROM copernicus_data;")
            most_recent_time = cur.fetchone()[0]
        
        if most_recent_time is None:
            return None, None

        # --- Step 2: Fetch all variables for that timestamp ---
        sql_query = """
        SELECT latitude, longitude, thetao, so, uo, vo
        FROM copernicus_data
        WHERE time = %s AND thetao IS NOT NULL;
        """
        df = pd.read_sql_query(sql_query, conn, params=(most_recent_time,))
        
        plot_title = f'Copernicus Data Heatmaps for {most_recent_time.strftime("%Y-%m-%d %H:%M")}'
        
    except Exception as e:
        st.error(f"Error during SQL query: {e}")
        return None, None
    finally:
        conn.close()

    print(f"Successfully fetched {len(df)} data points.")
    return df, plot_title

def create_plot(df):
    """Generates the 2x2 heatmap figure from a DataFrame."""
    print("Generating 2x2 geospatial heatmaps...")
    
    variables = ['thetao', 'so', 'uo', 'vo']
    titles = ['Temperature (°C)', 'Salinity', 'Eastward Velocity (m/s)', 'Northward Velocity (m/s)']
    cmaps = ['jet', 'viridis', 'RdBu_r', 'RdBu_r']
    
    fig, axes = plt.subplots(
        nrows=2, 
        ncols=2, 
        figsize=(16, 12), 
        subplot_kw={'projection': ccrs.PlateCarree()}
    )
    axes = axes.flatten()
    
    # Get boundaries from the data
    min_lon, max_lon = df['longitude'].min(), df['longitude'].max()
    min_lat, max_lat = df['latitude'].min(), df['latitude'].max()

    for i, var in enumerate(variables):
        ax = axes[i]
        lons = df['longitude']
        lats = df['latitude']
        values = df[var]

        # Use tricontourf for heatmap from unstructured (x,y,z) data
        plot = ax.tricontourf(lons, lats, values, levels=15, cmap=cmaps[i], transform=ccrs.PlateCarree())
        
        ax.coastlines()
        ax.gridlines(draw_labels=True, linestyle='--')
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
        
        fig.colorbar(plot, ax=ax, orientation='vertical', shrink=0.8)
        ax.set_title(titles[i])

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to make room for suptitle
    return fig

# --- Main Application ---
st.title("Copernicus Data Dashboard")

# The button will trigger a re-run of the script
if st.button("Refresh Data"):
    # This clears the cache for our function
    st.cache_data.clear()

# Fetch the data (from cache or DB)
df, plot_title = fetch_data()

if df is None or df.empty:
    st.warning("No data found in the database. Please run the importer.")
else:
    # Set the title for the plot
    st.header(plot_title)

    # Create and display the plot
    fig = create_plot(df)
    st.pyplot(fig)
    
    # Also display the raw data in a table
    st.header("Raw Data (Most Recent)")
    st.dataframe(df)