"""Seed script to populate initial sample laptop catalog in PostgreSQL."""

import asyncio

from sqlalchemy import select

from lapiq.infrastructure.database.models import CPU, GPU, Display, Laptop, Variant
from lapiq.infrastructure.database.session import async_session_factory


async def seed_data() -> None:
    """Populate database with initial sample laptops for all 4 user segments."""
    async with async_session_factory() as session:
        existing = await session.execute(select(Laptop))
        if existing.scalars().first() is not None:
            print("Database already seeded.")
            return

        # 1. CPUs
        cpu_i5 = CPU(
            brand="Intel",
            model="Core i5-13420H",
            core_count=8,
            thread_count=12,
            base_clock_ghz=2.1,
            boost_clock_ghz=4.6,
            benchmark_score=18500,
        )
        cpu_ryzen7 = CPU(
            brand="AMD",
            model="Ryzen 7 7840HS",
            core_count=8,
            thread_count=16,
            base_clock_ghz=3.8,
            boost_clock_ghz=5.1,
            benchmark_score=26000,
        )
        cpu_m3 = CPU(
            brand="Apple",
            model="M3",
            core_count=8,
            thread_count=8,
            base_clock_ghz=3.0,
            boost_clock_ghz=4.0,
            benchmark_score=22000,
        )
        session.add_all([cpu_i5, cpu_ryzen7, cpu_m3])
        await session.flush()

        # 2. GPUs
        gpu_integ = GPU(
            brand="Intel",
            model="Iris Xe Graphics",
            vram_gb=0,
            is_integrated=True,
            benchmark_score=4500,
        )
        gpu_rtx4050 = GPU(
            brand="NVIDIA",
            model="GeForce RTX 4050",
            vram_gb=6,
            is_integrated=False,
            benchmark_score=16500,
        )
        gpu_m3_gpu = GPU(
            brand="Apple", model="10-core GPU", vram_gb=8, is_integrated=True, benchmark_score=14000
        )
        session.add_all([gpu_integ, gpu_rtx4050, gpu_m3_gpu])
        await session.flush()

        # 3. Displays
        disp_fhd = Display(
            size_inches=15.6,
            resolution="1920x1080",
            refresh_rate_hz=60,
            panel_type="IPS",
            is_touchscreen=False,
            brightness_nits=300,
        )
        disp_gaming = Display(
            size_inches=15.6,
            resolution="1920x1080",
            refresh_rate_hz=144,
            panel_type="IPS",
            is_touchscreen=False,
            brightness_nits=350,
        )
        disp_retina = Display(
            size_inches=14.2,
            resolution="3024x1964",
            refresh_rate_hz=120,
            panel_type="Liquid Retina XDR",
            is_touchscreen=False,
            brightness_nits=600,
        )
        session.add_all([disp_fhd, disp_gaming, disp_retina])
        await session.flush()

        # 4. Laptops & Variants
        laptop_vivobook = Laptop(
            brand="ASUS",
            model_name="VivoBook 15",
            series="Slim",
            target_segment="Students",
            is_available=True,
        )
        laptop_loq = Laptop(
            brand="Lenovo",
            model_name="LOQ 15",
            series="Gaming",
            target_segment="Gamers",
            is_available=True,
        )
        laptop_macbook = Laptop(
            brand="Apple",
            model_name="MacBook Air M3",
            series="Air",
            target_segment="Professionals",
            is_available=True,
        )

        session.add_all([laptop_vivobook, laptop_loq, laptop_macbook])
        await session.flush()

        variant_vivobook = Variant(
            laptop_id=laptop_vivobook.id,
            sku="ASUS-VB15-I5-16GB",
            cpu_id=cpu_i5.id,
            gpu_id=gpu_integ.id,
            display_id=disp_fhd.id,
            ram_gb=16,
            storage_gb=512,
            weight_kg=1.7,
            os_type="Windows 11 Home",
            current_price_inr=54990,
            is_in_stock=True,
        )

        variant_loq = Variant(
            laptop_id=laptop_loq.id,
            sku="LEN-LOQ15-R7-4050",
            cpu_id=cpu_ryzen7.id,
            gpu_id=gpu_rtx4050.id,
            display_id=disp_gaming.id,
            ram_gb=16,
            storage_gb=512,
            weight_kg=2.4,
            os_type="Windows 11 Home",
            current_price_inr=78990,
            is_in_stock=True,
        )

        variant_macbook = Variant(
            laptop_id=laptop_macbook.id,
            sku="APL-MBA-M3-16-512",
            cpu_id=cpu_m3.id,
            gpu_id=gpu_m3_gpu.id,
            display_id=disp_retina.id,
            ram_gb=16,
            storage_gb=512,
            weight_kg=1.24,
            os_type="macOS",
            current_price_inr=114900,
            is_in_stock=True,
        )

        session.add_all([variant_vivobook, variant_loq, variant_macbook])
        await session.commit()
        print("Successfully seeded catalog database with sample laptops!")


if __name__ == "__main__":
    asyncio.run(seed_data())
