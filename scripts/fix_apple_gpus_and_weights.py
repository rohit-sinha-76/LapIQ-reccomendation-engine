"""Fix Apple GPU mislabeling and ROG Ally X weight in knowledge_base.csv & laptops_clean.json."""

import csv
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "knowledge_base.csv"
JSON_PATH = BASE_DIR / "data" / "laptops_clean.json"


def fix_apple_gpus_and_weights():
    if not CSV_PATH.exists():
        return

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    fixed_count = 0

    for r in rows:
        brand = r["brand"].upper().strip()
        cpu = r["cpu_model"]
        gpu = r["gpu_model"]
        weight = float(r["weight_kg"])

        # Fix Apple GPU mislabeling
        if brand == "APPLE" and "Intel" in gpu:
            if "M3" in cpu:
                r["gpu_model"] = "Apple M3 10-core GPU"
            elif "M2" in cpu:
                r["gpu_model"] = "Apple M2 8-core GPU"
            else:
                r["gpu_model"] = "Apple M1 7-core GPU"
            r["is_gpu_integrated"] = "True"
            fixed_count += 1

        # Fix ROG Ally X weight
        if weight < 0.8:
            r["weight_kg"] = "1.20"
            fixed_count += 1

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    logger.info(f"Fixed {fixed_count} Apple GPU and weight anomalies. Total dataset size: {len(rows)}")


if __name__ == "__main__":
    fix_apple_gpus_and_weights()
