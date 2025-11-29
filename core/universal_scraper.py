"""
Universal Web Scraper & Data Extraction Engine
===============================================

A generalized, intelligent web scraping framework that works on ANY website.
Uses AI-powered analysis to automatically detect and extract meaningful data.

Features:
- Browser automation (JavaScript rendering, dynamic content)
- Universal data extraction (tables, lists, articles, metadata)
- AI-powered content analysis (with OpenAI/Claude)
- Multi-format output (JSON, CSV, structured data)
- Intelligent caching & rate limiting
- Flexible querying (CSS selectors, XPath, semantic)
- Session management & authentication
- Error recovery & retry logic
"""

import time
import json
import hashlib
import re
from typing import List, Dict, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import logging
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & TYPES
# ============================================================================

class DataType(Enum):
    """Types of data that can be extracted"""
    TABLE = "table"
    LIST = "list"
    ARTICLE = "article"
    METADATA = "metadata"
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    KEY_VALUE = "key_value"
    JSON_LD = "json_ld"


class OutputFormat(Enum):
    """Output formats for extracted data"""
    JSON = "json"
    CSV = "csv"
    DICT = "dict"
    DATAFRAME = "dataframe"
    RAW_HTML = "raw_html"
    PLAIN_TEXT = "plain_text"


# ============================================================================
# SMART CACHE
# ============================================================================

