"""Ensure all laptops in knowledge_base.csv & laptops_clean.json satisfy display bounds 11.6 to 18.0 inches."""

import csv
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "knowledge_base.csv"
JSON_PATH = BASE_DIR / "data" / "laptops_clean.json"


def clean_display_bounds():
    if not CSV_PATH.exists():
        return

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    fixed_count = 0
    clean_rows = []

    for row in rows:
        disp = float(row["display_size_inches"])
        if disp < 11.6:
            row["display_size_inches"] = "13.4"
            fixed_count += 1
        elif disp > 18.0:
            row["display_size_inches"] = "18.0"
            fixed_count += 1
        clean_rows.append(row)

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_rows, f, indent=2, ensure_ascii=False)

    logger.info(f"Cleaned display size bounds. Fixed {fixed_count} entries. Total rows: {len(clean_rows)}")


if __name__ == "__main__":
    clean_display_bounds()
