# API Reference - Selenium Crawler

Complete API documentation for the Selenium Crawler framework.

## SeleniumCrawler (Main Class)

Main orchestration engine for web scraping.

### Constructor

```python
SeleniumCrawler(
    use_cache: bool = True,
    requests_per_minute: int = 30,
    headless: bool = True,
    cache_ttl_hours: int = 24
)
```

**Parameters:**
- `use_cache` (bool): Enable intelligent caching
- `requests_per_minute` (int): Rate limit for requests
- `headless` (bool): Run browser in headless mode
- `cache_ttl_hours` (int): Cache time-to-live in hours

**Example:**
```python
crawler = SeleniumCrawler(
    use_cache=True,
    requests_per_minute=20,
    headless=True,
    cache_ttl_hours=24
)
```

### Methods

#### `start()`
Start the Selenium WebDriver and browser.

```python
crawler.start()
```

#### `stop()`
Close the browser and clean up resources.

```python
crawler.stop()
```

#### `fetch_page(url: str, wait_time: int = 10) -> str`
Fetch and render a webpage.

**Parameters:**
- `url` (str): URL to fetch
- `wait_time` (int): Seconds to wait for dynamic content

**Returns:** HTML source code

**Example:**
```python
html = crawler.fetch_page("https://polymarket.com", wait_time=15)
```

#### `extract_polymarket_markets() -> List[Dict]`
Extract market data from Polymarket.

**Returns:** List of market dictionaries with keys:
- `title` (str): Market title
- `yes_price` (float): YES outcome price
- `no_price` (float): NO outcome price
- `volume` (float): Total trading volume
- `liquidity` (float): Available liquidity
- `url` (str): Market URL

**Example:**
```python
markets = crawler.extract_polymarket_markets()
for market in markets:
    print(f"{market['title']}: YES {market['yes_price']:.2f}")
```

#### `extract_platform_data(platform: str) -> List[Dict]`
Extract data from a specific platform.

**Parameters:**
- `platform` (str): Platform name ("polymarket", "hextrade", "topstep", etc.)

**Returns:** Platform-specific data

**Example:**
```python
hextrade_data = crawler.extract_platform_data("hextrade")
```

#### `get_page_data(page_num: int = 1) -> List[Dict]`
Get data from a specific page (for paginated results).

**Parameters:**
- `page_num` (int): Page number to fetch

**Returns:** List of data items from page

**Example:**
```python
page_data = crawler.get_page_data(2)
```

#### `scroll_page(scroll_times: int = 5)`
Scroll page for lazy-loaded content.

**Parameters:**
- `scroll_times` (int): Number of scroll operations

**Example:**
```python
crawler.scroll_page(scroll_times=10)
```

#### `take_screenshot(filepath: str)`
Capture page screenshot.

**Parameters:**
- `filepath` (str): Where to save screenshot

**Example:**
```python
crawler.take_screenshot("market_screenshot.png")
```

#### `save_results(data: List[Dict], format: str = "json", filepath: Optional[str] = None) -> str`
Save extraction results to file.

**Parameters:**
- `data` (List[Dict]): Data to save
- `format` (str): Output format ("json" or "csv")
- `filepath` (Optional[str]): Custom filepath (auto-generated if None)

**Returns:** Filepath where data was saved

**Example:**
```python
filepath = crawler.save_results(markets, format="json")
print(f"Saved to {filepath}")
```

#### `get_crawler_status() -> Dict`
Get current crawler status.

**Returns:** Dictionary with keys:
- `driver_running` (bool)
- `cache_enabled` (bool)
- `request_count` (int)
- `cache_size` (int)
- `last_request_time` (str)

**Example:**
```python
status = crawler.get_crawler_status()
print(f"Requests made: {status['request_count']}")
```

### Context Manager

Use crawler as context manager for automatic resource cleanup:

```python
with SeleniumCrawler() as crawler:
    markets = crawler.extract_polymarket_markets()
    # Browser automatically closes
```

---

## BrowserConfig

Configure and manage Selenium WebDriver.

### Constructor

```python
BrowserConfig(headless: bool = True, disable_images: bool = False)
```

**Parameters:**
- `headless` (bool): Run in headless mode
- `disable_images` (bool): Disable image loading for speed

### Methods

#### `get_driver() -> webdriver.Chrome`
Get configured WebDriver instance.

#### `setup_dynamic_waiting(driver: webdriver.Chrome, timeout: int = 10)`
Configure dynamic element waiting.

