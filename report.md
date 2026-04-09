# Data Scraping & Trust Scoring — Assignment Report

**Submitted by:** Sakshi Tiwari  
**Assignment:** Multi-Source Scraper + Trust Score System  
**Date:** April 2026

---

## 1. Scraping Strategy

The pipeline collects data from three distinct source types, each requiring a different
extraction approach.

**Blog Posts** are scraped using the `requests` library for HTTP and `BeautifulSoup`
for HTML parsing. The scraper first removes boilerplate elements (navigation bars,
footers, ads, scripts) before extracting the main article body. It attempts author
extraction in priority order: JSON-LD schema markup, Open Graph meta tags, and
finally CSS class patterns. Publish dates are parsed from `<time>` elements or
`article:published_time` meta attributes. A realistic browser User-Agent header
reduces the chance of being blocked.

**YouTube Videos** are scraped using two mechanisms. The primary mechanism is the
YouTube Data API v3, which returns structured JSON containing channel name, publish
date, description, view count, and like count. Transcripts are fetched separately
using `youtube-transcript-api`, which retrieves auto-generated or manually uploaded
captions. When no API key is provided, a fallback HTML parser reads Open Graph meta
tags to extract the title and description. The full content field is a concatenation
of title, description, and transcript, giving the downstream NLP pipeline sufficient
text to work with.

**PubMed Articles** are scraped via the NCBI E-utilities API (`eFetch` endpoint),
which returns structured XML containing the article title, all authors, journal name,
abstract with section labels, and MeSH vocabulary terms. Citation counts are retrieved
separately via the `eLink` endpoint by counting reverse-linked records in PubMed
Central. This API is free and does not require authentication for up to 3 requests
per second (10 requests/second with a free API key).

---

## 2. Topic Tagging Method

Automatic topic tagging combines two complementary approaches.

**Taxonomy Matching** maps a curated dictionary of 13 topic categories (AI, Machine
Learning, Deep Learning, Healthcare, Web Scraping, Python, NLP, etc.) to lists of
trigger phrases. If any trigger phrase appears in the lowercased text, the canonical
tag is assigned. This produces high-precision, human-readable labels with low recall.

**TF-IDF Keyword Extraction** complements the taxonomy by surfacing domain-specific
terms that are not covered by the hand-curated dictionary. A `TfidfVectorizer` from
scikit-learn is fitted on sentence-level splits of the text with bigrams enabled.
The top-scoring terms are added as additional tags after filtering stop words and
short tokens. On machines without scikit-learn, a simple term-frequency fallback
ensures the module always returns results.

The final tag list interleaves taxonomy tags first (for interpretability), followed
by TF-IDF keywords, capped at 8 tags per record.

---

## 3. Trust Score Algorithm

The trust score is a weighted linear combination of five normalised sub-scores,
each ranging from 0 to 1:

```
TrustScore = w1 × author_credibility  +  w2 × citation_score
           + w3 × domain_authority    +  w4 × recency_score
           + w5 × disclaimer_score
```

Multiplied by an **abuse prevention penalty** (0.50–1.00).

**Author Credibility** checks whether the author name contains references to
known credible organisations (NIH, WHO, CDC, Harvard, MIT, Nature, IEEE, etc.).
An unknown author scores 0.10; a name from a credible org scores 0.95.
Multiple authors receive an averaged score with a 5% consensus bonus.

**Citation Score** uses logarithmic thresholds calibrated to each source type.
For PubMed, 100+ citations earns a score of 1.0. For blogs, external hyperlinks
serve as a citation proxy. YouTube videos use a fixed baseline since inline
citations are rare, with a like/view engagement ratio used as a partial substitute.

**Domain Authority** uses a curated lookup table of 25 well-known domains
(Nature → 0.97, realpython.com → 0.85, blogspot.com → 0.30). Unknown domains
are estimated from their TLD: `.gov` earns 0.85, `.edu` earns 0.80, `.com`
earns 0.50. A production system would query the Moz or Ahrefs API for real
domain authority scores.

**Recency Score** decays from 1.0 (< 6 months) to 0.15 (> 10 years).
Content with an unknown publish date receives a neutral 0.40 to avoid
penalising sources that simply omit date metadata.

**Disclaimer Score** rewards health-related content that includes a medical
disclaimer ("consult a physician", "not medical advice", etc.). PubMed articles
automatically receive 1.0 as they are peer-reviewed and implicitly compliant.

**Weights** are tuned per source type. PubMed receives higher weight on citations
(0.30) reflecting the importance of peer validation in academic content. YouTube
receives higher weight on recency (0.25) and lower on citations (0.05). Blogs
balance domain authority (0.30) and author credibility (0.25).

---

## 4. Edge Case Handling

| Scenario | Handling |
|---|---|
| Missing author | Default to "Unknown"; author_credibility penalised to 0.10 |
| Missing publish date | Default recency score of 0.40 (neutral) |
| Multiple authors | Average credibility scores; 5% consensus bonus |
| Transcript unavailable | Use title + description only; flag `transcript_available: false` |
| Non-English content | `langdetect` detects language; stored in `language` field; chunking still works |
| Very long articles | Chunker splits by paragraph, then by sentence, with configurable overlap |
| Stub / very short content | Abuse penalty of × 0.75 applied if < 100 words |
| Medical content without disclaimer | Penalty × 0.65 if ≥ 3 medical keywords present |
| Keyword-stuffed SEO blogs | Penalty × 0.80 if top word frequency > 5% of total |
| Low-DA hosting platforms | Domains like blogspot, wix receive × 0.70 penalty |
| YouTube API quota exceeded | Graceful fallback to HTML meta-tag scraping |

---

## 5. Sample Results

| Source | Type | Trust Score | Top Tags |
|---|---|---|---|
| RealPython – BeautifulSoup guide | Blog | 0.430 | Web Scraping, Python, Data Engineering |
| TDS – Beginner ML guide | Blog | 0.365 | AI, Machine Learning, Deep Learning |
| Dataquest – BS4 tutorial | Blog | 0.421 | Data Science, Python, Research |
| Tech With Tim – Scraping YT | YouTube | 0.550 | Web Scraping, Python, Data Engineering |
| freeCodeCamp – Data Science YT | YouTube | 0.416 | AI, Machine Learning, Data Science |
| Topol 2019 – AI in Medicine (Nature) | PubMed | 0.601 | AI, Healthcare, Deep Learning |

The PubMed article scores highest, reflecting its 9,847 citations, high domain authority,
and guaranteed disclaimer score. The YouTube video by Tech With Tim benefits from high
engagement (8,900 likes / 145,000 views). Blog scores are moderated by unknown author
credibility and the absence of medical disclaimers on some posts.
