"""CEPS Score Aggregation Engine."""

from core.models import AgentResult

WEIGHTS = {
    "text": 0.25,
    "visual": 0.15,
    "ux": 0.25,
    "trust": 0.20,
    "tech": 0.15,
}


def calculate_ceps_score(
    text_result: AgentResult,
    visual_result: AgentResult,
    ux_result: AgentResult,
    trust_result: AgentResult,
    tech_result: AgentResult,
) -> tuple[float, str]:
    """Calculate weighted CEPS overall score and letter grade."""
    overall = (
        text_result.score * WEIGHTS["text"]
        + visual_result.score * WEIGHTS["visual"]
        + ux_result.score * WEIGHTS["ux"]
        + trust_result.score * WEIGHTS["trust"]
        + tech_result.score * WEIGHTS["tech"]
    )
    overall = round(overall, 1)
    return overall, _get_grade(overall)


def _get_grade(score: float) -> str:
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"
