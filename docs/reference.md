# Selenium Crawler - Complete Reference

## Installation

### Requirements
- Python 3.8+
- Chrome/Chromium browser
- Dependencies (install via pip):

```bash
pip install selenium>=4.10 \
    beautifulsoup4>=4.12 \
    pandas>=1.5 \
    webdriver-manager>=3.8
```

### Quick Start

```bash
git clone <repo>
cd "Selenium Crawler"
pip install -r requirements.txt
python -c "from core import SeleniumCrawler; print('Installation successful')"
```

---

## Architecture Overview

### Module Structure

**crawler_engine.py** - All core functionality consolidated:
- `SeleniumCrawler` - Main orchestration engine
- `BrowserConfig` - Selenium WebDriver configuration
- `AuthManager` - Authentication & session handling
- `RateLimiter` - Request throttling (default 30 req/min)
- `SmartCache` - TTL-based response caching (24h default)
- `DataParser` - HTML parsing and data extraction

### Design Principles

1. **Unified** - All components in single file for simplicity
2. **Stateful** - Browser session persists across requests
3. **Efficient** - Built-in caching reduces API calls
4. **Throttled** - Rate limiting prevents server overload
5. **Configurable** - All parameters customizable

---

## API Reference

### SeleniumCrawler

Main crawler class combining all functionality.

#### Constructor

```python
SeleniumCrawler(
    use_cache: bool = True,
    requests_per_minute: int = 30,
    headless: bool = True,
    cache_ttl_hours: int = 24
)
```

**Parameters:**
- `use_cache` - Enable/disable response caching
- `requests_per_minute` - Rate limit threshold (default 30)
- `headless` - Run browser in headless mode (default True)
- `cache_ttl_hours` - Cache expiration time in hours (default 24)

#### Methods

**start()**
```python
crawler.start()
```
Initialize and launch the browser. Called automatically with context manager.

**stop()**
```python
crawler.stop()
```
Close browser and cleanup resources. Called automatically on context manager exit.

**fetch_page(url, wait_for_element=None, scroll_to_bottom=False, use_cache=True)**
```python
html = crawler.fetch_page(
    url="https://example.com",
    wait_for_element=(By.CLASS_NAME, "content"),
    scroll_to_bottom=True,
    use_cache=True
)
```

Fetch page HTML with optional waiting and caching.

- `url` - Target URL to fetch
- `wait_for_element` - Tuple of (By, selector) to wait for
- `scroll_to_bottom` - Scroll to bottom before returning
- `use_cache` - Use cache if available

Returns: HTML string

**scroll_page(scroll_times=5)**
```python
crawler.scroll_page(scroll_times=10)
```
Scroll page multiple times for lazy-loaded content.

**take_screenshot(filepath)**
```python
crawler.take_screenshot("screenshot.png")
```
Capture page screenshot.

**extract_polymarket_markets()**
```python
markets = crawler.extract_polymarket_markets()
```

Extract market data from Polymarket. Returns list of dicts with:
- `title` - Market title
- `yes_price` - Yes option price
- `no_price` - No option price
- `volume` - Trading volume
- `url` - Market URL

**save_results(data, format="json", filepath=None)**
```python
filepath = crawler.save_results(
    data=markets,
    format="csv",
    filepath="markets.csv"
)
```

Export extraction results to file.

- `data` - List of dictionaries to export
- `format` - "json" or "csv"
- `filepath` - Output file path (auto-generated if None)

Returns: Path to saved file

**get_crawler_status()**
```python
status = crawler.get_crawler_status()
```

Get current crawler operational status including rate limiter and cache stats.

---

### BrowserConfig

Static utilities for WebDriver configuration.

#### Methods

**get_headless_chrome(headless=True)**
```python
driver = BrowserConfig.get_headless_chrome(headless=True)
```

Create optimized Chrome WebDriver with:
- No sandbox (for Linux)
- GPU disabled
- 1920x1080 window
- User-Agent spoofing
- Notification suppression

**wait_for_element(driver, by, selector, timeout=10)**
```python
found = BrowserConfig.wait_for_element(
    driver,
    By.CLASS_NAME,
    "market-card",
    timeout=10
)
```

Wait for element presence with timeout.

---

### AuthManager

Handle authentication and session persistence.

#### Methods

**login_polymarket(driver, username, password)**
```python
success = auth_mgr.login_polymarket(
    driver=driver,
    username="user@example.com",
    password="password123"
)
```

Authenticate to Polymarket. Returns: bool

**save_cookies(driver)**
Automatically called by login methods. Persists session cookies.

**load_cookies(driver)**
Load previously saved cookies into driver session.

---

### RateLimiter

Control request throttling.

#### Constructor

```python
limiter = RateLimiter(requests_per_minute=30)
```

#### Methods

**wait()**
```python
limiter.wait()
```
Block until rate limit allows next request.

**get_stats()**
```python
stats = limiter.get_stats()
```
Returns dictionary with:
- `requests_made` - Total requests throttled
- `requests_per_minute` - Current limit
- `last_request` - ISO timestamp of last request

---

### SmartCache

TTL-based response caching.

#### Constructor

```python
cache = SmartCache(default_ttl_hours=24)
```

#### Methods

**get(url)**
```python
html = cache.get("https://example.com")
```
Retrieve cached value if not expired. Returns: None if expired/missing

**set(url, value, ttl_hours=None)**
```python
cache.set(url, html_content, ttl_hours=48)
```
Store value in cache with optional custom TTL.

**clear()**
```python
cache.clear()
```
Remove all cached entries.

