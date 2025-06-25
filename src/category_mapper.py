"""
Category mapping for Haltech articles based on content and URL patterns
"""

import re
from typing import List, Optional, Tuple

# Engine category mappings
ENGINE_MAPPINGS = {
    # BMW
    'bmw': 'technical-library/engines/bmw',
    'm50': 'technical-library/engines/bmw',
    'm52': 'technical-library/engines/bmw',
    'm54': 'technical-library/engines/bmw',
    's50': 'technical-library/engines/bmw',
    's52': 'technical-library/engines/bmw',
    's54': 'technical-library/engines/bmw',
    'n54': 'technical-library/engines/bmw',
    'n55': 'technical-library/engines/bmw',
    
    # Ford
    'ford': 'technical-library/engines/ford',
    'barra': 'technical-library/engines/ford',
    'windsor': 'technical-library/engines/ford',
    'modular': 'technical-library/engines/ford',
    'coyote': 'technical-library/engines/ford',
    'ecoboost': 'technical-library/engines/ford',
    
    # Honda
    'honda': 'technical-library/engines/honda',
    'b-series': 'technical-library/engines/honda',
    'b16': 'technical-library/engines/honda',
    'b18': 'technical-library/engines/honda',
    'b20': 'technical-library/engines/honda',
    'd-series': 'technical-library/engines/honda',
    'd16': 'technical-library/engines/honda',
    'k-series': 'technical-library/engines/honda',
    'k20': 'technical-library/engines/honda',
    'k24': 'technical-library/engines/honda',
    
    # Mazda
    'mazda': 'technical-library/engines/mazda',
    'miata': 'technical-library/engines/mazda',
    'mx-5': 'technical-library/engines/mazda',
    'mx5': 'technical-library/engines/mazda',
    'na-nb': 'technical-library/engines/mazda',
    'bp': 'technical-library/engines/mazda',
    'b6': 'technical-library/engines/mazda',
    'rotary': 'technical-library/engines/mazda',
    '13b': 'technical-library/engines/mazda',
    '20b': 'technical-library/engines/mazda',
    
    # Mitsubishi
    'mitsubishi': 'technical-library/engines/mitsubishi',
    '4g63': 'technical-library/engines/mitsubishi',
    '4g93': 'technical-library/engines/mitsubishi',
    '4b11': 'technical-library/engines/mitsubishi',
    'evo': 'technical-library/engines/mitsubishi',
    
    # Nissan
    'nissan': 'technical-library/engines/nissan',
    'rb': 'technical-library/engines/nissan',
    'rb20': 'technical-library/engines/nissan',
    'rb25': 'technical-library/engines/nissan',
    'rb26': 'technical-library/engines/nissan',
    'rb30': 'technical-library/engines/nissan',
    'sr20': 'technical-library/engines/nissan',
    'vq': 'technical-library/engines/nissan',
    'vq35': 'technical-library/engines/nissan',
    'vr38': 'technical-library/engines/nissan',
    'ca18': 'technical-library/engines/nissan',
    
    # Subaru
    'subaru': 'technical-library/engines/subaru',
    'ej': 'technical-library/engines/subaru',
    'ej20': 'technical-library/engines/subaru',
    'ej25': 'technical-library/engines/subaru',
    'fa20': 'technical-library/engines/subaru',
    'fb': 'technical-library/engines/subaru',
    
    # Toyota
    'toyota': 'technical-library/engines/toyota',
    '1jz': 'technical-library/engines/toyota',
    '2jz': 'technical-library/engines/toyota',
    '1uz': 'technical-library/engines/toyota',
    '2uz': 'technical-library/engines/toyota',
    '3uz': 'technical-library/engines/toyota',
    '4ag': 'technical-library/engines/toyota',
    '3sg': 'technical-library/engines/toyota',
    '2zz': 'technical-library/engines/toyota',
    '1nz': 'technical-library/engines/toyota',
    '2az': 'technical-library/engines/toyota',
    '2rz': 'technical-library/engines/toyota',
    '3rz': 'technical-library/engines/toyota',
    
    # VW/Audi
    'vw': 'technical-library/engines/vw',
    'volkswagen': 'technical-library/engines/vw',
    'audi': 'technical-library/engines/vw',
    '1.8t': 'technical-library/engines/vw',
    '1.8-turbo': 'technical-library/engines/vw',
    '2.0t': 'technical-library/engines/vw',
    'vr6': 'technical-library/engines/vw',
    
    # GM/Chevrolet
    'gm': 'technical-library/engines/gm',
    'chevrolet': 'technical-library/engines/gm',
    'chevy': 'technical-library/engines/gm',
    'ls': 'technical-library/engines/gm',
    'ls1': 'technical-library/engines/gm',
    'ls2': 'technical-library/engines/gm',
    'ls3': 'technical-library/engines/gm',
    'ls6': 'technical-library/engines/gm',
    'ls7': 'technical-library/engines/gm',
    'lsx': 'technical-library/engines/gm',
}

# Product category mappings
PRODUCT_MAPPINGS = {
    # ECUs
    'elite': 'products/elite-series',
    'elite-1000': 'products/elite-series',
    'elite-1500': 'products/elite-series',
    'elite-2000': 'products/elite-series',
    'elite-2500': 'products/elite-series',
    'nexus': 'products/nexus-series',
    'nexus-r3': 'products/nexus-series',
    'nexus-r5': 'products/nexus-series',
    'nexus-s3': 'products/nexus-series',
    
    # Dashes and Displays
    'ic-7': 'products/displays',
    'iq3': 'products/displays',
    'dash': 'products/displays',
    'display': 'products/displays',
    
    # Wideband
    'wideband': 'products/sensors',
    'wb1': 'products/sensors',
    'wb2': 'products/sensors',
}

