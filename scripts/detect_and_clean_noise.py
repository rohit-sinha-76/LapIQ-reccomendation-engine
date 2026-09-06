"""Noise Detection & Advanced Cleaning Script for LapIQ Knowledge Base.

Scans all 479 laptop rows in data/knowledge_base.csv for:
1. CPU brand mislabeling (e.g. AMD CPUs assigned 'Intel' prefix like Intel 7320U / Intel 8645HS)
2. Marketing fluff & noise in model_name (strip 'with Office 2024', 'Backlit Keyboard', 'Thin and Light', 'MSO24')
3. Redundant brand prefix duplication (e.g. brand='ASUS', model_name='ASUS Vivobook 15' -> 'Vivobook 15')
4. Model name truncation and artifact trailing characters ('...', '|', ',')
"""

import csv
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "knowledge_base.csv"
JSON_PATH = BASE_DIR / "data" / "laptops_clean.json"


def clean_model_name(raw_name: str, brand: str) -> str:
    """Clean model name by stripping marketing noise, software bloat, and brand redundancy."""
    text = raw_name.strip()

    # Strip trailing ellipsis and pipe artifacts
    text = re.sub(r"\.+$", "", text).strip()
    text = re.sub(r"\s*\|\s*.*$", "", text).strip()

    # Strip marketing software & promo fluff phrases
    fluff_patterns = [
        r"with\s+Office\s+\d{4}.*$",
        r"with\s+MSO.*$",
        r"MSO'24.*$",
        r"with\s+Backlit\s+KB.*$",
        r"with\s+Backlit\s+Keyboard.*$",
        r"Thin\s+and\s+Light.*$",
        r"Full\s+Metal\s+OLED.*$",
        r"with\s+M365.*$",
        r"High-performance\s+processor.*$",
        r"3\s+Years\s+Warranty.*$",
    ]
    for pat in fluff_patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE).strip()

    # Strip trailing commas or hyphens left over after fluff removal
    text = re.sub(r"[,–\-\s]+$", "", text).strip()

    # Remove leading duplicate brand name if present
    if text.upper().startswith(brand.upper()):
        text = text[len(brand):].strip()
        text = re.sub(r"^[,\–\-\s]+", "", text).strip()

    return text if text else raw_name


def clean_cpu_model(cpu_str: str, raw_name: str) -> str:
    """Fix CPU mislabeling (e.g. AMD Ryzen models assigned 'Intel' prefix)."""
    text = f"{cpu_str} {raw_name}".upper()

    # Detect AMD Ryzen CPUs mistakenly prefixed with Intel
    amd_ryzen_models = ["7320U", "7330U", "5300U", "5500U", "5625U", "7430U", "7530U", "7730U", "8645HS", "6600H"]
    for model in amd_ryzen_models:
        if model in text:
            if "7730U" in model or "7" in model:
                return f"AMD Ryzen 7 {model}"
            if "7320U" in model or "5300U" in model or "3" in model:
                return f"AMD Ryzen 3 {model}"
            return f"AMD Ryzen 5 {model}"

    # Clean Intel formatting
    if cpu_str.startswith("Intel Intel"):
        return cpu_str.replace("Intel Intel", "Intel").strip()
    if cpu_str.startswith("Intel CORE"):
        return cpu_str.replace("Intel CORE", "Intel Core").strip()

    return cpu_str


def run_noise_cleaning() -> None:
    """Execute noise detection and clean knowledge_base.csv."""
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return

    print(f"Scanning {CSV_PATH} for data noise...")

    rows: list[dict[str, str]] = []
    noise_count = 0

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            brand = row["brand"]
            old_model = row["model_name"]
            old_cpu = row["cpu_model"]

            new_model = clean_model_name(old_model, brand)
            new_cpu = clean_cpu_model(old_cpu, old_model)

            if new_model != old_model:
                clean_old = old_model[:35].encode('ascii', 'ignore').decode('ascii')
                clean_new = new_model[:35].encode('ascii', 'ignore').decode('ascii')
                print(f"[MODEL NOISE CLEANED] '{clean_old}' -> '{clean_new}'")
                row["model_name"] = new_model
                noise_count += 1

            if new_cpu != old_cpu:
                clean_old_cpu = old_cpu.encode('ascii', 'ignore').decode('ascii')
                clean_new_cpu = new_cpu.encode('ascii', 'ignore').decode('ascii')
                print(f"[CPU MISMATCH CLEANED] '{clean_old_cpu}' -> '{clean_new_cpu}'")
                row["cpu_model"] = new_cpu
                noise_count += 1

            rows.append(row)

    print(f"\nCompleted noise scan across {len(rows)} rows. Total noise items cleaned: {noise_count}")

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

    print(f"Noise-cleaned dataset saved to {CSV_PATH} and {JSON_PATH}")


if __name__ == "__main__":
    run_noise_cleaning()
