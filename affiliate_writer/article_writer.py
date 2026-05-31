"""
Writes long-form affiliate articles using Claude API.
Targets the Excel / Power Automate / Power BI niche.
Output is Jekyll-ready Markdown with frontmatter.
"""
import logging
from datetime import date
from typing import Optional
from anthropic import AsyncAnthropic
from config.settings import settings

logger = logging.getLogger(__name__)

_claude = AsyncAnthropic(api_key=settings.anthropic_api_key)

AMAZON_TAG = "automatework-21"  # Amazon Associates UK tag — update if changed during signup

SYSTEM_PROMPT = """You are a technical writer for AutomateWork, a blog for business professionals
who use Microsoft Excel, Power Automate, Power BI, and automation tools.

Your writing style:
- Direct and practical — tell readers exactly what to do
- Step-by-step where the topic requires it
- No fluff, no padding, no motivational filler
- Assume the reader is competent but not an expert on this specific topic
- UK English spelling throughout

Affiliate link rules:
- Include 1-3 natural affiliate link mentions, formatted as markdown links
- Only recommend products that are genuinely useful for the topic
- Always add a disclosure line at the end
- Amazon links use tag: {amazon_tag}
- For Udemy courses, use placeholder: [UDEMY_AFFILIATE_LINK]

Article structure:
- Jekyll frontmatter block at the top
- H2 and H3 headings throughout
- 1,500-2,500 words
- End with a "Further reading" or "Recommended tools" section with affiliate links
""".format(amazon_tag=AMAZON_TAG)


async def write_article(keyword: str) -> Optional[str]:
    """
    Write a complete Jekyll article for the given keyword.
    Returns the full markdown string including frontmatter, or None on failure.
    """
    today = date.today().strftime("%Y-%m-%d")

    prompt = f"""Write a complete, practical article for the keyword: "{keyword}"

The article must:
1. Start with Jekyll frontmatter:
---
layout: post
title: "<SEO-optimised title>"
date: {today}
categories: [excel, power-automate, power-bi, or automation — pick most relevant]
description: "<150-char meta description>"
---

2. Be 1,500-2,500 words of genuinely useful content
3. Include step-by-step instructions where relevant
4. Include at least 2 affiliate mentions:
   - An Amazon book link (find a real, relevant Excel/automation book on Amazon UK)
   - A Udemy course mention with placeholder [UDEMY_AFFILIATE_LINK]
5. End with this disclosure line exactly:
*This article contains affiliate links. If you purchase through them I may earn a small commission at no extra cost to you. See [disclosure](/POD-and-Affiliate/privacy/).*

Write the complete article now:"""

    try:
        msg = await _claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        article = msg.content[0].text.strip()
        logger.info("Article written: %d chars for keyword '%s'", len(article), keyword[:60])
        return article
    except Exception as e:
        logger.error("Article writing failed for '%s': %s", keyword[:60], e)
        return None


def keyword_to_filename(keyword: str, pub_date: str) -> str:
    """Convert a keyword to a Jekyll post filename."""
    slug = keyword.lower()
    slug = "".join(c if c.isalnum() or c == " " else "" for c in slug)
    slug = "-".join(slug.split())[:60]
    return f"{pub_date}-{slug}.md"
