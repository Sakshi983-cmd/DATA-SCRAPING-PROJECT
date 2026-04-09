"""
Trust Score Module
==================
Calculates a 0–1 reliability score for any scraped content source.

Formula
-------
TrustScore = w1 * author_credibility
           + w2 * citation_score
           + w3 * domain_authority
           + w4 * recency_score
           + w5 * disclaimer_score

Weights sum to 1.0 and are tuned per source type.
"""

from __future__ import annotations
import re
from datetime import datetime, date
from typing import Optional


# ── Weights by source type ─────────────────────────────────────────────────
# Higher citation weight for academic sources; higher disclaimer weight for
# medical/health content.
WEIGHTS: dict[str, dict[str, float]] = {
    "pubmed": {
        "author_credibility": 0.20,
        "citation_score":     0.30,
        "domain_authority":   0.20,
        "recency":            0.15,
        "disclaimer":         0.15,
    },
    "blog": {
        "author_credibility": 0.25,
        "citation_score":     0.15,
        "domain_authority":   0.30,
        "recency":            0.20,
        "disclaimer":         0.10,
    },
    "youtube": {
        "author_credibility": 0.25,
        "citation_score":     0.05,
        "domain_authority":   0.30,
        "recency":            0.25,
        "disclaimer":         0.15,
    },
}
DEFAULT_WEIGHTS = WEIGHTS["blog"]


# ── Domain authority lookup ────────────────────────────────────────────────
# In production this would query Moz / Ahrefs API.
# Here we maintain a hand-curated lookup plus heuristic fallbacks.
DOMAIN_AUTHORITY_DB: dict[str, float] = {
    # Academic / research
    "pubmed.ncbi.nlm.nih.gov":  0.98,
    "nature.com":                0.97,
    "science.org":               0.97,
    "thelancet.com":             0.96,
    "nejm.org":                  0.96,
    "bmj.com":                   0.95,
    "jamanetwork.com":           0.95,
    "scholar.google.com":        0.92,
    "researchgate.net":          0.88,
    # Tech / data
    "towardsdatascience.com":    0.82,
    "realpython.com":            0.85,
    "medium.com":                0.78,
    "dataquest.io":              0.80,
    "analyticsvidhya.com":       0.76,
    "kaggle.com":                0.84,
    "arxiv.org":                 0.93,
    # Video
    "youtube.com":               0.80,
    # News
    "bbc.com":                   0.92,
    "reuters.com":               0.93,
    "nytimes.com":               0.90,
    "theguardian.com":           0.89,
    # Low-quality indicators
    "blogspot.com":              0.30,
    "wordpress.com":             0.35,
    "wix.com":                   0.25,
}

# Known credible author organisations
CREDIBLE_ORGS: set[str] = {
    "nih", "who", "cdc", "mayo clinic", "harvard", "mit", "stanford",
    "oxford", "cambridge", "google", "microsoft", "meta ai", "deepmind",
    "openai", "anthropic", "ieee", "acm", "nature", "lancet", "bmj",
    "nejm", "pubmed", "ncbi",
}


# ── Sub-scores ─────────────────────────────────────────────────────────────

def author_credibility_score(author: str | list[str], multiple_authors: bool = False) -> float:
    """
    Score 0–1.
    - Unknown / empty author → 0.1
    - Name matched against credible orgs → boost to 0.9–1.0
    - Multiple authors → average; if > 1 known org author, cap at 0.95
    - Generic single name with no org association → 0.5
    """
    if not author or author in ("Unknown", ["Unknown"]):
        return 0.1  # Missing author penalty

    if isinstance(author, list):
        scores = [_single_author_score(a) for a in author]
        avg = sum(scores) / len(scores)
        # Bonus for peer-reviewed multi-author consensus
        return min(avg * 1.05, 1.0) if len(scores) > 1 else avg

    return _single_author_score(author)


def _single_author_score(name: str) -> float:
    name_lower = name.lower()
    if not name_lower or name_lower == "unknown":
        return 0.1
    # Check against known credible organisations
    for org in CREDIBLE_ORGS:
        if org in name_lower:
            return 0.95
    # Has both first and last name → slightly more credible than anonymous
    parts = name_lower.split()
    if len(parts) >= 2:
        return 0.55
    return 0.40


