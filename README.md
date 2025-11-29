# Selenium Crawler - Web Scraping & Automation

Intelligent web scraping framework for automated data extraction from dynamic websites. Built for trading platforms like Polymarket, HexTrade, and TopStep.

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from core.crawler import SeleniumCrawler

# Simple extraction
with SeleniumCrawler(headless=True) as crawler:
    markets = crawler.extract_polymarket_markets()
    print(f"Extracted {len(markets)} markets")
```

## 📁 Project Structure

```
Selenium Crawler/
├── core/                           # Core modules
│   ├── __init__.py
│   ├── crawler.py                  # Main orchestration engine
│   ├── browser_config.py           # Selenium setup & control
│   ├── auth_manager.py             # Login & session handling
│   ├── rate_limiter.py             # Request throttling
│   ├── smart_cache.py              # Intelligent caching (TTL-based)
│   └── data_parser.py              # HTML parsing & extraction
│
├── examples/                       # Usage examples
│   ├── basic_extraction.py         # Simple market data extraction
│   └── platform_integration.py     # Platform-specific integration
│
├── platforms/                      # Platform-specific configs
│   ├── polymarket/                 # Polymarket guides
│   ├── hextrade/                   # HexTrade automation
│   │   └── HEXTRADE_EXAMPLE.txt
│   └── topstep/                    # TopStep trading automation
│       ├── TOPSTEP_AUTOMATION.txt
│       └── TOPSTEP_SIMPLE.txt
│
├── docs/                           # Documentation
│   ├── PROJECT_GUIDE.txt           # Technical documentation
│   ├── INSTALL.txt                 # Installation guide
│   └── Log_Crawler.md              # Original markdown docs
│
├── url_scraper_agent/              # AI agent for market creation (separate project)
├── README.md                       # This file
├── requirements.txt                # Python dependencies
└── archive/                        # Legacy files
```

## 🔧 Core Features

### Browser Automation
- Headless Chrome with Selenium
- JavaScript execution support
- Dynamic element waiting
- Page scrolling for lazy-loaded content
- Screenshot and source capture

### Authentication
- Automated login flows
- Cookie persistence
- Session management
- Multi-platform support

### Rate Limiting
- Configurable requests per minute
- Automatic inter-request delays
- Backoff strategy
- Statistics tracking

### Intelligent Caching
- TTL-based expiration
- MD5 hash key generation
- Automatic cleanup
- Cache statistics

### Data Parsing
- BeautifulSoup HTML extraction
- JSON parsing from scripts
- Table extraction to CSV/JSON
- Polymarket-specific extractors

## 📚 Usage Examples

### Example 1: Basic Market Extraction

```python
from core.crawler import SeleniumCrawler

crawler = SeleniumCrawler(use_cache=True, headless=True)
crawler.start()

# Extract markets
markets = crawler.extract_polymarket_markets()

# Save results
crawler.save_results(markets, format="json")

# Get status
status = crawler.get_crawler_status()
print(f"Extracted {len(markets)} markets")
print(f"Cache enabled: {status['cache_enabled']}")

crawler.stop()
```

See: `examples/basic_extraction.py`

### Example 2: Platform Integration

```python
from core.crawler import SeleniumCrawler

# Use context manager for automatic cleanup
with SeleniumCrawler() as crawler:
    # HexTrade extraction
    data = crawler.extract_platform_data("hextrade")
    
    # Multi-page navigation
    all_data = []
    for page in range(1, 5):
        page_data = crawler.get_page_data(page)
        all_data.extend(page_data)
    
    print(f"Extracted {len(all_data)} items across multiple pages")
```

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
