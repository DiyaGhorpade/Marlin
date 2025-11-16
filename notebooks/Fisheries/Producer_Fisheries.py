import os
import re
import json
import requests
import pdfplumber
import pandas as pd
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from urllib.parse import urljoin

# configuration
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'fisheries_data'
BASE_URL = "https://www.cmfri.org.in"
DATA_URL = "https://www.cmfri.org.in/data-publications"
DOWNLOAD_DIR = "data"

# set up directories
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# scrape PDF links
print("Fetching PDF links from CMFRI website...")
try:
    response = requests.get(DATA_URL, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    links = [
        urljoin(BASE_URL, a["href"])
        for a in soup.find_all("a", href=True)
        if a["href"].lower().endswith(".pdf")
        and "fish" in a["href"].lower()
        and "landing" in a["href"].lower()
    ]
    if not links:
        raise ValueError("No relevant PDF links found.")
    print(f"Found {len(links)} PDF links.")
except Exception as e:
    print("Error fetching links:", e)
    links = []

# download PDFs
downloaded_files = []
for link in links:
    filename = os.path.join(DOWNLOAD_DIR, link.split("/")[-1])
    try:
        if not os.path.exists(filename):
            print(f"Downloading {filename} ...")
            r = requests.get(link, timeout=15)
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)
        else:
            print(f"Already exists: {filename}")
        downloaded_files.append(filename)
    except Exception as e:
        print(f"Failed to download {link}: {e}")

if not downloaded_files:
    raise SystemExit("No PDFs downloaded. Exiting.")

# extract data
for pdf_path in downloaded_files:
    try:
        print(f"Processing {pdf_path} ...")
        year_match = re.search(r"(20\d{2})", pdf_path)
        year = int(year_match.group(1)) if year_match else None

        full_text = ""
        tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text
                for table in page.extract_tables():
                    if table:
                        df = pd.DataFrame(table)
                        tables.append(df)

        # --- Extract state-level summary ---
        state_pattern = r"([A-Za-z &]+)\s*Estimated Landings:\s*([\d\.]+)\s*lakh tonnes"
        matches = re.findall(state_pattern, full_text)
        if matches:
            state_df = pd.DataFrame(matches, columns=["State/UT", "Estimated Landings (lakh tonnes)"])
            state_df["Year"] = year
            state_df["Estimated Landings (tonnes)"] = (
                state_df["Estimated Landings (lakh tonnes)"].astype(float) * 100000
            )

            # Produce each record to Kafka
            for _, row in state_df.iterrows():
                record = row.to_dict()
                producer.send(KAFKA_TOPIC, {"type": "state", "data": record})
            print(f"✅ Produced {len(state_df)} state records to Kafka")

        # --- Extract species-level tables ---
        for df in tables:
            if df.shape[1] >= 2:
                first_col = df.iloc[:, 0].astype(str).str.lower()
                if any(w in first_col.iloc[0] for w in ["fish", "mackerel", "sardine", "prawn", "species"]):
                    cleaned = df.rename(columns={df.columns[0]: "Species/Group", df.columns[1]: "Landings (tonnes)"})
                    cleaned["Year"] = year
                    for _, row in cleaned.iterrows():
                        record = row.to_dict()
                        producer.send(KAFKA_TOPIC, {"type": "species", "data": record})
                    print(f"✅ Produced {len(cleaned)} species records to Kafka")

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

# --- STEP 4: FLUSH AND CLOSE ---
producer.flush()
producer.close()
print("\n🎣 All data successfully produced to Kafka topic:", KAFKA_TOPIC)
