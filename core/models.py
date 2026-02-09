from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class PageData:
    """Parsed webpage data passed to all agents."""
    url: str
    title: str = ""
    meta_description: str = ""
    text_content: str = ""
    image_urls: List[str] = field(default_factory=list)
    images_alt_texts: Dict[str, str] = field(default_factory=dict)
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    headings: Dict[str, List[str]] = field(default_factory=dict)
    has_ssl: bool = False
    has_viewport_meta: bool = False
    has_charset: bool = False
    has_lang_attr: bool = False
    has_favicon: bool = False
    has_structured_data: bool = False
    has_privacy_policy: bool = False
    has_contact_info: bool = False
    social_links: List[str] = field(default_factory=list)
    forms_count: int = 0
    scripts_count: int = 0
    stylesheets_count: int = 0
    html_size_kb: float = 0.0
    load_time_seconds: float = 0.0
    status_code: int = 200


@dataclass
class AgentResult:
    """Result from a single analysis agent."""
    agent_name: str
    score: float = 50.0
    findings: List[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class CEPSResult:
    """Aggregated CEPS analysis result."""
    url: str
    overall_score: float = 0.0
    grade: str = ""
    text_result: Optional[AgentResult] = None
    visual_result: Optional[AgentResult] = None
    ux_result: Optional[AgentResult] = None
    trust_result: Optional[AgentResult] = None
    tech_result: Optional[AgentResult] = None
