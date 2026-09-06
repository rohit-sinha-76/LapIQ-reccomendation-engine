"""Script to fix GPU model, Cinebench R23, and 3DMark TimeSpy benchmarks for all Intel Core Ultra entries in knowledge_base.csv.

Ensures Core Ultra Series 1 & Series 2 (Lunar Lake / Meteor Lake) CPUs accurately map to Intel Arc Graphics 140V / 130V / Arc Graphics instead of legacy Iris Xe.
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


def fix_core_ultra_entries():
    if not CSV_PATH.exists():
        logger.error(f"CSV path not found at {CSV_PATH}")
        return

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    fixed_count = 0

    for r in rows:
        title = r["model_name"]
        cpu = r["cpu_model"]
        gpu = r["gpu_model"]

        # Detect Core Ultra processors in title or cpu_model
        is_ultra = "ultra" in title.lower() or "ultra" in cpu.lower()
        has_nvidia = "nvidia" in gpu.lower() or "rtx" in gpu.lower() or "gtx" in gpu.lower()

        if is_ultra:
            # Series 2 (Lunar Lake 258V, 256V, 226V)
            if "258v" in title.lower() or "258v" in cpu.lower() or "256v" in title.lower() or "256v" in cpu.lower():
                r["cpu_model"] = "Intel Core Ultra 7 258V"
                r["cinebench_r23_score"] = "14200"
                if not has_nvidia:
                    r["gpu_model"] = "Intel Arc Graphics 140V"
                    r["threedmark_score"] = "4200"
                    r["is_gpu_integrated"] = "True"
                fixed_count += 1
            elif "226v" in title.lower() or "226v" in cpu.lower():
                r["cpu_model"] = "Intel Core Ultra 5 226V"
                r["cinebench_r23_score"] = "12500"
                if not has_nvidia:
                    r["gpu_model"] = "Intel Arc Graphics 130V"
                    r["threedmark_score"] = "3600"
                    r["is_gpu_integrated"] = "True"
                fixed_count += 1
            # Series 1 (Meteor Lake 155H, 185H, 125H)
            elif "185h" in title.lower() or "185h" in cpu.lower() or "ultra 9" in title.lower():
                r["cpu_model"] = "Intel Core Ultra 9 185H"
                r["cinebench_r23_score"] = "18200"
                if not has_nvidia:
                    r["gpu_model"] = "Intel Arc Graphics"
                    r["threedmark_score"] = "4000"
                    r["is_gpu_integrated"] = "True"
                fixed_count += 1
            elif "155h" in title.lower() or "155h" in cpu.lower() or "ultra 7" in title.lower():
                r["cpu_model"] = "Intel Core Ultra 7 155H"
                r["cinebench_r23_score"] = "14800"
                if not has_nvidia:
                    r["gpu_model"] = "Intel Arc Graphics"
                    r["threedmark_score"] = "3800"
                    r["is_gpu_integrated"] = "True"
                fixed_count += 1
            elif "125h" in title.lower() or "125h" in cpu.lower() or "ultra 5" in title.lower():
                r["cpu_model"] = "Intel Core Ultra 5 125H"
                r["cinebench_r23_score"] = "12800"
                if not has_nvidia:
                    r["gpu_model"] = "Intel Arc Graphics"
                    r["threedmark_score"] = "3400"
                    r["is_gpu_integrated"] = "True"
                fixed_count += 1

    # Save updated CSV
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Save updated JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    logger.info(f"Fixed {fixed_count} Intel Core Ultra GPU and benchmark entries. Total dataset size: {len(rows)}")


if __name__ == "__main__":
    fix_core_ultra_entries()
