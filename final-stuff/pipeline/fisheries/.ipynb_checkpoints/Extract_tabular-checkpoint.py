import os
import pdfplumber
import pandas as pd
from pipeline.common.paths import RAW_PATH

DATA_DIR = RAW_PATH("fisheries")
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

    for table in tables:
        
        # Deduplicate column names
        columns = table.columns.tolist()
        fixed_columns = []
        seen = {}

        for col in columns:
            if col not in seen:
                fixed_columns.append(col)
                seen[col] = 1
            else:
                new_col = f"{col}_{seen[col]}"
                fixed_columns.append(new_col)
                seen[col] += 1

        table.columns = fixed_columns
        df = table.copy()

        # Filtering for tables containing species-wise landing data
        if df.shape[1] >= 2: # ignore page nos list
            first_col = df.iloc[:, 0].astype(str).str.lower() # name of first col

            if any(keyword in " ".join(first_col.head(5)) # look for associated keywords in the first 5 rows
                   for keyword in ["fish", "prawn", "mackerel", "sardine", "species"]):

                # Standardise names
                df.columns = ["Species/Group", "Landings (tonnes)"] + df.columns[2:].tolist()

                df["Year"] = year
                species_records.append(df)

    # Final concatenation to obtain one combined dataset for given PDF file
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
