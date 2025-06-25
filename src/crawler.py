import asyncio
import json
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging
from src.utils import setup_logging, is_valid_url, normalize_url
import config

logger = setup_logging()

class HaltechCrawler:
    def __init__(self):
        self.discovered_urls = set()
        self.article_urls = set()
        self.category_structure = {}
        self.visited_urls = set()
        
    async def initialize_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            user_agent=config.USER_AGENT,
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
    async def close_browser(self):
        """Close browser and cleanup"""
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
        
    async def discover_site_structure(self):
        """Discover all categories and articles in the knowledge base"""
        logger.info(f"Starting site discovery from: {config.KB_URL}")
        
        await self.initialize_browser()
        
        try:
            # Start from the main KB page
            await self._discover_page(config.KB_URL)
            
            # Save discovered structure
            self._save_site_map()
            
        finally:
            await self.close_browser()
            
        logger.info(f"Discovery complete. Found {len(self.article_urls)} articles")
        return self.article_urls, self.category_structure
        
    async def _discover_page(self, url, depth=0, max_depth=5):
        """Recursively discover pages and categories"""
        if depth > max_depth:
            return
            
        if url in self.visited_urls:
            return
            
        normalized_url = normalize_url(url)
        if not is_valid_url(normalized_url):
            return
            
        self.visited_urls.add(normalized_url)
        logger.info(f"Discovering: {normalized_url} (depth: {depth})")
        
        try:
            # Navigate to the page
            await self.page.goto(normalized_url, 
                               timeout=config.TIMEOUT,
                               wait_until='networkidle')
            
            # Wait for content to load
            await asyncio.sleep(1)
            
            # Get page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'lxml')
            
            # Extract all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                absolute_url = normalize_url(href, normalized_url)
                
                if not is_valid_url(absolute_url):
                    continue
                    
                # Categorize the URL
                link_text = link.get_text(strip=True)
                
                # Check if it's an article or category
                if self._is_article_url(absolute_url, link_text):
                    self.article_urls.add(absolute_url)
                    logger.debug(f"Found article: {link_text}")
                elif self._is_category_url(absolute_url):
                    # Recursively discover category pages
                    if absolute_url not in self.visited_urls:
                        await self._discover_page(absolute_url, depth + 1, max_depth)
                        
            # Extract category information from breadcrumbs or navigation
            self._extract_category_info(soup, normalized_url)
            
        except Exception as e:
            logger.error(f"Error discovering {normalized_url}: {str(e)}")
            
    def _is_article_url(self, url, link_text):
        """Determine if URL is likely an article"""
        # Common patterns for KB articles
        article_patterns = [
            '/articles/',
            '/article/',
            '/solutions/',
            '/how-to/',
            '/guide/',
            '/tutorial/',
        ]
        
        # Check URL patterns
        url_lower = url.lower()
        for pattern in article_patterns:
            if pattern in url_lower:
                return True
                
        # Check if URL ends with common article identifiers
        if url_lower.endswith('.html') or '/kb/' in url_lower:
            # Additional checks to avoid false positives
            if link_text and len(link_text) > 10:  # Likely article title
                return True
                
        return False
        
    def _is_category_url(self, url):
        """Determine if URL is likely a category page"""
        category_patterns = [
            '/category/',
            '/categories/',
            '/section/',
            '/topic/',
        ]
        
        url_lower = url.lower()
        for pattern in category_patterns:
            if pattern in url_lower:
                return True
                
        # Check if it's a KB section
        if '/kb/' in url_lower and not self._is_article_url(url, ''):
            return True
            
        return False
        
    def _extract_category_info(self, soup, url):
        """Extract category information from the page"""
        # Look for breadcrumbs
        breadcrumbs = soup.find_all(['nav', 'ol', 'ul'], 
                                   class_=lambda x: x and 'breadcrumb' in x.lower() if x else False)
        
        if breadcrumbs:
            for breadcrumb in breadcrumbs:
                items = breadcrumb.find_all(['li', 'a'])
                if items:
                    category_path = [item.get_text(strip=True) for item in items]
                    self.category_structure[url] = category_path
                    
    def _save_site_map(self):
        """Save discovered URLs and structure to file"""
        site_map = {
            'total_articles': len(self.article_urls),
            'total_pages_visited': len(self.visited_urls),
            'articles': sorted(list(self.article_urls)),
            'category_structure': self.category_structure
        }
        
        output_file = config.LOGS_DIR / 'site_map.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(site_map, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Site map saved to: {output_file}")
        
        # Also save a simple list of URLs
        urls_file = config.LOGS_DIR / 'article_urls.txt'
        with open(urls_file, 'w', encoding='utf-8') as f:
            for url in sorted(self.article_urls):
                f.write(f"{url}\n")
                
        logger.info(f"Article URLs saved to: {urls_file}")


async def discover_haltech_kb():
    """Main function to discover Haltech KB structure"""
    crawler = HaltechCrawler()
    articles, categories = await crawler.discover_site_structure()
    return articles, categories


if __name__ == "__main__":
    # Run discovery when module is executed directly
    asyncio.run(discover_haltech_kb())