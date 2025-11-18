import json
import os
import xarray as xr
from datetime import datetime
from pipeline.common.paths import CLEAN_PATH

def clean(nc_path):
    # Output directory: /data/clean/ocean/
    outdir = CLEAN_PATH('ocean')
    outdir.mkdir(parents=True, exist_ok=True)

    # Timestamped output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = outdir / f"cleaned_{timestamp}.jsonl"

    try:
        # Load NetCDF
        ds = xr.open_dataset(nc_path)

        # Convert to DataFrame
        df = ds.to_dataframe().reset_index()

        # Basic filters
        df = df.dropna(subset=['time', 'latitude', 'longitude'])
        df = df[df['so'].between(0, 50)]
        df = df[df['thetao'].between(-5, 40)]

        # Write JSONL
        with open(outfile, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                f.write(json.dumps(row.to_dict(), default=str) + '\n')

    except Exception:
        # If anything fails, still create an empty JSONL file
        with open(outfile, 'w', encoding='utf-8'):
            print("Cleaning failed.")
            pass
    
    if os.path.getsize(outfile):
        return str(outfile)
    
    else:
        print("Empty ocean file.")


if __name__ == '__main__':
    import sys
    print(clean(sys.argv[1] if len(sys.argv) > 1 else '/data/raw/ocean/latest.nc'))
