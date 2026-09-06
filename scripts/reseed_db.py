"""Truncate old DB tables and seed authentic Indian laptops into PostgreSQL."""

import asyncio
import sys
from pathlib import Path

# Add project root and backend/src to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "src"))

from sqlalchemy import text
from lapiq.infrastructure.database.session import async_session_factory
from scripts.generate_embeddings import seed_and_generate_embeddings


async def main():
    print("Truncating old PostgreSQL tables...")
    async with async_session_factory() as session:
        async with session.begin():
            await session.execute(text("TRUNCATE TABLE variants, laptops, cpus, gpus, displays RESTART IDENTITY CASCADE;"))
    print("DB truncated. Seeding authentic Indian market laptops...")
    await seed_and_generate_embeddings()
    print("Re-seeding complete.")

if __name__ == "__main__":
    asyncio.run(main())
