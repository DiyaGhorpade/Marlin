import copernicusmarine
from datetime import datetime, timedelta
import xarray as xr
from dotenv import load_dotenv
from kafka import KafkaProducer
import os
import json

# Importing credentials

load_dotenv()  # reads from .env automatically
username = os.getenv("COPERNICUS_USERNAME")
password = os.getenv("COPERNICUS_PASSWORD")

KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'oceanographic_data'


# --- 1. Setup Kafka Producer ---
print(f"Connecting to Kafka broker at {KAFKA_BROKER}...")
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        # Serialize 'value' as JSON (and handle non-serializable types like timestamps)
        value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
    )
    print("Kafka Producer connected.")
except Exception as e:
    print(f"Error connecting to Kafka: {e}")
    print("Please ensure Kafka is running.")
    exit(1)


# Retrieving relevant subset
response = copernicusmarine.subset(
    username = username,
    password = password,
    dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
    variables=["so", "thetao", "uo", "vo", "zos"],
    minimum_longitude=62.7624394824933,
    maximum_longitude=95.10309461377467,
    minimum_latitude=3.1228444517411815,
    maximum_latitude=25.964845628380452,
    start_datetime=datetime.now() - timedelta(days = 2),
    end_datetime=datetime.now() - timedelta(days = 1),
    minimum_depth=0.49402499198913574,
    maximum_depth=0.49402499198913574,
)
print(f"Data downloaded: {response.file_path} (Size: {response.file_size} MB)")

# --- 4. Open Dataset with xarray ---
print("Opening .nc file with xarray...")
with xr.open_dataset(os.fspath(response.file_path), engine="h5netcdf") as data:

    # --- 5. Convert to DataFrame ---
    print("Converting to DataFrame...")
    # This flattens the multi-dimensional data into a 2D table
    df = data.to_dataframe()

    # --- 6. Clean the DataFrame ---
    # Move 'time', 'latitude', 'longitude', 'depth' from index to columns
    df = df.reset_index()
    # Remove any rows with missing data
    df = df.dropna()
    print(f"Converted to DataFrame with {len(df)} valid data points.")

    # --- 7. Iterate and Send to Kafka ---
    if not df.empty:
        print(f"Sending {len(df)} messages to Kafka topic '{KAFKA_TOPIC}'...")
        for _, row in df.iterrows():
            # Convert row to a dictionary
            message = row.to_dict()

            # Send the message
            producer.send(KAFKA_TOPIC, value=message)

        # Ensure all messages are sent before exiting
        producer.flush()
        print("All messages sent successfully.")
    else:
        print("No data to send.")

# --- 8. Clean up the downloaded file ---
if 'response' in locals() and os.path.exists(response.file_path):
    os.remove(response.file_path)
    print(f"Cleaned up file: {response.file_path}")

