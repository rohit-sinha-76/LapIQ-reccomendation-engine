"""Background worker scheduler process."""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    """Worker entry point."""
    logger.info("LapIQ Background Worker started.")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Worker shutting down.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
