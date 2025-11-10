import os
import time
import json
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

KAFKA_TOPIC = 'data_updates'
KAFKA_BROKER = 'kafka:9092'
POSTGRES_HOST = 'postgres'
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

def get_db_connection():
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST
            )
            print("Successfully connected to PostgreSQL.")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            print(f"Retrying in 5 seconds... ({retries} retries left)")
            retries -= 1
            time.sleep(5)
    
    print("❌ Failed to connect to PostgreSQL after multiple retries.")
    return None

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS copernicus_data (
            id SERIAL PRIMARY KEY,
            time TIMESTAMPTZ NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            depth FLOAT,
            so FLOAT,      -- Salinity
            thetao FLOAT,  -- Temperature
            uo FLOAT,      -- Eastward sea water velocity
            vo FLOAT       -- Northward sea water velocity
        );
        """)
        
        # Create an index on time for faster queries
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_copernicus_data_time 
        ON copernicus_data (time);
        """)
        conn.commit()
    print("✅ Table 'copernicus_data' is ready.")

def main():
    conn = get_db_connection()
    if conn is None:
        return # Exit if DB connection failed

    # Ensure the table exists
    create_table(conn)

    print(f"Connecting to Kafka broker at {KAFKA_BROKER}...")
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest', # Start from the beginning of the topic
        group_id='db-inserter-group',   # Allows multiple consumers to share the load
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print(f"🎧 Listening for messages on topic '{KAFKA_TOPIC}'...")

    insert_query = """
    INSERT INTO copernicus_data (time, latitude, longitude, depth, so, thetao, uo, vo)
    VALUES (%(time)s, %(latitude)s, %(longitude)s, %(depth)s, %(so)s, %(thetao)s, %(uo)s, %(vo)s)
    """

    for message in consumer:
        try:
            data = message.value
            # The data from your importer is already a perfect dict
            
            with conn.cursor() as cur:
                cur.execute(insert_query, data)
                conn.commit()
            
            print(f"Inserted data for time: {data.get('time')}")
        
        except Exception as e:
            print(f"Error processing message: {e}")
            conn.rollback() # Roll back the failed transaction

if __name__ == "__main__":
    main()