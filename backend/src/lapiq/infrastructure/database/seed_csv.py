"""CSV Seeder script to parse laptop.csv and populate the PostgreSQL catalog."""

import csv
import re
import asyncio
from typing import Optional, Tuple
from sqlalchemy import select
from lapiq.infrastructure.database.models import CPU, GPU, Display, Laptop, Variant
from lapiq.infrastructure.database.session import async_session_factory


# Benchmark estimate helpers for CPUs and GPUs
def estimate_cpu_benchmark(cpu_model: str, core_count: int) -> int:
    model_upper = cpu_model.upper()
    if "I9" in model_upper or "RYZEN 9" in model_upper or "M3 MAX" in model_upper or "M3 PRO" in model_upper:
        return 28000
    if "I7" in model_upper or "RYZEN 7" in model_upper or "M2 PRO" in model_upper or "M3" in model_upper:
        return 22000
    if "I5" in model_upper or "RYZEN 5" in model_upper or "M1" in model_upper or "M2" in model_upper:
        return 16000
    if "I3" in model_upper or "RYZEN 3" in model_upper:
        return 10000
    return max(core_count * 1500, 6000)


def estimate_gpu_benchmark(gpu_model: str, is_integrated: bool) -> int:
    if is_integrated:
        return 4500
    model_upper = gpu_model.upper()
    if "4090" in model_upper or "4080" in model_upper:
        return 24000
    if "4070" in model_upper or "3080" in model_upper:
        return 20000
    if "4060" in model_upper or "3070" in model_upper:
        return 17000
    if "4050" in model_upper or "3050" in model_upper or "6500M" in model_upper:
        return 13000
    if "2050" in model_upper or "1650" in model_upper:
        return 9000
    return 7000


def parse_price(price_str: str) -> int:
    cleaned = re.sub(r"[^\d]", "", price_str)
    return int(cleaned) if cleaned else 50000


def parse_ram(ram_str: str) -> int:
    match = re.search(r"(\d+)\s*GB", ram_str, re.IGNORECASE)
    return int(match.group(1)) if match else 8


def parse_storage(storage_str: str) -> int:
    match_tb = re.search(r"(\d+)\s*TB", storage_str, re.IGNORECASE)
    if match_tb:
        return int(match_tb.group(1)) * 1024
    match_gb = re.search(r"(\d+)\s*GB", storage_str, re.IGNORECASE)
    return int(match_gb.group(1)) if match_gb else 512


def parse_display(display_str: str) -> Tuple[float, str, bool]:
    size = 15.6
    size_match = re.search(r"(\d+(?:\.\d+)?)\s*inch", display_str, re.IGNORECASE)
    if size_match:
        size = float(size_match.group(1))

    res = "1920x1080"
    res_match = re.search(r"(\d+)\s*x\s*(\d+)", display_str, re.IGNORECASE)
    if res_match:
        res = f"{res_match.group(1)}x{res_match.group(2)}"

    is_touch = "touch" in display_str.lower()
    return size, res, is_touch


def parse_core_threads(core_str: str) -> Tuple[int, int]:
    cores = 4
    threads = 8
    core_match = re.search(r"(\d+)\s*Core", core_str, re.IGNORECASE)
    if core_match:
        cores = int(core_match.group(1))

    word_map = {"OCTA": 8, "HEXA": 6, "QUAD": 4, "DUAL": 2}
    for word, num in word_map.items():
        if word in core_str.upper():
            cores = num

    thread_match = re.search(r"(\d+)\s*Thread", core_str, re.IGNORECASE)
    if thread_match:
        threads = int(thread_match.group(1))
    else:
        threads = cores * 2

    return cores, threads


def parse_brand_model(model_str: str) -> Tuple[str, str, str]:
    parts = model_str.split()
    brand = parts[0] if parts else "Laptop"
    model_name = " ".join(parts[1:5]) if len(parts) > 1 else model_str
    series = parts[1] if len(parts) > 2 else "Standard"
    return brand, model_name, series


def determine_segment(name: str, price: int, gpu_name: str) -> str:
    name_upper = name.upper()
    gpu_upper = gpu_name.upper()
    if "GAMING" in name_upper or "RTX" in gpu_upper or "RX" in gpu_upper or "TUF" in name_upper or "LOQ" in name_upper or "VICTUS" in name_upper:
        return "Gamers"
    if "CREATOR" in name_upper or "PRO" in name_upper or "STUDIO" in name_upper or "SLIM 7" in name_upper:
        return "Creators"
    if price < 50000:
        return "Students"
    return "Professionals"


