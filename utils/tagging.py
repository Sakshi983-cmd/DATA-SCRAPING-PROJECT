"""
Topic Auto-Tagging Utility
==========================
Extracts meaningful topic tags from text using:
1. TF-IDF keyword extraction (scikit-learn)
2. Domain keyword matching against a curated taxonomy

Falls back gracefully if sklearn is not installed.
"""

from __future__ import annotations
import re
from collections import Counter

# ── Domain taxonomy ────────────────────────────────────────────────────────
# Maps canonical tag → list of trigger words / phrases
TAXONOMY: dict[str, list[str]] = {
    "AI": ["artificial intelligence", "ai model", "neural network", "deep learning",
           "machine learning", "llm", "large language model", "transformer",
           "gpt", "bert", "natural language processing", "nlp", "computer vision"],
    "Machine Learning": ["machine learning", "supervised learning", "unsupervised",
                         "random forest", "gradient boosting", "xgboost", "sklearn",
                         "classification", "regression", "clustering", "feature engineering"],
    "Deep Learning": ["deep learning", "convolutional", "cnn", "rnn", "lstm",
                      "attention mechanism", "backpropagation", "pytorch", "tensorflow",
                      "keras", "neural network"],
    "Data Science": ["data science", "data analysis", "exploratory data analysis",
                     "eda", "pandas", "numpy", "matplotlib", "seaborn", "jupyter"],
    "Data Engineering": ["data pipeline", "etl", "data scraping", "web scraping",
                         "data ingestion", "data warehouse", "spark", "kafka", "airflow"],
    "Healthcare": ["healthcare", "medical", "clinical", "patient", "diagnosis",
                   "treatment", "hospital", "disease", "symptom", "therapy",
                   "pharmaceutical", "biomedical"],
    "Python": ["python", "django", "flask", "fastapi", "pip", "virtualenv",
               "requests library", "beautifulsoup", "scrapy"],
    "Web Scraping": ["web scraping", "scraper", "beautiful soup", "selenium",
                     "playwright", "scrapy", "html parsing", "xpath", "css selector"],
    "NLP": ["natural language", "text classification", "sentiment analysis",
            "named entity", "tokenization", "word embedding", "word2vec",
            "text mining", "topic modeling", "lda"],
    "Research": ["study", "research", "journal", "publication", "peer-reviewed",
                 "meta-analysis", "systematic review", "clinical trial", "abstract"],
    "Cybersecurity": ["security", "vulnerability", "malware", "encryption",
                      "firewall", "phishing", "cyber attack", "penetration testing"],
    "Cloud": ["aws", "azure", "google cloud", "gcp", "kubernetes", "docker",
              "microservices", "serverless", "devops", "ci/cd"],
    "Statistics": ["statistics", "probability", "bayesian", "hypothesis testing",
                   "p-value", "confidence interval", "variance", "standard deviation"],
    "Ethics / Bias": ["bias", "fairness", "ethics", "responsible ai",
                      "algorithmic fairness", "explainability", "transparency"],
}

# Stop words to remove before TF-IDF
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "up", "about", "into", "through",
    "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "must", "can", "it", "its", "this", "that", "these",
    "those", "i", "we", "you", "he", "she", "they", "not", "no", "nor",
    "so", "yet", "both", "either", "neither", "also", "more", "most",
    "other", "such", "only", "same", "than", "then", "when", "where",
    "who", "which", "how", "what", "all", "each", "every", "any",
    "their", "our", "your", "his", "her", "my", "there", "here",
}


# ── TF-IDF based extractor ────────────────────────────────────────────────

def tfidf_keywords(text: str, top_n: int = 10) -> list[str]:
    """
    Extract top-N keywords using a simple term-frequency approach
    (no external library required).
    Falls back to plain word frequency if sklearn is unavailable.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np

        # We create a tiny 'corpus' from sliding paragraphs to get IDF signal
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", text) if len(s.strip()) > 20]
        if len(sentences) < 2:
            sentences = [text]

        vec = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=200,
            min_df=1,
        )
        X = vec.fit_transform(sentences)
        # Sum TF-IDF scores across all sentences for each term
        scores = np.asarray(X.sum(axis=0)).flatten()
        terms = vec.get_feature_names_out()
        top_indices = scores.argsort()[::-1][:top_n]
        return [terms[i] for i in top_indices]

    except ImportError:
        # Simple frequency fallback
        words = re.findall(r"\b[a-zA-Z][a-zA-Z_-]{3,}\b", text)
        words = [w.lower() for w in words if w.lower() not in STOP_WORDS]
        return [w for w, _ in Counter(words).most_common(top_n)]


# ── Taxonomy matcher ──────────────────────────────────────────────────────

def taxonomy_tags(text: str) -> list[str]:
    """Return canonical tags whose trigger words appear in the text."""
    text_lower = text.lower()
    matched = []
    for tag, triggers in TAXONOMY.items():
        if any(trigger in text_lower for trigger in triggers):
            matched.append(tag)
    return matched


# ── Public API ────────────────────────────────────────────────────────────

def auto_tag(text: str, max_tags: int = 8) -> list[str]:
    """
    Combine taxonomy matching with TF-IDF keyword extraction.

    Strategy
    --------
    1. Taxonomy tags  → high-confidence, human-readable labels
    2. TF-IDF keywords → catch domain-specific terms not in taxonomy
    3. Deduplicate & cap at max_tags

    Parameters
    ----------
    text     : Full article / description text
    max_tags : Maximum number of tags to return

    Returns
    -------
    List of tag strings, e.g. ["AI", "Healthcare", "deep learning"]
    """
    if not text or not text.strip():
        return ["Uncategorized"]

    # Step 1: taxonomy (high-precision, low recall)
    tags = taxonomy_tags(text)

    # Step 2: TF-IDF keywords (broader coverage)
    kw = tfidf_keywords(text, top_n=15)
    # Filter stop words and very short terms
    kw_clean = [k for k in kw if k not in STOP_WORDS and len(k) > 3]

    # Merge: taxonomy first, then TF-IDF fill-up
    combined = list(dict.fromkeys(tags + kw_clean))   # preserves order, deduplicates
    return combined[:max_tags] if combined else ["Uncategorized"]


# ── CLI demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    This article explores how deep learning and neural networks are being applied in
    clinical diagnosis. Researchers at Harvard Medical School have developed a new
    convolutional neural network (CNN) that can detect early-stage cancer from MRI scans
    with 94% accuracy. The model was trained on 50,000 patient records and validated
    through a peer-reviewed clinical trial. Always consult a physician before making
    any medical decisions.
    """
    print("Tags:", auto_tag(sample))