def citation_score(count: int, source_type: str = "blog") -> float:
    """
    Score 0–1 based on citation / external-link count.
    Thresholds differ by source type.
    """
    if source_type == "pubmed":
        # Academic: 100+ citations → 1.0
        thresholds = [(0, 0.10), (1, 0.30), (5, 0.50), (20, 0.70),
                      (50, 0.85), (100, 1.00)]
    elif source_type == "youtube":
        return 0.50   # YT doesn't have meaningful citation counts
    else:
        # Blog external links: proxy for reference quality
        thresholds = [(0, 0.10), (3, 0.30), (10, 0.50), (25, 0.70),
                      (50, 0.85), (100, 1.00)]

    score = 0.10
    for threshold, val in thresholds:
        if count >= threshold:
            score = val
    return score


def domain_authority_score(domain: str) -> float:
    """
    Return lookup value or estimate from TLD heuristics.
    """
    domain = domain.lower().replace("www.", "")

    # Exact match
    if domain in DOMAIN_AUTHORITY_DB:
        return DOMAIN_AUTHORITY_DB[domain]

    # Subdomain match (e.g., blog.example.com → example.com)
    parts = domain.split(".")
    for n in range(1, len(parts)):
        parent = ".".join(parts[n:])
        if parent in DOMAIN_AUTHORITY_DB:
            return DOMAIN_AUTHORITY_DB[parent] * 0.90  # slight subdomain penalty

    # TLD heuristic
    tld = parts[-1] if parts else "com"
    tld_defaults = {
        "edu": 0.80, "gov": 0.85, "ac": 0.78,
        "org": 0.60, "com": 0.50, "net": 0.45,
        "io":  0.50, "co":  0.45,
    }
    return tld_defaults.get(tld, 0.35)


def recency_score(published_date: str) -> float:
    """
    Score 0–1 based on how recently the content was published.

    Age bands
    ---------
    < 6 months  → 1.00
    6–12 months → 0.90
    1–2 years   → 0.75
    2–3 years   → 0.60
    3–5 years   → 0.45
    5–10 years  → 0.30
    > 10 years  → 0.15
    Unknown     → 0.40  (neutral penalty)
    """
    if not published_date or published_date == "Unknown":
        return 0.40

    try:
        # Try ISO date first, then year-only
        if len(published_date) == 4 and published_date.isdigit():
            pub = date(int(published_date), 6, 15)  # mid-year estimate
        else:
            pub = date.fromisoformat(published_date[:10])
    except (ValueError, TypeError):
        return 0.40

    age_days = (date.today() - pub).days
    age_years = age_days / 365.25

    if age_years < 0.5:  return 1.00
    if age_years < 1:    return 0.90
    if age_years < 2:    return 0.75
    if age_years < 3:    return 0.60
    if age_years < 5:    return 0.45
    if age_years < 10:   return 0.30
    return 0.15


def disclaimer_score(has_disclaimer: bool, source_type: str) -> float:
    """
    Medical disclaimer scoring.
    - PubMed: always assumed compliant (peer-reviewed)
    - Blog / YT with disclaimer: 1.0; without: 0.3
    """
    if source_type == "pubmed":
        return 1.0
    return 1.0 if has_disclaimer else 0.3


# ── Abuse prevention ──────────────────────────────────────────────────────

def abuse_penalties(
    domain: str,
    content: str,
    source_type: str,
    has_medical_disclaimer: bool,
) -> float:
    """
    Returns a penalty multiplier in [0.5, 1.0].
    A value of 1.0 means no penalty; 0.5 is the maximum penalty.

    Checks
    ------
    1. Low-DA spam domains
    2. SEO keyword stuffing (high keyword density)
    3. Medical content without disclaimer
    4. Extremely short content (stub articles)
    5. Clickbait title patterns
    """
    penalty = 1.0

    # 1 · Spam / low-authority hosting platforms
    spam_domains = {"blogspot.com", "wix.com", "weebly.com", "tripod.com",
                    "angelfire.com", "tumblr.com"}
    clean_domain = domain.lower().replace("www.", "")
    if any(clean_domain.endswith(sd) for sd in spam_domains):
        penalty *= 0.70

    # 2 · Keyword stuffing (same word appears > 5 % of total word count)
    words = re.findall(r"\b[a-z]{4,}\b", content.lower())
    if words:
        from collections import Counter
        top_word_freq = Counter(words).most_common(1)[0][1] / len(words)
        if top_word_freq > 0.05:
            penalty *= 0.80

    # 3 · Health / medical content without disclaimer
    medical_keywords = ["treatment", "cure", "diagnosis", "symptom",
                        "drug", "medicine", "therapy", "disease"]
    medical_hit_count = sum(
        1 for kw in medical_keywords if kw in content.lower()
    )
    if medical_hit_count >= 3 and not has_medical_disclaimer and source_type != "pubmed":
        penalty *= 0.65

    # 4 · Stub content (< 100 words)
    if len(words) < 100:
        penalty *= 0.75

    # 5 · Clickbait title signals in content
    clickbait_patterns = [
        r"you won'?t believe",
        r"shocking(ly)?",
        r"\d+ (weird|crazy|insane) (tricks|hacks|ways)",
        r"doctors hate",
    ]
    for pat in clickbait_patterns:
        if re.search(pat, content[:500].lower()):
            penalty *= 0.85
            break

    return max(penalty, 0.50)   # floor: never reduce by more than 50 %


