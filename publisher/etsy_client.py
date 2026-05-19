"""
Etsy API v3 client.
Handles: creating listings, uploading images, managing inventory.
Docs: https://developers.etsy.com/documentation
Register at: https://www.etsy.com/developers/register

OAuth setup: run `python setup_etsy_auth.py` once to get your access token.
"""
import logging
import aiohttp
from typing import Dict, Any, Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

ETSY_API = "https://openapi.etsy.com/v3"


class EtsyClient:
    def __init__(self):
        self.headers = {
            "x-api-key": settings.etsy_api_key,
            "Authorization": f"Bearer {settings.etsy_access_token}",
            "Content-Type": "application/json",
        }

    async def create_draft_listing(
        self,
        title: str,
        description: str,
        price_gbp: float,
        tags: List[str],
        materials: List[str],
        quantity: int = 999,
    ) -> Optional[Dict[str, Any]]:
        """Create a draft listing on Etsy. Returns listing data including listing_id."""
        if not settings.etsy_access_token or not settings.etsy_shop_id:
            logger.warning("Etsy credentials not configured")
            return None

        # Etsy tag rules: max 13 tags, each max 20 chars
        clean_tags = [t[:20] for t in tags[:13]]

        payload = {
            "quantity": quantity,
            "title": title[:140],
            "description": description,
            "price": price_gbp,
            "who_made": "i_did",
            "when_made": "made_to_order",
            "taxonomy_id": 68887441,    # Clothing > Tops & Tees > T-Shirts
            "shipping_profile_id": int(settings.etsy_shipping_profile_id) if settings.etsy_shipping_profile_id else None,
            "tags": clean_tags,
            "materials": materials[:13],
            "is_digital": False,
            "state": "draft",           # Draft first — review before publishing
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings"
                async with session.post(url, json=payload) as resp:
                    data = await resp.json()
                    if resp.status in (200, 201):
                        listing_id = data.get("listing_id")
                        logger.info("Etsy: draft listing created -> id=%s", listing_id)
                        return data
                    logger.error("Etsy listing error %s: %s", resp.status, data)
                    return None
        except Exception as e:
            logger.error("Etsy create listing error: %s", e)
            return None

    async def upload_listing_image(
        self,
        listing_id: int,
        image_path: str,
        rank: int = 1,
    ) -> bool:
        """Upload a product image to an Etsy listing."""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            import aiohttp as ah
            form = ah.FormData()
            form.add_field(
                "image",
                image_data,
                filename="design.png",
                content_type="image/png",
            )
            form.add_field("rank", str(rank))

            upload_headers = {
                "x-api-key": settings.etsy_api_key,
                "Authorization": f"Bearer {settings.etsy_access_token}",
            }

            async with aiohttp.ClientSession(headers=upload_headers) as session:
                url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings/{listing_id}/images"
                async with session.post(url, data=form) as resp:
                    if resp.status in (200, 201):
                        logger.info("Etsy: image uploaded to listing %s", listing_id)
                        return True
                    logger.error("Etsy image upload error %s: %s", resp.status, await resp.text())
                    return False
        except Exception as e:
            logger.error("Etsy upload image error: %s", e)
            return False

    async def publish_listing(self, listing_id: int) -> bool:
        """Change a draft listing to active (published)."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings/{listing_id}"
                async with session.patch(url, json={"state": "active"}) as resp:
                    if resp.status == 200:
                        logger.info("Etsy: listing %s published", listing_id)
                        return True
                    logger.error("Etsy publish error: %s", await resp.text())
                    return False
        except Exception as e:
            logger.error("Etsy publish error: %s", e)
            return False

    async def get_listing_stats(self, listing_id: int) -> Dict[str, Any]:
        """Fetch view and sale data for a listing."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                url = f"{ETSY_API}/application/listings/{listing_id}"
                async with session.get(url, params={"includes": ["stats"]}) as resp:
                    data = await resp.json()
                    return {
                        "views": data.get("views", 0),
                        "num_favorers": data.get("num_favorers", 0),
                    }
        except Exception:
            return {"views": 0, "num_favorers": 0}
