"""
Publishes affiliate articles to the affiliate branch via git.
The affiliate-site worktree lives at ../affiliate-site relative to this project.
"""
import logging
import os
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

# Absolute path to the affiliate-site git worktree
AFFILIATE_SITE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "affiliate-site")
)
POSTS_DIR = os.path.join(AFFILIATE_SITE_DIR, "_posts")


def _git(args: list, cwd: str = AFFILIATE_SITE_DIR) -> tuple[int, str]:
    """Run a git command, return (returncode, output)."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def publish_article(filename: str, content: str) -> bool:
    """
    Write article to _posts, commit, and push to affiliate branch.
    Returns True on success.
    """
    if not os.path.isdir(AFFILIATE_SITE_DIR):
        logger.error(
            "affiliate-site worktree not found at %s — "
            "run: git worktree add ../affiliate-site affiliate",
            AFFILIATE_SITE_DIR,
        )
        return False

    os.makedirs(POSTS_DIR, exist_ok=True)
    post_path = os.path.join(POSTS_DIR, filename)

    try:
        with open(post_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Article written: %s", post_path)
    except Exception as e:
        logger.error("Failed to write article file: %s", e)
        return False

    # git add
    code, out = _git(["add", os.path.join("_posts", filename)])
    if code != 0:
        logger.error("git add failed: %s", out)
        return False

    # git commit
    short_name = filename[11:-3].replace("-", " ")  # strip date and .md
    code, out = _git(["commit", "-m", f"feat: add article — {short_name[:60]}"])
    if code != 0:
        logger.error("git commit failed: %s", out)
        return False

    # git push
    code, out = _git(["push"])
    if code != 0:
        logger.error("git push failed: %s", out)
        return False

    logger.info("Article published to affiliate branch: %s", filename)
    return True


def worktree_exists() -> bool:
    return os.path.isdir(AFFILIATE_SITE_DIR) and os.path.isdir(
        os.path.join(AFFILIATE_SITE_DIR, "_posts")
    )