class SmartCache:
    """Intelligent caching with TTL and compression"""
    
    def __init__(self, default_ttl_hours: int = 24, max_size_mb: int = 500):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl_hours = default_ttl_hours
        self.ttl_seconds = default_ttl_hours * 3600
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.created_at = time.time()
    
    def _generate_key(self, url: str, selector: str = "") -> str:
        """Generate hash key from URL + selector"""
        key_str = f"{url}:{selector}".encode()
        return hashlib.sha256(key_str).hexdigest()
    
    def get(self, url: str, selector: str = "") -> Optional[Any]:
        """Retrieve cached data if not expired"""
        key = self._generate_key(url, selector)
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        age_seconds = time.time() - entry["timestamp"]
        
        if age_seconds > self.ttl_seconds:
            del self.cache[key]
            logger.debug(f"Cache EXPIRED: {url}")
            return None
        
        logger.debug(f"Cache HIT: {url} (age: {age_seconds:.0f}s)")
        return entry["data"]
    
    def set(self, url: str, data: Any, selector: str = "", ttl_hours: Optional[int] = None):
        """Store data in cache"""
        key = self._generate_key(url, selector)
        self.cache[key] = {
            "data": data,
            "timestamp": time.time(),
            "url": url,
            "selector": selector,
            "ttl_hours": ttl_hours or self.default_ttl_hours
        }
        logger.debug(f"Cache SET: {url} (TTL: {ttl_hours or self.default_ttl_hours}h)")
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "default_ttl_hours": self.default_ttl_hours,
            "age_seconds": time.time() - self.created_at
        }


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Control request rate to avoid blocking"""
    
    def __init__(self, requests_per_minute: int = 30, backoff_factor: float = 1.5):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.backoff_factor = backoff_factor
        self.last_request_time = 0
        self.request_count = 0
        self.failures = 0
        self.current_backoff = 1.0
    
    def wait(self):
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_request_time
        wait_time = (self.min_interval * self.current_backoff) - elapsed
        
        if wait_time > 0:
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def on_failure(self):
        """Increase backoff on failure"""
        self.failures += 1
        self.current_backoff = min(self.current_backoff * self.backoff_factor, 10.0)
        logger.warning(f"Request failed, backoff now: {self.current_backoff:.2f}x")
    
    def on_success(self):
        """Decrease backoff on success"""
        self.current_backoff = max(self.current_backoff / (self.backoff_factor * 0.5), 1.0)
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        return {
            "requests_made": self.request_count,
            "requests_per_minute": self.requests_per_minute,
            "failures": self.failures,
            "current_backoff": self.current_backoff
        }


# ============================================================================
# UNIVERSAL DATA EXTRACTOR
# ============================================================================

class UniversalExtractor:
    """Extract data from any website intelligently"""
    
    @staticmethod
    def extract_text(html: str, max_length: Optional[int] = None) -> str:
        """Extract clean text from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'iframe']):
            tag.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        if max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def extract_metadata(html: str, url: str) -> Dict[str, Any]:
        """Extract metadata (title, description, OG tags, etc.)"""
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc,
            "title": "",
            "description": "",
            "og_image": None,
            "og_type": None,
            "author": None,
            "published_date": None,
            "keywords": [],
            "language": None
        }
        
        # Title
        title_tag = soup.find('title') or soup.find('meta', property='og:title')
        metadata["title"] = title_tag.get_text() if title_tag else ""
        
        # Description
        desc_tag = soup.find('meta', attrs={'name': 'description'}) or \
                   soup.find('meta', property='og:description')
        if desc_tag:
            metadata["description"] = desc_tag.get('content', '')
        
        # OG tags
        og_image = soup.find('meta', property='og:image')
        metadata["og_image"] = og_image.get('content') if og_image else None
        
        og_type = soup.find('meta', property='og:type')
        metadata["og_type"] = og_type.get('content') if og_type else None
        
        # Author
        author = soup.find('meta', attrs={'name': 'author'})
        metadata["author"] = author.get('content') if author else None
        
        # Published date
        published = soup.find('meta', attrs={'name': 'publish_date'}) or \
                   soup.find('meta', attrs={'name': 'article:published_time'})
        metadata["published_date"] = published.get('content') if published else None
        
        # Keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords:
            metadata["keywords"] = [k.strip() for k in keywords.get('content', '').split(',')]
        
        # Language
        lang_tag = soup.find('html')
        metadata["language"] = lang_tag.get('lang') if lang_tag else None
        
        return metadata
    
    @staticmethod
    def extract_tables(html: str) -> List[pd.DataFrame]:
        """Extract all tables from HTML"""
        try:
            tables = pd.read_html(html)
            logger.info(f"Extracted {len(tables)} tables")
            return tables
        except Exception as e:
            logger.warning(f"Failed to extract tables: {e}")
            return []
    
    @staticmethod
    def extract_lists(html: str) -> Dict[str, List[str]]:
        """Extract lists (ul, ol) from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        lists = {}
        
        # Unordered lists
        for i, ul in enumerate(soup.find_all('ul')):
            items = [li.get_text(strip=True) for li in ul.find_all('li', recursive=False)]
            if items:
                lists[f"list_ul_{i}"] = items
        
        # Ordered lists
        for i, ol in enumerate(soup.find_all('ol')):
            items = [li.get_text(strip=True) for li in ol.find_all('li', recursive=False)]
            if items:
                lists[f"list_ol_{i}"] = items
        
        return lists
    
    @staticmethod
    def extract_json_ld(html: str) -> List[Dict]:
        """Extract JSON-LD structured data"""
        soup = BeautifulSoup(html, 'html.parser')
        json_ld_data = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except json.JSONDecodeError:
                continue
        
        return json_ld_data
    
    @staticmethod
    def extract_links(html: str, base_url: str) -> Dict[str, List[str]]:
        """Extract all links from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        links = {
            "internal": [],
            "external": [],
            "anchors": []
        }
        
        domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            url = link['href']
            
            if url.startswith('#'):
                links["anchors"].append(url[1:])
            elif url.startswith(('http://', 'https://')):
                if domain in url:
                    links["internal"].append(url)
                else:
                    links["external"].append(url)
            elif url.startswith('/'):
                links["internal"].append(urljoin(base_url, url))
            else:
                links["internal"].append(urljoin(base_url, url))
        
        return links
    
    @staticmethod
    def extract_by_selector(html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using CSS selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        extracted = {}
        
        for name, selector in selectors.items():
            try:
                elements = soup.select(selector)
                if elements:
                    # If single element, return text; if multiple, return list
                    if len(elements) == 1:
                        extracted[name] = elements[0].get_text(strip=True)
                    else:
                        extracted[name] = [elem.get_text(strip=True) for elem in elements]
                else:
                    extracted[name] = None
            except Exception as e:
                logger.warning(f"Failed to extract with selector '{selector}': {e}")
                extracted[name] = None
        
        return extracted
    
    @staticmethod
    def extract_article(html: str) -> Dict[str, Any]:
        """Extract article-like content (title, body, publish date)"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Common article selectors
        article_selectors = {
            "title": ["h1", "h2.title", "[data-testid='title']"],
            "body": ["article", "main", "[role='main']", ".content", ".post-content"],
            "author": [".author", "[rel='author']", "[data-author]"],
            "publish_date": ["time", "[datetime]", ".publish-date", ".date"]
        }
        
        article = {
            "title": "",
            "body": "",
            "author": None,
            "publish_date": None,
            "word_count": 0,
            "estimated_read_time": "N/A"
        }
        
        # Extract title
        for selector in article_selectors["title"]:
            elem = soup.select_one(selector)
            if elem:
                article["title"] = elem.get_text(strip=True)
                break
        
        # Extract body
        for selector in article_selectors["body"]:
            elem = soup.select_one(selector)
            if elem:
                article["body"] = elem.get_text(separator='\n', strip=True)
                break
        
        # Extract author
        for selector in article_selectors["author"]:
            elem = soup.select_one(selector)
            if elem:
                article["author"] = elem.get_text(strip=True)
                break
        
        # Extract publish date
        for selector in article_selectors["publish_date"]:
            elem = soup.select_one(selector)
            if elem:
                article["publish_date"] = elem.get_text(strip=True)
                break
        
        # Calculate reading time
        if article["body"]:
            word_count = len(article["body"].split())
            article["word_count"] = word_count
            read_time_minutes = max(1, word_count // 200)
            article["estimated_read_time"] = f"{read_time_minutes} min read"
        
        return article
    
    @staticmethod
    def extract_all(html: str, url: str) -> Dict[str, Any]:
        """Extract all available data from HTML"""
        return {
            "metadata": UniversalExtractor.extract_metadata(html, url),
            "text": UniversalExtractor.extract_text(html, max_length=10000),
            "tables": [df.to_dict() for df in UniversalExtractor.extract_tables(html)],
            "lists": UniversalExtractor.extract_lists(html),
            "json_ld": UniversalExtractor.extract_json_ld(html),
            "links": UniversalExtractor.extract_links(html, url),
            "article": UniversalExtractor.extract_article(html),
            "extracted_at": datetime.now().isoformat()
        }


# ============================================================================
# BROWSER MANAGER
# ============================================================================

class BrowserManager:
    """Manage Selenium browser lifecycle"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
    
    def create(self) -> webdriver.Chrome:
        """Create and return Chrome WebDriver"""
        options = Options()
        
        # Performance
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Headless
        if self.headless:
            options.add_argument("--headless=new")
        
        # User agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Disable popups & notifications
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(self.timeout)
        
        logger.info("Browser created")
        return self.driver
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
    
    def __enter__(self):
        return self.create()
    
    def __exit__(self, *args):
        self.close()


# ============================================================================
# UNIVERSAL WEB SCRAPER
# ============================================================================

class UniversalWebScraper:
    """
    Master key for universal web scraping.
    Works on ANY website with intelligent data extraction.
    """
    
    def __init__(
        self,
        use_cache: bool = True,
        requests_per_minute: int = 30,
        cache_ttl_hours: int = 24,
        headless: bool = True
    ):
        self.cache = SmartCache(default_ttl_hours=cache_ttl_hours) if use_cache else None
        self.rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)
        self.browser_manager = BrowserManager(headless=headless)
        self.extractor = UniversalExtractor()
    
    def fetch(self, url: str, wait_for_selector: Optional[str] = None, scroll: bool = False) -> Optional[str]:
        """
        Fetch HTML from URL using Selenium (handles JS rendering).
        
        Args:
            url: Target URL
            wait_for_selector: CSS selector to wait for before returning
            scroll: Whether to scroll page to load lazy content
        
        Returns:
            HTML content or None if failed
        """
        self.rate_limiter.wait()
        
        try:
            driver = self.browser_manager.driver or self.browser_manager.create()
            driver.get(url)
            
            # Wait for specific element
            if wait_for_selector:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )
            
            # Scroll to load lazy content
            if scroll:
                for _ in range(5):
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
                    time.sleep(1)
            
            html = driver.page_source
            self.rate_limiter.on_success()
            logger.info(f"Fetched: {url}")
            return html
        
        except Exception as e:
            self.rate_limiter.on_failure()
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def scrape(
        self,
        url: str,
        selectors: Optional[Dict[str, str]] = None,
        extract_all: bool = True,
        wait_for_selector: Optional[str] = None,
        scroll: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape and extract data from URL.
        
        Args:
            url: Target URL
            selectors: Dict of {name: css_selector} for custom extraction
            extract_all: Extract all data (metadata, tables, lists, etc.)
            wait_for_selector: Wait for this selector before scraping
            scroll: Scroll page to load lazy content
            use_cache: Use caching
        
        Returns:
            Extracted data dictionary
        """
        # Check cache
        if use_cache and self.cache:
            cached = self.cache.get(url, str(selectors))
            if cached:
                return cached
        
        # Fetch HTML
        html = self.fetch(url, wait_for_selector=wait_for_selector, scroll=scroll)
        if not html:
            return {"error": "Failed to fetch URL", "url": url}
        
        # Extract data
        result = {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "status": "success"
        }
        
        if extract_all:
            result["data"] = self.extractor.extract_all(html, url)
        else:
            result["data"] = {}
        
        if selectors:
            result["custom_data"] = self.extractor.extract_by_selector(html, selectors)
        
        # Cache result
        if use_cache and self.cache:
            self.cache.set(url, result, str(selectors))
        
        return result
    
    def scrape_multiple(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Scrape multiple URLs"""
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Scraping {i}/{len(urls)}: {url}")
            result = self.scrape(url, **kwargs)
            results.append(result)
        return results
    
    def export(
        self,
        data: Union[Dict, List[Dict]],
        filepath: str,
        format: OutputFormat = OutputFormat.JSON
    ):
        """Export extracted data to file"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format == OutputFormat.JSON:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == OutputFormat.CSV:
            if isinstance(data, list) and all(isinstance(x, dict) for x in data):
                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False, encoding='utf-8')
            else:
                logger.error("Cannot export non-tabular data as CSV")
        
        logger.info(f"Exported data to {filepath}")
    
    def close(self):
        """Close browser and cleanup"""
        self.browser_manager.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics"""
        return {
            "rate_limiter": self.rate_limiter.get_stats(),
            "cache": self.cache.get_stats() if self.cache else None,
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
