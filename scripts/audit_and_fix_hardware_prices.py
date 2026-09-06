"""Script to audit and fix hardware-vs-price sanity and CPU/title alignment across knowledge_base.csv.

Audits:
1. Model Title vs CPU Model alignment (e.g. Core Ultra 7 in title -> Core Ultra 7 in cpu_model).
2. CPU Tier vs Price Brackets (Core i3/Ryzen 3 clamped <= 45k; Core i5 <= 65k unless RTX gaming).
3. Standard RAM & Storage values.
4. Re-calculates 3-tier price points and discount percentages.
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


def audit_and_fix_hardware_prices():
    if not CSV_PATH.exists():
        logger.error(f"CSV path not found at {CSV_PATH}")
        return

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    corrections_count = 0

    for r in rows:
        title = r["model_name"]
        cpu = r["cpu_model"]
        gpu = r["gpu_model"]
        ram = int(r["ram_gb"])
        price = int(r["current_price_inr"])
        is_integrated = r["is_gpu_integrated"].lower() == "true"

        # 1. Align Title CPU vs cpu_model
        if "Core Ultra 7 258V" in title and "Ultra 7" not in cpu:
            r["cpu_model"] = "Intel Core Ultra 7 258V"
            r["cinebench_r23_score"] = "14200"
            corrections_count += 1
        elif "Core Ultra 5 125H" in title and "Ultra 5" not in cpu:
            r["cpu_model"] = "Intel Core Ultra 5 125H"
            r["cinebench_r23_score"] = "12800"
            corrections_count += 1

        # 2. ExpertBook P1 / P5 Price Sanity
        if "expertbook p1" in title.lower():
            if "i3" in cpu.lower() or "1315u" in cpu.lower():
                new_price = 38990
            elif "13420h" in cpu.lower() and ram <= 16:
                new_price = 48990
            elif "13420h" in cpu.lower() and ram == 32:
                new_price = 54990
            else:
                new_price = 58990

            if abs(price - new_price) > 5000:
                price = new_price
                r["current_price_inr"] = str(price)
                corrections_count += 1

        # 3. Core i3 / Ryzen 3 Price Clamp (Max 45,000 for budget integrated GPUs)
        elif ("i3" in cpu.lower() or "ryzen 3" in cpu.lower()) and is_integrated and price > 45000:
            price = 39990 if ram <= 8 else 44990
            r["current_price_inr"] = str(price)
            corrections_count += 1

        # 4. Core i5 / Ryzen 5 non-gaming integrated Price Clamp (Max 62,000)
        elif ("i5" in cpu.lower() or "ryzen 5" in cpu.lower()) and is_integrated and price > 65000 and "macbook" not in title.lower():
            price = 56990 if ram <= 16 else 62990
            r["current_price_inr"] = str(price)
            corrections_count += 1

        # 5. Non-standard RAM capacity normalization
        if ram not in {8, 12, 16, 24, 32, 36, 48, 64}:
            r["ram_gb"] = "16" if ram < 20 else "32"
            corrections_count += 1

        # Recalculate 3-tier price points
        min_disc = int(round(price * 0.88))
        max_mrp = int(round(price * 1.18))
        disc_pct = round(((max_mrp - min_disc) / max_mrp) * 100, 1)

        r["min_discount_price_inr"] = str(min_disc)
        r["avg_normal_price_inr"] = str(price)
        r["max_mrp_price_inr"] = str(max_mrp)
        r["max_discount_percentage"] = str(disc_pct)
        r["current_price_inr"] = str(price)

    # Save updated CSV
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Save updated JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    logger.info(f"Completed hardware-vs-price audit. Fixed {corrections_count} price and CPU anomalies. Dataset size: {len(rows)}")


if __name__ == "__main__":
    audit_and_fix_hardware_prices()
