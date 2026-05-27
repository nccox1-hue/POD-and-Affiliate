"""
Etsy API v3 client.
Handles: creating listings, uploading images, managing inventory.
Docs: https://developers.etsy.com/documentation
Register at: https://www.etsy.com/developers/register

OAuth setup: run `python setup_etsy_auth.py` once to get your access token.
"""
import logging
import aiohttp
import httpx
from dotenv import set_key
from typing import Dict, Any, Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

ETSY_API = "https://openapi.etsy.com/v3"


class EtsyClient:
    def __init__(self):
        self._access_token = settings.etsy_access_token
        self.headers = {
            "x-api-key": f"{settings.etsy_api_key}:{settings.etsy_api_secret}",
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }
        self._return_policy_id: Optional[int] = None

    async def _ensure_return_policy(self) -> Optional[int]:
        """Fetch the shop return policy ID. Cached after first call.
        Falls back to ETSY_RETURN_POLICY_ID in .env if API fetch fails."""
        if self._return_policy_id:
            return self._return_policy_id

        # Use .env value if configured
        if settings.etsy_return_policy_id:
            self._return_policy_id = int(settings.etsy_return_policy_id)
            return self._return_policy_id

        # Try to fetch from API (requires listings_r scope)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/policies/return"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results") or [data]
                    if results:
                        policy_id = results[0].get("return_policy_id")
                        if policy_id:
                            self._return_policy_id = int(policy_id)
                            logger.info("Etsy: return policy fetched -> id=%s", policy_id)
                            return self._return_policy_id
                else:
                    logger.warning(
                        "Etsy: cannot fetch return policy (%s) — "
                        "set ETSY_RETURN_POLICY_ID in .env (find it via Etsy dashboard > Policies)",
                        resp.status,
                    )

        return None

    async def _refresh_token(self) -> bool:
        """Refresh the Etsy access token using the refresh token. Updates .env and headers."""
        if not settings.etsy_refresh_token:
            logger.error("No ETSY_REFRESH_TOKEN in .env — re-run setup_etsy_auth.py")
            return False
        try:
            resp = httpx.post(
                "https://api.etsy.com/v3/public/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.etsy_api_key,
                    "refresh_token": settings.etsy_refresh_token,
                },
            )
            data = resp.json()
            if "access_token" not in data:
                logger.error("Etsy token refresh failed: %s", data)
                return False
            self._access_token = data["access_token"]
            self.headers["Authorization"] = f"Bearer {self._access_token}"
            set_key(".env", "ETSY_ACCESS_TOKEN", data["access_token"])
            if data.get("refresh_token"):
                set_key(".env", "ETSY_REFRESH_TOKEN", data["refresh_token"])
            logger.info("Etsy access token refreshed successfully")
            return True
        except Exception as e:
            logger.error("Etsy token refresh error: %s", e)
            return False

    async def create_draft_listing(
        self,
        title: str,
        description: str,
        price_gbp: float,
        tags: List[str],
        materials: List[str],
        quantity: int = 999,
        taxonomy_id: int = 559,
    ) -> Optional[Dict[str, Any]]:
        """Create a draft listing on Etsy. Returns listing data including listing_id."""
        if not settings.etsy_access_token or not settings.etsy_shop_id:
            logger.warning("Etsy credentials not configured")
            return None

        return_policy_id = await self._ensure_return_policy()

        import re as _re
        # Etsy tag rules: max 13 tags, each max 20 chars
        clean_tags = [t[:20] for t in tags[:13]]
        # Etsy material rules: letters, numbers, spaces, hyphens, apostrophes, ampersands; max 45 chars
        clean_materials = [
            _re.sub(r"[^a-zA-Z0-9 \-&']", "", m).strip()[:45]
            for m in materials[:13]
        ]
        clean_materials = [m for m in clean_materials if m]

        payload = {
            "quantity": quantity,
            "title": title[:140],
            "description": description,
            "price": price_gbp,
            "who_made": "i_did",
            "when_made": "made_to_order",
            "taxonomy_id": taxonomy_id,
            "shipping_profile_id": int(settings.etsy_shipping_profile_id) if settings.etsy_shipping_profile_id else None,
            "tags": clean_tags,
            "materials": clean_materials or ["Cotton"],
            "is_digital": False,
            "state": "draft",
            "readiness_state_id": 1488409015052,
            "return_policy_id": return_policy_id,
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        for attempt in range(2):
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings"
                    async with session.post(url, json=payload) as resp:
                        data = await resp.json()
                        if resp.status in (200, 201):
                            listing_id = data.get("listing_id")
                            logger.info("Etsy: draft listing created -> id=%s", listing_id)
                            return data
                        if resp.status == 401 and attempt == 0:
                            logger.warning("Etsy 401 — attempting token refresh")
                            if await self._refresh_token():
                                continue
                        logger.error("Etsy listing error %s: %s", resp.status, data)
                        return None
            except Exception as e:
                logger.error("Etsy create listing error: %s", e)
                return None
        return None

    async def upload_listing_image(
        self,
        listing_id: int,
        image_path: str,
        rank: int = 1,
    ) -> Optional[str]:
        """Upload a product image to an Etsy listing. Returns the full-size CDN URL on success."""
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
                "x-api-key": f"{settings.etsy_api_key}:{settings.etsy_api_secret}",
                "Authorization": f"Bearer {self._access_token}",
            }

            async with aiohttp.ClientSession(headers=upload_headers) as session:
                url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings/{listing_id}/images"
                async with session.post(url, data=form) as resp:
                    data = await resp.json()
                    if resp.status in (200, 201):
                        cdn_url = data.get("url_fullxfull") or data.get("url_570xN") or ""
                        logger.info("Etsy: image uploaded to listing %s -> %s", listing_id, cdn_url[:60])
                        return cdn_url
                    logger.error("Etsy image upload error %s: %s", resp.status, data)
                    return None
        except Exception as e:
            logger.error("Etsy upload image error: %s", e)
            return None

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
