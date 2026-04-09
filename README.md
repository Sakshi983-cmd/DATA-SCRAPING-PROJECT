# Multi-Source Scraper & Trust Scoring System

A data ingestion pipeline that scrapes structured content from blogs, YouTube, and PubMed,
then scores each source on a 0–1 reliability scale using a custom trust algorithm.

---

## Project Structure

```
project/
├── main.py                        ← Orchestrator: run this to scrape all sources
├── scraper/
│   ├── blog_scraper.py            ← Blog scraper (requests + BeautifulSoup)
│   ├── youtube_scraper.py         ← YouTube scraper (Data API v3 + transcript API)
│   └── pubmed_scraper.py          ← PubMed scraper (NCBI E-utilities)
├── scoring/
│   └── trust_score.py             ← Trust score algorithm + abuse prevention
├── utils/
│   ├── tagging.py                 ← Auto topic tagging (TF-IDF + taxonomy)
│   └── chunking.py                ← Content chunking with overlap
└── output/
    ├── scraped_data.json          ← Combined dataset (all 6 records)
    └── scraped_data/
        ├── blogs.json             ← 3 blog post records
        ├── youtube.json           ← 2 YouTube video records
        └── pubmed.json            ← 1 PubMed article record
```

---

## Setup & Installation

### Requirements
- Python 3.9+
- pip

### Install Dependencies
```bash
pip install requests beautifulsoup4 scikit-learn langdetect \
            youtube-transcript-api lxml
```

### Optional (for YouTube metadata)
Get a free API key from [Google Cloud Console](https://console.cloud.google.com/), enable the YouTube Data API v3, and set:
```bash
export YOUTUBE_API_KEY="your_key_here"
```

### Optional (for higher PubMed rate limits)
```bash
export NCBI_API_KEY="your_key_here"
```

---

## How to Run

```bash
cd project/
python main.py
```

This will:
1. Scrape 3 blog posts
2. Scrape 2 YouTube videos
3. Scrape 1 PubMed article
4. Calculate trust scores for all 6
5. Save output to `output/scraped_data/`

To run individual scrapers:
```bash
python scraper/blog_scraper.py
python scraper/youtube_scraper.py
python scraper/pubmed_scraper.py
```

---

## Tools & Libraries

| Library | Purpose |
|---|---|
| `requests` | HTTP requests for blog and PubMed |
| `beautifulsoup4` | HTML parsing for blogs |
| `lxml` | Fast HTML/XML parser backend |
| `youtube-transcript-api` | Fetch YouTube auto-captions |
| `scikit-learn` | TF-IDF keyword extraction |
| `langdetect` | Automatic language detection |
| NCBI E-utilities API | PubMed metadata + citations (free) |
| YouTube Data API v3 | Video metadata (requires key) |

---

## Scraping Approach

### Blogs
- HTTP GET with a realistic browser User-Agent to reduce bot detection.
- BeautifulSoup removes nav, footer, script, and ads before extracting text.
- Author extracted from `<meta name="author">`, JSON-LD schema, or CSS class patterns.
- Publish date extracted from `<time>`, `article:published_time` meta, or `itemprop`.

### YouTube
- Primary path: YouTube Data API v3 (`/videos?part=snippet,statistics`).
- Transcript: `youtube-transcript-api` — fetches auto-generated or manual captions.
- Fallback (no API key): scrape `og:title` and `og:description` from page HTML.
- Content = title + description + transcript (concatenated for tagging and chunking).

### PubMed
- Uses NCBI eFetch (`/efetch.fcgi?db=pubmed&retmode=xml`) — no API key required.
- Parses XML for title, all authors, journal, abstract (with section labels), MeSH terms.
- Citation count retrieved via NCBI eLink (`pubmed_pmc_refs`).

---

## Trust Score Design

### Formula
```
TrustScore = w1 × author_credibility
           + w2 × citation_score
           + w3 × domain_authority
           + w4 × recency_score
           + w5 × disclaimer_score
           × abuse_penalty_multiplier
```

All weights sum to 1.0. Weights are **tuned per source type**:

| Component | Blog | YouTube | PubMed |
|---|---|---|---|
| author_credibility | 0.25 | 0.25 | 0.20 |
| citation_score | 0.15 | 0.05 | 0.30 |
| domain_authority | 0.30 | 0.30 | 0.20 |
| recency | 0.20 | 0.25 | 0.15 |
| disclaimer | 0.10 | 0.15 | 0.15 |

### Component Details

**Author Credibility (0–1)**
- Unknown author → 0.1
- Author matched to known credible org (NIH, Harvard, WHO, etc.) → 0.95
- Full name (first + last) → 0.55; single/handle → 0.40
- Multiple authors → average with 1.05× consensus bonus

**Citation Score (0–1)**
- PubMed: log-scaled from 0 citations (0.10) to 100+ (1.00)
- Blog: external link count as citation proxy (0–100+)
- YouTube: fixed 0.50 (engagement substituted)

**Domain Authority (0–1)**
- Lookup table of ~25 curated domains (Nature → 0.97, blogspot → 0.30)
- TLD fallback: `.edu`→0.80, `.gov`→0.85, `.com`→0.50, `.io`→0.50
- YouTube engagement bonus: +0.10 max based on like/view ratio

**Recency Score (0–1)**
- < 6 months → 1.00, 6–12 months → 0.90, 1–2 yrs → 0.75
- 2–3 yrs → 0.60, 3–5 yrs → 0.45, 5–10 yrs → 0.30, > 10 yrs → 0.15
- Unknown date → 0.40 (neutral penalty)

**Disclaimer Score (0–1)**
- PubMed: always 1.0 (peer-reviewed)
- Blog/YouTube with disclaimer → 1.0; without → 0.30

---

## Abuse Prevention

| Attack | Detection | Penalty |
|---|---|---|
| Fake / anonymous author | Name not in credible org list | author_credibility → 0.10–0.40 |
| SEO keyword stuffing | Top word frequency > 5% of total words | × 0.80 |
| Medical content, no disclaimer | ≥ 3 medical keywords + no disclaimer | × 0.65 |
| Low-quality hosting | Domain in spam list (blogspot, wix, etc.) | × 0.70 |
| Stub / scraped thin content | < 100 words in body | × 0.75 |
| Clickbait titles | Regex match on "you won't believe", etc. | × 0.85 |

Maximum combined penalty: 0.50× (scores floored at 50% of raw).

---

## Limitations

1. **Network-dependent**: Scrapers require live internet access. Some sites block bots.
2. **YouTube API quota**: 10,000 units/day on free tier; transcript may be unavailable for some videos.
3. **Domain authority**: Lookup table is hand-curated. A production system would integrate Moz/Ahrefs API.
4. **Language detection**: `langdetect` is probabilistic and may misclassify short texts.
5. **PubMed citation count**: `eLink` only counts PMC references, not all-source citations. Crossref API would be more complete.
6. **Dynamic pages**: JavaScript-rendered blogs (React/Vue SPAs) require Playwright/Selenium instead of requests.

---

## Output Schema

```json
{
  "source_url": "https://...",
  "source_type": "blog | youtube | pubmed",
  "title": "Article / video title",
  "author": "Name or list of names",
  "published_date": "YYYY-MM-DD",
  "language": "en",
  "region": "Global/US",
  "topic_tags": ["AI", "Machine Learning", "Web Scraping"],
  "trust_score": 0.743,
  "content_chunks": ["Paragraph 1...", "Paragraph 2...", "..."]
}
```
