import re
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import logging
from src.utils import setup_logging

logger = setup_logging()

class HTMLToMarkdownConverter:
    def __init__(self):
        self.conversion_options = {
            'heading_style': 'ATX',
            'bullets': '-',
            'code_language': '',
            'strip': ['script', 'style', 'meta', 'link'],  # Note: 'img' is NOT in strip list
            'wrap': False,
            'wrap_width': 0,
            'default_title': True,  # Use alt text as title if no title attribute
            'exclude_styles': False  # Don't exclude styled elements
        }
        
    def convert(self, html_content, base_url=None):
        """Convert HTML content to Markdown"""
        try:
            # First, clean the HTML
            cleaned_html = self._clean_html(html_content, base_url)
            
            # Convert to markdown
            markdown = md(cleaned_html, **self.conversion_options)
            
            # Post-process the markdown
            markdown = self._post_process_markdown(markdown)
            
            return markdown
            
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {str(e)}")
            return ""
            
    def _clean_html(self, html_content, base_url=None):
        """Clean HTML before conversion"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove unwanted elements
        for tag in soup.find_all(['script', 'style', 'meta', 'link', 'noscript']):
            tag.decompose()
            
        # Remove navigation elements
        for nav in soup.find_all(['nav', 'header', 'footer']):
            nav.decompose()
            
        # Remove common sidebar/ad elements
        for element in soup.find_all(class_=re.compile(r'(sidebar|advertisement|banner|popup)', re.I)):
            element.decompose()
            
        # Clean up attributes
        for tag in soup.find_all(True):
            # Keep only essential attributes
            allowed_attrs = ['href', 'src', 'alt', 'title']
            attrs = dict(tag.attrs)
            for attr in attrs:
                if attr not in allowed_attrs:
                    del tag[attr]
                    
        # Convert relative URLs to absolute if base_url provided
        if base_url:
            for tag in soup.find_all(['a', 'img']):
                if tag.name == 'a' and tag.get('href'):
                    tag['href'] = self._make_absolute_url(tag['href'], base_url)
                elif tag.name == 'img' and tag.get('src'):
                    tag['src'] = self._make_absolute_url(tag['src'], base_url)
                    
        return str(soup)
        
    def _post_process_markdown(self, markdown):
        """Post-process the converted markdown"""
        # Remove excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Fix common conversion issues
        # Fix bullet points with no space after them
        markdown = re.sub(r'^(\s*)-([^\s])', r'\1- \2', markdown, flags=re.MULTILINE)
        
        # Fix numbered lists
        markdown = re.sub(r'^(\s*)(\d+)\.([^\s])', r'\1\2. \3', markdown, flags=re.MULTILINE)
        
        # Clean up code blocks
        markdown = re.sub(r'```\s*\n\s*```', '', markdown)
        
        # Ensure images are in proper markdown format
        # Convert any HTML img tags that weren't converted
        markdown = self._convert_remaining_img_tags(markdown)
        
        # Remove leading/trailing whitespace
        markdown = markdown.strip()
        
        return markdown
        
    def _convert_remaining_img_tags(self, markdown):
        """Convert any remaining HTML img tags to markdown format"""
        # Pattern to find HTML img tags
        img_pattern = r'<img\s+[^>]*?src=["\']([^"\']+)["\'][^>]*?>'
        
        def replace_img(match):
            full_tag = match.group(0)
            src = match.group(1)
            
            # Try to extract alt text
            alt_match = re.search(r'alt=["\']([^"\']*)["\']', full_tag)
            alt = alt_match.group(1) if alt_match else ''
            
            # Try to extract title
            title_match = re.search(r'title=["\']([^"\']*)["\']', full_tag)
            title = f' "{title_match.group(1)}"' if title_match else ''
            
            # Return markdown image syntax
            return f'![{alt}]({src}{title})'
        
        # Replace all img tags
        markdown = re.sub(img_pattern, replace_img, markdown)
        
        return markdown
        
    def _make_absolute_url(self, url, base_url):
        """Convert relative URL to absolute"""
        from urllib.parse import urljoin
        return urljoin(base_url, url)
        
    def extract_content_section(self, html_content, selectors=None):
        """Extract only the main content section from HTML"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Default selectors for content area
        if not selectors:
            selectors = [
                'article',
                'main',
                '.article-content',
                '.kb-article-content',
                '.content',
                '#content',
                '.post-content',
                'div[role="main"]'
            ]
            
        # Try each selector
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                logger.debug(f"Content found using selector: {selector}")
                return str(content)
                
        # Fallback: try to find the largest text block
        return self._find_main_content_heuristic(soup)
        
    def _find_main_content_heuristic(self, soup):
        """Use heuristics to find main content when selectors fail"""
        # Remove obvious non-content elements
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
            
        # Find all text containers
        text_containers = []
        for tag in soup.find_all(['div', 'article', 'section']):
            text_length = len(tag.get_text(strip=True))
            if text_length > 100:  # Minimum content length
                text_containers.append((tag, text_length))
                
        # Sort by text length and return the largest
        if text_containers:
            text_containers.sort(key=lambda x: x[1], reverse=True)
            return str(text_containers[0][0])
            
        # Last resort: return the body
        body = soup.find('body')
        return str(body) if body else str(soup)
        
    def extract_metadata(self, html_content):
        """Extract metadata from HTML"""
        soup = BeautifulSoup(html_content, 'lxml')
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        else:
            # Try to find h1
            h1 = soup.find('h1')
            if h1:
                metadata['title'] = h1.get_text(strip=True)
                
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')
            
        # Keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content', '')
            
        # Author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            metadata['author'] = meta_author.get('content', '')
            
        # Modified date
        meta_modified = soup.find('meta', attrs={'name': 'last-modified'})
        if meta_modified:
            metadata['last_modified'] = meta_modified.get('content', '')
            
        return metadata