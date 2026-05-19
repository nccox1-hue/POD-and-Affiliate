"""
AI image design generator.

Default: Pollinations.ai — completely FREE, no API key, no signup.
Fallback: Stability AI — free credits on signup at platform.stability.ai

Pollinations generates clean, print-ready designs from text prompts.
"""
import asyncio
import logging
import httpx
import urllib.parse
from pathlib import Path
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/designs")
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"


async def generate_design(
    prompt: str,
    filename: str,
    width: int = 4500,
    height: int = 5400,
) -> Optional[str]:
    """
    Generate a design image from a text prompt.
    Returns local file path if successful, None otherwise.

    Print-ready dimensions for Printful T-shirt: 4500x5400px at 150dpi.
    We generate 1080x1080 and Printful upscales — good enough for a start.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = str(OUTPUT_DIR / f"{filename}.png")

    # Try Stability AI first if key is set (higher quality)
    if settings.stability_api_key:
        result = await _generate_stability(prompt, output_path)
        if result:
            return result

    # Default: Pollinations.ai (free, no key)
    return await _generate_pollinations(prompt, output_path)


async def _generate_pollinations(prompt: str, output_path: str) -> Optional[str]:
    """Pollinations.ai — free, no API key required."""
    try:
        # Enhance prompt for POD design quality
        enhanced = (
            f"{prompt}, t-shirt design, vector art style, clean white background, "
            "bold graphic, print ready, no text unless specified, high contrast"
        )
        encoded = urllib.parse.quote(enhanced)
        url = POLLINATIONS_URL.format(prompt=encoded)
        url += "?width=1080&height=1080&nologo=true&seed=42"

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(resp.content)

        logger.info("Design generated (Pollinations): %s", output_path)
        return output_path
    except Exception as e:
        logger.error("Pollinations generation failed: %s", e)
        return None


async def _generate_stability(prompt: str, output_path: str) -> Optional[str]:
    """Stability AI — higher quality, free credits available."""
    try:
        enhanced = (
            f"{prompt}, t-shirt graphic design, vector illustration, "
            "white background, bold clean lines, DTG print ready"
        )
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image",
                headers={
                    "Authorization": f"Bearer {settings.stability_api_key}",
                    "Accept": "application/json",
                },
                json={
                    "text_prompts": [{"text": enhanced, "weight": 1}],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1024,
                    "steps": 30,
                    "samples": 1,
                },
            )
            data = resp.json()
            import base64
            image_data = base64.b64decode(data["artifacts"][0]["base64"])
            with open(output_path, "wb") as f:
                f.write(image_data)

        logger.info("Design generated (Stability AI): %s", output_path)
        return output_path
    except Exception as e:
        logger.debug("Stability AI failed: %s", e)
        return None


async def build_design_prompt(keyword: str, theme: str) -> str:
    """Use Gemini Flash to write a strong image generation prompt for the keyword."""
    if not settings.gemini_api_key:
        return f"{keyword} graphic design illustration, minimalist style"

    from google import genai

    def _call():
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=(
                f"Write a concise image generation prompt (max 30 words) for a "
                f"print-on-demand t-shirt design. Theme: {theme}. Keyword: {keyword}. "
                f"Focus on visual style only (no text). Output the prompt only, no explanation."
            ),
        )
        return response.text.strip()

    try:
        return await asyncio.get_event_loop().run_in_executor(None, _call)
    except Exception:
        return f"{keyword} {theme} graphic illustration, bold design"
