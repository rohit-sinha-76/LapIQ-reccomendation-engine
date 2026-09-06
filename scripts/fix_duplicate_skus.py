"""Script to fix duplicate SKUs in knowledge_base.csv and laptops_clean.json."""

import csv
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "knowledge_base.csv"
JSON_PATH = BASE_DIR / "data" / "laptops_clean.json"


def fix_duplicate_skus():
    if not CSV_PATH.exists():
        return

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    seen_skus = set()
    brand_counters = {}

    for row in rows:
        brand = row["brand"].upper().strip()
        sku = row["sku"]
        if sku in seen_skus:
            brand_counters[brand] = brand_counters.get(brand, 900) + 1
            new_sku = f"SKU-{brand}-{brand_counters[brand]:04d}"
            while new_sku in seen_skus:
                brand_counters[brand] += 1
                new_sku = f"SKU-{brand}-{brand_counters[brand]:04d}"
            row["sku"] = new_sku
            seen_skus.add(new_sku)
        else:
            seen_skus.add(sku)

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    logger.info(f"Fixed all duplicate SKUs. Total unique SKUs: {len(seen_skus)}")


if __name__ == "__main__":
    fix_duplicate_skus()
