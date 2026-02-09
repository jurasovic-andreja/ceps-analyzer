# CEPS Website Analyzer

AI-powered website analysis that scores pages across four dimensions: **Content · Experience · Performance · Security**.

Built with Streamlit + Google Gemini 2.5 Flash.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Gemini API key
cp .env.example .env
# Edit .env and set GEMINI_API_KEY

# 3. Run
streamlit run app.py
```

The app opens at `http://localhost:8501`. Enter a URL in the sidebar and click **Analyze**.

## How It Works

1. **Scraper** fetches the page HTML (with timeout & size limits)
2. **Parser** extracts text, images, links, headings, meta tags, and trust signals
3. **5 AI agents** run in parallel via `ThreadPoolExecutor`, each calling Gemini 2.5 Flash:
   - **Text Agent** — content quality, readability, grammar
   - **Visual Agent** — image analysis via Gemini Vision + alt-text audit
   - **UX Agent** — heading hierarchy, navigation, mobile signals
   - **Trust Agent** — SSL, privacy policy, contact info, social proof
   - **Tech Agent** — load time, SEO, structured data, resource count
4. **Scoring Engine** computes a weighted CEPS score (0–100) with a letter grade
5. **UI** renders a radar chart, score metrics, and expandable findings

## Project Structure

```
├── app.py                     # Entry point — streamlit run app.py
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
│
├── core/
│   ├── config.py              # Settings from .env
│   ├── models.py              # PageData, AgentResult, CEPSResult
│   └── scoring.py             # Weighted CEPS aggregation
│
├── services/
│   ├── scraper.py             # requests-based web scraper
│   ├── parser.py              # BeautifulSoup HTML parser
│   └── llm_router.py          # Gemini text + vision wrapper with token tracking
│
├── agents/
│   ├── text_agent.py          # Content quality analysis
│   ├── visual_agent.py        # Image & visual design analysis
│   ├── ux_agent.py            # Structure & UX analysis
│   ├── trust_agent.py         # Trust & credibility analysis
│   └── tech_agent.py          # Technical health & SEO analysis
│
└── ui/
    └── components/
        ├── header.py          # App title & styling
        ├── results.py         # Expandable agent findings
        └── charts.py          # Radar chart & score metrics
```

## Configuration

All settings are in `.env` (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | *(required)* | Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey)) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `MAX_IMAGES` | `3` | Max images sent to vision model per page |
| `MAX_TEXT_CHARS` | *(no limit)* | Truncate extracted text (set to e.g. `8000` to cap) |
| `SCRAPER_TIMEOUT` | `15` | Page fetch timeout in seconds |
| `MAX_PAGE_SIZE` | `5242880` | Max page size in bytes (5 MB) |

## Terminal Debugging

All pipeline steps, agent progress, and **token usage** are printed to the terminal where Streamlit is running:

```
============================================================
[CEPS] Starting analysis for: https://example.com
============================================================
[LLMRouter] Initialized with model: gemini-2.5-flash
[Scraper] Fetching https://example.com…
[Scraper] ✓ Done in 0.43s — status=200, size=12840 bytes
[Parser] ✓ Done in 0.01s
[Agents] Launching 5 agents in parallel…
[LLMRouter] Call #1 (text-agent)  prompt=482  completion=95  total_tokens=577
...
────────────────────────────────────────────────────────────
  Overall Score : 72.3/100  (Grade B)
  LLM Calls     : 7
  Total Tokens  : 3920
  Total Time    : 8.42s
============================================================
```

## CEPS Scoring Weights

| Dimension | Agent | Weight |
|-----------|-------|--------|
| **C**ontent | Text Agent | 25% |
| **E**xperience | UX Agent | 25% |
| **P**erformance | Tech Agent | 15% |
| **S**ecurity | Trust Agent | 20% |
| Visual | Visual Agent | 15% |

## Tech Stack

- **Frontend**: Streamlit
- **AI/LLM**: Google Gemini 2.5 Flash (text + vision)
- **Scraping**: requests + BeautifulSoup + lxml
- **Charts**: Plotly
- **Config**: python-dotenv
