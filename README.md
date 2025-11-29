# Universal Web Scraper

**Master key for web data extraction.** Works on ANY website. Max capability, minimum code.

---

## ⚡ Quick Start

```python
from scraper import scrape

# Scrape any URL
result = scrape("https://example.com/article")

# Access extracted data
print(result['data']['article']['title'])
print(result['data']['metadata']['author'])
print(result['data']['tables'])
```

---

## 🎯 Core Features

- ✨ **Works on ANY website** - articles, products, tables, metadata
- 🤖 **Intelligent extraction** - auto-detects content types
- 🧠 **Browser automation** - JS rendering, lazy loading, dynamic content
- 💾 **Smart caching** - TTL-based, prevents redundant requests
- 🎯 **Custom selectors** - CSS selectors for targeted extraction
- 📊 **Multiple formats** - JSON, CSV, DataFrames
- 🚀 **AI-ready** - works with OpenAI, Claude, etc.

---

## 📖 Usage

### Basic Scraping

```python
from scraper import scrape

# One-liner
result = scrape("https://techcrunch.com/article")
```

### Custom Extraction

```python
result = scrape(
    url="https://amazon.com/products",
    selectors={
        "names": ".product-name",
        "prices": ".price",
        "ratings": ".rating"
    },
    scroll=True  # Load lazy content
)

print(result['custom']['names'])
```

### Batch Scraping

```python
from scraper import scrape_batch

urls = ["https://example.com/1", "https://example.com/2"]
results = scrape_batch(urls)
```

### Advanced Configuration

```python
from scraper import Scraper

with Scraper(cache_ttl=24, req_per_min=10) as scraper:
    # Extract with custom options
    result = scraper.scrape(
        url="https://example.com",
        wait_for=".dynamic-element",  # Wait for element
        scroll=True,                    # Scroll to load content
        extract_all=True,               # Extract everything
        use_cache=True                  # Use caching
    )
    
    # Export to file
    from scraper import Format
    scraper.export(result, "output.json", fmt=Format.JSON)
```

---

## 📊 Extracted Data

All data automatically extracted:

```python
result['data'] = {
    'metadata': {
        'title', 'description', 'author', 'og_image', ...
    },
    'article': {
        'title', 'body', 'author', 'date', 'word_count', 'read_time'
    },
    'text': '...',           # Clean text
    'tables': [{...}],       # All tables
    'lists': {ul_0: [...]},  # Lists
    'json_ld': [{...}],      # Structured data
    'links': {
        'internal': [...],
        'external': [...],
        'anchors': [...]
    }
}
```

Plus custom data if selectors provided:
```python
result['custom'] = { 'selector_name': [...] }
```

---

## 🤖 AI Integration

```python
from openai import OpenAI
from scraper import scrape

client = OpenAI()

# Scrape
result = scrape("https://example.com/article")
content = result['data']['article']['body']

# Analyze with AI
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": f"Summarize: {content}"}]
)

print(response.choices[0].message.content)
```

---

## 📚 Examples

See all 15 examples:
```bash
python examples.py 1           # Basic scraping
python examples.py 2           # Custom selectors
python examples.py 3           # Batch scraping
python examples.py 4           # Extract tables
python examples.py 5           # Metadata
python examples.py 6           # Structured data
python examples.py 7           # Links
python examples.py 8           # Export
python examples.py 9           # Caching
python examples.py 10          # AI analysis
python examples.py 11          # Advanced config
python examples.py 12          # Error handling
python examples.py market_research
python examples.py news
python examples.py prediction
```

---

## 🔧 Configuration

```python
Scraper(
    cache_ttl=24,      # Cache TTL in hours (0 = disabled)
    req_per_min=30,    # Max requests per minute
    headless=True      # Run browser in background
)
```

---

## 📦 Installation

```bash
pip install selenium beautifulsoup4 webdriver-manager pandas openai
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Site blocks requests | Use `req_per_min=5` |
| JS content missing | Use `wait_for=".selector"` |
| Lazy content missing | Use `scroll=True` |
| Memory issues | Process in batches |

---

## 📁 Files

```
Selenium Crawler/
├── scraper.py        # Main module (all-in-one)
├── examples.py       # 15 usage examples
├── requirements.txt  # Dependencies
└── README.md         # This file
```

---

## ✨ Philosophy

- **One file, all features** - No unnecessary complexity
- **Works on ANY website** - Not tied to specific platforms
- **AI-ready** - Designed to work with modern AI
- **Production-ready** - Error handling, caching, rate limiting
- **Copy-paste examples** - Just run `examples.py`

---

## 🚀 Real-World Uses

- Market research (scrape competitor products)
- News aggregation (parse multiple sources)
- SEO analysis (extract metadata)
- Data collection (tables, structured data)
- AI analysis (feed to ChatGPT/Claude)
- Prediction markets (detect events → create markets)

---

Made for maximum capability with minimum complexity.
