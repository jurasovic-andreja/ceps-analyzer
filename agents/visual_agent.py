"""Visual Agent — analyses images, alt-text, and visual design via Gemini Vision."""

from core.models import PageData, AgentResult
from services.llm_router import LLMRouter

AGENT_NAME = "Visual Quality"

TEXT_PROMPT = """You are a website visual-design auditor.
Based on the image metadata below, evaluate the visual quality of the page.

URL: {url}
Number of images found: {image_count}
Images with alt-text: {alt_count} / {image_count}
Alt texts: {alt_texts}

Score the visual dimension 0-100 considering:
1. Presence and quantity of meaningful images
2. Alt-text quality and accessibility
3. Image-to-content ratio

IMPORTANT RULES:
- Base your score ONLY on the metadata numbers above.
- Every finding MUST cite the specific counts/texts provided.
- Do NOT assume anything about what the images look like from metadata alone.

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""

VISION_PROMPT = """You are a website visual-design auditor.
Look at the following website image(s) and evaluate:
1. Visual hierarchy and layout quality
2. Color scheme and contrast
3. Image relevance to likely page content
4. Overall aesthetic professionalism

IMPORTANT RULES:
- Base your evaluation ONLY on what you can see in the provided image(s).
- Each finding MUST describe something visible in the image(s).
- Do NOT speculate about parts of the website not shown.

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""


def _fallback(page_data: PageData) -> AgentResult:
    """Rule-based visual scoring when LLM is unavailable."""
    score = 30
    findings = []
    image_count = len(page_data.image_urls)
    alt_texts = page_data.images_alt_texts
    alt_count = sum(1 for url in page_data.image_urls if alt_texts.get(url, "").strip())

    if image_count == 0:
        score -= 10
        findings.append("No images found on page")
    elif image_count <= 2:
        score += 10
        findings.append(f"{image_count} image(s) found — minimal visuals")
    else:
        score += 20
        findings.append(f"{image_count} images found — good visual presence")

    if image_count > 0:
        pct = round(alt_count / image_count * 100)
        if pct == 100:
            score += 20
            findings.append(f"All {image_count} images have alt-text ✓")
        elif pct >= 50:
            score += 10
            findings.append(f"{alt_count}/{image_count} images have alt-text ({pct}%)")
        else:
            findings.append(f"Only {alt_count}/{image_count} images have alt-text ({pct}%) — poor accessibility")

    score = max(0, min(100, score))
    print(f"[VisualAgent] Fallback score={score} (rule-based, LLM unavailable)")
    return AgentResult(
        agent_name=AGENT_NAME,
        score=float(score),
        findings=findings,
        summary=f"Rule-based analysis: {image_count} image(s), {alt_count} with alt-text.",
    )


def analyze(page_data: PageData, llm: LLMRouter) -> AgentResult:
    """Run the visual agent — uses vision when images are available."""
    print(f"[VisualAgent] Starting analysis for {page_data.url}")
    image_count = len(page_data.image_urls)
    alt_texts = {
        url: alt
        for url, alt in page_data.images_alt_texts.items()
        if url in page_data.image_urls
    }
    alt_count = sum(1 for v in alt_texts.values() if v.strip())

    # Part 1: metadata-based scoring (always runs)
    meta_prompt = TEXT_PROMPT.format(
        url=page_data.url,
        image_count=image_count,
        alt_count=alt_count,
        alt_texts=str(list(alt_texts.values())[:10]),
    )
    meta_score: float | None = None
    meta_findings: list[str] = []
    try:
        print(f"[VisualAgent] Analyzing image metadata ({image_count} images, {alt_count} with alt)…")
        raw = llm.analyze_text(meta_prompt, label="visual-agent-meta")
        data = llm.parse_json(raw)
        if data and "score" in data:
            meta_score = float(data["score"])
            meta_findings = data.get("findings", [])
    except Exception as e:
        print(f"[VisualAgent] ⚠️ Metadata LLM error ({type(e).__name__}), skipping")

    # Part 2: vision-model scoring (only when images exist)
    vision_score: float | None = None
    vision_findings: list[str] = []
    if page_data.image_urls:
        try:
            print(f"[VisualAgent] Sending {len(page_data.image_urls)} image(s) to Gemini Vision…")
            raw = llm.analyze_images_batch(page_data.image_urls, VISION_PROMPT, label="visual-agent-vision")
            data = llm.parse_json(raw)
            if data and "score" in data:
                vision_score = float(data["score"])
                vision_findings = data.get("findings", [])
        except Exception as e:
            print(f"[VisualAgent] ⚠️ Vision LLM error ({type(e).__name__}), skipping")

    # Compute final score from whatever succeeded
    if meta_score is not None and vision_score is not None:
        final_score = round(vision_score * 0.6 + meta_score * 0.4, 1)
        all_findings = meta_findings + vision_findings
    elif vision_score is not None:
        final_score = vision_score
        all_findings = vision_findings
    elif meta_score is not None:
        final_score = meta_score
        all_findings = meta_findings
    else:
        # Both LLM calls failed → rule-based fallback
        return _fallback(page_data)

    print(f"[VisualAgent] ✓ Completed — score={final_score}")
    return AgentResult(
        agent_name=AGENT_NAME,
        score=final_score,
        findings=all_findings,
        summary=f"Visual score {final_score}/100 based on {image_count} image(s).",
    )
