"""
Affiliate article auto-publisher pipeline.

Each cycle:
  1. Pull next keyword from queue (data/affiliate_keywords.json)
  2. Claude Haiku writes a 1,500-2,500 word Jekyll article
  3. Article committed to affiliate-site worktree and pushed to affiliate branch
  4. GitHub Actions auto-deploys to GitHub Pages

Runs 3x per week via APScheduler.
"""
import logging
from datetime import date

from affiliate_writer.keyword_queue import next_keyword, mark_published, queue_status
from affiliate_writer.article_writer import write_article, keyword_to_filename
from affiliate_writer.git_publisher import publish_article, worktree_exists

logger = logging.getLogger(__name__)

ARTICLES_PER_CYCLE = 1  # one article per scheduled run keeps output quality high


class AffiliateWriterPipeline:
    async def run(self) -> int:
        """Run one cycle. Returns number of articles published."""
        if not worktree_exists():
            logger.warning(
                "Affiliate pipeline: affiliate-site worktree missing — "
                "run: git worktree add ../affiliate-site affiliate"
            )
            return 0

        status = queue_status()
        logger.info(
            "Affiliate pipeline: starting — %d keywords pending, %d published",
            status["pending"], status["published"],
        )

        published_count = 0

        for _ in range(ARTICLES_PER_CYCLE):
            keyword = next_keyword()
            if not keyword:
                logger.info("Affiliate pipeline: keyword queue empty")
                break

            logger.info("Affiliate pipeline: writing article for '%s'", keyword[:70])

            # Write article
            today = date.today().strftime("%Y-%m-%d")
            article_md = await write_article(keyword)
            if not article_md:
                logger.error("Article generation failed for '%s'", keyword[:60])
                continue

            # Publish to git
            filename = keyword_to_filename(keyword, today)
            success = publish_article(filename, article_md)

            if success:
                mark_published(keyword)
                published_count += 1
                logger.info("Affiliate pipeline: article published — %s", filename)
            else:
                logger.error("Affiliate pipeline: publish failed for '%s'", keyword[:60])

        logger.info("Affiliate pipeline: %d article(s) published this cycle", published_count)
        return published_count
