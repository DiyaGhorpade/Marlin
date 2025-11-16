import time
import json
import requests
from pathlib import Path
from pipeline.common.paths import RAW_PATH

HEADERS = {"User-Agent": "Mozilla/5.0"}
NODE_ID = "1a3b0f1a-4474-4d73-9ee1-d28f92a83996"
BASE_URL = "https://api.obis.org/dataset"


def fetch_page(offset=0, limit=200, retries=5, timeout=60):
    # ask for 200 items so we get all 77 in ONE request
    url = f"{BASE_URL}?nodeid={NODE_ID}&size={limit}&skip={offset}"

    for attempt in range(1, retries + 1):
        try:
            print(f"[fetch_page] Fetching offset={offset}")
            r = requests.get(url, timeout=timeout, headers=HEADERS)
            r.raise_for_status()
            print(f"[fetch_page] Success offset={offset}")
            return r.json()

        except requests.Timeout:
            wait = attempt * 2
            print(f"[fetch_page] Timeout offset={offset}. Retrying in {wait}s...")
            time.sleep(wait)

        except requests.RequestException as e:
            print(f"[fetch_page] Request error offset={offset}: {e}")
            if attempt == retries:
                raise
            time.sleep(attempt * 2)

    raise RuntimeError(f"[fetch_page] Failed after {retries} retries (offset {offset})")


def download(url, out_path, retries=5, timeout=120):
    print(f"[download] Downloading {url} → {out_path.name}")

    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=timeout, headers=HEADERS) as r:
                r.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
            print(f"[download] Done: {out_path.name}")
            return

        except requests.Timeout:
            wait = attempt * 2
            print(f"[download] Timeout for {url}. Retrying in {wait}s...")
            time.sleep(wait)

        except requests.RequestException as e:
            print(f"[download] Error: {e}")
            if attempt == retries:
                print(f"[download] Giving up: {url}")
                return
            time.sleep(attempt * 2)


def ingest():
    print("[ingest] Starting OBIS biodiversity ingestion...")
    raw_root = RAW_PATH("biodiversity")
    raw_root.mkdir(parents=True, exist_ok=True)

    # Fetch one big page containing all 77 datasets
    print("[ingest] Fetching datasets (single page)...")
    first = fetch_page(0, limit=200)  # ask for all in one go
    total = first["total"]
    datasets = first["results"]

    print(f"[ingest] Total datasets reported by OBIS: {total}")
    print(f"[ingest] Total datasets collected: {len(datasets)}")

    downloaded_ids = []

    for i, ds in enumerate(datasets, start=1):
        ds_id = ds["id"]
        archive_url = ds.get("archive")

        print(f"\n[ingest] ({i}/{len(datasets)}) Processing dataset: {ds_id}")

        if not archive_url:
            print("[ingest] Skipping (no archive URL)")
            continue

        ds_dir = raw_root / ds_id
        ds_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata properly
        meta_path = ds_dir / "meta.json"
        meta_path.write_text(json.dumps(ds, indent=2), encoding="utf-8")
        print("[ingest] Saved meta.json")

        # Download DWCA archive
        dwca_path = ds_dir / "dwca.zip"
        download(archive_url, dwca_path)

        # EML + metadata URLs
        base = archive_url.split("archive.do")[0]
        resource = archive_url.split("=")[1]

        eml_url = f"{base}eml.do?r={resource}"
        meta_url = f"{base}metadata.do?r={resource}"

        download(eml_url, ds_dir / "eml.xml")
        download(meta_url, ds_dir / "metadata.xml")

        downloaded_ids.append(ds_id)

    print(f"\n[ingest] Finished. Downloaded {len(downloaded_ids)} datasets.")
    return downloaded_ids


if __name__ == "__main__":
    print(ingest())
