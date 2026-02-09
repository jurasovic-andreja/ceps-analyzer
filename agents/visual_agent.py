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

Return ONLY this JSON:
{{
  "score": <integer 0-100>,
  "findings": ["<finding 1>", ...],
  "summary": "<one-sentence assessment>"
}}"""


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
    meta_score = 50
    meta_findings: list[str] = []
    try:
        print(f"[VisualAgent] Analyzing image metadata ({image_count} images, {alt_count} with alt)…")
        raw = llm.analyze_text(meta_prompt, label="visual-agent-meta")
        data = llm.parse_json(raw)
        if data:
            meta_score = float(data.get("score", 50))
            meta_findings = data.get("findings", [])
    except Exception as e:
        print(f"[VisualAgent] !! Metadata analysis error: {e}")
        meta_findings.append("Could not complete metadata visual analysis.")

    # Part 2: vision-model scoring (only when images exist)
    vision_score = meta_score
    vision_findings: list[str] = []
    if page_data.image_urls:
        try:
            print(f"[VisualAgent] Sending {len(page_data.image_urls)} image(s) to Gemini Vision…")
            raw = llm.analyze_images_batch(page_data.image_urls, VISION_PROMPT, label="visual-agent-vision")
            data = llm.parse_json(raw)
            if data:
                vision_score = float(data.get("score", 50))
                vision_findings = data.get("findings", [])
        except Exception as e:
            print(f"[VisualAgent] !! Vision analysis error: {e}")
            vision_findings.append("Vision analysis could not be completed.")

    # Blend scores (60 % vision, 40 % metadata when images exist)
    if page_data.image_urls:
        final_score = round(vision_score * 0.6 + meta_score * 0.4, 1)
    else:
        final_score = meta_score

    print(f"[VisualAgent] ✓ Completed — score={final_score}")
    return AgentResult(
        agent_name=AGENT_NAME,
        score=final_score,
        findings=meta_findings + vision_findings,
        summary=f"Visual score {final_score}/100 based on {image_count} image(s).",
    )
