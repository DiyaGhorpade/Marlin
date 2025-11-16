import os
import re
import pdfplumber
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from pipeline.common.paths import RAW_PATH

DATA_DIR = RAW_PATH("fisheries")
OUTPUT_FILE = "outputs/textual_data.csv"
os.makedirs("outputs", exist_ok=True)


# PDF text extraction (with OCR)
def extract_text_from_pdf(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()

            # If pdfplumber extracted real text → use it
            if page_text and page_text.strip():
                text += page_text + "\n"
                continue

            print(f"  ▸ Page {i+1}: no digital text found → running OCR")

            # Convert this page only to an image
            images = convert_from_path(
                pdf_path,
                dpi=300,
                first_page=i + 1,
                last_page=i + 1
            )

            if images:
                ocr_text = pytesseract.image_to_string(images[0])
                text += ocr_text + "\n"

    return text


# Simple text cleaner
def clean_text(text):
    return " ".join(text.split())


# Parse state landings
def parse_state_landings(text, year=None):
    
    # India’s maritime states and UTs with landings
    states = [
        "Gujarat", "Tamil Nadu", "Kerala", "Karnataka", "Maharashtra",
        "Andhra Pradesh", "West Bengal", "Odisha", "Goa", "Daman & Diu",
        "Puducherry", "Andaman and Nicobar Islands", "Andaman & Nicobar Islands"
    ]

    # Build a dynamic regex
    state_regex = "|".join([re.escape(s) for s in states])

    pattern = rf"({state_regex})[^0-9]{{0,50}}([\d]+(?:\.\d+)?)[ ]*lakh"

    matches = re.findall(pattern, text, flags=re.IGNORECASE)

    records = []

    for state, val in matches:
        state_clean = state.strip().title()  # normalize casing

        try:
            tonnes_lakh = float(val)
        except:
            print(f"  ⚠️ Bad number '{val}' for state '{state_clean}'")
            continue

        records.append({
            "State/UT": state_clean,
            "Estimated Landings (lakh tonnes)": tonnes_lakh,
            "Estimated Landings (tonnes)": tonnes_lakh * 100000,
            "Year": year
        })

    return pd.DataFrame(records)


def process_all_pdfs():
    all_records = []

    for file in os.listdir(DATA_DIR):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(DATA_DIR, file)
            print(f"Extracting text data from {file} ...")

            # Extract year (any 4-digit sequence)
            year = next(
                (int(x) for x in re.findall(r"\d{4}", file)),
                None
            )

            raw_text = extract_text_from_pdf(pdf_path)
            cleaned_text = clean_text(raw_text)

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