# ── Main entry point ──────────────────────────────────────────────────────

def calculate_trust_score(
    source_type: str,
    author: str | list[str],
    domain: str,
    published_date: str,
    content: str,
    citation_count: int = 0,
    has_medical_disclaimer: bool = False,
    multiple_authors: bool = False,
    view_count: int = 0,
    like_count: int = 0,
) -> float:
    """
    Compute the composite trust score (0–1) for a scraped source.

    Parameters
    ----------
    source_type          : 'blog', 'youtube', or 'pubmed'
    author               : Author name string or list of names
    domain               : Hostname of the source (e.g. 'medium.com')
    published_date       : ISO date string 'YYYY-MM-DD' or 'Unknown'
    content              : Full text of the article / transcript
    citation_count       : Number of citations or external links
    has_medical_disclaimer: Whether a disclaimer was detected
    multiple_authors     : True if > 1 author (for pubmed)
    view_count           : YouTube view count (optional)
    like_count           : YouTube like count (optional)

    Returns
    -------
    float in [0.0, 1.0]
    """
    w = WEIGHTS.get(source_type, DEFAULT_WEIGHTS)

    # ── Component scores ───────────────────────────────────────────────
    s_author = author_credibility_score(author, multiple_authors)
    s_cite   = citation_score(citation_count, source_type)
    s_domain = domain_authority_score(domain)
    s_recent = recency_score(published_date)
    s_disc   = disclaimer_score(has_medical_disclaimer, source_type)

    # YouTube engagement bonus (capped at 0.10 boost)
    engagement_boost = 0.0
    if source_type == "youtube" and view_count > 0:
        ratio = like_count / view_count if view_count else 0
        engagement_boost = min(ratio * 0.5, 0.10)

    raw_score = (
        w["author_credibility"] * s_author
        + w["citation_score"]     * s_cite
        + w["domain_authority"]   * s_domain
        + w["recency"]            * s_recent
        + w["disclaimer"]         * s_disc
        + engagement_boost
    )

    # ── Abuse prevention multiplier ───────────────────────────────────
    penalty = abuse_penalties(domain, content, source_type, has_medical_disclaimer)
    final_score = raw_score * penalty

    return round(min(max(final_score, 0.0), 1.0), 4)


# ── Scoring breakdown (for debugging / transparency) ──────────────────────

def score_breakdown(
    source_type: str,
    author: str | list[str],
    domain: str,
    published_date: str,
    content: str,
    citation_count: int = 0,
    has_medical_disclaimer: bool = False,
) -> dict:
    """Return a dict showing each component score for transparency."""
    w = WEIGHTS.get(source_type, DEFAULT_WEIGHTS)
    return {
        "author_credibility": {
            "raw": round(author_credibility_score(author), 3),
            "weight": w["author_credibility"],
        },
        "citation_score": {
            "raw": round(citation_score(citation_count, source_type), 3),
            "weight": w["citation_score"],
        },
        "domain_authority": {
            "raw": round(domain_authority_score(domain), 3),
            "weight": w["domain_authority"],
        },
        "recency": {
            "raw": round(recency_score(published_date), 3),
            "weight": w["recency"],
        },
        "disclaimer": {
            "raw": round(disclaimer_score(has_medical_disclaimer, source_type), 3),
            "weight": w["disclaimer"],
        },
        "abuse_penalty": round(
            abuse_penalties(domain, content, source_type, has_medical_disclaimer), 3
        ),
    }
