"""
Selenium Crawler Engine - Consolidated Module

Complete web scraping framework with:
- Headless browser automation
- Authentication & session management
- Request rate limiting
- Intelligent caching (TTL-based)
- HTML parsing and data extraction

All functionality unified in one clean module.
"""

import time
import json
import hashlib
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging

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
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Control request rate and throttling"""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0
        self.request_count = 0
    
    def wait(self):
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_stats(self) -> Dict:
        """Get rate limiting statistics"""
        return {
            "requests_made": self.request_count,
            "requests_per_minute": self.requests_per_minute,
            "last_request": datetime.fromtimestamp(self.last_request_time).isoformat()
        }


# ============================================================================
# SMART CACHE
# ============================================================================

class SmartCache:
    """Intelligent response caching with TTL-based expiration"""
    
    def __init__(self, default_ttl_hours: int = 24):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl_hours = default_ttl_hours
        self.ttl_seconds = default_ttl_hours * 3600
    
    def _generate_key(self, url: str) -> str:
        """Generate MD5 hash key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url: str) -> Optional[Any]:
        """Get cached value if not expired"""
        key = self._generate_key(url)
        if key not in self.cache:
            return None
        
        data, timestamp = self.cache[key]
        age_seconds = time.time() - timestamp
        
        if age_seconds > self.ttl_seconds:
            del self.cache[key]
            return None
        
        logger.debug(f"Cache HIT: {url} (age: {age_seconds:.0f}s)")
        return data
    
    def set(self, url: str, value: Any, ttl_hours: Optional[int] = None):
        """Store value in cache"""
        key = self._generate_key(url)
        self.cache[key] = (value, time.time())
        ttl = ttl_hours or self.default_ttl_hours
        logger.debug(f"Cache SET: {url} (TTL: {ttl}h)")
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "ttl_hours": self.default_ttl_hours,
            "entries": [
                {
                    "age_seconds": time.time() - timestamp,
                    "ttl_seconds": self.ttl_seconds
                }
                for _, timestamp in self.cache.values()
            ]
        }


# ============================================================================
# DATA PARSER
# ============================================================================

class DataParser:
    """Parse HTML and extract structured data"""
    
    @staticmethod
    def extract_polymarket_markets(html: str) -> List[Dict]:
        """Extract market data from Polymarket HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        markets = []
        
        # Look for market cards/items
        market_elements = soup.find_all(class_="market-card") or soup.find_all(class_="market")
        
        for element in market_elements:
            try:
                title_elem = element.find(class_="title") or element.find("h3")
                title = title_elem.text.strip() if title_elem else "Unknown"
                
                yes_price_elem = element.find(class_="yes-price")
                yes_price = float(yes_price_elem.text.strip()) if yes_price_elem else 0.0
                
                no_price_elem = element.find(class_="no-price")
                no_price = float(no_price_elem.text.strip()) if no_price_elem else 0.0
                
                volume_elem = element.find(class_="volume")
                volume = float(volume_elem.text.strip()) if volume_elem else 0.0
                
                markets.append({
                    "title": title,
                    "yes_price": yes_price,
                    "no_price": no_price,
                    "volume": volume,
                    "url": element.get("href", "")
                })
            except Exception as e:
                logger.warning(f"Failed to parse market element: {e}")
                continue
        
        return markets
    
    @staticmethod
    def extract_json_from_script(html: str) -> Optional[Dict]:
        """Extract JSON data from script tags"""
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                return data
            except json.JSONDecodeError:
                continue
        
        return None
    
    @staticmethod
    def parse_table(html: str) -> Optional[pd.DataFrame]:
        """Parse HTML table to DataFrame"""
        try:
            dfs = pd.read_html(html)
            return dfs[0] if dfs else None
        except Exception as e:
            logger.warning(f"Failed to parse table: {e}")
            return None
    
    @staticmethod
    def export_to_json(data: List[Dict], filepath: str):
        """Export data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported {len(data)} items to {filepath}")
    
    @staticmethod
    def export_to_csv(data: List[Dict], filepath: str):
        """Export data to CSV file"""
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        logger.info(f"Exported {len(data)} items to {filepath}")


# ============================================================================
# BROWSER CONFIG
# ============================================================================

class BrowserConfig:
    """Configure and manage Selenium WebDriver"""
    
    @staticmethod
    def get_headless_chrome(headless: bool = True) -> webdriver.Chrome:
        """Create Chrome WebDriver with optimized settings"""
        options = Options()
        
        # Performance options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        
        # Headless mode
        if headless:
            options.add_argument("--headless=new")
        
        # User agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Disable notifications
        options.add_experimental_option(
            "prefs",
            {"profile.default_content_setting_values.notifications": 2}
        )
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    @staticmethod
    def wait_for_element(driver: webdriver.Chrome, by: By, selector: str, timeout: int = 10):
        """Wait for element to be present"""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {selector}")
            return False


