import json
from pipeline.common.paths import CLEAN_PATH
def clean(file_paths):
    out = CLEAN_PATH('biodiversity')
    out.mkdir(parents=True, exist_ok=True)
    outpath = out / 'filtered_dwc.jsonl'
    # If JSON files exist in file_paths, try to extract 'results'
    written = 0
    for p in file_paths or []:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for rec in data.get('results', []):
                    out.write(json.dumps(rec) + '\n')
                    written += 1
        except Exception:
            pass
    open(outpath, 'a').close()
    return str(outpath)
if __name__=='__main__':
    print(clean([]))
