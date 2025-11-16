import requests
from bs4 import BeautifulSoup
import pdfplumber
from urllib.parse import urljoin
from pipeline.common.paths import RAW_PATH
import os

# Import parsing modules
from .Extract_tabular import process_all_pdfs as parse_tabular
from .Extract_text import process_all_pdfs as parse_text

def ingest():
    
    BASE_URL = "https://www.cmfri.org.in"
    DATA_URL = 'https://www.cmfri.org.in/data-publications'
    raw = RAW_PATH('fisheries')
    raw.mkdir(parents=True, exist_ok=True)

    # Scrape PDF links
    try:
        response = requests.get(DATA_URL, timeout=15)
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

    # Download PDFs from the links
    downloaded_files = []
    for link in links:
        filename = raw / link.split("/")[-1]
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
    
    
    print("\n----- Running Tabular Parser -----")
    parse_tabular()

    print("\n----- Running Text Parser -----")
    parse_text()

    return downloaded_files

if __name__ == '__main__':
    print(ingest())
