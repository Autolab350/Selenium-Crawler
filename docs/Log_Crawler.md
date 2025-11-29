# 1. Enhanced Web Crawling & Data Fetching

## Current Limitation
The basic `fetch_webpage` tool only retrieves static HTML content. It cannot:
- Execute JavaScript to load dynamic content
- Handle authentication/login pages
- Navigate multi-page data (pagination)
- Extract structured data from complex layouts

## What You Need

### Selenium/Playwright Implementation
**Use case: Polymarket betting data**
- Sites like Polymarket load markets dynamically via JavaScript
- Selenium/Playwright opens a real browser, executes JS, then extracts data
- Can click buttons, fill forms, navigate through pages automatically

**Example workflow:**
1. Open Polymarket in headless browser
2. Login if needed
3. Search for specific markets
4. Extract current odds, volume, historical data
5. Store results in structured format

### API Direct Integration
**Use case: Real-time market data**
- Instead of crawling, call APIs directly (faster, more reliable, better data)
- Examples for your workspace:
  * Alpaca API: Get stock/crypto prices, account data, execute trades
  * Polymarket API: Query markets, outcomes, prices
  * Exchange APIs: Binance, Dydx, etc.

**Benefits:**
- Real-time data vs delayed scraped data
- Structured JSON responses (easier parsing)
- No rate-limiting from web scraping
- Official, reliable data sources

### Rate-Limiting & Caching
**Why:** API providers block aggressive requests

**Implementation:**
- Cache responses with timestamps
- Respect rate limits (e.g., 100 requests/minute)
- Queue requests intelligently
- Fallback to cached data if APIs are down

**Example for your backtest data:**
- Cache daily OHLCV (Open, High, Low, Close, Volume) data
- Only fetch new data when needed
- Reuse cached data for multiple analysis runs

---# Selenium/Playwright Crawler for Dynamic Data Extraction

## Overview
This document details building a sophisticated web crawler using Selenium/Playwright to handle:
- JavaScript-rendered content (SPA/dynamic sites)
- Authentication and login flows
- Multi-page data extraction (pagination)
- Rate limiting and smart caching
- Structured data extraction from complex layouts

---

# Why Selenium/Playwright Over Simple Fetching?

## The Problem with Basic fetch_webpage

```
fetch_webpage limitations:
❌ Gets raw HTML only
❌ No JavaScript execution
❌ Can't interact with forms
❌ Can't handle dynamic content loading
❌ No session management

Result: Polymarket's JavaScript-rendered markets don't load
```

## Selenium/Playwright Solution

```
Selenium/Playwright advantages:
✅ Opens real browser (headless)
✅ Executes JavaScript like a user
✅ Fills forms, clicks buttons
✅ Waits for dynamic content to load
✅ Manages cookies/sessions

Result: Can extract live market data, odds, volume exactly as displayed
```

---

# Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Selenium Crawler                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐   │
│  │ Browser Config │  │  Auth Manager  │  │ Rate Limiter │   │
│  └────────────────┘  └────────────────┘  └──────────────┘   │
│           │                  │                   │            │
│           └──────────────────┴───────────────────┘            │
│                          │                                     │
│                   ┌──────▼─────────┐                          │
│                   │ Crawler Engine  │                          │
│                   └──────┬─────────┘                          │
│                          │                                     │
│           ┌──────────────┼──────────────┐                    │
│           ▼              ▼              ▼                     │
│      ┌────────┐  ┌────────────┐  ┌──────────┐               │
│      │ Cache  │  │ Parser     │  │ Data     │               │
│      │ Layer  │  │ (BeautifulSoup)│ Extractor│               │
│      └────────┘  └────────────┘  └──────────┘               │
│           │              │              │                    │
│           └──────────────┴──────────────┘                    │
│                          │                                     │
│                   ┌──────▼─────────┐                          │
│                   │ Output: JSON   │                          │
│                   │ or CSV         │                          │
│                   └────────────────┘                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

# Implementation: Selenium Crawler

## Part 1: Browser Configuration & Setup

