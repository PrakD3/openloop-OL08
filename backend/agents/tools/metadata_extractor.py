"""Deep metadata extraction for video URLs using yt-dlp and Reddit API."""

import logging
from datetime import date, datetime

import httpx
import yt_dlp

logger = logging.getLogger(__name__)


def _calc_account_age_days(info: dict) -> int | None:
    """Estimate account age from channel creation date if available."""
    raw = info.get("channel_creation_date") or info.get("uploader_creation_date")
    if not raw:
        return None
    try:
        created = datetime.strptime(str(raw), "%Y%m%d").date()
        return (date.today() - created).days
    except Exception:
        return None


async def extract_platform_metadata(url: str) -> dict:
    """
    Extract deep metadata from video URL using yt-dlp.
    Works for Reddit, YouTube, Instagram, Twitter/X, TikTok.
    Returns a structured dict — never raises, returns error key on failure.
    """
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        metadata = {
            "platform": _detect_platform(url),
            "uploader": info.get("uploader"),
            "uploader_id": info.get("uploader_id"),
            "uploader_url": info.get("uploader_url"),
            "subscriber_count": info.get("channel_follower_count"),
            "account_age_days": _calc_account_age_days(info),
            "upload_date": info.get("upload_date"),  # YYYYMMDD
            "upload_timestamp": info.get("timestamp"),  # Unix epoch
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "comment_count": info.get("comment_count"),
            "title": info.get("title", ""),
            "description": (info.get("description") or "")[:600],
            "tags": info.get("tags", [])[:15],
            "categories": info.get("categories", []),
            "original_url": info.get("original_url") or info.get("webpage_url"),
            "duration_seconds": info.get("duration"),
            "fps": info.get("fps"),
            "resolution": f"{info.get('width', '?')}x{info.get('height', '?')}",
            "video_codec": info.get("vcodec"),
            "audio_codec": info.get("acodec"),
            "filesize_bytes": info.get("filesize") or info.get("filesize_approx"),
            "age_limit": info.get("age_limit", 0),
            "is_live": info.get("is_live", False),
            "was_live": info.get("was_live", False),
            "live_status": info.get("live_status"),
            "availability": info.get("availability"),
            "playable_in_embed": info.get("playable_in_embed"),
        }

        logger.info(
            f"[METADATA] Extracted for {_detect_platform(url)}: uploader={metadata['uploader']}, date={metadata['upload_date']}"
        )
        return metadata

    except Exception as e:
        logger.error(f"[METADATA] yt-dlp extraction failed: {e}")
        return {"error": str(e), "platform": _detect_platform(url)}


async def extract_reddit_metadata(url: str) -> dict:
    """
    For Reddit URLs: fetch additional post/author data via public Reddit JSON API.
    No OAuth required. Returns empty dict if not a Reddit URL or on failure.
    """
    if "reddit.com" not in url:
        return {}

    json_url = url.split("?")[0].rstrip("/") + ".json?limit=1"
    headers = {"User-Agent": "Vigilens/1.0 (disaster verification tool)"}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(json_url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        post_data = data[0]["data"]["children"][0]["data"]

        # Fetch author profile
        author = post_data.get("author", "")
        author_data = {}
        if author and author != "[deleted]":
            try:
                async with httpx.AsyncClient(timeout=5.0) as author_client:
                    author_resp = await author_client.get(
                        f"https://www.reddit.com/user/{author}/about.json",
                        headers=headers,
                    )
                    if author_resp.status_code == 200:
                        ainfo = author_resp.json().get("data", {})
                        created_utc = ainfo.get("created_utc", 0)
                        account_age_days = (
                            int((datetime.now().timestamp() - created_utc) / 86400)
                            if created_utc
                            else None
                        )
                        author_data = {
                            "account_age_days": account_age_days,
                            "post_karma": ainfo.get("link_karma", 0),
                            "comment_karma": ainfo.get("comment_karma", 0),
                            "is_verified": ainfo.get("verified", False),
                            "has_verified_email": ainfo.get("has_verified_email", False),
                            "total_karma": ainfo.get("total_karma", 0),
                        }
            except Exception as ae:
                logger.warning(f"[METADATA/Reddit] Author fetch failed: {ae}")

        return {
            "subreddit": post_data.get("subreddit"),
            "subreddit_subscribers": post_data.get("subreddit_subscribers"),
            "post_score": post_data.get("score"),
            "upvote_ratio": post_data.get("upvote_ratio"),
            "num_comments": post_data.get("num_comments"),
            "over_18": post_data.get("over_18", False),
            "is_crosspost": bool(post_data.get("crosspost_parent")),
            "crosspost_parent": post_data.get("crosspost_parent"),
            "author": author,
            "post_flair": post_data.get("link_flair_text"),
            "author_flair": post_data.get("author_flair_text"),
            "author_profile": author_data,
        }

    except Exception as e:
        logger.warning(f"[METADATA/Reddit] Reddit API fetch failed: {e}")
        return {}


def _detect_platform(url: str) -> str:
    if "reddit.com" in url or "redd.it" in url:
        return "reddit"
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "instagram.com" in url:
        return "instagram"
    if "twitter.com" in url or "x.com" in url:
        return "twitter"
    if "tiktok.com" in url:
        return "tiktok"
    return "unknown"
