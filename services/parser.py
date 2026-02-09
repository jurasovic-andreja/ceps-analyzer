"""HTML parser — extracts structured data from raw HTML into PageData."""

import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from core.models import PageData
from core.config import MAX_TEXT_CHARS, MAX_IMAGES

SOCIAL_DOMAINS = [
    "facebook.com", "twitter.com", "x.com", "linkedin.com",
    "instagram.com", "youtube.com", "tiktok.com", "github.com",
]


def parse_html(html: str, final_url: str, load_time: float) -> PageData:
    """Parse raw HTML and return a structured PageData object."""
    soup = BeautifulSoup(html, "lxml")
    parsed_url = urlparse(final_url)
    base_domain = parsed_url.netloc

    page = PageData(url=final_url)
    page.has_ssl = final_url.startswith("https://")
    page.load_time_seconds = load_time
    page.html_size_kb = round(len(html.encode("utf-8")) / 1024, 1)

    # Title
    title_tag = soup.find("title")
    page.title = title_tag.get_text(strip=True) if title_tag else ""

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    page.meta_description = meta_desc.get("content", "") if meta_desc else ""

    # Viewport / charset / lang
    page.has_viewport_meta = bool(soup.find("meta", attrs={"name": "viewport"}))
    page.has_charset = bool(
        soup.find("meta", attrs={"charset": True})
        or soup.find("meta", attrs={"http-equiv": "Content-Type"})
    )
    html_tag = soup.find("html")
    page.has_lang_attr = bool(html_tag and html_tag.get("lang"))

    # Favicon
    page.has_favicon = bool(
        soup.find("link", rel=lambda v: v and "icon" in " ".join(v).lower())
    )

    # Structured data (JSON-LD or microdata)
    page.has_structured_data = bool(
        soup.find("script", attrs={"type": "application/ld+json"})
        or soup.find(attrs={"itemscope": True})
    )

    # Text content
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    raw_text = soup.get_text(separator=" ", strip=True)
    raw_text = re.sub(r"\s+", " ", raw_text)
    page.text_content = raw_text[:MAX_TEXT_CHARS] if MAX_TEXT_CHARS else raw_text

    # Headings
    for level in range(1, 7):
        tag_name = f"h{level}"
        headings = [h.get_text(strip=True) for h in soup.find_all(tag_name)]
        if headings:
            page.headings[tag_name] = headings

    # Re-parse for links / images (we decomposed some tags above)
    soup = BeautifulSoup(html, "lxml")

    # Images
    images_seen = set()
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if not src or src.startswith("data:"):
            continue
        abs_url = urljoin(final_url, src)
        if abs_url not in images_seen:
            images_seen.add(abs_url)
            alt = img.get("alt", "")
            page.images_alt_texts[abs_url] = alt
    page.image_urls = list(images_seen)[:MAX_IMAGES]

    # Links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        abs_href = urljoin(final_url, href)
        link_domain = urlparse(abs_href).netloc
        if link_domain == base_domain:
            page.internal_links.append(abs_href)
        else:
            page.external_links.append(abs_href)
            # Check social
            for sd in SOCIAL_DOMAINS:
                if sd in link_domain:
                    page.social_links.append(abs_href)
                    break

    # Privacy / contact heuristics
    lower_html = html.lower()
    page.has_privacy_policy = any(
        kw in lower_html for kw in ["privacy policy", "privacy-policy", "privacypolicy"]
    )
    page.has_contact_info = any(
        kw in lower_html
        for kw in ["contact us", "contact@", "mailto:", "phone", "tel:"]
    )

    # Counts
    soup2 = BeautifulSoup(html, "lxml")
    page.forms_count = len(soup2.find_all("form"))
    page.scripts_count = len(soup2.find_all("script"))
    page.stylesheets_count = len(
        soup2.find_all("link", rel=lambda v: v and "stylesheet" in " ".join(v).lower())
    )

    return page
