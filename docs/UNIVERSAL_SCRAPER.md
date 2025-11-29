# Universal Web Scraper - Master Key for Web Data Extraction

## Overview

The **Universal Web Scraper** is a generalized, production-ready framework for intelligently extracting data from ANY website. It's designed as a "master key" that works across different types of websites - news articles, e-commerce, forums, documentation, social media, and more.

### Key Philosophy

Instead of building platform-specific scrapers (Polymarket, HexTrade, etc.), this engine extracts **meaningful data from any HTML** using:

- **Intelligent extraction** - Recognizes articles, tables, metadata, lists automatically
- **Flexible selectors** - CSS selectors for custom extraction
- **Browser automation** - Handles JavaScript, dynamic content, lazy loading
- **Smart caching** - Avoids redundant requests with TTL-based caching
- **Rate limiting** - Respects server resources with adaptive backoff
- **AI integration** - Can be paired with OpenAI/Claude for semantic analysis

---

## Installation

```bash
pip install -r requirements.txt
```

### Requirements

```
selenium>=4.10.0
beautifulsoup4>=4.12.0
webdriver-manager>=3.9.0
pandas>=2.0.0
openai>=1.0.0  # Optional: for AI analysis
```

---

## Quick Start

### Basic Usage

```python
from core.universal_scraper import UniversalWebScraper

# Simple scrape
scraper = UniversalWebScraper(use_cache=True, headless=True)
result = scraper.scrape(url="https://example.com/article")

print(result["data"]["article"]["title"])
print(result["data"]["article"]["body"])

scraper.close()
```

### Using Context Manager (Recommended)

```python
from core.universal_scraper import UniversalWebScraper

with UniversalWebScraper() as scraper:
    result = scraper.scrape("https://example.com")
    print(result["data"]["metadata"]["title"])
```

---

## Core Features

### 1. Automatic Content Detection

The scraper **automatically identifies** different content types:

#### Article/Blog Post

```python
result = scraper.scrape("https://blog.example.com/article")
article = result["data"]["article"]

# Extract:
# - article["title"]        - Article headline
# - article["body"]         - Full text content
# - article["author"]       - Author name
# - article["publish_date"] - Publication date
# - article["word_count"]   - Word count
# - article["estimated_read_time"] - Reading time
```

#### Metadata (SEO, Social, OG tags)

```python
metadata = result["data"]["metadata"]

# Extract:
# - metadata["title"]            - Page title
# - metadata["description"]      - Meta description
# - metadata["og_image"]         - Open Graph image
# - metadata["author"]           - Author/creator
# - metadata["published_date"]   - Published date
# - metadata["keywords"]         - Keywords array
# - metadata["language"]         - Page language
```

#### Tables

```python
tables = result["data"]["tables"]  # List of pandas DataFrames

# Each table is automatically parsed as a DataFrame
for i, table in enumerate(tables):
    print(f"Table {i}:")
    print(table)
```

#### Lists

```python
lists = result["data"]["lists"]  # Dict of lists found on page

# Extract:
# - lists["list_ul_0"]  - Unordered list
# - lists["list_ol_0"]  - Ordered list
```

#### Links

```python
links = result["data"]["links"]

# Extract:
# - links["internal"]  - Internal links (same domain)
# - links["external"]  - External links
# - links["anchors"]   - Anchor links (#section)
```

#### Structured Data (JSON-LD)

```python
json_ld = result["data"]["json_ld"]  # List of structured data objects

# Common types:
# - Article, NewsArticle
# - Product, Person, Organization
# - Event, VideoObject
# - etc.
```

### 2. Custom CSS Selectors

Extract specific elements using CSS selectors:

```python
selectors = {
    "product_names": ".product-name",
    "prices": ".price",
    "ratings": ".rating",
    "images": "img.thumbnail"
}

result = scraper.scrape(
    url="https://shop.example.com/products",
    selectors=selectors,
    extract_all=False
)

custom_data = result["custom_data"]
print(custom_data["product_names"])  # List of product names
```

### 3. Browser Automation

Handle dynamic content and JavaScript-heavy websites:

