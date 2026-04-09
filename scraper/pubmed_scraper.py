"""
PubMed Scraper Module
Uses the NCBI E-utilities (free, no API key required for basic use)
to fetch article metadata and abstracts.
"""

import os
import re
import sys
import json
import requests
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tagging import auto_tag
from utils.chunking import chunk_text
from scoring.trust_score import calculate_trust_score

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
# Optionally set NCBI_API_KEY for higher rate limits (10 req/s vs 3 req/s).
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")


# ── helpers ───────────────────────────────────────────────────────────────

def extract_pmid(url: str) -> str:
    """Extract PMID from a PubMed URL like https://pubmed.ncbi.nlm.nih.gov/12345678/"""
    m = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", url)
    if m:
        return m.group(1)
    # Maybe the user just passed a plain PMID
    if url.strip().isdigit():
        return url.strip()
    raise ValueError(f"Cannot extract PMID from: {url}")


def fetch_pubmed_xml(pmid: str) -> ET.Element:
    """Fetch the eFetch XML record for a given PMID."""
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
        "rettype": "abstract",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    resp = requests.get(f"{NCBI_BASE}/efetch.fcgi", params=params, timeout=15)
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def _get_text(element: ET.Element, path: str, default="Unknown") -> str:
    node = element.find(path)
    return node.text.strip() if node is not None and node.text else default


def parse_authors(article_node: ET.Element) -> list[str]:
    authors = []
    for author in article_node.findall(".//Author"):
        last = _get_text(author, "LastName", "")
        fore = _get_text(author, "ForeName", "")
        if last:
            authors.append(f"{fore} {last}".strip())
    return authors or ["Unknown"]


def parse_abstract(article_node: ET.Element) -> str:
    """Concatenate all AbstractText sections."""
    parts = []
    for abs_text in article_node.findall(".//AbstractText"):
        label = abs_text.get("Label", "")
        text = abs_text.text or ""
        if label:
            parts.append(f"{label}: {text}")
        else:
            parts.append(text)
    return " ".join(parts).strip()


def fetch_citation_count(pmid: str) -> int:
    """
    Use eLink to count articles that cite this PMID in PubMed Central.
    Falls back to 0 if the call fails.
    """
    try:
        params = {
            "dbfrom": "pubmed",
            "db": "pmc",
            "id": pmid,
            "linkname": "pubmed_pmc_refs",
            "retmode": "json",
        }
        if NCBI_API_KEY:
            params["api_key"] = NCBI_API_KEY
        resp = requests.get(f"{NCBI_BASE}/elink.fcgi", params=params, timeout=10)
        data = resp.json()
        links = data.get("linksets", [{}])[0].get("linksetdbs", [])
        for lb in links:
            if lb.get("linkname") == "pubmed_pmc_refs":
                return len(lb.get("links", []))
    except Exception:
        pass
    return 0


# ── main function ─────────────────────────────────────────────────────────

def scrape_pubmed(url: str) -> dict:
    """
    Scrape a PubMed article by URL or PMID.

    Parameters
    ----------
    url : str  – PubMed article URL (or plain PMID string).

    Returns
    -------
    dict following the assignment JSON schema.
    """
    print(f"  Scraping PubMed: {url}")
    try:
        pmid = extract_pmid(url)
    except ValueError as e:
        return _empty_record(url, str(e))

    try:
        root = fetch_pubmed_xml(pmid)
    except Exception as e:
        return _empty_record(url, f"eFetch failed: {e}")

    article = root.find(".//PubmedArticle")
    if article is None:
        return _empty_record(url, "No PubmedArticle element found in XML")

    # ── Extract fields ─────────────────────────────────────────────────
    title = _get_text(article, ".//ArticleTitle")
    journal = _get_text(article, ".//Journal/Title")
    abstract = parse_abstract(article)
    authors = parse_authors(article)

    # Published year
    year = _get_text(article, ".//PubDate/Year")
    month = _get_text(article, ".//PubDate/Month", "01")
    day = _get_text(article, ".//PubDate/Day", "01")
    published_date = f"{year}-{month}-{day}" if year != "Unknown" else "Unknown"

    # MeSH keywords
    mesh_terms = [
        m.text for m in article.findall(".//MeshHeading/DescriptorName")
        if m.text
    ]

    # Combine text for tagging / chunking
    full_text = f"{title}\n{abstract}"
    topic_tags = list(set(auto_tag(full_text) + mesh_terms[:5]))
    chunks = chunk_text(full_text)

    # Citation count via eLink
    citation_count = fetch_citation_count(pmid)

    # Trust score
    trust = calculate_trust_score(
        source_type="pubmed",
        author=authors[0] if authors else "Unknown",
        domain="pubmed.ncbi.nlm.nih.gov",
        published_date=published_date,
        content=full_text,
        citation_count=citation_count,
        has_medical_disclaimer=True,   # PubMed is peer-reviewed; treat as having disclaimer
        multiple_authors=(len(authors) > 1),
    )

    return {
        "source_url": url if url.startswith("http") else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        "source_type": "pubmed",
        "pmid": pmid,
        "title": title,
        "author": authors,           # List for multi-author papers
        "journal": journal,
        "published_date": published_date,
        "language": "en",            # PubMed abstracts are English by default
        "region": "Global",
        "topic_tags": topic_tags,
        "trust_score": round(trust, 3),
        "citation_count": citation_count,
        "abstract": abstract,
        "mesh_terms": mesh_terms,
        "content_chunks": chunks,
    }


def _empty_record(url, error=""):
    return {
        "source_url": url,
        "source_type": "pubmed",
        "title": "Unknown",
        "author": ["Unknown"],
        "published_date": "Unknown",
        "language": "en",
        "region": "Unknown",
        "topic_tags": [],
        "trust_score": 0.0,
        "content_chunks": [],
        "error": error,
    }


# ── entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    # A well-cited AI/healthcare paper as the sample
    PUBMED_URLS = [
        "https://pubmed.ncbi.nlm.nih.gov/30617339/",  # AI in clinical medicine
    ]

    results = [scrape_pubmed(u) for u in PUBMED_URLS]
    os.makedirs("output/scraped_data", exist_ok=True)
    out_path = "output/scraped_data/pubmed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(results)} PubMed records → {out_path}")