**get_cache_stats()**
```python
stats = cache.get_cache_stats()
```
Returns cache size and entry ages.

---

### DataParser

Static methods for HTML parsing and data extraction.

#### Methods

**extract_polymarket_markets(html)**
```python
markets = DataParser.extract_polymarket_markets(html)
```
Parse Polymarket HTML and extract market data.

**extract_json_from_script(html)**
```python
data = DataParser.extract_json_from_script(html)
```
Extract JSON-LD data from script tags.

**parse_table(html)**
```python
df = DataParser.parse_table(html)
```
Parse HTML table to pandas DataFrame.

**export_to_json(data, filepath)**
```python
DataParser.export_to_json(markets, "markets.json")
```

**export_to_csv(data, filepath)**
```python
DataParser.export_to_csv(markets, "markets.csv")
```

---

## Usage Examples

### Basic Extraction (Context Manager)

```python
from core import SeleniumCrawler
from selenium.webdriver.common.by import By

with SeleniumCrawler() as crawler:
    # Fetch page
    html = crawler.fetch_page(
        "https://polymarket.com/markets",
        wait_for_element=(By.CLASS_NAME, "market-card")
    )
    
    # Extract data
    markets = crawler.extract_polymarket_markets()
    
    # Save results
    filepath = crawler.save_results(markets, format="csv")
    print(f"Saved {len(markets)} markets to {filepath}")
```

### Platform Integration

```python
from core import SeleniumCrawler, AuthManager

crawler = SeleniumCrawler(
    use_cache=True,
    requests_per_minute=20,
    cache_ttl_hours=12
)
crawler.start()

try:
    auth = AuthManager()
    auth.login_polymarket(crawler.driver, "user@example.com", "password")
    
    # Extract authenticated content
    html = crawler.fetch_page("https://polymarket.com/portfolio")
    # Parse and process...
    
finally:
    crawler.stop()
```

### Custom Rate Limiting

```python
from core import SeleniumCrawler

# Conservative rate limit (10 requests per minute)
crawler = SeleniumCrawler(requests_per_minute=10)

with crawler:
    for url in urls_to_crawl:
        html = crawler.fetch_page(url)
        # Process...
    
    # Check performance
    stats = crawler.get_crawler_status()
    print(f"Rate limit stats: {stats['rate_limiter_stats']}")
```

### Pagination with Scrolling

```python
from core import SeleniumCrawler

with SeleniumCrawler() as crawler:
    crawler.fetch_page("https://example.com/infinite-scroll")
    
    # Scroll to load all content
    crawler.scroll_page(scroll_times=20)
    
    # Parse fully loaded page
    html = crawler.driver.page_source
    # Extract...
```

### Error Handling

```python
from core import SeleniumCrawler
from selenium.common.exceptions import TimeoutException

crawler = SeleniumCrawler()
crawler.start()

try:
    html = crawler.fetch_page(
        "https://example.com",
        wait_for_element=(By.ID, "main-content"),
        timeout=5
    )
except TimeoutException:
    print("Page load timeout - retrying...")
    # Implement retry logic
finally:
    crawler.stop()
```

---

## Configuration

### Environment Variables

```bash
# Optional: Set custom Chrome binary path
export CHROME_BIN=/usr/bin/chromium

# Optional: Disable headless for debugging
export HEADLESS=false
```

### Custom Configuration

```python
from core import SeleniumCrawler

# Conservative settings for stability
crawler = SeleniumCrawler(
    headless=True,
    requests_per_minute=10,  # Slow down
    use_cache=True,
    cache_ttl_hours=48  # Longer cache
)

# Aggressive settings for speed
fast_crawler = SeleniumCrawler(
    headless=True,
    requests_per_minute=60,  # Speed up
    use_cache=False,  # No caching overhead
    cache_ttl_hours=1  # Short cache if used
)
```

---

## Troubleshooting

### "Chrome not found"
Install Chrome or Chromium:
```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser

# macOS
brew install chromium
```

### "Timeout waiting for element"
- Increase timeout: `wait_for_element(..., timeout=30)`
- Check selector: Verify CSS class/ID exists
- Enable debug: Set logging to DEBUG level

### "Connection refused"
- Target website down or blocking requests
- Check IP not rate-limited or banned
- Verify internet connection

### "Memory leak"
- Always use context manager: `with SeleniumCrawler()`
- Or explicitly call `crawler.stop()`
- Reduce cache TTL if memory grows

### Performance Issues
- Enable caching: `use_cache=True`
- Reduce rate limit: `requests_per_minute=10`
- Use headless mode: `headless=True` (faster)
- Clear cache periodically: `crawler.cache.clear()`

---

## Deployment

### Docker

```dockerfile
FROM selenium/standalone-chrome:latest

RUN pip install selenium beautifulsoup4 pandas webdriver-manager

COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
```

### Kubernetes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: crawler-pod
spec:
  containers:
  - name: crawler
    image: crawler:latest
    env:
    - name: REQUESTS_PER_MINUTE
      value: "20"
```

---

## Performance Metrics

Typical performance with default settings:

- **Page load time**: 2-5 seconds
- **Requests per minute**: 30 (configurable)
- **Cache hit rate**: 80%+ (depends on TTL and workload)
- **Memory usage**: 150-300MB per browser instance
- **CPU usage**: 20-40% during active crawling

---

## License & Attribution

Built with:
- Selenium 4.10+
- BeautifulSoup4
- Pandas
- WebDriver Manager

For trading platform integration only.