# ============================================================================
# AUTH MANAGER
# ============================================================================

class AuthManager:
    """Handle authentication and session management"""
    
    def __init__(self):
        self.cookies = {}
        self.session_data = {}
    
    def login_polymarket(self, driver: webdriver.Chrome, username: str, password: str) -> bool:
        """Login to Polymarket"""
        try:
            driver.get("https://polymarket.com/login")
            
            # Wait for login form
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Fill login form
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit
            submit_btn = driver.find_element(By.ID, "submit")
            submit_btn.click()
            
            # Wait for redirect to confirm login
            WebDriverWait(driver, 10).until(
                EC.url_contains("markets")
            )
            
            logger.info("Successfully logged in to Polymarket")
            self._save_cookies(driver)
            return True
        
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def _save_cookies(self, driver: webdriver.Chrome):
        """Save session cookies"""
        self.cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    
    def load_cookies(self, driver: webdriver.Chrome):
        """Load previously saved cookies"""
        for name, value in self.cookies.items():
            driver.add_cookie({"name": name, "value": value})


# ============================================================================
# SELENIUM CRAWLER - MAIN ENGINE
# ============================================================================

class SeleniumCrawler:
    """Main crawler engine combining all components"""
    
    def __init__(
        self,
        use_cache: bool = True,
        requests_per_minute: int = 30,
        headless: bool = True,
        cache_ttl_hours: int = 24
    ):
        """Initialize crawler"""
        self.use_cache = use_cache
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)
        self.cache = SmartCache(default_ttl_hours=cache_ttl_hours) if use_cache else None
        self.parser = DataParser()
        self.browser_config = BrowserConfig()
        self.auth_manager = AuthManager()
        logger.info(f"SeleniumCrawler initialized (headless={headless}, cache={use_cache})")
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
    
    def start(self):
        """Start the browser"""
        logger.info("Starting browser...")
        self.driver = self.browser_config.get_headless_chrome(headless=self.headless)
        logger.info("Browser started successfully")
    
    def stop(self):
        """Stop the browser and cleanup"""
        if self.driver:
            logger.info("Stopping browser...")
            self.driver.quit()
            self.driver = None
            logger.info("Browser stopped")
    
    def fetch_page(
        self,
        url: str,
        wait_for_element: Optional[Tuple[By, str]] = None,
        scroll_to_bottom: bool = False,
        use_cache: bool = True
    ) -> str:
        """Fetch page HTML with optional caching"""
        if not self.driver:
            raise RuntimeError("Browser not started. Call start() first.")
        
        # Check cache
        if use_cache and self.cache:
            cached = self.cache.get(url)
            if cached:
                return cached
        
        # Respect rate limits
        self.rate_limiter.wait()
        
        # Fetch page
        logger.info(f"Fetching: {url}")
        self.driver.get(url)
        
        # Wait for element
        if wait_for_element:
            by, selector = wait_for_element
            self.browser_config.wait_for_element(self.driver, by, selector)
        
        # Scroll if needed
        if scroll_to_bottom:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Get HTML
        html = self.driver.page_source
        
        # Cache it
        if use_cache and self.cache:
            self.cache.set(url, html)
        
        return html
    
    def extract_polymarket_markets(self) -> List[Dict]:
        """Extract markets from Polymarket"""
        html = self.fetch_page("https://polymarket.com/markets")
        return self.parser.extract_polymarket_markets(html)
    
    def scroll_page(self, scroll_times: int = 5):
        """Scroll page for lazy-loaded content"""
        for _ in range(scroll_times):
            self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(1)
    
    def take_screenshot(self, filepath: str):
        """Capture page screenshot"""
        if self.driver:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved to {filepath}")
    
    def save_results(
        self,
        data: List[Dict],
        format: str = "json",
        filepath: Optional[str] = None
    ) -> str:
        """Save extraction results to file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"crawled_data_{timestamp}.{format}"
        
        if format == "json":
            self.parser.export_to_json(data, filepath)
        elif format == "csv":
            self.parser.export_to_csv(data, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return filepath
    
    def get_crawler_status(self) -> Dict:
        """Get current crawler status"""
        return {
            "driver_running": self.driver is not None,
            "cache_enabled": self.cache is not None,
            "headless": self.headless,
            "rate_limiter_stats": self.rate_limiter.get_stats(),
            "cache_stats": self.cache.get_cache_stats() if self.cache else None
        }


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "SeleniumCrawler",
    "BrowserConfig",
    "AuthManager",
    "RateLimiter",
    "SmartCache",
    "DataParser"
]
