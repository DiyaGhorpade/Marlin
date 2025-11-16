#!/usr/bin/env python3
import zipfile
import pandas as pd
from pathlib import Path
from pipeline.common.paths import RAW_PATH, CLEAN_PATH


def extract_dwca(zip_path: Path, out_dir: Path):
    print(f"[extract] Extracting {zip_path} → {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)

    print("[extract] Done.")
    return out_dir


def load_if_exists(path: Path, sep="\t"):
    if path.exists():
        print(f"[load] Loading {path.name}")
        return pd.read_csv(path, sep=sep, low_memory=False)
    print(f"[load] {path.name} not found, skipping.")
    return None


def clean_occurrence(df):
    print("[clean] Cleaning occurrence.txt")

    df = df.dropna(axis=1, how="all")

    for col in ["decimalLatitude", "decimalLongitude"]:
        if col in df.columns:
            df.loc[:, col] = pd.to_numeric(df[col], errors="coerce")

    if "eventDate" in df.columns:
        df["eventDate"] = pd.to_datetime(df["eventDate"], errors="coerce", utc=True)

    important = ["scientificName", "decimalLatitude", "decimalLongitude"]
    df = df.dropna(subset=[c for c in important if c in df.columns])

    return df


def clean_event(df):
    print("[clean] Cleaning event.txt")
    df = df.dropna(axis=1, how="all")

    if "eventDate" in df.columns:
        df["eventDate"] = pd.to_datetime(df["eventDate"], errors="coerce")

    return df


def clean_mof(df):
    print("[clean] Cleaning measurementOrFact.txt")
    df = df.dropna(axis=1, how="all")
    return df


def clean_dataset(ds_raw_dir: Path, clean_root: Path):
    ds_id = ds_raw_dir.name
    print(f"\n[clean step] Processing dataset: {ds_id}")

    zip_path = ds_raw_dir / "dwca.zip"
    if not zip_path.exists():
        print("[clean step] No dwca.zip found → skipping.")
        return

    extract_dir = extract_dwca(zip_path, ds_raw_dir / "dwca_extracted")
    ds_clean_dir = clean_root / ds_id
    ds_clean_dir.mkdir(parents=True, exist_ok=True)

    occ = load_if_exists(extract_dir / "occurrence.txt")
    evt = load_if_exists(extract_dir / "event.txt")
    mof = load_if_exists(extract_dir / "measurementOrFact.txt")

    if occ is not None:
        occ = clean_occurrence(occ)
        occ.to_csv(ds_clean_dir / "occurrence_clean.csv", index=False)
        print("[save] occurrence_clean.csv")

    if evt is not None:
        evt = clean_event(evt)
        evt.to_csv(ds_clean_dir / "event_clean.csv", index=False)
        print("[save] event_clean.csv")

    if mof is not None:
        mof = clean_mof(mof)
        mof.to_csv(ds_clean_dir / "measurement_clean.csv", index=False)
        print("[save] measurement_clean.csv")

    print(f"[clean step] Completed: {ds_id}")


def run_clean_step():
    raw_root = RAW_PATH("biodiversity")
    clean_root = CLEAN_PATH("biodiversity")

    clean_root.mkdir(parents=True, exist_ok=True)

    print("[clean] Running clean step for all datasets...")

    for ds_dir in raw_root.iterdir():
        if ds_dir.is_dir():
            clean_dataset(ds_dir, clean_root)

    print("\n[clean] All datasets cleaned.")


if __name__ == "__main__":
    run_clean_step()
