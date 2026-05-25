"""
Migration: adds product_id column to design_jobs, creates ebay_orders table.
Safe to run multiple times (checks before altering).
"""
import asyncio
import aiosqlite


async def main():
    async with aiosqlite.connect("data/pod_bot.db") as db:
        # Add product_id to design_jobs if not present
        async with db.execute("PRAGMA table_info(design_jobs)") as cur:
            cols = {row[1] async for row in cur}
        if "product_id" not in cols:
            await db.execute("ALTER TABLE design_jobs ADD COLUMN product_id INTEGER")
            print("Added product_id to design_jobs")
        else:
            print("product_id already exists — skipping")

        # Create ebay_orders table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ebay_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ebay_order_id VARCHAR(100) UNIQUE NOT NULL,
                ebay_item_id VARCHAR(100),
                size VARCHAR(20),
                quantity INTEGER DEFAULT 1,
                buyer_name VARCHAR(255),
                address1 VARCHAR(255),
                address2 VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(100),
                postcode VARCHAR(20),
                country_code VARCHAR(5),
                printful_order_id VARCHAR(100),
                status VARCHAR(50) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("ebay_orders table ready")
        await db.commit()

    print("Migration complete.")


asyncio.run(main())