```python
# selenium_crawler/browser_config.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Optional, Callable

class BrowserConfig:
    """Configure headless browser for scraping"""
    
    @staticmethod
    def get_headless_chrome(headless: bool = True) -> webdriver.Chrome:
        """
        Create Chrome WebDriver with optimal settings for scraping
        
        Args:
            headless: Run in headless mode (no window)
        
        Returns:
            Configured Chrome WebDriver
        """
        chrome_options = Options()
        
        # Performance & behavior options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Headless mode
        if headless:
            chrome_options.add_argument("--headless=new")
        
        # User agent (pretend to be a real browser)
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Disable notifications/popups
        prefs = {
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        return driver
    
    @staticmethod
    def wait_for_element(driver: webdriver.Chrome, by: By, value: str, 
                        timeout: int = 10) -> bool:
        """
        Wait for element to appear (handles dynamic content loading)
        
        Args:
            driver: Selenium WebDriver
            by: Locator strategy (By.ID, By.CLASS_NAME, etc.)
            value: Locator value
            timeout: Max seconds to wait
        
        Returns:
            True if element found, False if timeout
        """
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except:
            return False
    
    @staticmethod
    def wait_for_elements_loaded(driver: webdriver.Chrome, 
                                 count: int, by: By, value: str,
                                 timeout: int = 10) -> bool:
        """Wait until specific number of elements are loaded"""
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: len(d.find_elements(by, value)) >= count
            )
            return True
        except:
            return False
```

---

## Part 2: Authentication Manager

```python
# selenium_crawler/auth_manager.py

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pickle
import os
from typing import Dict, Optional

class AuthManager:
    """Handle authentication, session management, cookies"""
    
    def __init__(self, cookies_dir: str = "./cookies"):
        """Initialize auth manager with cookie storage"""
        self.cookies_dir = cookies_dir
        os.makedirs(cookies_dir, exist_ok=True)
    
    def login_polymarket(self, driver: webdriver.Chrome, email: str, 
                        password: str, save_cookies: bool = True) -> bool:
        """
        Handle Polymarket login flow
        
        Args:
            driver: Selenium WebDriver
            email: Polymarket account email
            password: Polymarket account password
            save_cookies: Save session cookies for future use
        
        Returns:
            True if login successful
        """
        try:
            # Navigate to login
            driver.get("https://polymarket.com/auth/login")
            time.sleep(2)
            
            # Find and fill email field
            email_field = driver.find_element(By.NAME, "email")
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(0.5)
            
            # Find and fill password field
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(0.5)
            
            # Click login button
            login_button = driver.find_element(By.XPATH, 
                "//button[contains(text(), 'Sign In')]")
            login_button.click()
            
            # Wait for redirect to home (confirms login)
            time.sleep(3)
            if "dashboard" in driver.current_url or "markets" in driver.current_url:
                if save_cookies:
                    self.save_cookies(driver, "polymarket")
                return True
            return False
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def load_cookies(self, driver: webdriver.Chrome, site_name: str) -> bool:
        """
        Load saved session cookies (avoid re-login)
        
        Args:
            driver: Selenium WebDriver
            site_name: Name of site (e.g., "polymarket")
        
        Returns:
            True if cookies loaded
        """
        cookies_file = f"{self.cookies_dir}/{site_name}_cookies.pkl"
        
        if not os.path.exists(cookies_file):
            return False
        
        try:
            driver.get("https://polymarket.com")  # Need to visit domain first
            with open(cookies_file, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass  # Some cookies might fail, ignore
            time.sleep(1)
            driver.refresh()  # Refresh to apply cookies
            return True
        except Exception as e:
            print(f"Failed to load cookies: {e}")
            return False
    
    def save_cookies(self, driver: webdriver.Chrome, site_name: str):
        """Save session cookies for future logins"""
        cookies_file = f"{self.cookies_dir}/{site_name}_cookies.pkl"
        with open(cookies_file, 'wb') as f:
            pickle.dump(driver.get_cookies(), f)
```

