import os
import re
import pdfplumber
import pandas as pd
import spacy

DATA_DIR = "data"
OUTPUT_FILE = "outputs/textual_data.csv"
os.makedirs("outputs", exist_ok=True)

# Initialize SpaCy with GPU acceleration
if spacy.prefer_gpu():
    print("Using GPU for SpaCy processing")
    spacy.require_gpu()
else:
    print("GPU not detected; falling back to CPU")


# Load large English model
# Disable components you don’t need (speeds up PDF text handling)
nlp = spacy.load("en_core_web_lg", disable=["parser", "lemmatizer"])
nlp.max_length = 3_000_000  # handle long documents

# PDF text extraction
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# Regex + NLP text cleaning
def clean_text_with_spacy(text):
    doc = nlp(text)
    cleaned = " ".join([t.text for t in doc if not t.is_space])
    return cleaned


def parse_state_landings(text, year=None):
    pattern = r"([A-Za-z &]+)\s*Estimated Landings:\s*([\d\.]+)\s*lakh tonnes"
    matches = re.findall(pattern, text)
    records = []
    for state, val in matches:
        records.append({
            "State/UT": state.strip(),
            "Estimated Landings (lakh tonnes)": float(val),
            "Estimated Landings (tonnes)": float(val) * 100000,
            "Year": year
        })
    return pd.DataFrame(records)


# Main PDF loop
def process_all_pdfs():
    all_records = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(DATA_DIR, file)
            print(f"Extracting text data from {file} ...")

            # Try to extract year from filename
            year = next((int(x) for x in file.split("_") if x.isdigit() and len(x) == 4), None)

            # Extract and clean
            raw_text = extract_text_from_pdf(pdf_path)
            cleaned_text = clean_text_with_spacy(raw_text)

            # Parse structured data
            df = parse_state_landings(cleaned_text, year)
            if not df.empty:
                all_records.append(df)

    if all_records:
        combined = pd.concat(all_records, ignore_index=True)
        combined.to_csv(OUTPUT_FILE, index=False)
        print(f"Saved combined textual data to {OUTPUT_FILE}")
    else:
        print("No textual data extracted.")


if __name__ == "__main__":
    process_all_pdfs()
