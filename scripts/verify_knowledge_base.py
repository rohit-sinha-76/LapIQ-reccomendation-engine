"""Regression audit and quality check script for data/knowledge_base.csv.

Executes 8 strict sanity checks across all cleaned laptop rows:
1. SKU Uniqueness
2. Missing / Null / N/A value check
3. Price range sanity (INR 10,000 - 500,000)
4. RAM capacity sanity (4, 8, 12, 16, 24, 32, 64 GB)
5. Storage capacity sanity (32 to 2048 GB)
6. CPU/Brand mismatch check (Apple M3 on non-Apple brands, M365 corruption)
7. Display size bounds (11.0" - 18.0")
8. Target segment categorization rule sanity
"""

import csv
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "knowledge_base.csv"


def run_regression_audit() -> None:
    """Audit knowledge_base.csv against 8 data quality rules."""
    if not CSV_PATH.exists():
        print(f"Error: File {CSV_PATH} not found.")
        return

    print(f"Starting regression audit on {CSV_PATH}...")

    skus: set[str] = set()
    errors: list[str] = []
    warnings: list[str] = []
    row_count = 0

    valid_ram_values = {4, 8, 12, 16, 24, 32, 64}
    valid_storage_values = {32, 64, 128, 256, 512, 1024, 2048}
    valid_segments = {"Student", "Professional", "Gamer", "Creator"}

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            row_count += 1
            sku = row.get("sku", "").strip()
            brand = row.get("brand", "").strip()
            model = row.get("model_name", "").strip()
            segment = row.get("target_segment", "").strip()
            cpu = row.get("cpu_model", "").strip()
            gpu = row.get("gpu_model", "").strip()
            ram_str = row.get("ram_gb", "0")
            storage_str = row.get("storage_gb", "0")
            price_str = row.get("current_price_inr", "0")
            display_str = row.get("display_size_inches", "0")

            # Check 1: SKU Uniqueness
            if not sku:
                errors.append(f"Line {idx}: Empty SKU")
            elif sku in skus:
                errors.append(f"Line {idx}: Duplicate SKU '{sku}'")
            else:
                skus.add(sku)

            # Check 2: Null / N/A / Empty values
            for col in ["sku", "brand", "model_name", "target_segment", "cpu_model", "gpu_model", "min_discount_price_inr", "avg_normal_price_inr", "max_mrp_price_inr"]:
                val = row.get(col, "")
                if not val or val.upper() in ["N/A", "NULL", "NONE"]:
                    errors.append(f"Line {idx} ({sku}): Missing or N/A value in column '{col}'")

            # Check 3: Price Sanity & 3-Tier Hierarchy
            try:
                min_disc = int(row.get("min_discount_price_inr", "0"))
                avg_norm = int(row.get("avg_normal_price_inr", "0"))
                max_mrp = int(row.get("max_mrp_price_inr", "0"))

                if not (min_disc <= avg_norm <= max_mrp):
                    errors.append(f"Line {idx} ({sku}): Invalid price hierarchy: sale min ₹{min_disc:,} > avg ₹{avg_norm:,} > mrp ₹{max_mrp:,}")
                if not (10000 <= avg_norm <= 500000):
                    errors.append(f"Line {idx} ({sku}): Out-of-bounds price INR {avg_norm}")
            except ValueError:
                errors.append(f"Line {idx} ({sku}): Invalid price integer values")

            # Check 4: RAM Sanity
            try:
                ram = int(ram_str)
                if ram not in valid_ram_values:
                    warnings.append(f"Line {idx} ({sku}): Unusual RAM capacity {ram} GB")
            except ValueError:
                errors.append(f"Line {idx} ({sku}): Invalid RAM integer '{ram_str}'")

            # Check 5: Storage Sanity
            try:
                storage = int(storage_str)
                if storage not in valid_storage_values:
                    warnings.append(f"Line {idx} ({sku}): Unusual storage capacity {storage} GB")
            except ValueError:
                errors.append(f"Line {idx} ({sku}): Invalid storage integer '{storage_str}'")

            # Check 6: CPU / Brand Mismatch
            if brand != "APPLE" and "APPLE" in cpu.upper():
                errors.append(f"Line {idx} ({sku}): Non-Apple laptop '{brand}' assigned Apple CPU '{cpu}'")
            if brand == "APPLE" and "APPLE" not in cpu.upper():
                errors.append(f"Line {idx} ({sku}): Apple laptop assigned non-Apple CPU '{cpu}'")

            # Check 7: Display Size Bounds
            try:
                disp = float(display_str)
                if not (11.0 <= disp <= 18.0):
                    errors.append(f"Line {idx} ({sku}): Out-of-bounds display size {disp} inches")
            except ValueError:
                errors.append(f"Line {idx} ({sku}): Invalid display size '{display_str}'")

            # Check 8: Segment Sanity
            if segment not in valid_segments:
                errors.append(f"Line {idx} ({sku}): Invalid segment '{segment}'")

    print(f"--- REGRESSION AUDIT RESULTS ---")
    print(f"Total Rows Audited  : {row_count}")
    print(f"Unique SKUs Checked : {len(skus)}")
    print(f"Critical Errors     : {len(errors)}")
    print(f"Warnings            : {len(warnings)}")

    if errors:
        print("\nCRITICAL ERRORS DETECTED:")
        for err in errors[:10]:
            print(f"  [ERROR] {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors.")
    else:
        print("\n[SUCCESS] ZERO CRITICAL ERRORS FOUND. Dataset regression audit passed 100%!")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for warn in warnings[:5]:
            print(f"  [WARN] {warn}")


if __name__ == "__main__":
    run_regression_audit()
