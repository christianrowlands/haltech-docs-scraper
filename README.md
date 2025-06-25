# Haltech Documentation Scraper

A Python web scraper that downloads the Haltech knowledge base documentation and converts it to markdown files for offline access and AI tool integration.

## Features

- **Automatic Discovery**: Crawls the entire Haltech knowledge base to discover all articles
- **JavaScript Support**: Uses Playwright to handle dynamic content
- **Markdown Conversion**: Converts HTML articles to clean markdown format
- **Image Downloads**: Optionally downloads and localizes images
- **Organized Output**: Creates a hierarchical folder structure matching the site
- **Progress Tracking**: Shows real-time progress with detailed logging
- **Error Recovery**: Automatic retries and failed URL tracking
- **Rate Limiting**: Configurable delays to be respectful to the server

## Installation

1. Clone the repository:
```bash
cd haltech-docs-scraper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

### Basic Usage

Run the full scraping process:
```bash
python main.py
```

### Discovery Only

To only discover and map the site structure without downloading:
```bash
python main.py --discover-only
```

### Command Line Options

- `--discover-only`: Only run discovery phase to map site structure
- `--use-sitemap`: Use existing site map from previous discovery (skip discovery phase)
- `--no-images`: Skip downloading images
- `--concurrent N`: Number of concurrent downloads (default: 3)
- `--delay N`: Delay between requests in seconds (default: 1.5)

### Examples

```bash
# Run with custom settings
python main.py --concurrent 5 --delay 2.0

# Run without downloading images
python main.py --no-images

# Just discover the site structure
python main.py --discover-only

# Use existing site map to skip discovery
python main.py --use-sitemap

# Use existing site map with custom settings
python main.py --use-sitemap --concurrent 5 --no-images
```

## Output Structure

```
output/
├── index.md                 # Main index file
├── category-1/
│   ├── article-1.md
│   ├── article-2.md
│   └── ...
├── category-2/
│   └── ...
└── images/                  # Downloaded images (if enabled)
    ├── image1.jpg
    └── ...
```

## Markdown Format

Each article is saved with YAML front matter:

```markdown
---
title: Article Title
url: https://support.haltech.com/...
date_scraped: 2024-01-20
category: Main Category
subcategory: Subcategory
---

# Article Title

Article content in markdown...
```

## Logs

- `logs/scraper.log`: Main scraping log
- `logs/site_map.json`: Discovered site structure
- `logs/article_urls.txt`: List of all article URLs
- `logs/failed_urls.txt`: URLs that failed to scrape (if any)

## Configuration

Edit `config.py` to customize:

- Base URLs
- Output directories
- Request delays and timeouts
- Content selectors
- File naming conventions

## Troubleshooting

### Common Issues

1. **No articles found**: The site structure may have changed. Check the selectors in `config.py`

2. **Rate limiting**: Increase the delay between requests using `--delay`

3. **JavaScript not loading**: Increase the `TIMEOUT` value in `config.py`

4. **Memory issues**: Reduce concurrent downloads using `--concurrent`

## Notes

- Be respectful of the website's resources
- Check the website's terms of service and robots.txt
- This tool is for personal/educational use
- Consider reaching out to Haltech for API access if available

## License

This project is for educational purposes. Please respect Haltech's terms of service and intellectual property.