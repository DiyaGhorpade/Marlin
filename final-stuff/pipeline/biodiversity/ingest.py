import requests
from pipeline.common.paths import RAW_PATH
def scrape_links():
    url = 'https://obis.org/node/1a3b0f1a-4474-4d73-9ee1-d28f92a83996'
    try:
        r = requests.get(url, timeout=15)
        return [url]  # simplified for test; actual link scraping occurs in dedicated script
    except Exception as e:
        print('scrape error', e)
        return []
def ingest():
    raw = RAW_PATH('biodiversity')
    raw.mkdir(parents=True, exist_ok=True)
    return []
if __name__ == '__main__':
    print(ingest())
