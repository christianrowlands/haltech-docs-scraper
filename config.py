import os
from pathlib import Path

# Base URLs
BASE_URL = "https://support.haltech.com"
KB_URL = f"{BASE_URL}/portal/en/kb/haltech"

# Paths
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Scraping settings
REQUEST_DELAY = 1.5  # Seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30000  # Milliseconds for Playwright
CONCURRENT_DOWNLOADS = 3

# Content settings
DOWNLOAD_IMAGES = True
IMAGES_DIR = OUTPUT_DIR / "images"
if DOWNLOAD_IMAGES:
    IMAGES_DIR.mkdir(exist_ok=True)

# User agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "scraper.log"

# File naming
MAX_FILENAME_LENGTH = 200
SLUG_SEPARATOR = "-"

# Content selectors (to be refined based on actual HTML structure)
ARTICLE_SELECTORS = {
    "title": ["h1", ".article-title", ".kb-article-title"],
    "content": [".article-content", ".kb-article-content", "article", "main"],
    "category": [".breadcrumb", ".category-path"],
}

# Exclusion patterns
EXCLUDE_PATTERNS = [
    "login",
    "signup",
    "account",
    "portal/api",
]