```python
result = scraper.scrape(
    url="https://app.example.com",
    wait_for_selector=".dynamic-content",  # Wait for element
    scroll=True  # Scroll to load lazy content
)
```

### 4. Intelligent Caching

Avoid redundant requests with TTL-based caching:

```python
scraper = UniversalWebScraper(
    use_cache=True,
    cache_ttl_hours=24  # Cache for 24 hours
)

# First request: Fetches from web
result1 = scraper.scrape("https://example.com")

# Second request: Returns from cache
result2 = scraper.scrape("https://example.com")

# Clear cache if needed
scraper.cache.clear()
```

### 5. Rate Limiting with Adaptive Backoff

Respects server resources:

```python
scraper = UniversalWebScraper(
    requests_per_minute=30,  # Max 30 requests/min
)

# Scraper automatically:
# - Waits between requests
# - Increases backoff on failures
# - Decreases backoff on success

stats = scraper.get_stats()
print(stats["rate_limiter"])
```

### 6. Batch Scraping

Scrape multiple URLs efficiently:

```python
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

results = scraper.scrape_multiple(urls, extract_all=True)

for result in results:
    print(result["data"]["metadata"]["title"])
```

### 7. Export Data

Save extracted data to files:

```python
from core.universal_scraper import OutputFormat

# Export as JSON
scraper.export(
    data=result,
    filepath="output/data.json",
    format=OutputFormat.JSON
)

# Export as CSV
scraper.export(
    data=result["data"]["tables"][0],
    filepath="output/table.csv",
    format=OutputFormat.CSV
)
```

---

## Advanced Usage

### AI-Powered Analysis

Combine web scraping with AI for intelligent content understanding:

```python
from openai import OpenAI

client = OpenAI()

with UniversalWebScraper() as scraper:
    # Scrape content
    result = scraper.scrape("https://techcrunch.com/article")
    article = result["data"]["article"]
    
    # Use AI to understand it
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Summarize this article in 3 bullet points:\n\n{article['body']}"
        }]
    )
    
    print(response.choices[0].message.content)
```

### Custom Extraction Pipeline

Create specialized extraction for your use case:

```python
def extract_news_sources(url):
    """Extract news with publication source"""
    scraper = UniversalWebScraper()
    
    result = scraper.scrape(
        url=url,
        selectors={
            "headlines": "h2.headline",
            "byline": ".byline",
            "content": ".article-body",
            "published": "time[datetime]"
        }
    )
    
    metadata = result["data"]["metadata"]
    custom = result["custom_data"]
    
    return {
        "source": metadata["domain"],
        "title": metadata["title"],
        "author": custom["byline"],
        "content": custom["content"],
        "published": custom["published"],
        "url": url
    }

news = extract_news_sources("https://example.com/news")
```

### Streaming Large Datasets

For large-scale scraping:

```python
import json

urls = load_urls_from_file("urls.txt")
scraper = UniversalWebScraper(use_cache=True)

# Stream results to JSONL (one JSON per line)
with open("results.jsonl", "w") as f:
    for url in urls:
        try:
            result = scraper.scrape(url, extract_all=True)
            f.write(json.dumps(result) + "\n")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
```

---

## Data Types & Structures

### Scrape Result Structure

```json
{
  "url": "https://example.com",
  "scraped_at": "2024-01-15T10:30:00",
  "status": "success",
  "data": {
    "metadata": { ... },
    "text": "...",
    "tables": [ ... ],
    "lists": { ... },
    "json_ld": [ ... ],
    "links": { ... },
    "article": { ... }
  },
  "custom_data": { ... }
}
```

### Common Data Patterns

**E-Commerce Product:**
```python
selectors = {
    "name": ".product-title",
    "price": ".product-price",
    "rating": ".product-rating",
    "reviews": ".review-count",
    "image": "img.product-image",
    "description": ".product-description"
}
```

**News Article:**
```python
selectors = {
    "headline": "h1",
    "author": ".author-name",
    "date": "time[datetime]",
    "category": ".article-category",
    "body": ".article-body",
    "tags": "a.article-tag"
}
```

**Social Media Post:**
```python
selectors = {
    "author": ".post-author",
    "timestamp": ".post-time",
    "content": ".post-content",
    "likes": ".like-count",
    "comments": ".comment-count",
    "shares": ".share-count"
}
```

