"""
Selenium Crawler Core Module

Unified web scraping framework with:
- Headless browser automation (Selenium 4.10+)
- Smart caching with TTL expiration
- Rate limiting and request throttling
- HTML parsing and data extraction
- Authentication and session management

Usage:
    from core import SeleniumCrawler
    
    with SeleniumCrawler() as crawler:
        html = crawler.fetch_page("https://example.com")
        markets = crawler.extract_polymarket_markets()
"""

from .crawler_engine import (
    SeleniumCrawler,
    BrowserConfig,
    AuthManager,
    RateLimiter,
    SmartCache,
    DataParser
)

__version__ = "2.0"
__author__ = "Trading Automation"

__all__ = [
    "SeleniumCrawler",
    "BrowserConfig",
    "AuthManager",
    "RateLimiter",
    "SmartCache",
    "DataParser"
]