async def seed_from_csv(csv_filepath: str) -> None:
    """Parse Indian laptops CSV and seed database."""
    async with async_session_factory() as session:
        count = 0
        with open(csv_filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                model_raw = row.get("Model", "")
                price_raw = row.get("Price", "")
                gen_raw = row.get("Generation", "")
                core_raw = row.get("Core", "")
                ram_raw = row.get("Ram", "")
                ssd_raw = row.get("SSD", "")
                disp_raw = row.get("Display", "")
                gfx_raw = row.get("Graphics", "")
                os_raw = row.get("OS", "Windows 11 OS")

                if not model_raw or not price_raw:
                    continue

                price = parse_price(price_raw)
                ram_gb = parse_ram(ram_raw)
                storage_gb = parse_storage(ssd_raw)
                disp_size, disp_res, is_touch = parse_display(disp_raw)
                core_count, thread_count = parse_core_threads(core_raw)
                brand, model_name, series = parse_brand_model(model_raw)
                segment = determine_segment(model_raw, price, gfx_raw)

                # 1. CPU
                cpu_brand = "AMD" if "AMD" in gen_raw or "Ryzen" in gen_raw else ("Apple" if "Apple" in gen_raw or "M1" in gen_raw or "M2" in gen_raw or "M3" in gen_raw else "Intel")
                cpu_model = gen_raw if gen_raw else "Core Processor"
                cpu_bench = estimate_cpu_benchmark(cpu_model, core_count)

                cpu = CPU(
                    brand=cpu_brand[:50],
                    model=cpu_model[:100],
                    core_count=core_count,
                    thread_count=thread_count,
                    base_clock_ghz=2.4,
                    boost_clock_ghz=4.5,
                    benchmark_score=cpu_bench,
                )
                session.add(cpu)
                await session.flush()

                # 2. GPU
                is_integrated = "INTEGRATED" in gfx_raw.upper() or "UHD" in gfx_raw.upper() or "IRIS" in gfx_raw.upper() or "RADEON GRAPHICS" in gfx_raw.upper() or "APPLE" in gfx_raw.upper()
                gpu_brand = "NVIDIA" if "NVIDIA" in gfx_raw.upper() or "GeForce" in gfx_raw.upper() else ("AMD" if "RADEON" in gfx_raw.upper() or "RX" in gfx_raw.upper() else ("Apple" if "APPLE" in gfx_raw.upper() else "Intel"))
                gpu_vram = 0
                vram_match = re.search(r"(\d+)\s*GB", gfx_raw, re.IGNORECASE)
                if vram_match and not is_integrated:
                    gpu_vram = int(vram_match.group(1))

                gpu_bench = estimate_gpu_benchmark(gfx_raw, is_integrated)

                gpu = GPU(
                    brand=gpu_brand[:50],
                    model=gfx_raw[:100] if gfx_raw else "Integrated Graphics",
                    vram_gb=gpu_vram,
                    is_integrated=is_integrated,
                    benchmark_score=gpu_bench,
                )
                session.add(gpu)
                await session.flush()

                # 3. Display
                disp = Display(
                    size_inches=disp_size,
                    resolution=disp_res[:50],
                    refresh_rate_hz=144 if "Gamers" in segment else 60,
                    panel_type="IPS",
                    is_touchscreen=is_touch,
                    brightness_nits=300,
                )
                session.add(disp)
                await session.flush()

                # 4. Laptop
                laptop = Laptop(
                    brand=brand[:100],
                    model_name=model_name[:200],
                    series=series[:100],
                    target_segment=segment,
                    is_available=True,
                )
                session.add(laptop)
                await session.flush()

                # 5. Variant SKU
                sku = f"SKU-{count+1:04d}-{brand[:3].upper()}-{ram_gb}GB"

                variant = Variant(
                    laptop_id=laptop.id,
                    sku=sku,
                    cpu_id=cpu.id,
                    gpu_id=gpu.id,
                    display_id=disp.id,
                    ram_gb=ram_gb,
                    storage_gb=storage_gb,
                    weight_kg=1.5 if "Air" in model_raw or "Slim" in model_raw else (2.3 if segment == "Gamers" else 1.8),
                    os_type="macOS" if "Mac" in model_raw or "Apple" in brand else "Windows 11",
                    current_price_inr=price,
                    is_in_stock=True,
                )
                session.add(variant)
                count += 1

                if count % 100 == 0:
                    await session.commit()
                    print(f"Seeded {count} laptops into database...")

        await session.commit()
        print(f"Successfully seeded full Indian laptop catalog! Total imported: {count} laptops.")


if __name__ == "__main__":
    from pathlib import Path
    data_in_container = Path("/app/data/knowledge_base.csv")
    data_local = Path(__file__).resolve().parents[4] / "data" / "knowledge_base.csv"
    root_laptop_csv = Path(__file__).resolve().parents[4] / "laptop.csv"

    if data_in_container.exists():
        default_path = data_in_container
    elif data_local.exists():
        default_path = data_local
    else:
        default_path = root_laptop_csv

    asyncio.run(seed_from_csv(str(default_path)))