---

## Configuration

### Environment Variables

```bash
# .env file
CACHE_TTL_HOURS=24
REQUESTS_PER_MINUTE=30
HEADLESS_BROWSER=true
BROWSER_TIMEOUT=30
```

### Initialization Options

```python
scraper = UniversalWebScraper(
    use_cache=True,              # Enable caching
    requests_per_minute=30,      # Rate limit
    cache_ttl_hours=24,          # Cache expiration
    headless=True                # Headless browser
)
```

---

## Performance Tips

### 1. Use Caching

```python
# Good - Cache enabled
scraper = UniversalWebScraper(use_cache=True)
```

### 2. Batch Operations

```python
# Good - Process multiple URLs efficiently
results = scraper.scrape_multiple(urls)

# Bad - Creates overhead
for url in urls:
    scraper.scrape(url)
```

### 3. Extract Only What You Need

```python
# Good - Only extract what you need
result = scraper.scrape(
    url=url,
    selectors={"product_name": ".name"},
    extract_all=False
)

# Okay - Extract everything
result = scraper.scrape(url=url, extract_all=True)
```

### 4. Respect Rate Limits

```python
# Good - Reasonable rate
scraper = UniversalWebScraper(requests_per_minute=10)

# Bad - Too aggressive
scraper = UniversalWebScraper(requests_per_minute=1000)
```

---

## Error Handling

```python
from core.universal_scraper import UniversalWebScraper

with UniversalWebScraper() as scraper:
    try:
        result = scraper.scrape("https://example.com")
        
        if result.get("status") == "success":
            print(result["data"]["metadata"]["title"])
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"Scraping failed: {e}")
```

---

## Use Cases

### 1. Market Research
- Extract product data from e-commerce sites
- Monitor competitor pricing
- Analyze product reviews and ratings

### 2. News Aggregation
- Extract articles from multiple news sources
- Parse metadata and structured data
- Automated content curation

### 3. SEO Analysis
- Extract metadata and Open Graph tags
- Analyze page structure
- Monitor keyword presence

### 4. Content Intelligence
- Extract information for AI analysis
- Generate summaries and insights
- Feed data to machine learning models

### 5. Data Collection
- Gather structured data (tables, lists)
- Extract contact information
- Aggregate directory data

### 6. Integration with AI
- Feed extracted content to ChatGPT/Claude
- Generate insights automatically
- Create prediction markets from events

---

## Troubleshooting

### Website Blocks Requests
```python
# Increase delay between requests
scraper = UniversalWebScraper(requests_per_minute=5)
```

### JavaScript Not Rendered
```python
# Wait for dynamic content
result = scraper.scrape(
    url=url,
    wait_for_selector=".dynamic-element"
)
```

### Lazy-Loaded Content Missing
```python
# Scroll to trigger lazy loading
result = scraper.scrape(
    url=url,
    scroll=True
)
```

### Memory Issues
```python
# Process in batches, clear cache
results = scraper.scrape_multiple(urls[:100])
scraper.cache.clear()
results = scraper.scrape_multiple(urls[100:])
```

---

## API Reference

### UniversalWebScraper

**Methods:**
- `fetch(url, wait_for_selector, scroll)` - Get HTML
- `scrape(url, selectors, extract_all, wait_for_selector, scroll, use_cache)` - Scrape and extract
- `scrape_multiple(urls, **kwargs)` - Batch scrape
- `export(data, filepath, format)` - Save data
- `close()` - Cleanup
- `get_stats()` - Get statistics

### UniversalExtractor

**Static Methods:**
- `extract_text(html, max_length)` - Extract clean text
- `extract_metadata(html, url)` - Extract metadata
- `extract_tables(html)` - Extract all tables
- `extract_lists(html)` - Extract lists
- `extract_json_ld(html)` - Extract structured data
- `extract_links(html, base_url)` - Extract links
- `extract_by_selector(html, selectors)` - Extract with CSS selectors
- `extract_article(html)` - Extract article content
- `extract_all(html, url)` - Extract everything

---

## License

MIT License

---

## Support

For issues, questions, or contributions, please open an issue on GitHub.
