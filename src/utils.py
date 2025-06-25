import re
import logging
from pathlib import Path
from datetime import datetime
from slugify import slugify
from urllib.parse import urljoin, urlparse
import config
from src.category_mapper import categorize_article, extract_category_from_path

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def create_slug(text, max_length=None):
    """Convert text to a URL-friendly slug"""
    if max_length is None:
        max_length = config.MAX_FILENAME_LENGTH
    
    slug = slugify(text, separator=config.SLUG_SEPARATOR)
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit(config.SLUG_SEPARATOR, 1)[0]
    
    return slug

def is_valid_url(url):
    """Check if URL is valid and should be scraped"""
    if not url:
        return False
    
    # Check if URL belongs to the target domain
    parsed = urlparse(url)
    if not parsed.netloc.startswith('support.haltech.com'):
        return False
    
    # Check exclusion patterns
    for pattern in config.EXCLUDE_PATTERNS:
        if pattern in url.lower():
            return False
    
    return True

def normalize_url(url, base_url=None):
    """Normalize URL to absolute form"""
    if base_url:
        url = urljoin(base_url, url)
    
    # Remove fragment and trailing slash
    parsed = urlparse(url)
    normalized = parsed._replace(fragment='').geturl()
    if normalized.endswith('/'):
        normalized = normalized[:-1]
    
    return normalized

def extract_domain_path(url):
    """Extract path components from URL for directory structure"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    
    # Remove common prefixes
    prefixes = ['portal/en/kb/haltech/', 'portal/kb/', 'kb/']
    for prefix in prefixes:
        if path.startswith(prefix):
            path = path[len(prefix):]
            break
    
    return path.split('/')

def create_output_path(url, title=None, content=None, breadcrumbs=None):
    """Create output file path based on URL and title"""
    path_parts = extract_domain_path(url)
    
    # Try to determine proper category structure
    if '/kb/articles/' in url and breadcrumbs and len(breadcrumbs) <= 2:
        # Article without clear navigation - use category mapper
        category_path, _ = categorize_article(url, title or '', content or '')
        dir_path = config.OUTPUT_DIR / Path(category_path)
    elif breadcrumbs and len(breadcrumbs) > 2:
        # Use breadcrumb navigation if available
        # Skip the first two items (Knowledge Base, Haltech) and create path
        clean_breadcrumbs = [create_slug(b) for b in breadcrumbs[2:]]
        if clean_breadcrumbs:
            dir_path = config.OUTPUT_DIR / Path(*clean_breadcrumbs)
        else:
            dir_path = config.OUTPUT_DIR
    else:
        # Use URL structure
        if len(path_parts) > 1:
            dir_path = config.OUTPUT_DIR / Path(*path_parts[:-1])
        else:
            dir_path = config.OUTPUT_DIR
    
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Always use URL slug for filename to ensure uniqueness
    if path_parts:
        # Use the last part of the URL as filename
        filename = path_parts[-1] + '.md'
    else:
        # Fallback to index if no path parts
        filename = 'index.md'
    
    # Ensure the filename is clean
    filename = clean_filename(filename)
    
    return dir_path / filename

def create_metadata_header(title, url, category=None, subcategory=None):
    """Create YAML front matter for markdown file"""
    metadata = [
        "---",
        f"title: {title}",
        f"url: {url}",
        f"date_scraped: {datetime.now().strftime('%Y-%m-%d')}",
    ]
    
    if category:
        metadata.append(f"category: {category}")
    
    if subcategory:
        metadata.append(f"subcategory: {subcategory}")
    
    metadata.append("---\n")
    
    return '\n'.join(metadata)

def clean_filename(filename):
    """Remove invalid characters from filename"""
    # Remove invalid characters for filenames
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    
    return filename.strip()

def get_image_filename(url, index=None):
    """Generate filename for downloaded image"""
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    
    if not filename or filename == '/':
        filename = f"image_{index or 0}"
    
    # Ensure proper extension
    if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
        filename += '.jpg'
    
    return clean_filename(filename)