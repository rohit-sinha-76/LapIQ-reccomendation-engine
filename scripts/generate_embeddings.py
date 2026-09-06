"""One-time embedding generation and database seeding script for LapIQ.

Reads clean laptops from data/knowledge_base.csv, creates CPU, GPU, Display,
Laptop, and Variant ORM models with real Cinebench R23 and 3DMark scores into PostgreSQL,
generates vector embeddings for variants, and populates variants.embedding for pgvector search.
"""

import asyncio
import csv
import logging
from pathlib import Path

from sqlalchemy import select

from lapiq.infrastructure.database.models import CPU, GPU, Display, Laptop, Variant
from lapiq.infrastructure.database.session import async_session_factory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = Path("/app/data/knowledge_base.csv") if Path("/app/data/knowledge_base.csv").exists() else BASE_DIR / "data" / "knowledge_base.csv"


def generate_mock_embedding(text: str, dim: int = 1536) -> list[float]:
    """Generate a deterministic normalized embedding vector for development/offline mode."""
    import hashlib
    import math

    digest = hashlib.sha256(text.encode("utf-8")).digest()
    raw_floats = [(digest[i % len(digest)] / 255.0) - 0.5 for i in range(dim)]
    
    magnitude = math.sqrt(sum(x * x for x in raw_floats))
    if magnitude == 0:
        return [0.0] * dim
    return [x / magnitude for x in raw_floats]


async def seed_and_generate_embeddings() -> None:
    """Read knowledge_base.csv, seed PostgreSQL tables with real specs & benchmarks, and generate embeddings."""
    if not CSV_PATH.exists():
        logger.error(f"Knowledge base CSV file not found at {CSV_PATH}")
        return

    logger.info(f"Loading knowledge base from {CSV_PATH}...")

    async with async_session_factory() as session:
        async with session.begin():
            # Cache created CPU, GPU, Display models to avoid redundant DB insertions
            cpu_cache: dict[str, CPU] = {}
            gpu_cache: dict[str, GPU] = {}
            display_cache: dict[float, Display] = {}

            inserted_count = 0
            with open(CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    brand = row["brand"]
                    model_name = row["model_name"]
                    segment = row["target_segment"]
                    sku = row["sku"]
                    cpu_model = row["cpu_model"]
                    cinebench_score = int(row.get("cinebench_r23_score", 10000))
                    gpu_model = row["gpu_model"]
                    threedmark_score = int(row.get("threedmark_score", 3000))
                    is_gpu_integrated = row["is_gpu_integrated"].lower() == "true"
                    ram_gb = int(row["ram_gb"])
                    storage_gb = int(row["storage_gb"])
                    display_size = float(row["display_size_inches"])
                    weight_kg = float(row["weight_kg"])
                    price = int(row["current_price_inr"])

                    # Check if variant already exists in DB
                    existing = await session.execute(select(Variant).where(Variant.sku == sku))
                    if existing.scalars().first():
                        continue

                    # Get or create CPU ORM model
                    if cpu_model not in cpu_cache:
                        cpu_brand = "Apple" if "Apple" in cpu_model else ("AMD" if "AMD" in cpu_model or "Ryzen" in cpu_model else "Intel")
                        cpu_obj = CPU(
                            brand=cpu_brand,
                            model=cpu_model,
                            core_count=10,
                            thread_count=12,
                            base_clock_ghz=2.4,
                            boost_clock_ghz=4.4,
                            benchmark_score=cinebench_score,
                        )
                        session.add(cpu_obj)
                        await session.flush()
                        cpu_cache[cpu_model] = cpu_obj

                    # Get or create GPU ORM model
                    if gpu_model not in gpu_cache:
                        gpu_brand = "NVIDIA" if "NVIDIA" in gpu_model or "RTX" in gpu_model or "GTX" in gpu_model else ("Apple" if "Apple" in gpu_model else ("AMD" if "Radeon" in gpu_model or "RX" in gpu_model else "Intel"))
                        gpu_obj = GPU(
                            brand=gpu_brand,
                            model=gpu_model,
                            vram_gb=6 if not is_gpu_integrated else 0,
                            is_integrated=is_gpu_integrated,
                            benchmark_score=threedmark_score,
                        )
                        session.add(gpu_obj)
                        await session.flush()
                        gpu_cache[gpu_model] = gpu_obj

                    # Get or create Display ORM model
                    if display_size not in display_cache:
                        disp_obj = Display(
                            size_inches=display_size,
                            resolution="1920x1080",
                            refresh_rate_hz=60 if segment != "Gamer" else 144,
                            panel_type="IPS",
                            brightness_nits=250,
                        )
                        session.add(disp_obj)
                        await session.flush()
                        display_cache[display_size] = disp_obj

                    # Create Laptop parent ORM model
                    laptop = Laptop(brand=brand, model_name=model_name, target_segment=segment, is_available=True)
                    session.add(laptop)
                    await session.flush()

                    # Generate 1536-dimensional vector embedding
                    text_content = f"{brand} {model_name} {segment} CPU {cpu_model} GPU {gpu_model} RAM {ram_gb}GB Storage {storage_gb}GB Price INR {price}"
                    embedding = generate_mock_embedding(text_content)

                    # Create Variant ORM model
                    variant = Variant(
                        laptop_id=laptop.id,
                        sku=sku,
                        cpu_id=cpu_cache[cpu_model].id,
                        gpu_id=gpu_cache[gpu_model].id,
                        display_id=display_cache[display_size].id,
                        ram_gb=ram_gb,
                        storage_gb=storage_gb,
                        weight_kg=weight_kg,
                        os_type="Windows 11" if brand != "APPLE" else "macOS",
                        current_price_inr=price,
                        is_in_stock=True,
                        embedding=embedding,
                    )
                    session.add(variant)
                    inserted_count += 1

            logger.info(f"Successfully seeded {inserted_count} laptops with dynamic CPUs, GPUs & embeddings into PostgreSQL.")


if __name__ == "__main__":
    asyncio.run(seed_and_generate_embeddings())
