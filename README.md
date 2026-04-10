<div align="center">

<!-- Animated Header -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=180&section=header&text=Multi-Source%20Web%20Scraper%20%F0%9F%95%B7%EF%B8%8F&fontSize=38&fontColor=fff&animation=twinkling&fontAlignY=32&desc=Data%20Scraping%20%7C%20Trust%20Scoring%20%7C%20AI%20Pipeline&descAlignY=55&descSize=18"/>

<!-- Typing Animation -->
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&pause=1000&color=7C3AED&center=true&vCenter=true&width=700&lines=Scraping+Blogs+%7C+YouTube+%7C+PubMed+%F0%9F%94%8D;Auto+Topic+Tagging+with+TF-IDF+%F0%9F%8F%B7%EF%B8%8F;Trust+Score+Algorithm+%280.0+%E2%86%92+1.0%29+%F0%9F%A7%A0;Abuse+Prevention+%7C+Edge+Cases+%7C+JSON+Output+%F0%9F%92%BE" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-HTML%20Parsing-4CAF50?style=for-the-badge)
![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![PubMed](https://img.shields.io/badge/NCBI-PubMed%20API-326599?style=for-the-badge)
![YouTube](https://img.shields.io/badge/YouTube-Data%20API%20v3-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![Status](https://img.shields.io/badge/Status-✅%20Complete-brightgreen?style=for-the-badge)

</div>

---

<!-- About This Project -->
<img align="right" width="280" src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDd2dHZjbzRtNnVyZjFkdzFzMXFrbnR6Mm8ydGZxdzVldGZhMGowNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qgQUggAC3Pfv687qPC/giphy.gif"/>

### 🧠 What This Project Does

```python
class MultiSourceScraper:
    name     = "Data Scraping Pipeline"
    sources  = ["Blogs", "YouTube", "PubMed"]
    
    task_1   = "Scrape + Structure Data → JSON"
    task_2   = "Calculate Trust Score (0→1)"
    
    tools    = ["BeautifulSoup", "NCBI API",
                "YouTube API", "TF-IDF"]
    
    output   = "scraped_data.json"
    records  = 6   # 3 blogs + 2 YT + 1 PubMed
    
    def run(self):
        return "python main.py 🚀"
```

<br clear="right"/>

---

## 🖥️ Pipeline Output — Real Run

> `python main.py` — live internet data scraped successfully:

![Pipeline Output](assets/Screenshot%202026-04-09%20200030.png)

---

## 🔄 Full Pipeline — How It Works

```
╔══════════════════════════════════════════════════════════════╗
║                    python main.py  🚀                        ║
╚══════════════════════════╦═══════════════════════════════════╝
                           ║
          ╔════════════════╬════════════════╗
          ║                ║                ║
          ▼                ▼                ▼
  ╔══════════════╗ ╔══════════════╗ ╔══════════════╗
  ║ 📰  BLOGS   ║ ║ 📺 YOUTUBE  ║ ║ 🔬  PUBMED  ║
  ║─────────────║ ║─────────────║ ║─────────────║
  ║ requests    ║ ║ YT API v3   ║ ║ NCBI eFetch ║
  ║ +BS4        ║ ║ +Transcript ║ ║ (Free XML)  ║
  ║─────────────║ ║─────────────║ ║─────────────║
  ║ → Title     ║ ║ → Channel   ║ ║ → Title     ║
  ║ → Author    ║ ║ → Date      ║ ║ → Authors   ║
  ║ → Date      ║ ║ → Transcript║ ║ → Abstract  ║
  ║ → Content   ║ ║ → Views     ║ ║ → Citations ║
  ╚══════╦═══════╝ ╚══════╦══════╝ ╚══════╦══════╝
         ║                ║               ║
         ╚════════════════╬═══════════════╝
                          ║
                          ▼
          ╔═══════════════════════════════╗
          ║         🛠️  UTILS             ║
          ║                               ║
          ║  📌 tagging.py                ║
          ║  ┌─────────────────────────┐  ║
          ║  │ Step 1: Taxonomy Match  │  ║
          ║  │ → "AI", "Healthcare".. │  ║
          ║  │ Step 2: TF-IDF Keywords │  ║
          ║  │ → domain-specific terms │  ║
          ║  └─────────────────────────┘  ║
          ║                               ║
          ║  ✂️  chunking.py              ║
          ║  ┌─────────────────────────┐  ║
          ║  │ Para → Sentence → Split │  ║
          ║  │ + Overlap between chunks│  ║
          ║  └─────────────────────────┘  ║
          ╚═══════════════╦═══════════════╝
                          ║
                          ▼
          ╔═══════════════════════════════╗
          ║      🧠  TRUST SCORE          ║
          ║                               ║
          ║  Score = w1 × author          ║
          ║        + w2 × citations       ║
          ║        + w3 × domain          ║
          ║        + w4 × recency         ║
          ║        + w5 × disclaimer      ║
          ║        × abuse_penalty        ║
          ║                               ║
          ║   0.0 ━━━━━━━━━━━━━━━━ 1.0   ║
          ║   ❌ Spam        ✅ Trusted   ║
          ╚═══════════════╦═══════════════╝
                          ║
                          ▼
          ╔═══════════════════════════════╗
          ║       💾  OUTPUT JSON         ║
          ║                               ║
          ║  output/scraped_data.json     ║
          ║  output/scraped_data/         ║
          ║    ├── blogs.json    (3)      ║
          ║    ├── youtube.json  (2)      ║
          ║    └── pubmed.json   (1)      ║
          ╚═══════════════════════════════╝
```

---

## 📁 Project Structure

```
DATA-SCRAPING-PROJECT/
│
├── 📄 main.py                    ← Run this — orchestrates all
├── 📘 README.md
├── 📝 report.md
│
├── 🕷️ scraper/
│   ├── blog_scraper.py           ← requests + BeautifulSoup
│   ├── youtube_scraper.py        ← YouTube API v3 + Transcripts
│   └── pubmed_scraper.py         ← NCBI E-utilities (free)
│
├── 🧠 scoring/
│   └── trust_score.py            ← Weighted trust algorithm
│
├── 🛠️ utils/
│   ├── tagging.py                ← TF-IDF auto topic tagging
│   └── chunking.py               ← Overlap-aware chunker
│
├── 🖼️ assets/
│   └── Screenshot 2026-04-09 200030.png  ← Pipeline output
│
└── 📊 output/
    ├── scraped_data.json          ← All 6 records combined
    └── scraped_data/
        ├── blogs.json
        ├── youtube.json
        └── pubmed.json
```

---

## ⚙️ Quick Start

```bash
# Step 1 — Clone
git clone https://github.com/Sakshi983-cmd/DATA-SCRAPING-PROJECT.git
cd DATA-SCRAPING-PROJECT

# Step 2 — Install libraries
pip install requests beautifulsoup4 scikit-learn langdetect youtube-transcript-api lxml

# Step 3 — Run pipeline
python main.py
```

---

## 🧠 Trust Score — Weight Table

| Component | 📰 Blog | 📺 YouTube | 🔬 PubMed |
|:---|:---:|:---:|:---:|
| 👤 Author Credibility | 0.25 | 0.25 | 0.20 |
| 📚 Citation Score | 0.15 | 0.05 | **0.30** |
| 🌐 Domain Authority | **0.30** | **0.30** | 0.20 |
| 🕐 Recency | 0.20 | **0.25** | 0.15 |
| ⚕️ Medical Disclaimer | 0.10 | 0.15 | 0.15 |

### Results From This Run

| Source | Type | Score |
|:---|:---:|:---:|
| Beautiful Soup Guide — RealPython | 📰 Blog | `0.630` ⭐ |
| Web Scraping Crash Course — YouTube | 📺 YouTube | `0.329` |
| High-performance Medicine — Nature | 🔬 PubMed | `0.612` ⭐ |

---

## 🛡️ Abuse Prevention

| 🚨 Attack | 🔍 How Detected | ⚠️ Penalty |
|:---|:---|:---:|
| 👤 Fake Author | Not in credible org database | Score → `0.10` |
| 🔁 Keyword Stuffing | Top word freq > 5% of text | `× 0.80` |
| 🏥 Medical, No Disclaimer | ≥3 medical keywords found | `× 0.65` |
| 🗑️ Spam Domain | blogspot / wix / weebly | `× 0.70` |
| 📄 Thin Content | Less than 100 words | `× 0.75` |
| 🎣 Clickbait Title | Regex pattern match | `× 0.85` |

---

## ⚠️ Edge Cases Handled

| Scenario | Solution |
|:---|:---|
| Missing author | "Unknown" → credibility `0.10` |
| Missing publish date | Neutral recency score `0.40` |
| Multiple authors | Average score + `1.05×` consensus bonus |
| Transcript unavailable | Uses title + description only |
| Non-English content | `langdetect` auto-detects language |
| Website blocks scraper | Graceful error + skips with warning |
| Very long articles | Para → Sentence → Hard split |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|:---|:---|
| `requests` | HTTP requests to websites |
| `beautifulsoup4` | HTML parsing |
| `lxml` | Fast XML/HTML parser |
| `scikit-learn` | TF-IDF vectorization |
| `langdetect` | Language detection |
| `youtube-transcript-api` | YouTube captions |
| NCBI E-utilities | PubMed data (free, no key needed) |
| YouTube Data API v3 | Video metadata |

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer&animation=twinkling"/>

**Built with 🖤 by Sakshi Tiwari**

*AI Internship Assignment — GutBut 2026*

</div>
