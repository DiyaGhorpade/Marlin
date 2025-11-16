import psycopg2
import pandas as pd

# ---- CONFIG ----
DB_NAME = "Marlin"
DB_USER = "postgres"
DB_PASS = ""
DB_HOST = "localhost"
DB_PORT = "5432"

CSV_FILE = "indOBIS_cleaned.csv"

# ----------------

def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biodiversity_data (
            sl_no SERIAL PRIMARY KEY,
            occurrenceID TEXT,
            scientificName TEXT,
            kingdom TEXT,
            phylum TEXT,
            class TEXT,
            order_name TEXT,
            family TEXT,
            genus TEXT,
            species TEXT,
            decimalLatitude DOUBLE PRECISION,
            decimalLongitude DOUBLE PRECISION,
            country TEXT,
            locality TEXT,
            waterBody TEXT,
            eventDate TEXT
        );
    """)

def load_csv(cursor):
    df = pd.read_csv(CSV_FILE)

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO biodiversity_data (
                occurrenceID, scientificName, kingdom, phylum, class,
                order_name, family, genus, species,
                decimalLatitude, decimalLongitude, country,
                locality, waterBody, eventDate
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            row.get("occurrenceID"),
            row.get("scientificName"),
            row.get("kingdom"),
            row.get("phylum"),
            row.get("class"),
            row.get("order"),
            row.get("family"),
            row.get("genus"),
            row.get("species"),
            row.get("decimalLatitude"),
            row.get("decimalLongitude"),
            row.get("country"),
            row.get("locality"),
            row.get("waterBody"),
            row.get("eventDate")
        ))


def main():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    print("Creating table...")
    create_table(cursor)

    print("Loading CSV...")
    load_csv(cursor)

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Biodiversity CSV imported successfully!")


if __name__ == "__main__":
    main()
