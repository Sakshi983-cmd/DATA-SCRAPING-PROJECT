<div align="center">

<!-- Animated Header -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=180&section=header&text=Multi-Source%20Web%20Scraper%20%F0%9F%95%B7%EF%B8%8F&fontSize=38&fontColor=fff&animation=twinkling&fontAlignY=32&desc=Data%20Scraping%20%7C%20Trust%20Scoring%20%7C%20AI%20Pipeline&descAlignY=55&descSize=18"/>

<!-- Typing Animation -->
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&pause=1000&color=7C3AED&center=true&vCenter=true&width=700&lines=Scraping+Blogs+%7C+YouTube+%7C+PubMed+%F0%9F%94%8D;Auto+Topic+Tagging+with+TF-IDF+%F0%9F%8F%B7%EF%B8%8F;Trust+Score+Algorithm+%280.0+%E2%86%92+1.0%29+%F0%9F%A7%A0;Built+by+Sakshi+Tiwari+%F0%9F%9A%80" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Scraping-4CAF50?style=for-the-badge)
![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![YouTube](https://img.shields.io/badge/YouTube-API%20v3-FF0000?style=for-the-badge&logo=youtube&logoColor=white)
![PubMed](https://img.shields.io/badge/NCBI-PubMed-326599?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-✅%20Complete-brightgreen?style=for-the-badge)

</div>

---

## 👩‍💻 Hi, I'm Sakshi!

<img align="right" width="260" src="https://media.giphy.com/media/L1R1tvI9svkIWwpVYr/giphy.gif"/>

```python
class Sakshi:
    name      = "Sakshi Tiwari"
    role      = "Junior AI Engineer Intern"
    location  = "India 🇮🇳"

    built     = "Multi-Source Scraper"
    sources   = ["Blogs", "YouTube", "PubMed"]
    skills    = ["Web Scraping", "NLP",
                 "Trust Scoring", "Python"]

    fun_fact  = "I let AI help me build AI tools 🤖"

    def say_hi(self):
        return "Let's scrape the internet! 🕷️"
```

<br clear="right"/>

---

## 🖥️ Live Pipeline Output

> Real run — `python main.py` — data scraped from live internet:

![Pipeline Output](assets/Screenshot%202026-04-09%20200030.png)

---

## 🌈 How It Works — Colorful Flow

```
  ╔══════════════════════════════════════════════════════════╗
  ║  🟣  python main.py  — Entry Point                      ║
  ╚══════════════════════╦═══════════════════════════════════╝
                         ║
       ┌─────────────────┼──────────────────┐
       │                 │                  │
       ▼                 ▼                  ▼
╔════════════╗    ╔════════════╗    ╔════════════╗
║ 🔵  BLOG  ║    ║ 🔴  YouTube║    ║ 🟢  PubMed ║
║────────────║    ║────────────║    ║────────────║
║ requests   ║    ║ YT API v3  ║    ║ NCBI API   ║
║ +BS4       ║    ║ +Transcript║    ║ Free XML   ║
║────────────║    ║────────────║    ║────────────║
║ → Title    ║    ║ → Channel  ║    ║ → Title    ║
║ → Author   ║    ║ → Date     ║    ║ → Authors  ║
║ → Date     ║    ║ → Captions ║    ║ → Abstract ║
║ → Content  ║    ║ → Views 👁️ ║    ║ → Citations║
╚═════╦══════╝    ╚═════╦══════╝    ╚═════╦══════╝
      └─────────────────┼──────────────────┘
                        ▼
        ╔═══════════════════════════════╗
        ║  🟡  UTILS — Processing       ║
        ║                               ║
        ║  🏷️  tagging.py               ║
        ║  ├─ Taxonomy Match (13 tags)  ║
        ║  └─ TF-IDF Keywords           ║
        ║     → ["AI","Healthcare"...]  ║
        ║                               ║
        ║  ✂️  chunking.py              ║
        ║  └─ Para → Sentence → Split   ║
        ║     + Overlap between chunks  ║
        ╚═══════════════╦═══════════════╝
                        ▼
        ╔═══════════════════════════════╗
        ║  🟣  TRUST SCORE ENGINE       ║
        ║                               ║
        ║  Score =                      ║
        ║   🔵 w1 × author_credibility  ║
        ║   🔴 w2 × citation_score      ║
        ║   🟢 w3 × domain_authority    ║
        ║   🟡 w4 × recency_score       ║
        ║   🟠 w5 × disclaimer_score    ║
        ║        × 🛡️ abuse_penalty     ║
        ║                               ║
        ║  0.0 ━━━━━━━━━━━━━━━━━ 1.0   ║
        ║  ❌ Spam          ✅ Trusted  ║
        ╚═══════════════╦═══════════════╝
                        ▼
        ╔═══════════════════════════════╗
        ║  💾  OUTPUT — Structured JSON ║
        ║                               ║
        ║  output/scraped_data.json     ║
        ║  output/scraped_data/         ║
        ║   🔵 blogs.json    → 3 posts  ║
        ║   🔴 youtube.json  → 2 videos ║
        ║   🟢 pubmed.json   → 1 paper  ║
        ╚═══════════════════════════════╝
```

---

## 📁 Project Structure

```
DATA-SCRAPING-PROJECT/
│
├── 📄 main.py                    ← 🟣 Run this!
├── 📘 README.md
├── 📝 report.md
│
├── 🔵 scraper/
│   ├── blog_scraper.py           ← requests + BeautifulSoup
│   ├── youtube_scraper.py        ← YouTube API + Transcripts
│   └── pubmed_scraper.py         ← NCBI E-utilities (free)
│
├── 🟣 scoring/
│   └── trust_score.py            ← Trust algorithm (0→1)
│
├── 🟡 utils/
│   ├── tagging.py                ← TF-IDF auto tagging
│   └── chunking.py               ← Overlap chunker
│
├── 🖼️ assets/
│   └── Screenshot 2026-04-09 200030.png
│
└── 📊 output/
    ├── scraped_data.json
    └── scraped_data/
        ├── blogs.json
        ├── youtube.json
        └── pubmed.json
```

---

## ⚙️ Quick Start

```bash
# 1️⃣ Clone
git clone https://github.com/Sakshi983-cmd/DATA-SCRAPING-PROJECT.git
cd DATA-SCRAPING-PROJECT

# 2️⃣ Install
pip install requests beautifulsoup4 scikit-learn langdetect youtube-transcript-api lxml

# 3️⃣ Run
python main.py
```

---

## 🧠 Trust Score Weights

| Component | 🔵 Blog | 🔴 YouTube | 🟢 PubMed |
|:---|:---:|:---:|:---:|
| 👤 Author Credibility | 0.25 | 0.25 | 0.20 |
| 📚 Citation Score | 0.15 | 0.05 | **0.30** |
| 🌐 Domain Authority | **0.30** | **0.30** | 0.20 |
| 🕐 Recency | 0.20 | **0.25** | 0.15 |
| ⚕️ Disclaimer | 0.10 | 0.15 | 0.15 |

### 📊 Scores From This Run

| Source | Type | Trust Score |
|:---|:---:|:---:|
| Beautiful Soup Guide — RealPython | 🔵 Blog | `0.630` ⭐ |
| Web Scraping Crash Course | 🔴 YouTube | `0.329` |
| High-performance Medicine — Nature | 🟢 PubMed | `0.612` ⭐ |

---

## 🛡️ Abuse Prevention

| 🚨 Attack | 🔍 Detection | ⚠️ Penalty |
|:---|:---|:---:|
| 👤 Fake Author | Not in credible org list | `0.10` |
| 🔁 Keyword Stuffing | Top word > 5% of text | `× 0.80` |
| 🏥 Medical, No Disclaimer | ≥3 medical keywords | `× 0.65` |
| 🗑️ Spam Domain | blogspot / wix etc. | `× 0.70` |
| 📄 Thin Content | < 100 words | `× 0.75` |
| 🎣 Clickbait | Regex pattern match | `× 0.85` |

---

## ⚠️ Edge Cases Handled

| Scenario | How Handled |
|:---|:---|
| ❓ Missing author | Score → `0.10` |
| 📅 Missing date | Neutral recency `0.40` |
| 👥 Multiple authors | Average + `1.05×` bonus |
| 🔇 No transcript | Title + description only |
| 🌍 Non-English | `langdetect` auto-detects |
| 🚫 Site blocks bot | Graceful skip + warning |
| 📜 Very long article | Para → Sentence → Hard split |

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer&animation=twinkling"/>

**Built with 🖤 by [Sakshi Tiwari](https://github.com/Sakshi983-cmd)**

*AI Internship Assignment — GutBut 2026*

</div>
