"""Tech Agent — evaluates technical health, performance, and SEO fundamentals."""

from core.models import PageData, AgentResult
from services.llm_router import LLMRouter

AGENT_NAME = "Technical Health"

PROMPT_TEMPLATE = """You are a website technical health auditor.
Analyse the following technical signals and score the page's technical quality.

URL: {url}
Load time: {load_time}s
Page size: {page_size} KB
Has SSL: {ssl}
Has viewport meta: {viewport}
Has charset declaration: {charset}
Has language attribute: {lang}
Has favicon: {favicon}
Has structured data: {structured}
Scripts count: {scripts}
Stylesheets count: {stylesheets}
Images count: {images}
Title present: {has_title}
Meta description present: {has_meta}
Title: {title}
Meta description: {meta_desc}

Evaluate:
1. Page load time (< 2s excellent, > 5s poor)
2. Page size optimization
3. Basic SEO (title, meta description, lang, charset)
4. Mobile-readiness (viewport meta)
5. Resource count (scripts/stylesheets — fewer is better)
6. Favicon and branding basics
7. Structured data for rich search results

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""


def analyze(page_data: PageData, llm: LLMRouter) -> AgentResult:
    print(f"[TechAgent] Starting analysis for {page_data.url}")
    prompt = PROMPT_TEMPLATE.format(
        url=page_data.url,
        load_time=page_data.load_time_seconds,
        page_size=page_data.html_size_kb,
        ssl=page_data.has_ssl,
        viewport=page_data.has_viewport_meta,
        charset=page_data.has_charset,
        lang=page_data.has_lang_attr,
        favicon=page_data.has_favicon,
        structured=page_data.has_structured_data,
        scripts=page_data.scripts_count,
        stylesheets=page_data.stylesheets_count,
        images=len(page_data.image_urls),
        has_title=bool(page_data.title),
        has_meta=bool(page_data.meta_description),
        title=page_data.title,
        meta_desc=page_data.meta_description,
    )
    try:
        raw = llm.analyze_text(prompt, label="tech-agent")
        data = llm.parse_json(raw)
        if data:
            print(f"[TechAgent] ✓ Completed — score={data.get('score')}")
            return AgentResult(
                agent_name=AGENT_NAME,
                score=float(data.get("score", 50)),
                findings=data.get("findings", []),
                summary=data.get("summary", ""),
            )
    except Exception as e:
        print(f"[TechAgent] !! Error: {e}")
        return AgentResult(
            agent_name=AGENT_NAME,
            score=50,
            findings=[f"Analysis error: {e}"],
            summary="Could not complete tech analysis.",
        )
    print("[TechAgent] ✓ Completed")
    return AgentResult(agent_name=AGENT_NAME)
