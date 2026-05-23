"""
Printful API v2 client.
Handles: creating products, uploading designs, generating mockups.
Docs: https://developers.printful.com/docs/
Free account at: https://www.printful.com
"""
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

PRINTFUL_API = "https://api.printful.com"

# Printful variant IDs for the most popular products
# T-shirt (Bella+Canvas 3001) size/colour variants — white, black, navy
PRODUCT_VARIANTS = {
    71: {  # Unisex Staple T-Shirt (Bella+Canvas 3001)
        "name": "Unisex T-Shirt",
        "variants": [4012, 4013, 4014, 4015, 4016, 4017],  # S-2XL in white
        "placement": "front",
        "print_area_width": 4500,
        "print_area_height": 5400,
    },
    19: {  # Mug 11oz
        "name": "Mug 11oz",
        "variants": [1320],
        "placement": "front",
        "print_area_width": 2400,
        "print_area_height": 1200,
    },
    358: {  # Canvas Tote Bag
        "name": "Canvas Tote Bag",
        "variants": [9964],
        "placement": "front",
        "print_area_width": 3000,
        "print_area_height": 3000,
    },
}


class PrintfulClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.printful_api_key}",
            "Content-Type": "application/json",
            "X-PF-Store-Id": settings.printful_store_id,
        }

    async def upload_design_file(self, image_path: str, filename: str, source_url: Optional[str] = None) -> Optional[str]:
        """Upload a design image to Printful file library. Returns file URL.
        Prefers source_url (direct URL) over base64 to avoid large payloads."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                if source_url:
                    payload = {"type": "default", "filename": filename, "url": source_url}
                else:
                    if not Path(image_path).exists():
                        logger.error("Design file not found: %s", image_path)
                        return None
                    import base64
                    with open(image_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode()
                    payload = {"type": "default", "filename": filename, "contents": image_data}

                async with session.post(f"{PRINTFUL_API}/files", json=payload) as resp:
                    data = await resp.json()
                    if data.get("code") == 200:
                        file_url = data["result"]["url"]
                        logger.info("Printful: file uploaded -> %s", file_url)
                        return file_url
                    logger.error("Printful file upload error: %s", data)
                    return None
        except Exception as e:
            logger.error("Printful upload error: %s", e)
            return None

    async def create_sync_product(
        self,
        name: str,
        description: str,
        design_url: str,
        product_id: int,
        retail_price: str,
        etsy_shop_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a Printful sync product and optionally connect to Etsy store."""
        product_config = PRODUCT_VARIANTS.get(product_id)
        if not product_config:
            logger.error("Unknown Printful product ID: %s", product_id)
            return None

        sync_variants = []
        for variant_id in product_config["variants"]:
            sync_variants.append({
                "variant_id": variant_id,
                "retail_price": retail_price,
                "files": [{
                    "type": product_config["placement"],
                    "url": design_url,
                }],
            })

        payload = {
            "sync_product": {
                "name": name,
                "description": description,
            },
            "sync_variants": sync_variants,
        }

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(f"{PRINTFUL_API}/store/products", json=payload) as resp:
                    data = await resp.json()
                    if data.get("code") == 200:
                        logger.info("Printful: product created -> id=%s", data["result"]["id"])
                        return data["result"]
                    logger.error("Printful product creation error: %s", data)
                    return None
        except Exception as e:
            logger.error("Printful create product error: %s", e)
            return None

    async def get_mockup_url(self, product_id: int, variant_ids: List[int], design_url: str) -> Optional[str]:
        """Generate a product mockup image URL."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                payload = {
                    "variant_ids": variant_ids[:1],
                    "files": [{"placement": "front", "image_url": design_url, "position": {"area_width": 1800, "area_height": 2100, "width": 1800, "height": 2100, "top": 0, "left": 0}}],
                }
                async with session.post(
                    f"{PRINTFUL_API}/mockup-generator/create-task/{product_id}",
                    json=payload,
                ) as resp:
                    data = await resp.json()
                    task_key = data.get("result", {}).get("task_key")
                    if not task_key:
                        return None

                # Poll for mockup result
                for _ in range(15):
                    await asyncio.sleep(4)
                    async with session.get(
                        f"{PRINTFUL_API}/mockup-generator/task?task_key={task_key}"
                    ) as resp:
                        result = await resp.json()
                        status = result.get("result", {}).get("status")
                        if status == "completed":
                            mockups = result["result"].get("mockups", [])
                            if mockups:
                                return mockups[0]["mockup_url"]
                        elif status == "failed":
                            return None

        except Exception as e:
            logger.error("Printful mockup error: %s", e)
        return None
