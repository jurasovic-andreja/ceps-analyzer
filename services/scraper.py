"""Web scraping service — fetches HTML from a given URL."""

import time
import requests
from core.config import SCRAPER_TIMEOUT, MAX_PAGE_SIZE

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def scrape_url(url: str) -> tuple[str, str, float, int]:
    """
    Fetch a webpage.

    Returns
    -------
    html : str
    final_url : str  (after redirects)
    load_time : float  (seconds)
    status_code : int
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    start = time.time()
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=SCRAPER_TIMEOUT,
        allow_redirects=True,
    )
    response.raise_for_status()
    load_time = round(time.time() - start, 2)

    if len(response.content) > MAX_PAGE_SIZE:
        raise ValueError(
            f"Page too large: {len(response.content)} bytes "
            f"(max {MAX_PAGE_SIZE})"
        )

    return response.text, response.url, load_time, response.status_code