---

## Part 3: Rate Limiter

```python
# selenium_crawler/rate_limiter.py

import time
from datetime import datetime, timedelta
from typing import Dict
from collections import deque

class RateLimiter:
    """Respect API/website rate limits, avoid blocking"""
    
    def __init__(self, requests_per_minute: int = 30, 
                 delay_between_requests: float = 0.5):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Max requests per minute
            delay_between_requests: Minimum delay between requests (seconds)
        """
        self.requests_per_minute = requests_per_minute
        self.delay_between_requests = delay_between_requests
        self.request_times = deque(maxlen=requests_per_minute)
        self.last_request_time = None
    
    def wait(self) -> float:
        """
        Block until safe to make next request
        
        Returns:
            Time waited (seconds)
        """
        now = datetime.now()
        start_time = now
        
        # Check rate limit (requests per minute)
        if len(self.request_times) == self.requests_per_minute:
            oldest_request = self.request_times[0]
            time_since_oldest = (now - oldest_request).total_seconds()
            
            if time_since_oldest < 60:
                wait_time = 60 - time_since_oldest
                print(f"Rate limit: waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                now = datetime.now()
        
        # Check delay between requests
        if self.last_request_time:
            elapsed = (now - self.last_request_time).total_seconds()
            if elapsed < self.delay_between_requests:
                wait_time = self.delay_between_requests - elapsed
                time.sleep(wait_time)
                now = datetime.now()
        
        # Record this request
        self.request_times.append(now)
        self.last_request_time = now
        
        total_wait = (now - start_time).total_seconds()
        return total_wait
```

---

## Part 4: Cache Layer

```python
# selenium_crawler/smart_cache.py

import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional
import hashlib

class SmartCache:
    """Intelligent caching with TTL and smart invalidation"""
    
    def __init__(self, cache_dir: str = "./cache", default_ttl_hours: int = 24):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl_hours: Default time-to-live for cached data
        """
        self.cache_dir = cache_dir
        self.default_ttl_hours = default_ttl_hours
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url: str, params: dict = None) -> str:
        """Generate consistent cache key from URL and params"""
        cache_str = f"{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(self, url: str, params: dict = None, 
            ttl_hours: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve cached data if fresh
        
        Args:
            url: Request URL
            params: Request parameters
            ttl_hours: Custom TTL for this cache entry
        
        Returns:
            Cached data or None if expired/missing
        """
        cache_key = self._get_cache_key(url, params)
        cache_file = f"{self.cache_dir}/{cache_key}.json"
        
        if not os.path.exists(cache_file):
            return None
        
        # Check cache age
        file_age = datetime.now() - datetime.fromtimestamp(
            os.path.getmtime(cache_file)
        )
        
        ttl = ttl_hours or self.default_ttl_hours
        if file_age > timedelta(hours=ttl):
            os.remove(cache_file)  # Delete expired cache
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                return cached.get('data')
        except:
            return None
    
    def set(self, url: str, data: Any, params: dict = None):
        """Store data in cache"""
        cache_key = self._get_cache_key(url, params)
        cache_file = f"{self.cache_dir}/{cache_key}.json"
        
        cache_entry = {
            'url': url,
            'params': params,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_entry, f, indent=2)
    
    def clear_old(self, older_than_hours: int = 72):
        """Remove old cache entries"""
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        
        for filename in os.listdir(self.cache_dir):
            filepath = f"{self.cache_dir}/{filename}"
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_time < cutoff:
                os.remove(filepath)
```

---

## Part 5: Data Parser & Extractor

