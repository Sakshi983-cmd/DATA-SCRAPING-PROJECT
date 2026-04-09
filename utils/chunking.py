"""
Content Chunking Utility
========================
Splits long text into manageable, semantically coherent chunks
for downstream processing (vector search, summarisation, etc.).

Strategy
--------
1. Split by double-newline (paragraphs) first.
2. If a paragraph exceeds max_chunk_size, split by sentence.
3. Optionally add overlapping context between adjacent chunks.
"""

from __future__ import annotations
import re

# ── Defaults ───────────────────────────────────────────────────────────────
DEFAULT_MAX_CHUNK_CHARS = 800   # ~150–200 tokens per chunk
DEFAULT_OVERLAP_CHARS   = 100   # overlap between consecutive chunks


def _split_sentences(text: str) -> list[str]:
    """Naïve sentence splitter using punctuation boundaries."""
    # Split on '. ', '! ', '? ', but keep the delimiter
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s.strip()]


def _merge_short_chunks(chunks: list[str], min_length: int = 80) -> list[str]:
    """
    Merge chunks that are too short into the previous one to avoid
    fragmented outputs.
    """
    merged = []
    for chunk in chunks:
        if merged and len(chunk) < min_length:
            merged[-1] = merged[-1].rstrip() + " " + chunk.strip()
        else:
            merged.append(chunk)
    return merged


def chunk_text(
    text: str,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
    min_chunk_chars: int = 80,
) -> list[str]:
    """
    Split text into overlapping chunks suitable for NLP processing.

    Parameters
    ----------
    text            : Input text to chunk.
    max_chunk_chars : Maximum character length per chunk.
    overlap_chars   : Characters of overlap between adjacent chunks.
    min_chunk_chars : Minimum chars; shorter chunks are merged with previous.

    Returns
    -------
    List of non-empty string chunks.

    Edge Cases Handled
    ------------------
    - Empty / whitespace-only text → returns []
    - Single paragraph shorter than max_chunk_chars → returns [text]
    - Very long single paragraph (no newlines) → sentence-splits it
    - Non-English text → same logic applies (sentence boundary heuristic)
    """
    if not text or not text.strip():
        return []

    # ── Step 1: paragraph-level split ─────────────────────────────────
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    raw_chunks: list[str] = []

    for para in paragraphs:
        if len(para) <= max_chunk_chars:
            raw_chunks.append(para)
        else:
            # ── Step 2: sentence-level split for long paragraphs ──────
            sentences = _split_sentences(para)
            current = ""
            for sent in sentences:
                if len(current) + len(sent) + 1 <= max_chunk_chars:
                    current = (current + " " + sent).strip()
                else:
                    if current:
                        raw_chunks.append(current)
                    # If a single sentence itself exceeds the limit, hard-split
                    if len(sent) > max_chunk_chars:
                        for i in range(0, len(sent), max_chunk_chars):
                            raw_chunks.append(sent[i:i + max_chunk_chars])
                        current = ""
                    else:
                        current = sent
            if current:
                raw_chunks.append(current)

    # ── Step 3: add overlap between consecutive chunks ─────────────────
    if overlap_chars > 0 and len(raw_chunks) > 1:
        overlapped = [raw_chunks[0]]
        for i in range(1, len(raw_chunks)):
            tail = raw_chunks[i - 1][-overlap_chars:]
            overlapped.append(tail + " " + raw_chunks[i])
        raw_chunks = overlapped

    # ── Step 4: merge tiny trailing chunks ────────────────────────────
    final_chunks = _merge_short_chunks(raw_chunks, min_chunk_chars)

    return [c.strip() for c in final_chunks if c.strip()]


# ── CLI demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    Web scraping is the process of automatically extracting information from websites.
    It is used extensively in data science, competitive intelligence, and research.

    Python is the most popular language for web scraping thanks to libraries such as
    BeautifulSoup, Scrapy, and Playwright. BeautifulSoup parses HTML documents and
    allows developers to navigate the parse tree with simple Pythonic idioms.

    Scrapy is a full-featured scraping framework with support for crawling, item
    pipelines, and middleware. It is suitable for large-scale projects. Playwright
    supports dynamic JavaScript-rendered pages, making it ideal for modern SPAs.

    Trust scoring of scraped content is equally important. A trust score system
    evaluates author credibility, domain authority, recency, citation count, and
    the presence of medical disclaimers. This helps downstream applications filter
    unreliable sources and prioritise high-quality information.
    """

    chunks = chunk_text(sample, max_chunk_chars=300, overlap_chars=50)
    for i, c in enumerate(chunks, 1):
        print(f"\n── Chunk {i} ({len(c)} chars) ──")
        print(c)
