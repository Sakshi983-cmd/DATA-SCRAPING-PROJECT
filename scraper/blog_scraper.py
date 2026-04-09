"""
Blog Scraper Module
Extracts structured content from blog posts using requests + BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tagging import auto_tag
from utils.chunking import chunk_text
from scoring.trust_score import calculate_trust_score


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def detect_language(text: str) -> str:
    """Simple heuristic language detection (extend with langdetect in prod)."""
    try:
        from langdetect import detect
        return detect(text[:500])
    except Exception:
        return "en"


def extract_author(soup: BeautifulSoup) -> str:
    """Try multiple common HTML patterns to find the author."""
    # Meta tags
    for attr in ["name", "property"]:
        tag = soup.find("meta", attrs={attr: re.compile(r"author", re.I)})
        if tag and tag.get("content"):
            return tag["content"].strip()

    # Schema.org / JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            data = json.loads(script.string or "{}")
            if isinstance(data, list):
                data = data[0]
            author = data.get("author", {})
            if isinstance(author, dict):
                return author.get("name", "Unknown")
            if isinstance(author, str):
                return author
        except Exception:
            pass

    # Common CSS classes / rel attributes
    for selector in [
        {"class": re.compile(r"author", re.I)},
        {"rel": "author"},
        {"itemprop": "author"},
    ]:
        tag = soup.find(attrs=selector)
        if tag:
            return tag.get_text(strip=True)[:100]

    return "Unknown"


def extract_published_date(soup: BeautifulSoup) -> str:
    """Extract publish date from meta tags or time elements."""
    # <time> element
    time_tag = soup.find("time")
    if time_tag:
        return time_tag.get("datetime") or time_tag.get_text(strip=True)

    # Meta
    for prop in ["article:published_time", "datePublished", "pubdate"]:
        tag = soup.find("meta", attrs={"property": prop}) or \
              soup.find("meta", attrs={"name": prop}) or \
              soup.find("meta", attrs={"itemprop": prop})
        if tag and tag.get("content"):
            return tag["content"][:10]

    return "Unknown"


def clean_text(soup: BeautifulSoup) -> str:
    """Remove nav, footer, ads; return clean article text."""
    for tag in soup(["nav", "footer", "header", "aside", "script",
                     "style", "noscript", "form", "iframe"]):
        tag.decompose()

    # Try <article> first, then <main>, then fall back to <body>
    article = soup.find("article") or soup.find("main") or soup.find("body")
    if article:
        return article.get_text(separator="\n", strip=True)
    return soup.get_text(separator="\n", strip=True)


def scrape_blog(url: str) -> dict:
    """
    Scrape a single blog post and return a structured dict.

    Parameters
    ----------
    url : str  – Public URL of the blog post.

    Returns
    -------
    dict following the assignment JSON schema.
    """
    print(f"  Scraping blog: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    [WARN] Request failed: {e}")
        return _empty_record(url, "blog", error=str(e))

    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"

    author = extract_author(soup)
    published_date = extract_published_date(soup)
    raw_text = clean_text(soup)
    language = detect_language(raw_text)
    topic_tags = auto_tag(raw_text)
    chunks = chunk_text(raw_text)

    # Region: try to infer from URL TLD or meta
    region = _infer_region(url, soup)

    # Gather scoring signals
    domain = url.split("/")[2].replace("www.", "")
    trust = calculate_trust_score(
        source_type="blog",
        author=author,
        domain=domain,
        published_date=published_date,
        content=raw_text,
        citation_count=_count_citations(soup),
        has_medical_disclaimer=_has_medical_disclaimer(raw_text),
    )

    return {
        "source_url": url,
        "source_type": "blog",
        "title": title,
        "author": author,
        "published_date": published_date,
        "language": language,
        "region": region,
        "topic_tags": topic_tags,
        "trust_score": round(trust, 3),
        "content_chunks": chunks,
    }


# ── helpers ────────────────────────────────────────────────────────────────

def _empty_record(url, source_type, error=""):
    return {
        "source_url": url,
        "source_type": source_type,
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


def _infer_region(url: str, soup: BeautifulSoup) -> str:
    tld = url.split("/")[2].rsplit(".", 1)[-1].split(":")[0].lower()
    tld_map = {
        "uk": "United Kingdom", "in": "India", "au": "Australia",
        "ca": "Canada", "de": "Germany", "fr": "France",
        "com": "Global/US", "org": "Global", "io": "Global",
    }
    return tld_map.get(tld, "Unknown")


def _count_citations(soup: BeautifulSoup) -> int:
    links = soup.find_all("a", href=True)
    external = [l for l in links if l["href"].startswith("http")]
    return len(external)


def _has_medical_disclaimer(text: str) -> bool:
    patterns = [
        r"not (a )?medical advice",
        r"consult (a |your )?(doctor|physician|healthcare)",
        r"this (article|content|post) is (for )?informational",
        r"disclaimer",
    ]
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


if __name__ == "__main__":
    import json

    BLOG_URLS = [
        "https://towardsdatascience.com/a-beginners-guide-to-web-scraping-with-python-97cf9b297ad5",
        "https://realpython.com/beautiful-soup-web-scraper-python/",
        "https://www.dataquest.io/blog/web-scraping-python-using-beautiful-soup/",
    ]

    results = [scrape_blog(u) for u in BLOG_URLS]
    os.makedirs("output/scraped_data", exist_ok=True)
    out_path = "output/scraped_data/blogs.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(results)} blog records → {out_path}")
