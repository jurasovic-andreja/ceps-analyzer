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

IMPORTANT RULES:
- Base your evaluation ONLY on the structural data provided above.
- Every finding MUST reference a specific metric or value from the data (e.g. "viewport meta is True", "3 internal links").
- Do NOT guess about visual layout, colors, or anything not represented in the data.

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""


def _fallback(page_data: PageData) -> AgentResult:
    """Rule-based UX scoring when LLM is unavailable."""
    score = 30
    findings = []

    # Heading hierarchy
    h1s = page_data.headings.get("h1", [])
    h2s = page_data.headings.get("h2", [])
    if len(h1s) == 1:
        score += 10
        findings.append(f"Single H1 heading present: \"{h1s[0][:50]}\"")
    elif len(h1s) > 1:
        score += 5
        findings.append(f"Multiple H1 headings ({len(h1s)}) — should have exactly one")
    else:
        findings.append("No H1 heading — poor hierarchy")

    if h2s:
        score += 5
        findings.append(f"{len(h2s)} H2 subheadings found")

    # Mobile
    if page_data.has_viewport_meta:
        score += 15
        findings.append("Viewport meta tag present — mobile-friendly ✓")
    else:
        findings.append("No viewport meta tag — not mobile-optimized")

    # Language
    if page_data.has_lang_attr:
        score += 5
        findings.append("Language attribute set ✓")

    # Navigation
    int_links = len(page_data.internal_links)
    if int_links >= 10:
        score += 10
        findings.append(f"{int_links} internal links — good navigation")
    elif int_links >= 3:
        score += 5
        findings.append(f"{int_links} internal links — moderate navigation")
    else:
        findings.append(f"Only {int_links} internal links — weak navigation")

    # Load time
    lt = page_data.load_time_seconds
    if lt < 2:
        score += 10
        findings.append(f"Fast load time ({lt}s)")
    elif lt < 5:
        score += 5
        findings.append(f"Acceptable load time ({lt}s)")
    else:
        findings.append(f"Slow load time ({lt}s)")

    score = max(0, min(100, score))
    print(f"[UXAgent] Fallback score={score} (rule-based, LLM unavailable)")
    return AgentResult(
        agent_name=AGENT_NAME,
        score=float(score),
        findings=findings,
        summary=f"Rule-based analysis: {int_links} links, viewport={'yes' if page_data.has_viewport_meta else 'no'}, load={lt}s.",
    )


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
        if data and "score" in data:
            print(f"[UXAgent] ✓ Completed — score={data['score']}")
            return AgentResult(
                agent_name=AGENT_NAME,
                score=float(data["score"]),
                findings=data.get("findings", []),
                summary=data.get("summary", ""),
            )
        else:
            print("[UXAgent] ⚠️ LLM returned unparseable response, using fallback")
            return _fallback(page_data)
    except Exception as e:
        print(f"[UXAgent] ⚠️ LLM error ({type(e).__name__}), using fallback")
        return _fallback(page_data)
