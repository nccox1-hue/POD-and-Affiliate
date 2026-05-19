"""
Aggregates all trend sources and filters them against the user's chosen themes.
Returns a ranked list of design opportunities: keyword + theme + score.
"""
import asyncio
import logging
from typing import List, Dict, Any

from config.settings import settings
from config.themes import THEME_CATALOGUE
from scraper.etsy_scraper import get_etsy_trending_for_theme, scrape_etsy_bestsellers
from scraper.google_trends import get_google_trends_for_keywords
from scraper.pinterest_trends import get_pinterest_trends

logger = logging.getLogger(__name__)


class TrendAggregator:
    async def scan(self) -> List[Dict[str, Any]]:
        """Run all scrapers and return a deduplicated, scored opportunity list."""
        active_themes = {
            name: data
            for name, data in THEME_CATALOGUE.items()
            if name in settings.theme_list
        }

        if not active_themes:
            logger.warning("No matching themes found in catalogue — using all themes")
            active_themes = THEME_CATALOGUE

        # Collect all seed keywords from active themes
        all_seeds = []
        for theme_name, theme_data in active_themes.items():
            all_seeds.extend(theme_data["seed_keywords"])

        # Run all scrapers concurrently
        pinterest, google, etsy_best = await asyncio.gather(
            get_pinterest_trends("GB"),
            get_google_trends_for_keywords(all_seeds[:5]),
            scrape_etsy_bestsellers("t-shirts"),
            return_exceptions=True,
        )

        etsy_theme_results = await asyncio.gather(
            *[
                get_etsy_trending_for_theme(theme_data["seed_keywords"])
                for theme_data in active_themes.values()
            ],
            return_exceptions=True,
        )

        # Merge everything
        all_results: List[Dict[str, Any]] = []
        for r in [pinterest, google, etsy_best]:
            if isinstance(r, list):
                all_results.extend(r)

        for r in etsy_theme_results:
            if isinstance(r, list):
                all_results.extend(r)

        # Tag each result with its best matching theme
        tagged = []
        for item in all_results:
            kw = item["keyword"].lower()
            best_theme = self._match_theme(kw, active_themes)
            item["theme"] = best_theme
            tagged.append(item)

        # Deduplicate and boost cross-source keywords
        merged = self._deduplicate(tagged)
        merged.sort(key=lambda x: x["score"], reverse=True)

        logger.info("TrendAggregator: %d unique design opportunities", len(merged))
        return merged[:settings.listings_per_cycle * 4]

    def _match_theme(self, keyword: str, themes: Dict[str, Any]) -> str:
        for theme_name, theme_data in themes.items():
            for seed in theme_data["seed_keywords"]:
                if any(word in keyword for word in seed.lower().split()):
                    return theme_name
        # Fallback: check theme name itself
        for theme_name in themes:
            if theme_name.replace("_", " ") in keyword:
                return theme_name
        return list(themes.keys())[0]

    def _deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen: Dict[str, Dict[str, Any]] = {}
        for item in items:
            key = item["keyword"].lower().strip()[:60]
            if key in seen:
                seen[key]["score"] = min(100.0, seen[key]["score"] + 10)
            else:
                seen[key] = item
        return list(seen.values())
