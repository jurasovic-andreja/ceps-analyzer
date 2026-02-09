"""
CEPS Website Analyzer — Streamlit entry-point.

Run with:
    streamlit run app.py
"""

import time
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.config import GEMINI_API_KEY
from services.scraper import scrape_url
from services.parser import parse_html
from services.llm_router import LLMRouter
from agents import text_agent, visual_agent, ux_agent, trust_agent, tech_agent
from core.scoring import calculate_ceps_score
from ui.components.header import render_header
from ui.components.results import render_results
from ui.components.charts import render_charts


def _run_analysis(url: str):
    """Orchestrate the full scrape → parse → agents → score pipeline."""
    pipeline_start = time.time()

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env file")

    print("\n" + "=" * 60)
    print(f"[CEPS] Starting analysis for: {url}")
    print("=" * 60)

    llm = LLMRouter(GEMINI_API_KEY)

    # Step 1 — Scrape
    print(f"\n[Scraper] Fetching {url}…")
    progress = st.progress(0, text="🌐 Fetching page…")
    scrape_start = time.time()
    html, final_url, load_time, status_code = scrape_url(url)
    print(f"[Scraper] ✓ Done in {time.time() - scrape_start:.2f}s — "
          f"status={status_code}, size={len(html)} bytes, load_time={load_time}s")
    progress.progress(15, text="📄 Parsing HTML…")

    # Step 2 — Parse
    print(f"\n[Parser] Extracting structured data…")
    parse_start = time.time()
    page_data = parse_html(html, final_url, load_time)
    page_data.status_code = status_code
    print(f"[Parser] ✓ Done in {time.time() - parse_start:.2f}s")
    print(f"[Parser]   title        = {page_data.title[:80]!r}")
    print(f"[Parser]   text_length  = {len(page_data.text_content)} chars")
    print(f"[Parser]   images       = {len(page_data.image_urls)}")
    print(f"[Parser]   int_links    = {len(page_data.internal_links)}")
    print(f"[Parser]   ext_links    = {len(page_data.external_links)}")
    print(f"[Parser]   ssl={page_data.has_ssl}  viewport={page_data.has_viewport_meta}  "
          f"lang={page_data.has_lang_attr}  structured_data={page_data.has_structured_data}")
    progress.progress(25, text="🤖 Running AI agents in parallel…")

    # Step 3 — Run agents (max 2 concurrent to avoid rate-limit bursts)
    print(f"\n[Agents] Launching 5 agents (max 2 concurrent to respect rate limits)…")
    agents_start = time.time()
    agent_map = {
        "text": text_agent,
        "visual": visual_agent,
        "ux": ux_agent,
        "trust": trust_agent,
        "tech": tech_agent,
    }
    results: dict = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(mod.analyze, page_data, llm): key
            for key, mod in agent_map.items()
        }
        done_count = 0
        for future in as_completed(futures):
            key = futures[future]
            results[key] = future.result()
            done_count += 1
            pct = 25 + int(done_count / len(futures) * 60)
            progress.progress(pct, text=f"✅ {results[key].agent_name} done")

    print(f"[Agents] ✓ All 5 agents finished in {time.time() - agents_start:.2f}s")
    fallback_agents = [k for k, v in results.items() if "rule-based" in v.summary.lower()]
    if fallback_agents:
        print(f"[Agents] ⚠️  Fallback used for: {', '.join(fallback_agents)}")

    # Step 4 — Score
    progress.progress(90, text="📊 Calculating CEPS score…")
    overall, grade = calculate_ceps_score(
        results["text"],
        results["visual"],
        results["ux"],
        results["trust"],
        results["tech"],
    )
    progress.progress(100, text="✅ Analysis complete!")

    # ── Final summary in terminal ───────────────────────────────────
    usage = llm.get_usage_summary()
    total_time = round(time.time() - pipeline_start, 2)

    print("\n" + "─" * 60)
    print(f"[CEPS] RESULTS for {final_url}")
    print(f"─" * 60)
    print(f"  Overall Score : {overall}/100  (Grade {grade})")
    print(f"  Content       : {results['text'].score}")
    print(f"  Visual        : {results['visual'].score}")
    print(f"  UX            : {results['ux'].score}")
    print(f"  Trust         : {results['trust'].score}")
    print(f"  Tech          : {results['tech'].score}")
    print(f"─" * 60)
    print(f"  LLM Calls     : {usage['total_calls']}")
    print(f"  Retries (429) : {usage['total_retries']}")
    print(f"  Prompt Tokens : {usage['total_prompt_tokens']}")
    print(f"  Compl. Tokens : {usage['total_completion_tokens']}")
    print(f"  Total Tokens  : {usage['total_tokens']}")
    print(f"  Total Time    : {total_time}s")
    print("=" * 60 + "\n")

    return overall, grade, results, page_data, usage


def main():
    render_header()

    # ── Sidebar ─────────────────────────────────────────────────────
    with st.sidebar:
        st.header("🔗 Analyze a Website")
        url = st.text_input(
            "Enter URL",
            placeholder="https://example.com",
        )
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)

        st.divider()
        st.caption(
            "CEPS scores five dimensions:\n"
            "**C**ontent · **E**xperience · **P**erformance · **S**ecurity"
        )

    # ── Main area ───────────────────────────────────────────────────
    if analyze_btn:
        if not GEMINI_API_KEY:
            st.error("⚠️ `GEMINI_API_KEY` is not set. Add it to your `.env` file and restart.")
            return
        if not url:
            st.error("Please enter a URL to analyze.")
            return

        try:
            overall, grade, results, page_data, usage = _run_analysis(url)

            # Store in session for re-renders
            st.session_state["ceps_result"] = {
                "overall": overall,
                "grade": grade,
                "results": results,
                "page_data": page_data,
                "usage": usage,
            }
        except Exception as e:
            print(f"[CEPS] !! PIPELINE ERROR: {e}")
            st.error(f"Analysis failed: {e}")
            return

    # ── Display stored results ──────────────────────────────────────
    if "ceps_result" in st.session_state:
        data = st.session_state["ceps_result"]
        page_data = data["page_data"]
        usage = data["usage"]

        st.markdown(
            f"**Analyzed:** `{page_data.url}`  ·  "
            f"**Load time:** {page_data.load_time_seconds}s  ·  "
            f"**Size:** {page_data.html_size_kb} KB  ·  "
            f"**Tokens used:** {usage['total_tokens']}"
        )

        render_charts(data["overall"], data["grade"], data["results"])
        render_results(data["results"])
    else:
        st.info("👈 Enter a URL in the sidebar and click **Analyze** to get started.")


if __name__ == "__main__":
    main()
