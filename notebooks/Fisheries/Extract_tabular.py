import os
import pdfplumber
import pandas as pd

DATA_DIR = "data"
OUTPUT_FILE = "outputs/tabular_data.csv"

os.makedirs("outputs", exist_ok=True)


def extract_tabular_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                if table and len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df["source_file"] = os.path.basename(pdf_path)
                    tables.append(df)
    return tables


def parse_species_tables(tables, year=None):
    species_records = []
    for df in tables:
        if df.shape[1] >= 2:
            first_col = df.iloc[:, 0].astype(str).str.lower()
            if any(keyword in " ".join(first_col.head(5))
                   for keyword in ["fish", "prawn", "mackerel", "sardine", "species"]):
                df.columns = ["Species/Group", "Landings (tonnes)"] + df.columns[2:].tolist()
                df["Year"] = year
                species_records.append(df)
    return pd.concat(species_records, ignore_index=True) if species_records else pd.DataFrame()


def process_all_pdfs():
    all_records = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(DATA_DIR, file)
            print(f"📄 Processing tables from {file} ...")
            year = next((int(x) for x in file.split("_") if x.isdigit() and len(x) == 4), None)
            tables = extract_tabular_from_pdf(pdf_path)
            df = parse_species_tables(tables, year)
            if not df.empty:
                all_records.append(df)
    if all_records:
        combined = pd.concat(all_records, ignore_index=True)
        combined.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Saved combined tabular data to {OUTPUT_FILE}")
    else:
        print("⚠️ No tabular data extracted.")


if __name__ == "__main__":
    process_all_pdfs()