# Technical topic mappings
TECHNICAL_MAPPINGS = {
    # Triggers
    'trigger': 'technical-library/triggers',
    'crank-trigger': 'technical-library/triggers',
    'cam-trigger': 'technical-library/triggers',
    'home-signal': 'technical-library/triggers',
    
    # Fuel
    'fuel': 'technical-library/fuel',
    'injector': 'technical-library/fuel',
    'fuel-pump': 'technical-library/fuel',
    'flex-fuel': 'technical-library/fuel',
    'e85': 'technical-library/fuel',
    
    # Ignition
    'ignition': 'technical-library/ignition-systems',
    'coil': 'technical-library/ignition-systems',
    'spark': 'technical-library/ignition-systems',
    'cdi': 'technical-library/ignition-systems',
    
    # Sensors
    'sensor': 'technical-library/sensors',
    'map': 'technical-library/sensors',
    'maf': 'technical-library/sensors',
    'tps': 'technical-library/sensors',
    'iat': 'technical-library/sensors',
    'ect': 'technical-library/sensors',
    'lambda': 'technical-library/sensors',
    'o2': 'technical-library/sensors',
    
    # Functions
    'boost': 'technical-library/functions',
    'idle': 'technical-library/functions',
    'launch': 'technical-library/functions',
    'antilag': 'technical-library/functions',
    'traction': 'technical-library/functions',
    'nitrous': 'technical-library/functions',
    'cam-control': 'technical-library/functions',
    'vvt': 'technical-library/functions',
}

# Software mappings
SOFTWARE_MAPPINGS = {
    'nsp': 'nexus-software-programmer-nsp',
    'nexus-software': 'nexus-software-programmer-nsp',
    'esp': 'elite-software-programmer',
    'elite-software': 'elite-software-programmer',
    'datalog': 'software/datalog',
    'tuning': 'software/tuning',
}


def categorize_article(url: str, title: str = '', content: str = '') -> Tuple[str, List[str]]:
    """
    Determine the category path for an article based on URL, title, and content
    
    Returns:
        Tuple of (directory_path, breadcrumb_list)
    """
    # Convert to lowercase for matching
    url_lower = url.lower()
    title_lower = title.lower() if title else ''
    content_lower = content.lower() if content else ''
    
    # Combined text for searching
    combined_text = f"{url_lower} {title_lower} {content_lower[:500]}"
    
    # Check engine mappings first (most specific)
    for keyword, category in ENGINE_MAPPINGS.items():
        if keyword in combined_text:
            parts = category.split('/')
            breadcrumbs = ['Knowledge Base', 'Haltech'] + [p.replace('-', ' ').title() for p in parts]
            return category, breadcrumbs
    
    # Check product mappings
    for keyword, category in PRODUCT_MAPPINGS.items():
        if keyword in combined_text:
            parts = category.split('/')
            breadcrumbs = ['Knowledge Base', 'Haltech'] + [p.replace('-', ' ').title() for p in parts]
            return category, breadcrumbs
    
    # Check technical mappings
    for keyword, category in TECHNICAL_MAPPINGS.items():
        if keyword in combined_text:
            parts = category.split('/')
            breadcrumbs = ['Knowledge Base', 'Haltech'] + [p.replace('-', ' ').title() for p in parts]
            return category, breadcrumbs
    
    # Check software mappings
    for keyword, category in SOFTWARE_MAPPINGS.items():
        if keyword in combined_text:
            parts = category.split('/')
            breadcrumbs = ['Knowledge Base', 'Haltech'] + [p.replace('-', ' ').title() for p in parts]
            return category, breadcrumbs
    
    # Default fallback based on URL structure
    if '/kb/articles/' in url:
        # Extract article slug and use it
        match = re.search(r'/kb/articles/([^/?]+)', url)
        if match:
            article_slug = match.group(1)
            # Try to guess category from article slug
            if any(engine in article_slug for engine in ['engine', 'motor']):
                return 'technical-library/engines', ['Knowledge Base', 'Haltech', 'Technical Library', 'Engines']
            elif any(term in article_slug for term in ['trigger', 'crank', 'cam']):
                return 'technical-library/triggers', ['Knowledge Base', 'Haltech', 'Technical Library', 'Triggers']
            elif any(term in article_slug for term in ['fuel', 'injector']):
                return 'technical-library/fuel', ['Knowledge Base', 'Haltech', 'Technical Library', 'Fuel']
            elif any(term in article_slug for term in ['wire', 'wiring', 'harness', 'pinout']):
                return 'technical-library/wiring', ['Knowledge Base', 'Haltech', 'Technical Library', 'Wiring']
            elif any(term in article_slug for term in ['tune', 'tuning', 'map']):
                return 'technical-library/tuning', ['Knowledge Base', 'Haltech', 'Technical Library', 'Tuning']
    
    # Ultimate fallback - put in articles directory
    return 'articles', ['Knowledge Base', 'Haltech', 'Articles']


def extract_category_from_path(url: str) -> Optional[str]:
    """
    Extract category from URL path structure
    """
    # Remove domain and common prefixes
    path = re.sub(r'https?://[^/]+/', '', url)
    path = re.sub(r'portal/en/kb/', '', path)
    
    # Split path and look for category indicators
    parts = path.split('/')
    if len(parts) > 1 and parts[0] == 'haltech':
        # Return the path after 'haltech'
        return '/'.join(parts[1:])
    
    return None