import os
import time
import json
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

KAFKA_TOPIC = "oceanographic_data"
KAFKA_BROKER = "kafka:9092"

POSTGRES_HOST = "postgres"
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


# Helper logging with colors (matches your style)
def info(msg):
    print(f"\033[96m[INFO]\033[0m {msg}")

def success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")

def warn(msg):
    print(f"\033[93m[WARN]\033[0m {msg}")

def error(msg):
    print(f"\033[91m[ERROR]\033[0m {msg}")


# Database connection
def get_db():
    retries = 10
    while retries > 0:
        try:
            info("Connecting to PostgreSQL...")
            conn = psycopg2.connect(
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST
            )
            success("Connected to PostgreSQL.")
            return conn
        except psycopg2.OperationalError as e:
            warn(f"Postgres connection failed: {e}")
            warn(f"Retrying in 5 seconds... ({retries} retries left)")
            retries -= 1
            time.sleep(5)

    error("Failed to connect to PostgreSQL after multiple retries.")
    return None


# Create table + index
def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS copernicus_data (
            id SERIAL PRIMARY KEY,
            time TIMESTAMPTZ NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            depth FLOAT,
            so FLOAT,
            thetao FLOAT,
            uo FLOAT,
            vo FLOAT
        );
        """)

        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_copernicus_data_time 
        ON copernicus_data (time);
        """)

        conn.commit()

    success("Table 'copernicus_data' is ready.")


# Main consumer
def main():
    conn = get_db()
    if conn is None:
        return

    create_table(conn)

    info(f"Connecting to Kafka broker at {KAFKA_BROKER}...")
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        group_id="ocean-db-writer",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    success(f"Listening for messages on topic '{KAFKA_TOPIC}'...\n")

    insert_query = """
        INSERT INTO copernicus_data (
            time, latitude, longitude, depth, so, thetao, uo, vo
        )
        VALUES (
            %(time)s, %(latitude)s, %(longitude)s,
            %(depth)s, %(so)s, %(thetao)s, %(uo)s, %(vo)s
        )
    """

    count = 0

    for message in consumer:
        try:
            data = message.value

            with conn.cursor() as cur:
                cur.execute(insert_query, data)
                conn.commit()

            count += 1
            success(f"Inserted #{count}: time={data.get('time')} lat={data.get('latitude')} lon={data.get('longitude')}")

        except Exception as e:
            conn.rollback()
            error(f"Insert failed: {e}")
            warn(f"Offending record: {data}")
            time.sleep(0.3)


if __name__ == "__main__":
    main()
