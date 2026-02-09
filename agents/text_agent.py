"""Text Agent — analyses content quality, readability, and relevance."""

from core.models import PageData, AgentResult
from services.llm_router import LLMRouter

AGENT_NAME = "Content Quality"

PROMPT_TEMPLATE = """You are a website content quality auditor.
Analyse the following webpage text and metadata, then return a JSON object — nothing else.

URL: {url}
Title: {title}
Meta description: {meta_description}
Text excerpt (first 4000 chars):
\"\"\"
{text_excerpt}
\"\"\"

Evaluate:
1. Clarity and readability
2. Grammar and spelling quality
3. Content depth and usefulness
4. Keyword relevance to page title / meta
5. Call-to-action effectiveness

IMPORTANT RULES:
- Base your evaluation ONLY on the actual text provided above.
- Every finding MUST reference a specific detail from the provided data.
- Do NOT assume or infer anything not present in the text.
- If the text is empty or very short, score it low and explain why.

Return ONLY this JSON (no markdown, no explanation):
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", "<finding 2>", ...],
  "summary": "<one-sentence overall assessment>"
}}"""


def _fallback(page_data: PageData) -> AgentResult:
    """Rule-based scoring when LLM is unavailable."""
    score = 30  # baseline
    findings = []

    text_len = len(page_data.text_content)
    if text_len > 2000:
        score += 20
        findings.append(f"Good content volume ({text_len} characters)")
    elif text_len > 500:
        score += 10
        findings.append(f"Moderate content volume ({text_len} characters)")
    else:
        findings.append(f"Very thin content ({text_len} characters)")

    if page_data.title:
        score += 10
        findings.append(f"Page title present: \"{page_data.title[:60]}\"")
    else:
        score -= 10
        findings.append("Missing page title")

    if page_data.meta_description:
        score += 10
        findings.append("Meta description present")
    else:
        findings.append("Missing meta description")

    if page_data.headings.get("h1"):
        score += 10
        findings.append(f"H1 heading found: \"{page_data.headings['h1'][0][:60]}\"")
    else:
        findings.append("No H1 heading found")

    heading_count = sum(len(v) for v in page_data.headings.values())
    if heading_count >= 3:
        score += 5
        findings.append(f"{heading_count} headings provide good structure")

    score = max(0, min(100, score))
    print(f"[TextAgent] Fallback score={score} (rule-based, LLM unavailable)")
    return AgentResult(
        agent_name=AGENT_NAME,
        score=float(score),
        findings=findings,
        summary=f"Rule-based analysis: {text_len} chars of content evaluated.",
    )


def analyze(page_data: PageData, llm: LLMRouter) -> AgentResult:
    """Run the text quality agent and return an AgentResult."""
    print(f"[TextAgent] Starting analysis for {page_data.url}")
    prompt = PROMPT_TEMPLATE.format(
        url=page_data.url,
        title=page_data.title,
        meta_description=page_data.meta_description,
        text_excerpt=page_data.text_content[:4000],
    )
    try:
        raw = llm.analyze_text(prompt, label="text-agent")
        data = llm.parse_json(raw)
        if data and "score" in data:
            print(f"[TextAgent] ✓ Completed — score={data['score']}")
            return AgentResult(
                agent_name=AGENT_NAME,
                score=float(data["score"]),
                findings=data.get("findings", []),
                summary=data.get("summary", ""),
            )
        else:
            print("[TextAgent] ⚠️ LLM returned unparseable response, using fallback")
            return _fallback(page_data)
    except Exception as e:
        print(f"[TextAgent] ⚠️ LLM error ({type(e).__name__}), using fallback")
        return _fallback(page_data)
