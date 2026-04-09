"""
YouTube Scraper Module
Extracts channel name, publish date, description, and transcript
using the YouTube Data API v3 + youtube_transcript_api.
"""

import os
import re
import sys
import json
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tagging import auto_tag
from utils.chunking import chunk_text
from scoring.trust_score import calculate_trust_score

# ── config ────────────────────────────────────────────────────────────────
# Set YOUTUBE_API_KEY in your environment, or paste it here for testing.
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY_HERE")
YT_API_BASE = "https://www.googleapis.com/youtube/v3"


# ── helpers ───────────────────────────────────────────────────────────────

def extract_video_id(url: str) -> str:
    """Parse video ID from any common YouTube URL format."""
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"embed/([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError(f"Cannot extract video ID from: {url}")


def fetch_video_metadata(video_id: str) -> dict:
    """Call the YouTube Data API to get snippet + statistics."""
    url = f"{YT_API_BASE}/videos"
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": YOUTUBE_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("items", [])
    if not items:
        raise ValueError(f"No metadata found for video_id={video_id}")
    return items[0]


def fetch_transcript(video_id: str) -> str:
    """
    Fetch the auto-generated or manual transcript.
    Returns empty string if unavailable.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(seg["text"] for seg in transcript_list)
    except Exception as e:
        print(f"    [WARN] Transcript unavailable for {video_id}: {e}")
        return ""


def _has_medical_disclaimer(text: str) -> bool:
    patterns = [
        r"not (a )?medical advice",
        r"consult (a |your )?(doctor|physician|healthcare)",
        r"disclaimer",
    ]
    return any(re.search(p, text.lower()) for p in patterns)


def _detect_language(text: str) -> str:
    try:
        from langdetect import detect
        return detect(text[:500]) if text.strip() else "en"
    except Exception:
        return "en"


# ── main function ─────────────────────────────────────────────────────────

def scrape_youtube(url: str) -> dict:
    """
    Scrape a single YouTube video and return structured data.

    Parameters
    ----------
    url : str  – YouTube video URL.

    Returns
    -------
    dict following the assignment JSON schema.
    """
    print(f"  Scraping YouTube: {url}")
    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        return _empty_record(url, str(e))

    # ── Metadata from API ──────────────────────────────────────────────
    try:
        item = fetch_video_metadata(video_id)
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        channel_name = snippet.get("channelTitle", "Unknown")
        published_date = snippet.get("publishedAt", "Unknown")[:10]
        description = snippet.get("description", "")
        title = snippet.get("title", "Unknown")
        view_count = int(stats.get("viewCount", 0))
        like_count = int(stats.get("likeCount", 0))

    except Exception as e:
        print(f"    [WARN] API call failed (key missing / quota?): {e}")
        # Graceful fallback: scrape basic info from page HTML
        channel_name, published_date, description, title = _html_fallback(url)
        view_count, like_count = 0, 0

    # ── Transcript ────────────────────────────────────────────────────
    transcript = fetch_transcript(video_id)
    combined_text = f"{title}\n{description}\n{transcript}"

    language = _detect_language(combined_text)
    topic_tags = auto_tag(combined_text)
    chunks = chunk_text(combined_text)

    # ── Trust score ───────────────────────────────────────────────────
    trust = calculate_trust_score(
        source_type="youtube",
        author=channel_name,
        domain="youtube.com",
        published_date=published_date,
        content=combined_text,
        citation_count=0,          # YT videos rarely cite inline
        has_medical_disclaimer=_has_medical_disclaimer(description),
        view_count=view_count,
        like_count=like_count,
    )

    return {
        "source_url": url,
        "source_type": "youtube",
        "video_id": video_id,
        "title": title,
        "author": channel_name,
        "published_date": published_date,
        "language": language,
        "region": "Global",
        "topic_tags": topic_tags,
        "trust_score": round(trust, 3),
        "description": description,
        "transcript_available": bool(transcript),
        "view_count": view_count,
        "like_count": like_count,
        "content_chunks": chunks,
    }


# ── fallback ──────────────────────────────────────────────────────────────

def _html_fallback(url: str):
    """Parse rudimentary info from YouTube page HTML (no API key required)."""
    try:
        import requests
        from bs4 import BeautifulSoup
        resp = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0"
        }, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag else "Unknown"
        desc_tag = soup.find("meta", property="og:description")
        description = desc_tag["content"] if desc_tag else ""
        return "Unknown Channel", "Unknown", description, title
    except Exception:
        return "Unknown Channel", "Unknown", "", "Unknown"


def _empty_record(url, error=""):
    return {
        "source_url": url,
        "source_type": "youtube",
        "title": "Unknown",
        "author": "Unknown",
        "published_date": "Unknown",
        "language": "Unknown",
        "region": "Unknown",
        "topic_tags": [],
        "trust_score": 0.0,
        "content_chunks": [],
        "error": error,
    }


# ── entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    YOUTUBE_URLS = [
        "https://www.youtube.com/watch?v=EiNiSFIPIVE",  # Python web scraping tutorial
        "https://www.youtube.com/watch?v=XVv6mJpFOb0",  # Data Science overview
    ]

    results = [scrape_youtube(u) for u in YOUTUBE_URLS]
    os.makedirs("output/scraped_data", exist_ok=True)
    out_path = "output/scraped_data/youtube.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(results)} YouTube records → {out_path}")
