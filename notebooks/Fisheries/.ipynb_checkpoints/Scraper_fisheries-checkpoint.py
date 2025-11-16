import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# config
BASE_URL = "https://www.cmfri.org.in"
DATA_URL = "https://www.cmfri.org.in/data-publications"
DOWNLOAD_DIR = "data"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# scrape PDF links
def fetch_pdf_links():
    print("Fetching PDF links from CMFRI website...")
    try:
        response = requests.get(DATA_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        links = [
            urljoin(BASE_URL, a["href"])
            for a in soup.find_all("a", href=True)
            if a["href"].lower().endswith(".pdf")
            and re.search(r"fish.*landing", a["href"].lower())
        ]
        print(f"Found {len(links)} PDF links.")
        return links
    except Exception as e:
        print("Error fetching links:", e)
        return []


# download PDFs
def download_pdfs(links):
    downloaded_files = []
    for link in links:
        filename = os.path.join(DOWNLOAD_DIR, os.path.basename(link))
        try:
            if not os.path.exists(filename):
                print(f"Downloading {filename} ...")
                r = requests.get(link, timeout=15)
                r.raise_for_status()
                with open(filename, "wb") as f:
                    f.write(r.content)
                print(f"Saved: {filename}")
            else:
                print(f"Already exists: {filename}")
            downloaded_files.append(filename)
        except Exception as e:
            print(f"Failed to download {link}: {e}")
    return downloaded_files

if __name__ == "__main__":
    links = fetch_pdf_links()
    if not links:
        print("No relevant PDF links found. Exiting.")
        exit()

    files = download_pdfs(links)
    if not files:
        print("No PDFs downloaded. Exiting.")
    else:
        print(f"\nStage 1 complete. Downloaded {len(files)} file(s):")
        for f in files:
            print("   -", f)