```python
# selenium_crawler/data_parser.py

from bs4 import BeautifulSoup
from selenium import webdriver
from typing import List, Dict, Any
import json
import re

class DataParser:
    """Parse HTML and extract structured data"""
    
    @staticmethod
    def parse_html(html: str) -> BeautifulSoup:
        """Parse HTML into BeautifulSoup object"""
        return BeautifulSoup(html, 'html.parser')
    
    @staticmethod
    def get_page_html(driver: webdriver.Chrome) -> str:
        """Get current page HTML from browser"""
        return driver.page_source
    
    @staticmethod
    def extract_polymarket_markets(html: str) -> List[Dict]:
        """
        Extract market data from Polymarket page HTML
        
        Returns list of markets with:
        - title: Market title
        - id: Market ID
        - yes_price: YES outcome price
        - no_price: NO outcome price
        - volume: Trading volume
        - liquidity: Available liquidity
        """
        soup = DataParser.parse_html(html)
        markets = []
        
        # Find market cards (adjust selectors based on actual HTML)
        market_cards = soup.find_all('div', class_='market-card')
        
        for card in market_cards:
            try:
                # Extract market info
                title_elem = card.find('h3', class_='market-title')
                id_elem = card.find('a', href=True)
                
                if not title_elem or not id_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                market_id = id_elem['href'].split('/')[-1]
                
                # Extract prices
                price_elements = card.find_all('span', class_='price')
                prices = [p.get_text(strip=True) for p in price_elements]
                
                yes_price = float(prices[0]) if len(prices) > 0 else None
                no_price = float(prices[1]) if len(prices) > 1 else None
                
                # Extract volume and liquidity
                volume_elem = card.find('span', class_='volume')
                volume = volume_elem.get_text(strip=True) if volume_elem else None
                
                markets.append({
                    'title': title,
                    'id': market_id,
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'volume': volume,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error parsing market card: {e}")
                continue
        
        return markets
    
    @staticmethod
    def extract_json_data(html: str, script_id: str = None) -> Dict:
        """
        Extract JSON data from script tags
        (many modern sites store data in JSON blocks)
        """
        soup = DataParser.parse_html(html)
        
        # Find script tags with JSON
        scripts = soup.find_all('script', {'type': 'application/json'})
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                return data
            except:
                continue
        
        return {}
```

---

## Part 6: Main Crawler Engine

```python
# selenium_crawler/crawler.py

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from typing import List, Dict, Optional, Callable
from datetime import datetime
import json

from .browser_config import BrowserConfig
from .auth_manager import AuthManager
from .rate_limiter import RateLimiter
from .smart_cache import SmartCache
from .data_parser import DataParser

class SeleniumCrawler:
    """Main crawler engine combining all components"""
    
    def __init__(self, use_cache: bool = True, 
                 requests_per_minute: int = 30,
                 headless: bool = True):
        """
        Initialize crawler
        
        Args:
            use_cache: Enable caching
            requests_per_minute: Rate limit
            headless: Run browser headless
        """
        self.browser_config = BrowserConfig()
        self.auth_manager = AuthManager()
        self.rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)
        self.cache = SmartCache() if use_cache else None
        self.data_parser = DataParser()
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
    
    def start(self):
        """Start the browser"""
        self.driver = self.browser_config.get_headless_chrome(
            headless=self.headless
        )
    
    def stop(self):
        """Stop the browser"""
        if self.driver:
            self.driver.quit()
    
    def fetch_page(self, url: str, wait_for_element: Optional[tuple] = None,
                  use_cache: bool = True) -> str:
        """
        Fetch page HTML with optional caching
        
        Args:
            url: URL to fetch
            wait_for_element: (By, selector) to wait for loading
            use_cache: Use cache if available
        
        Returns:
            Page HTML
        """
        # Check cache
        if use_cache and self.cache:
            cached_html = self.cache.get(url)
            if cached_html:
                print(f"Cache hit: {url}")
                return cached_html
        
        # Respect rate limits
        self.rate_limiter.wait()
        
        # Fetch page
        print(f"Fetching: {url}")
        self.driver.get(url)
        
        # Wait for dynamic content if specified
        if wait_for_element:
            by, selector = wait_for_element
            self.browser_config.wait_for_element(self.driver, by, selector)
        else:
            time.sleep(2)  # Default wait
        
        html = self.data_parser.get_page_html(self.driver)
        
        # Cache result
        if self.cache:
            self.cache.set(url, html)
        
        return html
    
    def handle_pagination(self, base_url: str, page_selector: str,
                         next_button_xpath: str, max_pages: int = 5,
                         parser_func: Optional[Callable] = None) -> List[Dict]:
        """
        Handle multi-page extraction
        
        Args:
            base_url: Starting URL
            page_selector: CSS selector for page elements
            next_button_xpath: XPath to "next" button
            max_pages: Maximum pages to crawl
            parser_func: Function to parse each page
        
        Returns:
            Aggregated data from all pages
        """
        all_data = []
        current_page = 1
        
        while current_page <= max_pages:
            # Fetch current page
            html = self.fetch_page(base_url)
            
            # Parse data
            if parser_func:
                page_data = parser_func(html)
            else:
                page_data = self.data_parser.extract_polymarket_markets(html)
            
            all_data.extend(page_data)
            print(f"Page {current_page}: Extracted {len(page_data)} items")
            
            # Try to go to next page
            try:
                next_button = self.driver.find_element(By.XPATH, next_button_xpath)
                if not next_button.is_enabled():
                    break  # No more pages
                
                next_button.click()
                time.sleep(2)
                current_page += 1
            except:
                break  # No next button found
        
        return all_data
    
    def extract_polymarket_markets(self) -> List[Dict]:
        """
        Complete workflow to extract Polymarket market data
        
        Returns:
            List of markets with prices, volume, etc.
        """
        url = "https://polymarket.com/markets"
        
        # Fetch page (waits for market cards to load)
        html = self.fetch_page(url, wait_for_element=(By.CLASS_NAME, "market-card"))
        
        # Extract markets
        markets = self.data_parser.extract_polymarket_markets(html)
        
        return markets
```

