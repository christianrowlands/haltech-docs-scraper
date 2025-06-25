import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime
import logging
from tqdm.asyncio import tqdm
from playwright.async_api import async_playwright

from src.crawler import HaltechCrawler
from src.parser import ArticleParser
from src.converter import HTMLToMarkdownConverter
from src.utils import (
    setup_logging, create_output_path, create_metadata_header,
    get_image_filename, is_valid_url, normalize_url
)
import config

logger = setup_logging()

class HaltechScraper:
    def __init__(self):
        self.crawler = HaltechCrawler()
        self.parser = ArticleParser()
        self.converter = HTMLToMarkdownConverter()
        self.session = None
        self.browser = None
        self.context = None
        self.scraped_urls = set()
        self.failed_urls = set()
        
    async def initialize(self):
        """Initialize browser and session"""
        # Initialize aiohttp session for image downloads
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': config.USER_AGENT}
        )
        
        # Initialize Playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def scrape_all(self, use_existing_sitemap=False):
        """Main scraping orchestrator"""
        try:
            await self.initialize()
            
            # Phase 1: Discover all articles or load from existing sitemap
            if use_existing_sitemap:
                logger.info("Phase 1: Loading existing site map...")
                articles, categories = self._load_existing_sitemap()
                if not articles:
                    logger.error("No existing site map found, running discovery...")
                    articles, categories = await self.crawler.discover_site_structure()
            else:
                logger.info("Phase 1: Discovering site structure...")
                articles, categories = await self.crawler.discover_site_structure()
            
            if not articles:
                logger.error("No articles found")
                return
                
            logger.info(f"Found {len(articles)} articles to scrape")
            
            # Phase 2: Scrape articles
            logger.info("Phase 2: Scraping articles...")
            await self._scrape_articles(articles)
            
            # Phase 3: Generate index files
            logger.info("Phase 3: Generating index files...")
            await self._generate_index_files()
            
            # Summary
            logger.info(f"\nScraping complete!")
            logger.info(f"Successfully scraped: {len(self.scraped_urls)} articles")
            logger.info(f"Failed: {len(self.failed_urls)} articles")
            
            if self.failed_urls:
                failed_file = config.LOGS_DIR / 'failed_urls.txt'
                with open(failed_file, 'w') as f:
                    for url in self.failed_urls:
                        f.write(f"{url}\n")
                logger.info(f"Failed URLs saved to: {failed_file}")
                
        finally:
            await self.cleanup()
            
    def _load_existing_sitemap(self):
        """Load existing site map from file"""
        site_map_file = config.LOGS_DIR / 'site_map.json'
        
        if not site_map_file.exists():
            logger.warning(f"Site map file not found: {site_map_file}")
            return set(), {}
            
        try:
            with open(site_map_file, 'r', encoding='utf-8') as f:
                site_map = json.load(f)
                
            articles = set(site_map.get('articles', []))
            categories = site_map.get('category_structure', {})
            
            logger.info(f"Loaded {len(articles)} articles from existing site map")
            return articles, categories
            
        except Exception as e:
            logger.error(f"Error loading site map: {str(e)}")
            return set(), {}
            
    async def _scrape_articles(self, article_urls):
        """Scrape all articles with rate limiting"""
        # Create semaphore for concurrent downloads
        semaphore = asyncio.Semaphore(config.CONCURRENT_DOWNLOADS)
        
        # Progress bar
        tasks = []
        for url in article_urls:
            task = self._scrape_article_with_semaphore(url, semaphore)
            tasks.append(task)
            
        # Process all articles with progress bar
        for task in tqdm.as_completed(tasks, desc="Scraping articles"):
            await task
            
    async def _scrape_article_with_semaphore(self, url, semaphore):
        """Scrape single article with semaphore for rate limiting"""
        async with semaphore:
            await self._scrape_article(url)
            # Rate limiting
            await asyncio.sleep(config.REQUEST_DELAY)
            
    async def _scrape_article(self, url, retry_count=0):
        """Scrape a single article"""
        if url in self.scraped_urls:
            return
            
        try:
            logger.info(f"Scraping: {url}")
            
            # Create new page for each article
            context = await self.browser.new_context(
                user_agent=config.USER_AGENT,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                # Navigate to the article
                await page.goto(url, timeout=config.TIMEOUT, wait_until='networkidle')
                
                # Wait a bit for dynamic content
                await asyncio.sleep(1)
                
                # Get page content
                html_content = await page.content()
                
                # Parse article
                article_data = self.parser.parse_article(html_content, url)
                
                if not article_data['content']:
                    raise ValueError("No content extracted from article")
                
                # Clean content
                cleaned_content = self.parser.clean_content(article_data['content'])
                
                # Convert to markdown
                markdown_content = self.converter.convert(cleaned_content, url)
                
                if not markdown_content.strip():
                    raise ValueError("Empty markdown content after conversion")
                
                # Download images if enabled
                if config.DOWNLOAD_IMAGES and article_data['images']:
                    markdown_content = await self._process_images(
                        markdown_content, 
                        article_data['images'], 
                        url
                    )
                
                # Create output file
                output_path = create_output_path(url, article_data['title'])
                
                # Add metadata header
                category = article_data['breadcrumbs'][1] if len(article_data['breadcrumbs']) > 1 else None
                subcategory = article_data['breadcrumbs'][2] if len(article_data['breadcrumbs']) > 2 else None
                
                metadata_header = create_metadata_header(
                    article_data['title'],
                    url,
                    category,
                    subcategory
                )
                
                # Write to file
                full_content = metadata_header + "\n" + markdown_content
                output_path.write_text(full_content, encoding='utf-8')
                
                logger.info(f"Saved: {output_path}")
                self.scraped_urls.add(url)
                
            finally:
                await page.close()
                await context.close()
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            
            if retry_count < config.MAX_RETRIES:
                logger.info(f"Retrying {url} (attempt {retry_count + 1})")
                await asyncio.sleep(2)
                await self._scrape_article(url, retry_count + 1)
            else:
                self.failed_urls.add(url)
                
    async def _process_images(self, markdown_content, images, article_url):
        """Download images and update markdown references"""
        for i, img_data in enumerate(images):
            src = img_data['src']
            if not src:
                continue
                
            # Make absolute URL
            absolute_url = normalize_url(src, article_url)
            
            try:
                # Download image
                async with self.session.get(absolute_url, timeout=30) as response:
                    if response.status == 200:
                        # Generate filename
                        filename = get_image_filename(absolute_url, i)
                        image_path = config.IMAGES_DIR / filename
                        
                        # Save image
                        content = await response.read()
                        image_path.write_bytes(content)
                        
                        # Update markdown to reference local image
                        relative_path = f"../images/{filename}"
                        markdown_content = markdown_content.replace(src, relative_path)
                        markdown_content = markdown_content.replace(absolute_url, relative_path)
                        
                        logger.debug(f"Downloaded image: {filename}")
                        
            except Exception as e:
                logger.warning(f"Failed to download image {src}: {str(e)}")
                
        return markdown_content
        
    async def _generate_index_files(self):
        """Generate index files for navigation"""
        logger.info("Generating index files...")
        
        # Main index
        index_content = [
            "# Haltech Knowledge Base",
            f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\nTotal articles: {len(self.scraped_urls)}",
            "\n## Categories\n"
        ]
        
        # Walk through output directory
        for category_dir in sorted(config.OUTPUT_DIR.iterdir()):
            if category_dir.is_dir() and category_dir.name != 'images':
                category_name = category_dir.name.replace('-', ' ').title()
                index_content.append(f"\n### {category_name}")
                
                # List articles in category
                articles = list(category_dir.glob('*.md'))
                for article in sorted(articles):
                    if article.name != 'index.md':
                        # Read title from file
                        try:
                            content = article.read_text(encoding='utf-8')
                            lines = content.split('\n')
                            for line in lines:
                                if line.startswith('title:'):
                                    title = line.replace('title:', '').strip()
                                    relative_path = f"{category_dir.name}/{article.name}"
                                    index_content.append(f"- [{title}]({relative_path})")
                                    break
                        except:
                            pass
                            
        # Write main index
        index_path = config.OUTPUT_DIR / 'index.md'
        index_path.write_text('\n'.join(index_content), encoding='utf-8')
        logger.info(f"Created main index: {index_path}")


async def main():
    """Main entry point"""
    scraper = HaltechScraper()
    await scraper.scrape_all()


if __name__ == "__main__":
    asyncio.run(main())