import os
import json
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

KAFKA_TOPIC = 'fisheries_data'
KAFKA_BROKER = 'kafka:9092'

POSTGRES_HOST = 'postgres'
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# --- CONNECT TO POSTGRES ---
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        conn.autocommit = True
        print("✅ Connected to PostgreSQL")
        return conn
    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)
        raise

# --- CREATE TABLES IF NOT EXISTS ---
def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS state_landings (
            id SERIAL PRIMARY KEY,
            state VARCHAR(255),
            year INT,
            landings_lakh FLOAT,
            landings_tonnes FLOAT
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS species_landings (
            id SERIAL PRIMARY KEY,
            species VARCHAR(255),
            year INT,
            landings_tonnes FLOAT
        );
        """)
        print("✅ Tables ensured in PostgreSQL")

# --- INSERT FUNCTIONS ---
def insert_state_record(conn, record):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO state_landings (state, year, landings_lakh, landings_tonnes)
            VALUES (%s, %s, %s, %s);
        """, (
            record.get("State/UT"),
            record.get("Year"),
            record.get("Estimated Landings (lakh tonnes)"),
            record.get("Estimated Landings (tonnes)")
        ))

def insert_species_record(conn, record):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO species_landings (species, year, landings_tonnes)
            VALUES (%s, %s, %s);
        """, (
            record.get("Species/Group"),
            record.get("Year"),
            record.get("Landings (tonnes)")
        ))

# --- MAIN CONSUMER LOOP ---
def consume_kafka_messages():
    conn = get_db_connection()
    create_tables(conn)

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='fish_data_consumers'
    )

    print(f"🎣 Listening for messages on Kafka topic: {KAFKA_TOPIC}")

    try:
        for message in consumer:
            msg = message.value
            msg_type = msg.get("type")
            data = msg.get("data", {})

            if msg_type == "state":
                insert_state_record(conn, data)
                print(f"⬇ Inserted state record: {data.get('State/UT')}")
            elif msg_type == "species":
                insert_species_record(conn, data)
                print(f"⬇ Inserted species record: {data.get('Species/Group')}")
            else:
                print("⚠ Unknown message type:", msg_type)

    except KeyboardInterrupt:
        print("\n🛑 Stopping consumer gracefully...")
    except Exception as e:
        print("❌ Error while consuming messages:", e)
    finally:
        conn.close()
        consumer.close()

# --- ENTRY POINT ---
if __name__ == "__main__":
    consume_kafka_messages()
