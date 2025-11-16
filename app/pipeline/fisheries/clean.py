import json
import os
import pandas as pd
from pathlib import Path
from pipeline.common.paths import CLEAN_PATH

TABULAR_CSV = "outputs/tabular_data.csv"
TEXTUAL_CSV = "outputs/textual_data.csv"


def load_if_exists(path):
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            print(f"[clean] Failed loading {path}: {e}")
    return pd.DataFrame()


def normalize_tabular(df):
    if df.empty:
        return df

    df_norm = pd.DataFrame()

    df_norm["source"] = "tabular"
    df_norm["species"] = df.get("Species/Group")
    df_norm["state"] = None
    df_norm["landings_tonnes"] = pd.to_numeric(df.get("Landings (tonnes)"), errors="coerce")
    df_norm["landings_lakh_tonnes"] = None
    df_norm["year"] = df.get("Year")
    df_norm["eventDate"] = df_norm["year"].apply(
        lambda y: str(int(y)) if pd.notnull(y) else None
    )
    df_norm["source_file"] = df.get("source_file")

    return df_norm.dropna(subset=["species", "landings_tonnes"], how="all")


def normalize_textual(df):
    if df.empty:
        return df

    df_norm = pd.DataFrame()

    df_norm["source"] = "textual"
    df_norm["species"] = None
    df_norm["state"] = df.get("State/UT")
    df_norm["landings_tonnes"] = pd.to_numeric(df.get("Estimated Landings (tonnes)"), errors="coerce")
    df_norm["landings_lakh_tonnes"] = pd.to_numeric(df.get("Estimated Landings (lakh tonnes)"), errors="coerce")
    df_norm["year"] = df.get("Year")
    df_norm["source_file"] = None

    return df_norm.dropna(subset=["state", "landings_tonnes"], how="all")


def clean(pdf_files=None):
    """
    Combine fisheries tabular + textual extraction outputs
    into a single cleaned JSONL.
    """
    outdir = CLEAN_PATH("fisheries")
    outdir.mkdir(parents=True, exist_ok=True)

    outpath = outdir / "cleaned_dwc.jsonl"

    print("[clean] Loading extraction outputs...")
    tab_df = load_if_exists(TABULAR_CSV)
    txt_df = load_if_exists(TEXTUAL_CSV)

    print(f"[clean] Tabular rows: {len(tab_df)}")
    print(f"[clean] Textual rows: {len(txt_df)}")

    tab_norm = normalize_tabular(tab_df)
    txt_norm = normalize_textual(txt_df)

    final = pd.concat([tab_norm, txt_norm], ignore_index=True)

    print(f"[clean] Combined cleaned rows: {len(final)}")

    # Write JSONL
    with open(outpath, "w", encoding="utf-8") as f:
        for _, row in final.iterrows():
            f.write(json.dumps(row.to_dict()) + "\n")

    print(f"[clean] Saved cleaned JSONL → {outpath}")
    return str(outpath)


if __name__ == "__main__":
    clean()
