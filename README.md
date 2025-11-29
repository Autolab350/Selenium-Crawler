# Universal Web Scraper - Master Key for Web Data Extraction

A generalized, intelligent web scraping engine that works on **ANY website**. Extract meaningful data from news articles, e-commerce sites, forums, documentation, social media, and more using browser automation, AI integration, and smart extraction.

**Previous Version:** Legacy trading platform-specific scrapers (Polymarket, HexTrade, TopStep) now unified into a universal engine.

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage - Works on ANY Website

```python
from core.universal_scraper import UniversalWebScraper

# Scrape any URL
with UniversalWebScraper() as scraper:
    result = scraper.scrape("https://techcrunch.com/article")
    
    # Automatically extract:
    article = result["data"]["article"]        # Article title, body, author, date
    metadata = result["data"]["metadata"]      # SEO, OG tags, keywords
    tables = result["data"]["tables"]          # All HTML tables as DataFrames
    links = result["data"]["links"]            # Internal, external, anchors
    json_ld = result["data"]["json_ld"]        # Structured data
    
    print(f"Title: {article['title']}")
    print(f"By: {article['author']}")
```

### Custom Extraction with CSS Selectors

```python
# Extract specific elements
result = scraper.scrape(
    url="https://shop.example.com/products",
    selectors={
        "product_names": ".product-name",
        "prices": ".price",
        "ratings": ".rating"
    },
    scroll=True  # Scroll to load lazy content
)

print(result["custom_data"]["product_names"])
```

## 📁 Project Structure

```
Selenium Crawler/
├── core/
│   ├── __init__.py
│   ├── universal_scraper.py        # ⭐ Universal scraper engine
│   └── crawler_engine.py           # Legacy: trading platform support
│
├── examples/
│   ├── universal_examples.py       # Examples for all website types
│   └── basic_extraction.py         # Legacy examples
│
├── docs/
│   ├── UNIVERSAL_SCRAPER.md        # ⭐ Full documentation
│   ├── PROJECT_GUIDE.txt           # Technical details
│   ├── API_reference.md            # API docs
│   └── INSTALL.txt                 # Installation guide
│
├── README.md                       # This file
├── requirements.txt                # Python dependencies
└── url_scraper_agent/              # AI-powered market creator
```

## 🔧 Core Features

### Universal Data Extraction
- **Article Detection** - Automatically extract article titles, bodies, authors, dates
- **Metadata Extraction** - SEO metadata, Open Graph tags, keywords, structured data
- **Table Parsing** - Extract all HTML tables as pandas DataFrames
- **List Extraction** - Unordered and ordered lists
- **JSON-LD** - Structured data (schema.org, etc.)
- **Link Extraction** - Internal, external, anchor links
- **Custom Selectors** - CSS selectors for targeted extraction

### Browser Automation
- Headless Chrome with Selenium
- JavaScript execution & DOM rendering
- Dynamic element waiting
- Page scrolling for lazy-loaded content
- Screenshot & source capture

### Intelligent Features
- **Smart Caching** - TTL-based caching, MD5 hash keys
- **Rate Limiting** - Configurable requests/min with adaptive backoff
- **Error Recovery** - Automatic retry with exponential backoff
- **Session Management** - Cookie persistence, authentication

### Export & Integration
- JSON, CSV, DataFrame formats
- Batch scraping of multiple URLs
- Statistics & monitoring
- AI-ready (compatible with OpenAI, Claude, etc.)

## 📚 Usage Examples

### Example 1: News Article Extraction

```python
from core.universal_scraper import UniversalWebScraper

with UniversalWebScraper() as scraper:
    result = scraper.scrape("https://techcrunch.com/article")
    article = result["data"]["article"]
    
    print(article["title"])
    print(article["word_count"])
    print(article["estimated_read_time"])
```

### Example 2: E-Commerce Products

```python
with UniversalWebScraper() as scraper:
    result = scraper.scrape(
        url="https://shop.example.com/products",
        selectors={
            "names": ".product-name",
            "prices": ".price",
            "ratings": ".rating"
        },
        scroll=True  # Load lazy content
    )
    
    products = result["custom_data"]
```

