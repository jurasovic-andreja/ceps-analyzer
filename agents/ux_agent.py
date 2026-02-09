"""UX Agent — evaluates structure, navigation, and user-experience signals."""

from core.models import PageData, AgentResult
from services.llm_router import LLMRouter

AGENT_NAME = "User Experience"

PROMPT_TEMPLATE = """You are a UX auditor for websites.
Analyse the following structural data and evaluate the user experience.

URL: {url}
Title: {title}
Heading structure: {headings}
Internal links count: {internal_links}
External links count: {external_links}
Forms count: {forms}
Has viewport meta (mobile-friendly signal): {viewport}
Has language attribute: {lang}
Load time: {load_time}s
Page size: {page_size} KB
Text excerpt (first 2000 chars):
\"\"\"
{text_excerpt}
\"\"\"

Evaluate:
1. Heading hierarchy (proper H1→H2→H3 structure)
2. Navigation clarity (enough internal links, logical structure)
3. Mobile-friendliness signals
4. Page load-time perception
5. Content scannability and readability layout
6. Form usability (if any)

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""


def analyze(page_data: PageData, llm: LLMRouter) -> AgentResult:
    print(f"[UXAgent] Starting analysis for {page_data.url}")
    prompt = PROMPT_TEMPLATE.format(
        url=page_data.url,
        title=page_data.title,
        headings=str(page_data.headings),
        internal_links=len(page_data.internal_links),
        external_links=len(page_data.external_links),
        forms=page_data.forms_count,
        viewport=page_data.has_viewport_meta,
        lang=page_data.has_lang_attr,
        load_time=page_data.load_time_seconds,
        page_size=page_data.html_size_kb,
        text_excerpt=page_data.text_content[:2000],
    )
    try:
        raw = llm.analyze_text(prompt, label="ux-agent")
        data = llm.parse_json(raw)
        if data:
            print(f"[UXAgent] ✓ Completed — score={data.get('score')}")
            return AgentResult(
                agent_name=AGENT_NAME,
                score=float(data.get("score", 50)),
                findings=data.get("findings", []),
                summary=data.get("summary", ""),
            )
    except Exception as e:
        print(f"[UXAgent] !! Error: {e}")
        return AgentResult(
            agent_name=AGENT_NAME,
            score=50,
            findings=[f"Analysis error: {e}"],
            summary="Could not complete UX analysis.",
        )
    print("[UXAgent] ✓ Completed")
    return AgentResult(agent_name=AGENT_NAME)
