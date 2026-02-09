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

IMPORTANT RULES:
- Base your evaluation ONLY on the metrics provided above.
- Every finding MUST cite a specific value (e.g. "Load time is 1.2s", "14 scripts loaded").
- Do NOT guess about JavaScript performance, rendering, or anything not in the data.
- Use the exact True/False values as given for each boolean field.

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""


def _fallback(page_data: PageData) -> AgentResult:
    """Rule-based tech scoring when LLM is unavailable."""
    score = 20
    findings = []

    # Load time
    lt = page_data.load_time_seconds
    if lt < 1:
        score += 15
        findings.append(f"Excellent load time ({lt}s)")
    elif lt < 2:
        score += 12
        findings.append(f"Good load time ({lt}s)")
    elif lt < 5:
        score += 5
        findings.append(f"Moderate load time ({lt}s)")
    else:
        findings.append(f"Slow load time ({lt}s)")

    # Page size
    size = page_data.html_size_kb
    if size < 100:
        score += 10
        findings.append(f"Lightweight page ({size} KB)")
    elif size < 500:
        score += 5
        findings.append(f"Moderate page size ({size} KB)")
    else:
        findings.append(f"Heavy page ({size} KB)")

    # SEO basics
    if page_data.has_ssl:
        score += 10
        findings.append("HTTPS enabled ✓")
    if page_data.title:
        score += 5
        findings.append(f"Title tag present ✓")
    else:
        findings.append("Missing title tag")
    if page_data.meta_description:
        score += 5
        findings.append("Meta description present ✓")
    else:
        findings.append("Missing meta description")
    if page_data.has_viewport_meta:
        score += 5
        findings.append("Viewport meta present ✓")
    if page_data.has_charset:
        score += 3
        findings.append("Charset declared ✓")
    if page_data.has_lang_attr:
        score += 3
        findings.append("Language attribute set ✓")
    if page_data.has_favicon:
        score += 3
        findings.append("Favicon present ✓")
    if page_data.has_structured_data:
        score += 5
        findings.append("Structured data found ✓")

    # Resources
    if page_data.scripts_count > 20:
        score -= 5
        findings.append(f"High script count ({page_data.scripts_count})")
    elif page_data.scripts_count > 0:
        findings.append(f"{page_data.scripts_count} scripts loaded")

    score = max(0, min(100, score))
    print(f"[TechAgent] Fallback score={score} (rule-based, LLM unavailable)")
    return AgentResult(
        agent_name=AGENT_NAME,
        score=float(score),
        findings=findings,
        summary=f"Rule-based analysis: load={lt}s, size={size}KB, {page_data.scripts_count} scripts.",
    )


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
        if data and "score" in data:
            print(f"[TechAgent] ✓ Completed — score={data['score']}")
            return AgentResult(
                agent_name=AGENT_NAME,
                score=float(data["score"]),
                findings=data.get("findings", []),
                summary=data.get("summary", ""),
            )
        else:
            print("[TechAgent] ⚠️ LLM returned unparseable response, using fallback")
            return _fallback(page_data)
    except Exception as e:
        print(f"[TechAgent] ⚠️ LLM error ({type(e).__name__}), using fallback")
        return _fallback(page_data)