---

## Part 7: Usage Examples

```python
# examples/crawl_polymarket.py

from selenium_crawler.crawler import SeleniumCrawler
import json

def example_1_simple_market_extraction():
    """Simple: Fetch Polymarket markets once"""
    crawler = SeleniumCrawler(use_cache=True, headless=True)
    crawler.start()
    
    try:
        markets = crawler.extract_polymarket_markets()
        
        print(f"Extracted {len(markets)} markets:")
        for market in markets[:5]:  # Show first 5
            print(f"  - {market['title']}")
            print(f"    YES: {market['yes_price']}, NO: {market['no_price']}")
        
        # Save results
        with open('polymarket_markets.json', 'w') as f:
            json.dump(markets, f, indent=2)
        
    finally:
        crawler.stop()

def example_2_with_authentication():
    """With login: Access authenticated data"""
    crawler = SeleniumCrawler(use_cache=True, headless=False)  # Show browser
    crawler.start()
    
    try:
        # Try to load existing session
        if not crawler.auth_manager.load_cookies(crawler.driver, "polymarket"):
            # Need to login
            email = input("Enter Polymarket email: ")
            password = input("Enter Polymarket password: ")
            
            if not crawler.auth_manager.login_polymarket(
                crawler.driver, email, password
            ):
                print("Login failed!")
                return
        
        # Now extract authenticated data
        markets = crawler.extract_polymarket_markets()
        print(f"Extracted {len(markets)} markets")
        
    finally:
        crawler.stop()

def example_3_pagination():
    """Handle paginated results"""
    crawler = SeleniumCrawler(use_cache=True, headless=True)
    crawler.start()
    
    try:
        markets = crawler.handle_pagination(
            base_url="https://polymarket.com/markets",
            page_selector=".market-card",
            next_button_xpath="//button[contains(@aria-label, 'Next')]",
            max_pages=3
        )
        
        print(f"Total markets from 3 pages: {len(markets)}")
        
    finally:
        crawler.stop()

if __name__ == "__main__":
    example_1_simple_market_extraction()
```

---

## Part 8: Integration with Agent Data Router

