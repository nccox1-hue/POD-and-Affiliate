"""
Creates and publishes Etsy digital download listings.
Uploads multiple PNG size variants as the downloadable files.
"""
import logging
import os
from typing import List, Optional, Dict
import aiohttp
import httpx
from dotenv import set_key
from config.settings import settings

logger = logging.getLogger(__name__)
ETSY_API = "https://openapi.etsy.com/v3"

# Etsy taxonomy ID for Art Prints (digital)
DIGITAL_ART_TAXONOMY_ID = 2078


# Cached token — refreshed on 401
_current_token: str = ""


def _get_token() -> str:
    global _current_token
    if not _current_token:
        _current_token = settings.etsy_access_token
    return _current_token


async def _refresh_token() -> bool:
    """Refresh the Etsy access token and update the in-memory cache."""
    global _current_token
    if not settings.etsy_refresh_token:
        logger.error("No ETSY_REFRESH_TOKEN — re-run setup_etsy_auth.py")
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
        _current_token = data["access_token"]
        set_key(".env", "ETSY_ACCESS_TOKEN", _current_token)
        if data.get("refresh_token"):
            set_key(".env", "ETSY_REFRESH_TOKEN", data["refresh_token"])
        logger.info("Etsy access token refreshed successfully")
        return True
    except Exception as e:
        logger.error("Etsy token refresh error: %s", e)
        return False


def _headers(content_type: bool = True) -> Dict:
    h = {
        "x-api-key": f"{settings.etsy_api_key}:{settings.etsy_api_secret}",
        "Authorization": f"Bearer {_get_token()}",
    }
    if content_type:
        h["Content-Type"] = "application/json"
    return h


async def create_digital_listing(
    title: str,
    description: str,
    tags: List[str],
    price_gbp: float = 2.99,
) -> Optional[int]:
    """Create a draft digital listing. Returns listing_id or None."""
    clean_tags = [t[:20] for t in tags[:13]]
    payload = {
        "quantity": 999,
        "title": title[:140],
        "description": description,
        "price": price_gbp,
        "who_made": "i_did",
        "when_made": "2020_2026",
        "taxonomy_id": DIGITAL_ART_TAXONOMY_ID,
        "type": "download",
        "tags": clean_tags,
        "state": "draft",
    }

    for attempt in range(2):
        try:
            async with aiohttp.ClientSession(headers=_headers()) as session:
                url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings"
                async with session.post(url, json=payload) as resp:
                    data = await resp.json()
                    if resp.status in (200, 201):
                        listing_id = data.get("listing_id")
                        logger.info("Digital listing created: id=%s title=%s", listing_id, title[:50])
                        return listing_id
                    if resp.status == 401 and attempt == 0:
                        logger.warning("Etsy 401 — refreshing token and retrying")
                        if await _refresh_token():
                            continue
                    logger.error("Create digital listing error %s: %s", resp.status, data)
                    return None
        except Exception as e:
            logger.error("Create digital listing exception: %s", e)
            return None
    return None


async def upload_digital_files(listing_id: int, file_paths: List[str]) -> int:
    """Upload PNG files as digital download files. Returns count of successful uploads."""
    uploaded = 0
    upload_headers = {
        "x-api-key": f"{settings.etsy_api_key}:{settings.etsy_api_secret}",
        "Authorization": f"Bearer {settings.etsy_access_token}",
    }

    for rank, path in enumerate(file_paths, 1):
        if not os.path.exists(path):
            continue
        try:
            filename = os.path.basename(path)
            with open(path, "rb") as f:
                file_data = f.read()

            form = aiohttp.FormData()
            form.add_field("file", file_data, filename=filename, content_type="image/png")
            form.add_field("name", filename)
            form.add_field("rank", str(rank))

            async with aiohttp.ClientSession(headers=upload_headers) as session:
                url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings/{listing_id}/files"
                async with session.post(url, data=form) as resp:
                    if resp.status in (200, 201):
                        logger.info("Uploaded file %s to listing %s", filename, listing_id)
                        uploaded += 1
                    else:
                        body = await resp.text()
                        logger.warning("File upload error %s: %s", resp.status, body[:200])
        except Exception as e:
            logger.error("File upload exception for %s: %s", path, e)

    return uploaded


async def upload_preview_image(listing_id: int, image_path: str) -> bool:
    """Upload a preview image (visible to buyers before purchase)."""
    upload_headers = {
        "x-api-key": f"{settings.etsy_api_key}:{settings.etsy_api_secret}",
        "Authorization": f"Bearer {settings.etsy_access_token}",
    }
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        form = aiohttp.FormData()
        form.add_field("image", data, filename="preview.png", content_type="image/png")
        form.add_field("rank", "1")

        async with aiohttp.ClientSession(headers=upload_headers) as session:
            url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings/{listing_id}/images"
            async with session.post(url, data=form) as resp:
                if resp.status in (200, 201):
                    logger.info("Preview image uploaded to listing %s", listing_id)
                    return True
                logger.warning("Preview upload error %s", resp.status)
                return False
    except Exception as e:
        logger.error("Preview upload exception: %s", e)
        return False


async def publish_listing(listing_id: int) -> bool:
    """Set listing state to active (published)."""
    try:
        async with aiohttp.ClientSession(headers=_headers()) as session:
            url = f"{ETSY_API}/application/shops/{settings.etsy_shop_id}/listings/{listing_id}"
            async with session.patch(url, json={"state": "active"}) as resp:
                if resp.status == 200:
                    logger.info("Digital listing %s published", listing_id)
                    return True
                logger.error("Publish error %s: %s", resp.status, await resp.text())
                return False
    except Exception as e:
        logger.error("Publish exception: %s", e)
        return False
