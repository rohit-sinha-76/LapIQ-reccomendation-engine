"""Fix ExpertBook P1 synthetic RAM anomalies and align specs with real-world retail sheets in knowledge_base.csv.

Standardizes ASUS ExpertBook P1 configurations:
- Core i3 1315U: 8 GB RAM | 512 GB SSD @ ₹36,990
- Core i5 13420H: 16 GB RAM | 512 GB SSD @ ₹51,990
- Core i7 13620H: 16 GB RAM | 512 GB SSD @ ₹62,990
Removes fake 32GB RAM artifacts on budget sub-60k laptops.
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


def fix_expertbook_and_spec_realism():
    if not CSV_PATH.exists():
        logger.error(f"CSV path not found at {CSV_PATH}")
        return

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    fixed_count = 0
    clean_rows = []

    for r in rows:
        title = r["model_name"]
        cpu = r["cpu_model"]
        ram = int(r["ram_gb"])
        price = int(r["current_price_inr"])
        is_integrated = r["is_gpu_integrated"].lower() == "true"

        # 1. Standardize ExpertBook P1 models to authentic retail specs
        if "expertbook p1" in title.lower():
            if "1315u" in cpu.lower() or "i3" in title.lower():
                r["ram_gb"] = "8"
                r["current_price_inr"] = "36990"
            elif "13620h" in cpu.lower() or "i7" in title.lower():
                r["ram_gb"] = "16"
                r["current_price_inr"] = "62990"
            else:
                r["ram_gb"] = "16"
                r["current_price_inr"] = "51990"
            fixed_count += 1

        # 2. Fix synthetic 32GB RAM on non-gaming budget laptops under ₹70,000
        elif ram == 32 and price < 70000 and is_integrated and "macbook" not in title.lower():
            r["ram_gb"] = "16"
            fixed_count += 1

        # Recalculate 3-tier price points
        p = int(r["current_price_inr"])
        min_disc = int(round(p * 0.88))
        max_mrp = int(round(p * 1.18))
        disc_pct = round(((max_mrp - min_disc) / max_mrp) * 100, 1)

        r["min_discount_price_inr"] = str(min_disc)
        r["avg_normal_price_inr"] = str(p)
        r["max_mrp_price_inr"] = str(max_mrp)
        r["max_discount_percentage"] = str(disc_pct)

        clean_rows.append(r)

    # Save updated CSV
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)

    # Save updated JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_rows, f, indent=2, ensure_ascii=False)

    logger.info(f"Cleaned ExpertBook P1 and synthetic RAM anomalies. Fixed {fixed_count} entries. Total rows: {len(clean_rows)}")


if __name__ == "__main__":
    fix_expertbook_and_spec_realism()
