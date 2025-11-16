import os
import time
import json
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

TOPIC = "fisheries_data"

# -------------------------------------------------
# Kafka Consumer
# -------------------------------------------------
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="kafka:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)


# -------------------------------------------------
# DB connection helper
# -------------------------------------------------
def get_db():
    for _ in range(8):
        try:
            return psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST", "postgres"),
            )
        except Exception:
            time.sleep(2)
    raise RuntimeError("DB connection failed")


conn = get_db()

# -------------------------------------------------
# Create table if not exists
# -------------------------------------------------
with conn.cursor() as cur:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS fisheries_dwc(
            id SERIAL PRIMARY KEY,
            eventDate DATE,
            locality TEXT,
            measurementType TEXT,
            measurementValue DOUBLE PRECISION,
            measurementUnit TEXT,
            verbatimDepth TEXT,
            scientificName TEXT,
            occurrenceRemarks TEXT,
            source_file TEXT
        )
        """
    )
    conn.commit()


# -------------------------------------------------
# Insert SQL
# -------------------------------------------------
ins = """
INSERT INTO fisheries_dwc(
    eventDate,
    locality,
    measurementType,
    measurementValue,
    measurementUnit,
    verbatimDepth,
    scientificName,
    occurrenceRemarks,
    source_file
)
VALUES (
    %(eventDate)s,
    %(locality)s,
    %(measurementType)s,
    %(measurementValue)s,
    %(measurementUnit)s,
    %(verbatimDepth)s,
    %(scientificName)s,
    %(occurrenceRemarks)s,
    %(source_file)s
)
"""


# -------------------------------------------------
# Consume + Insert Loop
# -------------------------------------------------
print("🔥 Fisheries consumer started. Waiting for messages...")

for msg in consumer:
    try:
        v = msg.value  # Raw fisheries record from clean.py

        # -------------------------------
        # Map Fisheries → Darwin Core
        # -------------------------------
        rec = {
            # eventDate from "2021" → "2021-01-01"
            "eventDate": None,
            "locality": v.get("state"),
            "measurementType": "landings_tonnes",
            "measurementValue": v.get("landings_tonnes"),
            "measurementUnit": "tonnes",
            "verbatimDepth": None,
            "scientificName": v.get("species"),
            "occurrenceRemarks": v.get("source"),
            "source_file": v.get("source_file"),
        }

        # EventDate conversion
        if v.get("eventDate"):
            # Convert "2021" → "2021-01-01"
            year = str(v["eventDate"])[:4]
            rec["eventDate"] = f"{year}-01-01"

        # -------------------------------
        # Insert into Postgres
        # -------------------------------
        with conn.cursor() as cur:
            cur.execute(ins, rec)
            conn.commit()

    except Exception as e:
        conn.rollback()
        print("❌ insert error:", e)