```python
# agent_tools/crawler_resource_adapter.py

from selenium_crawler.crawler import SeleniumCrawler
from agent_tools.agent_data_router import AgentDataRouter
from typing import Dict, Any

class CrawlerResourceAdapter:
    """Bridge between Selenium Crawler and Agent Data Router"""
    
    def __init__(self, router: AgentDataRouter):
        """Initialize adapter"""
        self.router = router
        self.crawler = SeleniumCrawler(use_cache=True, headless=True)
    
    def register_polymarket_resource(self, resource_name: str):
        """Register Polymarket crawler as a resource"""
        from agent_tools.agent_data_router import ResourceAssignment
        
        assignment = ResourceAssignment(
            resource_name=resource_name,
            resource_type="market_data",
            source="selenium_crawler",
            location="https://polymarket.com/markets",
            access_key="POLYMARKET_CRAWLER",
            metadata={
                "crawler_type": "selenium",
                "extraction_type": "polymarket_markets",
                "cache_ttl_hours": 4  # Refresh every 4 hours
            }
        )
        
        self.router.register_resource(assignment)
    
    def fetch_via_crawler(self, crawler_type: str) -> Dict[str, Any]:
        """Execute crawler and return data"""
        self.crawler.start()
        
        try:
            if crawler_type == "polymarket_markets":
                data = self.crawler.extract_polymarket_markets()
                return {
                    "status": "success",
                    "data": data,
                    "source": "selenium_crawler",
                    "extraction_method": "polymarket_markets",
                    "count": len(data)
                }
        finally:
            self.crawler.stop()
        
        return {"status": "error", "message": "Unknown crawler type"}

# Usage in agent workflow
if __name__ == "__main__":
    router = AgentDataRouter()
    adapter = CrawlerResourceAdapter(router)
    
    # Register resource
    adapter.register_polymarket_resource("live_polymarket_data")
    
    # Agent can now access it
    result = adapter.fetch_via_crawler("polymarket_markets")
    print(result)
```

---

## Installation & Requirements

```bash
# Install required packages
pip install selenium beautifulsoup4 pandas

# For Chrome driver, use webdriver-manager:
pip install webdriver-manager

# Then update browser_config.py to use:
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# In get_headless_chrome():
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

---

## Key Capabilities

| Feature | Capability |
|---------|-----------|
| **JavaScript Execution** | ✅ Renders SPA/dynamic sites |
| **Authentication** | ✅ Login & session management |
| **Pagination** | ✅ Multi-page extraction |
| **Rate Limiting** | ✅ Respects limits, avoids blocking |
| **Caching** | ✅ Smart TTL-based cache |
| **Data Extraction** | ✅ Structured HTML parsing |
| **Error Handling** | ✅ Robust fallbacks |
| **Agent Integration** | ✅ Works with Claude agents |

---

## Claude Agent Usage

```python
# What Claude agent can do:

router = AgentDataRouter()

# Agent asks: "Get latest Polymarket data"
data = router.get_resource("live_polymarket_data")

# Agent gets:
{
    "status": "success",
    "data": [
        {
            "title": "Will Bitcoin exceed $100k by Dec 2025?",
            "id": "market_12345",
            "yes_price": 0.65,
            "no_price": 0.35,
            "volume": "$2.4M",
            "timestamp": "2025-11-21T15:30:00"
        },
        # ... more markets
    ],
    "source": "selenium_crawler",
    "count": 50
}

# Agent can now:
# - Analyze pricing across markets
# - Find arbitrage opportunities
# - Detect market sentiment shifts
# - Compare with backtest data
```

---

## Benefits Over Basic Fetching

```
Basic fetch_webpage:
- 1-2 minutes setup
- Limited to static HTML
- Can't extract live data
- No pagination support
- Can't authenticate

Selenium Crawler:
- 30 minutes setup
- Handles dynamic SPA content
- Extracts live data exactly as displayed
- Built-in pagination
- Full authentication support
- Rate limiting & caching
- Resiliency to layout changes
```

Use Selenium/Playwright for:
- ✅ Polymarket live odds
- ✅ Trading platforms with authentication
- ✅ Real-time market data from non-API sources
- ✅ Complex multi-step workflows
