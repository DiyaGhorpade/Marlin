import os
import time
import json
import pandas as pd
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()
KAFKA_BROKER = 'kafka:9092'
POSTGRES_HOST = 'postgres'
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
TOPIC = "biodiversity_data"

# --- Pretty Colored Output ---
def info(msg):
    print(f"\033[96m[INFO]\033[0m {msg}")

def success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")

def warn(msg):
    print(f"\033[93m[WARN]\033[0m {msg}")

def error(msg):
    print(f"\033[91m[ERROR]\033[0m {msg}")


# --- DB Connection Helper ---
def get_db():
    for attempt in range(1, 9):
        try:
            info(f"Connecting to Postgres (attempt {attempt}/8)...")
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST", "postgres")
            )
            success("Connected to Postgres.")
            return conn
        except Exception as e:
            warn(f"DB connection failed: {e}")
            time.sleep(2)
    raise RuntimeError("Could not connect to DB after 8 attempts.")


# --- Connect Kafka Consumer ---
def get_consumer():
    for attempt in range(1, 9):
        try:
            info(f"Connecting to Kafka (attempt {attempt}/8)...")
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers="kafka:9092",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True
            )
            success(f"Subscribed to topic '{TOPIC}'.")
            return consumer
        except Exception as e:
            warn(f"Kafka connection failed: {e}")
            time.sleep(2)
    raise RuntimeError("Could not connect to Kafka.")


# --- Setup ---
conn = get_db()
consumer = get_consumer()

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS biodiversity_dwc (
            id SERIAL PRIMARY KEY,
            eventDate DATE,
            decimalLatitude FLOAT,
            decimalLongitude FLOAT,
            minimumDepthInMeters FLOAT,
            maximumDepthInMeters FLOAT,
            scientificName TEXT,
            occurrenceID TEXT,
            source_file TEXT
        )
    """)
    conn.commit()
    success("Table ensured: biodiversity_dwc")


# --- Insert Query ---
ins = """
INSERT INTO biodiversity_dwc (
    eventDate,
    decimalLatitude,
    decimalLongitude,
    minimumDepthInMeters,
    maximumDepthInMeters,
    scientificName,
    occurrenceID,
    source_file
)
VALUES (
    %(eventDate)s,
    %(decimalLatitude)s,
    %(decimalLongitude)s,
    %(minimumDepthInMeters)s,
    %(maximumDepthInMeters)s,
    %(scientificName)s,
    %(occurrenceID)s,
    %(source_file)s
)
"""


# --- Main Consumer Loop ---
info("Listening for messages...\n")

count = 0
for msg in consumer:
    try:
        v = msg.value

        # Normalize depth fields
        v["minimumDepthInMeters"] = (
            None if pd.isna(v.get("minimumDepthInMeters")) else v.get("minimumDepthInMeters")
        )
        
        v["maximumDepthInMeters"] = (
            None if pd.isna(v.get("maximumDepthInMeters")) else v.get("maximumDepthInMeters")
        )

        # Clean eventDate
        date = v.get("eventDate")

        if isinstance(date, str) and len(date) >= 10:
            v["eventDate"] = date[:10]
        else:
            v["eventDate"] = None

        with conn.cursor() as cur:
            cur.execute(ins, v)
            conn.commit()

        count += 1
        success(f"Inserted #{count}: {v.get('scientificName', 'unknown')} (occID={v.get('occurrenceID')})")

    except Exception as e:
        conn.rollback()
        error(f"Insert failed: {e}")
        warn(f"Offending record: {v}")
        time.sleep(0.5)
