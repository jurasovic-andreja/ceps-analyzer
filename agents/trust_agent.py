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

IMPORTANT RULES:
- Base your evaluation ONLY on the data provided above.
- Every finding MUST reference a specific value (e.g. "SSL is True", "0 social links found").
- Do NOT speculate about content, design, or anything not in the data.
- If a field is True, treat it as a positive signal. If False, treat it as a gap.

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""


def _fallback(page_data: PageData) -> AgentResult:
    """Rule-based trust scoring when LLM is unavailable."""
    score = 20
    findings = []

    if page_data.has_ssl:
        score += 20
        findings.append("HTTPS / SSL enabled ✓")
    else:
        findings.append("No HTTPS — major trust concern")

    if page_data.has_privacy_policy:
        score += 15
        findings.append("Privacy policy detected ✓")
    else:
        findings.append("No privacy policy found")

    if page_data.has_contact_info:
        score += 15
        findings.append("Contact information detected ✓")
    else:
        findings.append("No contact information found")

    social_count = len(page_data.social_links)
    if social_count >= 2:
        score += 10
        findings.append(f"{social_count} social media links — good legitimacy signal")
    elif social_count == 1:
        score += 5
        findings.append("1 social media link found")
    else:
        findings.append("No social media links")

    if page_data.has_structured_data:
        score += 10
        findings.append("Structured data (schema.org) present ✓")

    if page_data.title and page_data.meta_description:
        score += 5
        findings.append("Professional title and meta description present")

    score = max(0, min(100, score))
    print(f"[TrustAgent] Fallback score={score} (rule-based, LLM unavailable)")
    return AgentResult(
        agent_name=AGENT_NAME,
        score=float(score),
        findings=findings,
        summary=f"Rule-based analysis: SSL={'yes' if page_data.has_ssl else 'no'}, privacy={'yes' if page_data.has_privacy_policy else 'no'}, contact={'yes' if page_data.has_contact_info else 'no'}.",
    )


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
        if data and "score" in data:
            print(f"[TrustAgent] ✓ Completed — score={data['score']}")
            return AgentResult(
                agent_name=AGENT_NAME,
                score=float(data["score"]),
                findings=data.get("findings", []),
                summary=data.get("summary", ""),
            )
        else:
            print("[TrustAgent] ⚠️ LLM returned unparseable response, using fallback")
            return _fallback(page_data)
    except Exception as e:
        print(f"[TrustAgent] ⚠️ LLM error ({type(e).__name__}), using fallback")
        return _fallback(page_data)
