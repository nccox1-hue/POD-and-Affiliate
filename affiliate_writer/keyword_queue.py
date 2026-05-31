"""
Manages the keyword queue for the affiliate article pipeline.
Queue is persisted as data/affiliate_keywords.json.
"""
import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

QUEUE_PATH = os.path.join("data", "affiliate_keywords.json")

# Seed keywords — specific, low-competition, Excel/Power Automate niche
SEED_KEYWORDS = [
    "how to merge tables in excel without vlookup using power query",
    "power automate approval workflow step by step",
    "excel power query combine multiple files from folder",
    "how to remove duplicates in excel power query",
    "power bi desktop tutorial for beginners excel users",
    "power automate vs zapier which is better for small business",
    "excel dynamic arrays spill formulas complete guide",
    "how to automate weekly reports in excel",
    "power automate send email when sharepoint list updated",
    "make com vs zapier comparison 2026",
    "excel power query unpivot columns tutorial",
    "how to connect power bi to excel file automatically",
    "power automate approval with teams notification",
    "excel index match vs xlookup guide",
    "how to build a kpi dashboard in excel",
    "power automate scheduled flows run daily",
    "excel power query group by and aggregate",
    "monday com vs excel for project management",
    "how to automate email reports from excel data",
    "power automate conditions and expressions tutorial",
    "excel advanced filter extract to another sheet",
    "notion vs excel for personal productivity",
    "power query m language basics tutorial",
    "excel pivot table calculated fields guide",
    "how to use microsoft forms with power automate",
    "power bi dax formulas for beginners",
    "excel get and transform data power query tutorial",
    "automate invoice processing with power automate",
    "excel vba vs power automate which should i learn",
    "best excel courses udemy 2026 review",
]


def _load() -> dict:
    if not os.path.exists(QUEUE_PATH):
        return {"pending": list(SEED_KEYWORDS), "published": []}
    with open(QUEUE_PATH) as f:
        data = json.load(f)
    # Add any new seed keywords not already in the queue
    existing = set(data.get("pending", [])) | set(data.get("published", []))
    new = [k for k in SEED_KEYWORDS if k not in existing]
    data["pending"] = data.get("pending", []) + new
    return data


def _save(data: dict) -> None:
    os.makedirs("data", exist_ok=True)
    with open(QUEUE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def next_keyword() -> Optional[str]:
    """Pop the next pending keyword. Returns None if queue is empty."""
    data = _load()
    if not data["pending"]:
        logger.info("Keyword queue: empty — all keywords published")
        return None
    keyword = data["pending"].pop(0)
    _save(data)
    return keyword


def mark_published(keyword: str) -> None:
    """Move a keyword from pending to published."""
    data = _load()
    if keyword in data.get("pending", []):
        data["pending"].remove(keyword)
    if keyword not in data.get("published", []):
        data["published"].append(keyword)
    _save(data)
    logger.debug("Keyword marked published: '%s'", keyword)


def add_keywords(keywords: list) -> None:
    """Add new keywords to the pending queue."""
    data = _load()
    existing = set(data.get("pending", [])) | set(data.get("published", []))
    new = [k for k in keywords if k not in existing]
    data["pending"].extend(new)
    _save(data)
    logger.info("Keyword queue: added %d new keywords", len(new))


def queue_status() -> dict:
    data = _load()
    return {"pending": len(data.get("pending", [])), "published": len(data.get("published", []))}
