"""
GitHub API trigger — dispatches workflow_dispatch on deploy-frontend.yml
so the Next.js static build picks up newly generated blog posts.
"""
from __future__ import annotations

import logging
import urllib.request
import urllib.error
import json

from ssm import get_ssm_parameter

logger = logging.getLogger(__name__)

_REPO  = "tjkimcloud/nova-kid-life"
_WORKFLOW = "deploy-frontend.yml"


def trigger_frontend_rebuild() -> bool:
    """POST to GitHub Actions API to dispatch a frontend rebuild.

    Returns True on success, False on failure (non-fatal — posts are saved,
    the site will just pick them up on the next scheduled deploy).
    """
    try:
        token = get_ssm_parameter("/novakidlife/github/token")
    except RuntimeError as exc:
        logger.warning("GitHub token not available — skipping rebuild trigger: %s", exc)
        return False

    url     = f"https://api.github.com/repos/{_REPO}/actions/workflows/{_WORKFLOW}/dispatches"
    payload = json.dumps({"ref": "main"}).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization":        f"Bearer {token}",
            "Accept":               "application/vnd.github+json",
            "Content-Type":         "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            # 204 No Content = success
            if resp.status == 204:
                logger.info("Frontend rebuild triggered successfully")
                return True
            logger.warning("Unexpected GitHub API status: %s", resp.status)
            return False
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        logger.error("GitHub API error %s: %s", exc.code, body)
        return False
    except Exception as exc:
        logger.error("Failed to trigger frontend rebuild: %s", exc)
        return False
