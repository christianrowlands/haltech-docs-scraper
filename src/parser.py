import re
from bs4 import BeautifulSoup
import logging
from src.utils import setup_logging

logger = setup_logging()

class ArticleParser:
    def __init__(self):
        self.content_selectors = [
            '.article-content',
            '.kb-article-content',
            '.content-wrapper',
            'article',
            'main',
            '.main-content',
            '#main-content',
            '.post-content',
            '.entry-content',
            'div[role="main"]'
        ]
        
        self.title_selectors = [
            'h1.article-title',
            'h1.kb-title',
            'h1',
            '.page-title',
            '.article-header h1'
        ]
        
        self.breadcrumb_selectors = [
            '.breadcrumb',
            'nav[aria-label="breadcrumb"]',
            '.breadcrumbs',
            'ol.breadcrumb',
            'ul.breadcrumb'
        ]
        
    def parse_article(self, html_content, url):
        """Parse article content and metadata from HTML"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        article_data = {
            'url': url,
            'title': self._extract_title(soup),
            'content': self._extract_content(soup),
            'breadcrumbs': self._extract_breadcrumbs(soup),
            'metadata': self._extract_metadata(soup),
            'images': self._extract_images(soup)
        }
        
        return article_data
        
    def _extract_title(self, soup):
        """Extract article title"""
        # Try specific selectors first
        for selector in self.title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title:
                    logger.debug(f"Title found with selector: {selector}")
                    return title
                    
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Clean common suffixes
            title = re.sub(r'\s*[\|–-]\s*Haltech.*$', '', title)
            return title
            
        return "Untitled Article"
        
    def _extract_content(self, soup):
        """Extract main article content"""
        # Try specific content selectors
        for selector in self.content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Clone the element to avoid modifying the original
                content = content_elem
                
                # Remove nested navigation, sidebars, etc.
                for unwanted in content.select('nav, aside, .sidebar, .related-articles'):
                    unwanted.decompose()
                    
                # Check if there's substantial content
                text_content = content.get_text(strip=True)
                if len(text_content) > 100:
                    logger.debug(f"Content found with selector: {selector}")
                    return str(content)
                    
        # Fallback: use heuristics
        return self._extract_content_heuristic(soup)
        
    def _extract_content_heuristic(self, soup):
        """Extract content using heuristics when selectors fail"""
        # Remove obvious non-content
        soup_copy = BeautifulSoup(str(soup), 'lxml')
        for tag in soup_copy.select('script, style, nav, header, footer, aside, .sidebar'):
            tag.decompose()
            
        # Find the container with the most text
        containers = []
        for elem in soup_copy.select('div, article, section, main'):
            text_length = len(elem.get_text(strip=True))
            # Count paragraphs and other content indicators
            p_count = len(elem.find_all('p'))
            score = text_length + (p_count * 50)
            
            if score > 200:  # Minimum score threshold
                containers.append((elem, score))
                
        if containers:
            # Sort by score and return the best match
            containers.sort(key=lambda x: x[1], reverse=True)
            return str(containers[0][0])
            
        # Last resort
        body = soup_copy.find('body')
        return str(body) if body else ""
        
    def _extract_breadcrumbs(self, soup):
        """Extract breadcrumb navigation"""
        for selector in self.breadcrumb_selectors:
            breadcrumb_elem = soup.select_one(selector)
            if breadcrumb_elem:
                # Extract breadcrumb items
                items = []
                
                # Try different breadcrumb structures
                # Structure 1: <ol><li><a>Text</a></li></ol>
                for li in breadcrumb_elem.select('li'):
                    text = li.get_text(strip=True)
                    if text and text not in ['>', '/', '»']:
                        items.append(text)
                        
                # Structure 2: <nav><a>Text</a><span>/</span><a>Text</a></nav>
                if not items:
                    for elem in breadcrumb_elem.find_all(['a', 'span']):
                        text = elem.get_text(strip=True)
                        if text and text not in ['>', '/', '»', '›']:
                            items.append(text)
                            
                if items:
                    logger.debug(f"Breadcrumbs found: {items}")
                    return items
                    
        return []
        
    def _extract_metadata(self, soup):
        """Extract additional metadata"""
        metadata = {}
        
        # Last modified date
        date_patterns = [
            r'(?:Last\s+)?(?:Modified|Updated):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:Date|Published):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        page_text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, page_text, re.I)
            if match:
                metadata['last_modified'] = match.group(1)
                break
                
        # Article ID (if present in URL or page)
        article_id_match = re.search(r'article[/-]?(\d+)', str(soup), re.I)
        if article_id_match:
            metadata['article_id'] = article_id_match.group(1)
            
        # Author
        author_elem = soup.find(class_=re.compile(r'author|by-line', re.I))
        if author_elem:
            metadata['author'] = author_elem.get_text(strip=True)
            
        # Tags/Keywords
        tag_container = soup.find(class_=re.compile(r'tags|keywords', re.I))
        if tag_container:
            tags = []
            for tag in tag_container.find_all(['a', 'span']):
                tag_text = tag.get_text(strip=True)
                if tag_text and len(tag_text) < 50:
                    tags.append(tag_text)
            if tags:
                metadata['tags'] = tags
                
        return metadata
        
    def _extract_images(self, soup):
        """Extract image URLs from content"""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                alt = img.get('alt', '')
                title = img.get('title', '')
                
                images.append({
                    'src': src,
                    'alt': alt,
                    'title': title
                })
                
        return images
        
    def clean_content(self, content_html):
        """Clean extracted content for conversion"""
        soup = BeautifulSoup(content_html, 'lxml')
        
        # Remove empty paragraphs
        for p in soup.find_all('p'):
            if not p.get_text(strip=True):
                p.decompose()
                
        # Remove excessive br tags
        for br in soup.find_all('br'):
            next_sibling = br.next_sibling
            if next_sibling and next_sibling.name == 'br':
                br.decompose()
                
        # Clean up divs with no content
        for div in soup.find_all('div'):
            if not div.get_text(strip=True) and not div.find_all(['img', 'video', 'iframe']):
                div.decompose()
                
        return str(soup)