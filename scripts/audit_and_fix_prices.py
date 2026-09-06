"""Price Inaccuracy Audit & Realistic Market Alignment Script for LapIQ.

Audits all 479 laptops in data/knowledge_base.csv for price inaccuracies:
1. Checks price vs hardware spec sanity (Celeron/Chromebook vs i7/RTX/Apple M3)
2. Corrects any seller listing typos or misaligned price rows
3. Ensures realistic Indian market retail prices across all 4 segments.
"""

import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "knowledge_base.csv"
JSON_PATH = BASE_DIR / "data" / "laptops_clean.json"


def get_expected_price_range(cpu: str, gpu: str, ram_gb: int, brand: str) -> tuple[int, int]:
    """Calculate realistic Indian market price range for given hardware specs."""
    cpu_u = cpu.upper()
    gpu_u = gpu.upper()
    brand_u = brand.upper()

    # Apple M3 / M2
    if brand_u == "APPLE":
        if "M3" in cpu_u:
            return (110000, 220000)
        if "M2" in cpu_u:
            return (85000, 160000)
        return (70000, 130000)

    # Gaming laptops with dedicated GPUs
    if "RTX 4070" in gpu_u or "RTX 4080" in gpu_u or "RTX 4090" in gpu_u:
        return (130000, 350000)
    if "RTX 4060" in gpu_u or "14700HX" in cpu_u:
        return (95000, 180000)
    if "RTX 4050" in gpu_u or "RTX 3060" in gpu_u:
        return (70000, 115000)
    if "RTX 3050" in gpu_u or "RTX 2050" in gpu_u:
        return (52000, 85000)

    # High-end CPUs (i7 / Ryzen 7)
    if "I7" in cpu_u or "13620H" in cpu_u or "13500H" in cpu_u or "RYZEN 7" in cpu_u or "8645HS" in cpu_u:
        return (52000, 105000)

    # Mid-range CPUs (i5 / Ryzen 5)
    if "I5" in cpu_u or "RYZEN 5" in cpu_u or "12450H" in cpu_u or "120U" in cpu_u or "210H" in cpu_u:
        return (38000, 72000)

    # Entry-level CPUs (i3 / Ryzen 3)
    if "I3" in cpu_u or "RYZEN 3" in cpu_u or "100U" in cpu_u or "1315U" in cpu_u or "1215U" in cpu_u:
        return (25000, 46000)

    # Budget Chromebooks & Celeron
    if "CELERON" in cpu_u or "MEDIATEK" in cpu_u or "HELIO" in cpu_u:
        return (11000, 26000)

    return (20000, 90000)


def audit_and_fix_prices() -> None:
    """Audit prices in knowledge_base.csv and correct hardware/price discrepancies."""
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return

    rows: list[dict[str, str]] = []
    corrections_count = 0

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku = row["sku"]
            brand = row["brand"]
            cpu = row["cpu_model"]
            gpu = row["gpu_model"]
            ram_gb = int(row["ram_gb"])
            current_price = int(row["current_price_inr"])

            min_expected, max_expected = get_expected_price_range(cpu, gpu, ram_gb, brand)

            # Detect price anomaly and clamp
            if current_price < min_expected or current_price > max_expected:
                current_price = min_expected if current_price < min_expected else max_expected
                print(f"[PRICE CORRECTION] {sku} ({brand} {row['model_name'][:30]}): Clamped to INR {current_price:,}")
                corrections_count += 1

            # Recalculate 3 explicit price points (Minimum Discount, Average Normal, Maximum MRP)
            avg_normal_price = current_price
            max_mrp_price = int(round(current_price * 1.18))
            min_discount_price = int(round(current_price * 0.88))
            discount_pct = round(((max_mrp_price - min_discount_price) / max_mrp_price) * 100, 1)

            row["current_price_inr"] = str(current_price)
            row["min_discount_price_inr"] = str(min_discount_price)
            row["avg_normal_price_inr"] = str(avg_normal_price)
            row["max_mrp_price_inr"] = str(max_mrp_price)
            row["max_discount_percentage"] = str(discount_pct)

            rows.append(row)

    print(f"\nCompleted 3-tier price audit across {len(rows)} laptops. Total price corrections: {corrections_count}")

    # Write updated clean CSV
    fieldnames = list(rows[0].keys())
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write updated clean JSON
    json_data = []
    for r in rows:
        j_row = dict(r)
        j_row["cinebench_r23_score"] = int(r["cinebench_r23_score"])
        j_row["threedmark_score"] = int(r["threedmark_score"])
        j_row["is_gpu_integrated"] = r["is_gpu_integrated"].lower() == "true"
        j_row["ram_gb"] = int(r["ram_gb"])
        j_row["storage_gb"] = int(r["storage_gb"])
        j_row["display_size_inches"] = float(r["display_size_inches"])
        j_row["weight_kg"] = float(r["weight_kg"])
        j_row["min_discount_price_inr"] = int(r["min_discount_price_inr"])
        j_row["avg_normal_price_inr"] = int(r["avg_normal_price_inr"])
        j_row["max_mrp_price_inr"] = int(r["max_mrp_price_inr"])
        j_row["max_discount_percentage"] = float(r["max_discount_percentage"])
        j_row["current_price_inr"] = int(r["current_price_inr"])
        j_row["rating"] = float(r["rating"])
        json_data.append(j_row)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Updated dataset saved to {CSV_PATH} and {JSON_PATH}")


if __name__ == "__main__":
    audit_and_fix_prices()
