"""
One-shot pipeline test — runs one listing end-to-end with a hardcoded keyword.
Usage: python test_pipeline.py
"""
import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

from publisher.publisher import Publisher


async def main():
    opportunity = {"keyword": "funny cat mum gift", "theme": "funny"}
    publisher = Publisher()
    success = await publisher.run(opportunity)
    if success:
        print("\nPipeline complete — check your Etsy drafts.")
    else:
        print("\nPipeline failed — check the log output above.")


if __name__ == "__main__":
    asyncio.run(main())