### Example 3: Extract Tables

```python
with UniversalWebScraper() as scraper:
    result = scraper.scrape("https://en.wikipedia.org/wiki/Python_(programming_language)")
    
    # All tables extracted as pandas DataFrames
    for i, table in enumerate(result["data"]["tables"]):
        print(f"Table {i}: {table.shape}")
        print(table)
```

### Example 4: Batch Scraping

```python
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

with UniversalWebScraper(use_cache=True) as scraper:
    results = scraper.scrape_multiple(urls)
    
    for result in results:
        print(result["data"]["metadata"]["title"])
```

See full examples: `examples/universal_examples.py`

See: `examples/platform_integration.py` and `platforms/hextrade/`

## ⚙️ Configuration

### Rate Limiting

```python
crawler = SeleniumCrawler(
    requests_per_minute=30,  # 30 requests per minute
    headless=True
)
```

### Caching

```python
crawler = SeleniumCrawler(
    use_cache=True,           # Enable caching
    cache_ttl_hours=24        # 24-hour TTL
)

# Get cache statistics
stats = crawler.cache.get_cache_stats()
print(f"Cached {stats['total_entries']} entries")

# Clear cache
crawler.cache.clear()
```

### Authentication

```python
from core.auth_manager import AuthManager

auth = AuthManager()
auth.login_polymarket(username="user@example.com", password="pass")

# Use authenticated session
crawler.auth_manager = auth
```

## 📖 Platform-Specific Guides

- **Polymarket**: See examples and `platforms/polymarket/`
- **HexTrade**: See `platforms/hextrade/HEXTRADE_EXAMPLE.txt`
- **TopStep**: See `platforms/topstep/TOPSTEP_AUTOMATION.txt` and `TOPSTEP_SIMPLE.txt`

## 🔌 Integration with Agents

The crawler integrates seamlessly with AI agents for automated workflows:

```python
# Use with AI agent router
from core.crawler import SeleniumCrawler

crawler = SeleniumCrawler()
crawler.start()

# Agent queries crawler
agent_results = crawler.extract_polymarket_markets()

# Agent processes results
processed = process_market_data(agent_results)

# Agent stores findings
save_to_database(processed)

crawler.stop()
```

## 📊 Performance Metrics

- **Average extraction time**: 5-30 seconds per page (depending on content)
- **Cache hit rate**: 80-90% with 24h TTL
- **Memory usage**: 150-300MB per Chrome instance
- **Concurrent crawlers**: 3-5 recommended (OS-dependent)

## 🐛 Troubleshooting

### Issue: "ChromeDriver not found"
**Solution**: Install webdriver-manager (included in requirements.txt)

### Issue: "JavaScript not executing"
**Solution**: Ensure `headless=False` or increase page wait time

### Issue: "Rate limited by target site"
**Solution**: Decrease `requests_per_minute` or add delays

### Issue: "Memory leak after long runs"
**Solution**: Periodically restart crawler instances or use context manager

## 🔗 Related Projects

- **url_scraper_agent/**: AI-powered URL scraping and market creation (separate project)
- **Navitaire/API Testground/**: API testing infrastructure
- **Navitaire/Network Testground/**: Network automation

## 📝 Dependencies

- `selenium>=4.10.0` - Browser automation
- `beautifulsoup4>=4.12.0` - HTML parsing
- `webdriver-manager>=3.9.0` - ChromeDriver management
- `pandas>=2.0.0` - Data manipulation

## 📄 Documentation

- **PROJECT_GUIDE.txt**: Technical implementation details
- **INSTALL.txt**: Step-by-step installation
- **Log_Crawler.md**: Original development documentation
- **Platform guides**: See `platforms/` directory

## 🤝 Contributing

When adding new features:
1. Add platform-specific code to `platforms/`
2. Update examples in `examples/`
3. Document in `docs/`
4. Keep core modules in `core/`

---

**Last Updated**: November 24, 2025
