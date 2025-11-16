#!/usr/bin/env python3
import json
import pandas as pd
from pathlib import Path
from pipeline.common.paths import CLEAN_PATH
import math


def merge_cleaned_biodiversity():
    clean_root = CLEAN_PATH("biodiversity")
    output_file = clean_root / "cleaned_dwc.jsonl"

    print(f"[merge] Scanning cleaned dataset folders in: {clean_root}")

    count = 0

    with open(output_file, "w", encoding="utf-8") as out:

        for ds_dir in clean_root.iterdir():
            if not ds_dir.is_dir():
                continue

            ds_id = ds_dir.name
            csv_path = ds_dir / "occurrence_clean.csv"

            if not csv_path.exists():
                print(f"[merge] No CSV found for dataset {ds_id}, skipping.")
                continue

            print(f"[merge] Reading: {csv_path}")

            try:
                df = pd.read_csv(csv_path)
            except Exception as e:
                print(f"[merge] Failed to load {csv_path}: {e}")
                continue

            # Convert dataframe rows to JSONL records
            for _, row in df.iterrows():

                record = row.to_dict()

                # Convert NaN → None (Postgres-safe)
                for k, v in record.items():
                    if isinstance(v, float) and math.isnan(v):
                        record[k] = None

                # Add required DWCA provenance field
                record["source_file"] = ds_id

                out.write(json.dumps(record) + "\n")
                count += 1

    print(f"[merge] Finished merging → {output_file}")
    print(f"[merge] Total records written: {count}")

    return output_file

def merge(files):
    return merge_cleaned_biodiversity()

    
if __name__ == "__main__":
    merge_cleaned_biodiversity()
