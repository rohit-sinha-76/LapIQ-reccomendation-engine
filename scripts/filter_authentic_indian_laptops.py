"""Script to filter out obscure, non-standard, or unvalidated brands from knowledge_base.csv.

Keeps 100% authentic, mainstream Indian retail market brands:
HP, LENOVO, ASUS, ACER, DELL, MSI, SAMSUNG, APPLE, MICROSOFT, INFINIX, ZEBRONICS.
"""

import csv
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "knowledge_base.csv"
JSON_PATH = BASE_DIR / "data" / "laptops_clean.json"

AUTHENTIC_BRANDS = {
    "HP",
    "LENOVO",
    "ASUS",
    "ACER",
    "DELL",
    "MSI",
    "SAMSUNG",
    "APPLE",
    "MICROSOFT",
    "INFINIX",
    "ZEBRONICS",
}


def filter_authentic_laptops() -> None:
    if not CSV_PATH.exists():
        logger.error(f"CSV file not found at {CSV_PATH}")
        return

    logger.info(f"Filtering knowledge base dataset at {CSV_PATH}...")

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    initial_count = len(rows)
    clean_rows = []
    removed_brands = set()

    for row in rows:
        brand = row["brand"].upper().strip()
        if brand in AUTHENTIC_BRANDS:
            clean_rows.append(row)
        else:
            removed_brands.add(brand)

    # Save clean CSV
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)

    # Save clean JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_rows, f, indent=2, ensure_ascii=False)

    logger.info(f"Initial count: {initial_count}")
    logger.info(f"Authentic Indian market laptop count: {len(clean_rows)}")
    logger.info(f"Removed {initial_count - len(clean_rows)} entries from obscure/non-standard brands: {sorted(removed_brands)}")


if __name__ == "__main__":
    filter_authentic_laptops()
