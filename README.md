<div align="center">

# 🕷️ Multi-Source Web Scraper & Trust Scoring System

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=6C63FF&center=true&vCenter=true&width=600&lines=Web+Scraping+%2B+Trust+Scoring+Pipeline;Blogs+%7C+YouTube+%7C+PubMed;Built+with+Python+%F0%9F%90%8D" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Scraping-4CAF50?style=for-the-badge)
![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Status](https://img.shields.io/badge/Status-✅%20Complete-brightgreen?style=for-the-badge)

<br/>

> 🤖 **An AI-powered pipeline that automatically scrapes the internet, understands content, and judges how trustworthy each source is — all in one command.**

</div>

---

## 🖥️ Pipeline Output

> Real output from running `python main.py` on live internet data:

![Pipeline Output](assets/Screenshot%202026-04-09%20200030.png)

---

## 🔄 How It Works — Full Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        python main.py                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │  📰  BLOGS   │    │  📺 YOUTUBE  │    │  🔬 PUBMED   │
  │              │    │              │    │              │
  │  requests +  │    │  YT API v3   │    │  NCBI API    │
  │BeautifulSoup │    │  +Transcript │    │  (Free XML)  │
  │              │    │              │    │              │
  │ → Title      │    │ → Channel    │    │ → Title      │
  │ → Author     │    │ → Date       │    │ → Authors    │
  │ → Date       │    │ → Transcript │    │ → Abstract   │
  │ → Content    │    │ → Views/Likes│    │ → Citations  │
  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
          ┌──────────────────────────────────┐
          │           🛠️ UTILS               │
          │                                  │
          │  tagging.py                      │
          │  ┌────────────────────────────┐  │
          │  │ TF-IDF + Taxonomy Matching │  │
          │  │ → ["AI", "Healthcare",     │  │
          │  │    "Web Scraping", ...]    │  │
          │  └────────────────────────────┘  │
          │                                  │
          │  chunking.py                     │
          │  ┌────────────────────────────┐  │
          │  │ Split long text into       │  │
          │  │ paragraph-sized chunks     │  │
          │  │ with overlap               │  │
          │  └────────────────────────────┘  │
          └─────────────────┬────────────────┘
                            │
                            ▼
          ┌──────────────────────────────────┐
          │        🧠 TRUST SCORE            │
          │                                  │
          │  Score = w1 × author_credibility │
          │        + w2 × citation_score     │
          │        + w3 × domain_authority   │
          │        + w4 × recency_score      │
          │        + w5 × disclaimer_score   │
          │        × abuse_penalty           │
          │                                  │
          │  Result → 0.0 ──────────── 1.0   │
          │           ❌ Spam      ✅ Trusted │
          └─────────────────┬────────────────┘
                            │
                            ▼
          ┌──────────────────────────────────┐
          │         💾 OUTPUT JSON           │
          │                                  │
          │  output/scraped_data.json        │
          │  output/scraped_data/            │
          │    ├── blogs.json                │
          │    ├── youtube.json              │
          │    └── pubmed.json               │
          └──────────────────────────────────┘
```

---

## 📁 Project Structure

```
DATA-SCRAPING-PROJECT/
│
├── 📄 main.py                 ← Entry point — runs everything
├── 📘 README.md
├── 📝 report.md
│
├── 🕷️ scraper/
│   ├── blog_scraper.py        ← BeautifulSoup + requests
│   ├── youtube_scraper.py     ← YouTube API v3 + Transcripts
│   └── pubmed_scraper.py      ← NCBI E-utilities (free)
│
├── 🧠 scoring/
│   └── trust_score.py         ← Weighted trust algorithm
│
├── 🛠️ utils/
│   ├── tagging.py             ← TF-IDF auto topic tagging
│   └── chunking.py            ← Overlap-aware chunker
│
├── 🖼️ assets/
│   └── Screenshot 2026-04-09 200030.png
│
└── 📊 output/
    ├── scraped_data.json       ← All 6 records
    └── scraped_data/
        ├── blogs.json
        ├── youtube.json
        └── pubmed.json
```

---

## ⚙️ Quick Start

```bash
# 1. Clone
git clone https://github.com/Sakshi983-cmd/DATA-SCRAPING-PROJECT.git
cd DATA-SCRAPING-PROJECT

# 2. Install
pip install requests beautifulsoup4 scikit-learn langdetect youtube-transcript-api lxml

# 3. Run
python main.py
```

---

## 🧠 Trust Score — Deep Dive

### Formula
```
TrustScore = w1×author + w2×citations + w3×domain + w4×recency + w5×disclaimer
           × abuse_penalty_multiplier

Range: 0.0 (Spam) → 1.0 (Highly Trusted)
```

### Weight Table

| Component | 📰 Blog | 📺 YouTube | 🔬 PubMed |
|:---|:---:|:---:|:---:|
| 👤 Author Credibility | 0.25 | 0.25 | 0.20 |
| 📚 Citation Score | 0.15 | 0.05 | **0.30** |
| 🌐 Domain Authority | **0.30** | **0.30** | 0.20 |
| 🕐 Recency | 0.20 | **0.25** | 0.15 |
| ⚕️ Disclaimer | 0.10 | 0.15 | 0.15 |

### Real Scores from This Run

| Source | Type | Trust Score |
|:---|:---:|:---:|
| Beautiful Soup Guide — RealPython | 📰 Blog | `0.630` ⭐ |
| Web Scraping Crash Course | 📺 YouTube | `0.329` |
| High-performance Medicine — Nature | 🔬 PubMed | `0.612` ⭐ |

---

## 🛡️ Abuse Prevention Logic

| 🚨 Attack | 🔍 Detection | ⚠️ Penalty |
|:---|:---|:---:|
| 👤 Fake/Anonymous Author | Not in credible org database | Score → `0.10` |
| 🔁 SEO Keyword Stuffing | Top word freq > 5% of total | `× 0.80` |
| 🏥 Medical, No Disclaimer | ≥3 medical keywords detected | `× 0.65` |
| 🗑️ Spam Domain | blogspot / wix / weebly etc. | `× 0.70` |
| 📄 Thin Content | < 100 words | `× 0.75` |
| 🎣 Clickbait Title | Regex: "you won't believe" etc. | `× 0.85` |

> 🔒 Max combined penalty: **0.50×** — score never drops below half of raw value.

---

## 🏷️ Auto Topic Tagging Example

```python
Input:  "Deep learning model trained on clinical data for cancer detection..."

Output: ["AI", "Deep Learning", "Healthcare", "clinical", "neural network"]
```

**Two-step process:**
1. **Taxonomy Matching** → 13 curated categories (AI, Healthcare, Python, NLP...)
2. **TF-IDF Keywords** → catches domain-specific terms not in taxonomy

---

## 📋 Output JSON Sample

```json
{
  "source_url": "https://pubmed.ncbi.nlm.nih.gov/30617339/",
  "source_type": "pubmed",
  "title": "High-performance medicine: convergence of human and AI",
  "author": ["Eric J. Topol"],
  "published_date": "2019-01-07",
  "language": "en",
  "region": "Global",
  "topic_tags": ["AI", "Healthcare", "Deep Learning"],
  "trust_score": 0.612,
  "citation_count": 9847,
  "content_chunks": [
    "Background: Artificial intelligence holds great promise...",
    "Deep learning algorithms achieved diagnostic accuracy..."
  ]
}
```

---

## 🛠️ Tech Stack

| Library | Use |
|:---|:---|
| `requests` | HTTP calls to websites |
| `beautifulsoup4` | HTML parsing |
| `lxml` | Fast XML parser |
| `scikit-learn` | TF-IDF keyword extraction |
| `langdetect` | Auto language detection |
| `youtube-transcript-api` | YouTube captions |
| NCBI E-utilities | PubMed data (free) |

---

<div align="center">

**Made with 🖤 by Sakshi Tiwari**
*AI Internship Assignment — GutBut 2026*

</div>
