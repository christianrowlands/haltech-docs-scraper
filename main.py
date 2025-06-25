#!/usr/bin/env python3
"""
Haltech Documentation Scraper
Scrapes the Haltech knowledge base and converts articles to markdown format
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.scraper import HaltechScraper
from src.crawler import discover_haltech_kb
from src.utils import setup_logging
import config

logger = setup_logging()

async def discover_only():
    """Run discovery phase only"""
    logger.info("Running discovery phase only...")
    articles, categories = await discover_haltech_kb()
    logger.info(f"Discovery complete. Found {len(articles)} articles")
    
async def scrape_all(use_existing_sitemap=False):
    """Run full scraping process"""
    scraper = HaltechScraper()
    await scraper.scrape_all(use_existing_sitemap=use_existing_sitemap)

def main():
    parser = argparse.ArgumentParser(
        description="Scrape Haltech documentation and convert to markdown"
    )
    
    parser.add_argument(
        '--discover-only',
        action='store_true',
        help='Only run discovery phase to map site structure'
    )
    
    parser.add_argument(
        '--use-sitemap',
        action='store_true',
        help='Use existing site map from previous discovery (skip discovery phase)'
    )
    
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Skip downloading images'
    )
    
    parser.add_argument(
        '--concurrent',
        type=int,
        default=3,
        help='Number of concurrent downloads (default: 3)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.5,
        help='Delay between requests in seconds (default: 1.5)'
    )
    
    args = parser.parse_args()
    
    # Update config based on arguments
    if args.no_images:
        config.DOWNLOAD_IMAGES = False
    
    config.CONCURRENT_DOWNLOADS = args.concurrent
    config.REQUEST_DELAY = args.delay
    
    # Print configuration
    logger.info("Haltech Documentation Scraper")
    logger.info(f"Target URL: {config.KB_URL}")
    logger.info(f"Output directory: {config.OUTPUT_DIR}")
    logger.info(f"Download images: {config.DOWNLOAD_IMAGES}")
    logger.info(f"Concurrent downloads: {config.CONCURRENT_DOWNLOADS}")
    logger.info(f"Request delay: {config.REQUEST_DELAY}s")
    
    # Run appropriate function
    if args.discover_only:
        asyncio.run(discover_only())
    else:
        asyncio.run(scrape_all(use_existing_sitemap=args.use_sitemap))

if __name__ == "__main__":
    main()