**Parameters:**
- `driver`: WebDriver instance
- `timeout`: Wait timeout in seconds

---

## AuthManager

Handle authentication and session management.

### Methods

#### `login_polymarket(username: str, password: str) -> bool`
Login to Polymarket.

**Parameters:**
- `username` (str): Email address
- `password` (str): Password

**Returns:** True if successful

**Example:**
```python
auth = AuthManager()
auth.login_polymarket("user@example.com", "password")
```

#### `save_cookies(filepath: str)`
Save session cookies for later reuse.

**Parameters:**
- `filepath` (str): Where to save cookies

#### `load_cookies(filepath: str)`
Load previously saved cookies.

**Parameters:**
- `filepath` (str): Cookie file location

---

## RateLimiter

Control request rate and throttling.

### Constructor

```python
RateLimiter(requests_per_minute: int = 30)
```

**Parameters:**
- `requests_per_minute` (int): Max requests per minute

### Methods

#### `wait_if_needed()`
Wait if necessary to respect rate limit.

**Example:**
```python
limiter = RateLimiter(requests_per_minute=20)
limiter.wait_if_needed()
# Make request
```

#### `get_stats() -> Dict`
Get rate limiting statistics.

**Returns:** Dictionary with request counts and timing info

---

## SmartCache

Intelligent response caching with TTL.

### Constructor

```python
SmartCache(default_ttl_hours: int = 24)
```

**Parameters:**
- `default_ttl_hours` (int): Default cache time-to-live

### Methods

#### `get(key: str) -> Optional[Any]`
Retrieve cached value if not expired.

**Parameters:**
- `key` (str): Cache key

**Returns:** Cached data or None

**Example:**
```python
cache = SmartCache(default_ttl_hours=24)
data = cache.get("polymarket_markets")
```

#### `set(key: str, value: Any, ttl_hours: Optional[int] = None)`
Store value in cache.

**Parameters:**
- `key` (str): Cache key
- `value` (Any): Data to cache
- `ttl_hours` (Optional[int]): Override default TTL

#### `clear()`
Clear all cached entries.

#### `get_cache_stats() -> Dict`
Get cache statistics.

**Returns:** Dictionary with cache info

---

## DataParser

Parse HTML and extract structured data.

### Methods

#### `extract_polymarket_markets(html: str) -> List[Dict]`
Extract market data from Polymarket HTML.

**Parameters:**
- `html` (str): HTML source code

**Returns:** List of market dictionaries

#### `extract_json_from_script(html: str, script_id: Optional[str] = None) -> Dict`
Extract JSON data from script tags.

**Parameters:**
- `html` (str): HTML source code
- `script_id` (Optional[str]): Specific script ID to extract

**Returns:** Parsed JSON data

#### `parse_table(html: str, table_id: Optional[str] = None) -> pd.DataFrame`
Parse HTML table to DataFrame.

**Parameters:**
- `html` (str): HTML source code
- `table_id` (Optional[str]): Specific table ID

**Returns:** Pandas DataFrame

#### `export_to_csv(data: List[Dict], filepath: str)`
Export data to CSV file.

**Parameters:**
- `data` (List[Dict]): Data to export
- `filepath` (str): Output filepath

#### `export_to_json(data: List[Dict], filepath: str)`
Export data to JSON file.

**Parameters:**
- `data` (List[Dict]): Data to export
- `filepath` (str): Output filepath

---

## Error Handling

### Common Exceptions

**TimeoutException**
```python
from selenium.common.exceptions import TimeoutException

try:
    data = crawler.extract_polymarket_markets()
except TimeoutException:
    print("Page load timeout")
```

**NoSuchElementException**
```python
from selenium.common.exceptions import NoSuchElementException

try:
    element = crawler.driver.find_element(By.ID, "missing")
except NoSuchElementException:
    print("Element not found")
```

---

## Configuration Examples

### Fast Scraping (No Cache)

```python
crawler = SeleniumCrawler(
    use_cache=False,
    headless=True,
    requests_per_minute=60  # High rate
)
```

### Safe Scraping (High Cache)

```python
crawler = SeleniumCrawler(
    use_cache=True,
    cache_ttl_hours=48,  # Long TTL
    requests_per_minute=10  # Low rate
)
```

### Authenticated Scraping

```python
auth = AuthManager()
auth.login_polymarket("user@example.com", "password")

crawler = SeleniumCrawler()
crawler.auth_manager = auth
crawler.start()
```

---

**Last Updated**: November 24, 2025
