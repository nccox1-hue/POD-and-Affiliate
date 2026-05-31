"""
Generates printable wall art images via Pollinations.ai (free, no API key).
Resizes to standard print dimensions and saves as high-resolution PNGs.
"""
import asyncio
import logging
import os
import tempfile
from typing import List, Tuple
import httpx
from PIL import Image

logger = logging.getLogger(__name__)

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"

# Print sizes as (width_px, height_px) at 150dpi — good quality for digital downloads
# Using 150dpi keeps file sizes manageable while still printing well
PRINT_SIZES: List[Tuple[str, int, int]] = [
    ("A4",   1240, 1754),   # A4 portrait at 150dpi
    ("A3",   1754, 2480),   # A3 portrait at 150dpi
    ("8x10", 1200, 1500),   # 8x10 inches at 150dpi
    ("5x7",  750,  1050),   # 5x7 inches at 150dpi
]

# Prompt templates for wall art — produces clean, print-ready artwork
PROMPT_TEMPLATES = {
    "botanical":      "elegant botanical illustration, leaves and flowers, white background, fine art print style, high detail",
    "minimalist":     "minimalist abstract geometric design, clean lines, neutral palette, modern art print",
    "inspirational":  "typographic art print, inspirational quote layout, elegant serif font, clean white background",
    "motivational":   "bold motivational poster design, modern typography, clean minimal layout",
    "floral":         "delicate watercolour floral illustration, pastel colours, white background, art print",
    "nature":         "serene nature landscape illustration, minimalist style, soft colours, wall art",
    "abstract":       "modern abstract art print, bold shapes, contemporary colour palette, gallery wall art",
    "nursery":        "cute nursery wall art, soft pastel colours, friendly illustration, children's room",
    "geometric":      "geometric pattern art print, clean lines, modern colour palette, Scandinavian style",
    "vintage":        "vintage botanical illustration, antique style, aged paper effect, art print",
    "celestial":      "celestial moon and stars illustration, dark navy background, gold accents, art print",
    "watercolour":    "loose watercolour wash abstract art, soft blended colours, white background, art print",
}

DEFAULT_PROMPT = "elegant minimalist abstract art print, neutral palette, clean modern design, white background"


async def generate_artwork(theme: str, output_dir: str) -> List[str]:
    """
    Generate a wall art image for the given theme.
    Saves multiple print sizes as PNG files to output_dir.
    Returns list of saved file paths.
    """
    prompt_text = PROMPT_TEMPLATES.get(theme, DEFAULT_PROMPT)
    encoded = prompt_text.replace(" ", "%20").replace(",", "%2C")
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1240&height=1754&model=flux&nologo=true"

    logger.info("Generating artwork: theme='%s'", theme)

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(url)
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                break
            logger.warning("Pollinations attempt %d: status %s", attempt + 1, resp.status_code)
            await asyncio.sleep(3)
        except Exception as e:
            logger.warning("Pollinations attempt %d error: %s", attempt + 1, e)
            await asyncio.sleep(3)
    else:
        logger.error("Artwork generation failed after 3 attempts for theme '%s'", theme)
        return []

    # Save base image to temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(resp.content)
        base_path = tmp.name

    try:
        base_img = Image.open(base_path).convert("RGBA")
        saved_paths = []

        for size_name, width, height in PRINT_SIZES:
            # Resize maintaining aspect ratio with white letterboxing
            resized = _fit_image(base_img, width, height)
            out_path = os.path.join(output_dir, f"wall_art_{size_name}.png")
            resized.convert("RGB").save(out_path, "PNG", optimize=True)
            saved_paths.append(out_path)
            logger.debug("Saved %s: %s", size_name, out_path)

        logger.info("Artwork saved: %d sizes in %s", len(saved_paths), output_dir)
        return saved_paths

    except Exception as e:
        logger.error("Image processing error: %s", e)
        return []
    finally:
        os.unlink(base_path)


def _fit_image(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Fit image into target dimensions with white background letterboxing."""
    canvas = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 255))
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    offset_x = (target_w - img.width) // 2
    offset_y = (target_h - img.height) // 2
    canvas.paste(img, (offset_x, offset_y), img if img.mode == "RGBA" else None)
    return canvas
