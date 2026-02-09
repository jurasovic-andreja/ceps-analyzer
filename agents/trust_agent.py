"""Trust Agent — evaluates trust signals, security, and credibility."""

from core.models import PageData, AgentResult
from services.llm_router import LLMRouter

AGENT_NAME = "Trust & Credibility"

PROMPT_TEMPLATE = """You are a website trust and credibility auditor.
Analyse the following signals and score the page's trustworthiness.

URL: {url}
Has SSL (HTTPS): {ssl}
Has privacy policy: {privacy}
Has contact information: {contact}
Social media links found: {social_count}
Social URLs: {social_urls}
External links count: {ext_links}
Has structured data (schema.org): {structured}
Forms count: {forms}
Title: {title}
Meta description: {meta_desc}

Evaluate:
1. SSL / HTTPS security
2. Privacy policy presence
3. Contact information availability
4. Social media presence (legitimacy signal)
5. Professional presentation (title, meta)
6. Structured data for search credibility
7. Any red-flag patterns (e.g. excessive forms, no legal pages)

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""


def analyze(page_data: PageData, llm: LLMRouter) -> AgentResult:
    print(f"[TrustAgent] Starting analysis for {page_data.url}")
    prompt = PROMPT_TEMPLATE.format(
        url=page_data.url,
        ssl=page_data.has_ssl,
        privacy=page_data.has_privacy_policy,
        contact=page_data.has_contact_info,
        social_count=len(page_data.social_links),
        social_urls=page_data.social_links[:5],
        ext_links=len(page_data.external_links),
        structured=page_data.has_structured_data,
        forms=page_data.forms_count,
        title=page_data.title,
        meta_desc=page_data.meta_description,
    )
    try:
        raw = llm.analyze_text(prompt, label="trust-agent")
        data = llm.parse_json(raw)
        if data:
            print(f"[TrustAgent] ✓ Completed — score={data.get('score')}")
            return AgentResult(
                agent_name=AGENT_NAME,
                score=float(data.get("score", 50)),
                findings=data.get("findings", []),
                summary=data.get("summary", ""),
            )
    except Exception as e:
        print(f"[TrustAgent] !! Error: {e}")
        return AgentResult(
            agent_name=AGENT_NAME,
            score=50,
            findings=[f"Analysis error: {e}"],
            summary="Could not complete trust analysis.",
        )
    print("[TrustAgent] ✓ Completed")
    return AgentResult(agent_name=AGENT_NAME)
