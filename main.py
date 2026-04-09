"""
Main Pipeline Runner
====================
Orchestrates all three scrapers and writes the combined output dataset.

Usage
-----
    python main.py

Output
------
    output/scraped_data/blogs.json
    output/scraped_data/youtube.json
    output/scraped_data/pubmed.json
    output/scraped_data.json          ← combined file
"""

import json
import os
import sys
from datetime import datetime

# ── Target URLs ───────────────────────────────────────────────────────────
BLOG_URLS = [
    "https://realpython.com/beautiful-soup-web-scraper-python/",
    "https://towardsdatascience.com/a-beginners-guide-to-web-scraping-with-python-97cf9b297ad5",
    "https://www.dataquest.io/blog/web-scraping-python-using-beautiful-soup/",
]

YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=EiNiSFIPIVE",
    "https://www.youtube.com/watch?v=XVv6mJpFOb0",
]

PUBMED_URLS = [
    "https://pubmed.ncbi.nlm.nih.gov/30617339/",  # AI in clinical medicine (Nature)
]


def run_pipeline():
    os.makedirs("output/scraped_data", exist_ok=True)

    print("=" * 60)
    print("  Multi-Source Scraper & Trust Scoring Pipeline")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_results = []

    # ── 1. Blog posts ──────────────────────────────────────────────────
    print("\n[1/3] Scraping blog posts...")
    from scraper.blog_scraper import scrape_blog
    blogs = [scrape_blog(url) for url in BLOG_URLS]
    _save_json(blogs, "output/scraped_data/blogs.json")
    all_results.extend(blogs)
    print(f"      → {len(blogs)} blogs scraped.")

    # ── 2. YouTube videos ─────────────────────────────────────────────
    print("\n[2/3] Scraping YouTube videos...")
    from scraper.youtube_scraper import scrape_youtube
    videos = [scrape_youtube(url) for url in YOUTUBE_URLS]
    _save_json(videos, "output/scraped_data/youtube.json")
    all_results.extend(videos)
    print(f"      → {len(videos)} videos scraped.")

    # ── 3. PubMed article ─────────────────────────────────────────────
    print("\n[3/3] Scraping PubMed articles...")
    from scraper.pubmed_scraper import scrape_pubmed
    papers = [scrape_pubmed(url) for url in PUBMED_URLS]
    _save_json(papers, "output/scraped_data/pubmed.json")
    all_results.extend(papers)
    print(f"      → {len(papers)} articles scraped.")

    # ── Combined output ────────────────────────────────────────────────
    combined_path = "output/scraped_data.json"
    _save_json(all_results, combined_path)

    print("\n" + "=" * 60)
    print(f"  Pipeline complete. {len(all_results)} records saved.")
    print(f"  Combined: {combined_path}")
    print("=" * 60)

    # ── Trust score summary ────────────────────────────────────────────
    print("\n  Trust Score Summary")
    print("  " + "-" * 40)
    for rec in all_results:
        title = rec.get("title", rec.get("source_url", "?"))[:50]
        score = rec.get("trust_score", "?")
        stype = rec.get("source_type", "?").upper()
        print(f"  [{stype:7}] {score:.3f}  {title}")

    return all_results


def _save_json(data: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"      Saved: {path}")


if __name__ == "__main__":
    run_pipeline()
