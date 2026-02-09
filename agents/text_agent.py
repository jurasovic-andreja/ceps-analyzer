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

Return ONLY this JSON (no markdown, no explanation):
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", "<finding 2>", ...],
  "summary": "<one-sentence overall assessment>"
}}"""


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
        if data:
            return AgentResult(
                agent_name=AGENT_NAME,
                score=float(data.get("score", 50)),
                findings=data.get("findings", []),
                summary=data.get("summary", ""),
            )
    except Exception as e:
        print(f"[TextAgent] !! Error: {e}")
        return AgentResult(
            agent_name=AGENT_NAME,
            score=50,
            findings=[f"Analysis error: {e}"],
            summary="Could not complete text analysis.",
        )

    print("[TextAgent] ✓ Completed")
    return AgentResult(agent_name=AGENT_NAME)
