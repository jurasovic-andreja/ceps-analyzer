import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_IMAGES = int(os.getenv("MAX_IMAGES", "3"))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS")) if os.getenv("MAX_TEXT_CHARS") else None
SCRAPER_TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "15"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", str(5 * 1024 * 1024)))  # 5MB
