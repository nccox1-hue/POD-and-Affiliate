"""
Minimal v0.1.0 test — verify Gemini + Pollinations work end-to-end.
No scraping, no Etsy, no Printful. Just content generation and image generation.

Usage:
  python test_v0_1_0.py
"""
import asyncio
import os
from config.settings import settings
from generator.listing_generator import generate_listing
from generator.design_generator import generate_design, build_design_prompt

os.makedirs("data/designs", exist_ok=True)


async def test_gemini_and_pollinations():
    """Test Gemini listing generation + Pollinations image generation."""
    test_keyword = "motivational fitness quote"
    theme = "motivational"
    filename = "test_v0_1_0_design"

    print(f"\n[TEST v0.1.0] Testing Gemini + Pollinations")
    print(f"Keyword: {test_keyword}")
    print(f"Theme: {theme}")

    # Step 1: Build design prompt via Gemini
    print("\n--- Step 1: Building design prompt (Gemini) ---")
    design_prompt = await build_design_prompt(test_keyword, theme)
    if design_prompt:
        print("OK Design prompt created:")
        print(f"  {design_prompt}")
    else:
        print("FAIL Design prompt generation failed")
        return False

    # Step 2: Generate design image via Pollinations
    print("\n--- Step 2: Generating design image (Pollinations) ---")
    image_path = await generate_design(design_prompt, filename)
    if image_path and os.path.exists(image_path):
        file_size = os.path.getsize(image_path)
        print("OK Design image generated:")
        print(f"  Path: {image_path}")
        print(f"  Size: {file_size} bytes")
    else:
        print(f"FAIL Design image generation failed (path={image_path})")
        return False

    # Step 3: Generate listing copy via Gemini
    print("\n--- Step 3: Generating Etsy listing (Gemini) ---")
    listing = await generate_listing(test_keyword, theme, "t-shirt")
    if listing:
        print("OK Gemini returned listing:")
        print(f"  Title: {listing.get('title', 'N/A')[:60]}...")
        print(f"  Tags: {listing.get('tags', [])[:3]}")
    else:
        print("FAIL Gemini listing generation failed")
        return False

    print("\n[SUCCESS] v0.1.0 milestone verified: Gemini + Pollinations working end-to-end")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_gemini_and_pollinations())
    exit(0 if success else 1)
