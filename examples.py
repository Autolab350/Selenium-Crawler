#!/usr/bin/env python3
"""
Scraper Usage Examples
======================

All features demonstrated in one file. Copy-paste ready.
"""

from scraper import Scraper, scrape, scrape_batch, Format


# ============================================================================
# BASIC EXAMPLES
# ============================================================================

def example_1_basic():
    """Simplest possible usage"""
    result = scrape("https://techcrunch.com/2024/01/15/ai-breakthrough/")
    
    print(f"Title: {result['data']['article']['title']}")
    print(f"Author: {result['data']['article']['author']}")
    print(f"Read time: {result['data']['article']['read_time']}")


def example_2_custom_selectors():
    """Extract specific elements from any website"""
    result = scrape(
        url="https://amazon.com/s?k=laptop",
        selectors={
            "product_names": ".product-name",
            "prices": ".price",
            "ratings": ".rating"
        },
        scroll=True  # Load lazy content
    )
    
    print("Products found:")
    print(result['custom'])


def example_3_batch_scraping():
    """Scrape multiple URLs efficiently"""
    urls = [
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3"
    ]
    
    results = scrape_batch(urls, extract_all=True)
    
    for result in results:
        print(f"- {result['data']['metadata']['title']}")


def example_4_extract_tables():
    """Extract tables from Wikipedia or any site"""
    result = scrape("https://en.wikipedia.org/wiki/Cryptocurrency")
    
    tables = result['data']['tables']
    print(f"Found {len(tables)} tables")
    
    if tables:
        print(f"First table: {tables[0]}")


def example_5_metadata():
    """Extract SEO metadata and open graph tags"""
    result = scrape("https://example.com/article")
    
    meta = result['data']['metadata']
    print(f"Title: {meta['title']}")
    print(f"Description: {meta['description']}")
    print(f"Author: {meta['author']}")
    print(f"OG Image: {meta['og_image']}")


def example_6_structured_data():
    """Extract JSON-LD structured data"""
    result = scrape("https://www.imdb.com/title/tt0111161/")
    
    json_ld = result['data']['json_ld']
    print(f"Found {len(json_ld)} structured data blocks")
    print(json_ld[0] if json_ld else "No JSON-LD found")


def example_7_links():
    """Extract all links from page"""
    result = scrape("https://github.com/topics/web-scraping")
    
    links = result['data']['links']
    print(f"Internal links: {len(links['internal'])}")
    print(f"External links: {len(links['external'])}")
    print(f"Anchors: {len(links['anchors'])}")


def example_8_export():
    """Scrape and export to file"""
    with Scraper(cache_ttl=24) as scraper:
        result = scraper.scrape("https://example.com/data")
        
        # Export as JSON
        scraper.export(result, "output/data.json", fmt=Format.JSON)
        
        # Export table as CSV
        if result['data']['tables']:
            scraper.export(result['data']['tables'][0], "output/table.csv", fmt=Format.CSV)


def example_9_with_caching():
    """Use caching to avoid redundant requests"""
    with Scraper(cache_ttl=24) as scraper:
        # First request - fetches from web
        result1 = scraper.scrape("https://example.com")
        
        # Second request - from cache
        result2 = scraper.scrape("https://example.com")
        
        # They're the same
        assert result1 == result2
        
        # Clear cache if needed
        scraper.cache.clear()


def example_10_ai_analysis():
    """Combine with AI for intelligent analysis"""
    from openai import OpenAI
    
    client = OpenAI()
    
    with Scraper() as scraper:
        # Scrape content
        result = scraper.scrape("https://techcrunch.com/article")
        content = result['data']['article']['body']
        
        # Analyze with GPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Summarize this in 3 bullet points:\n\n{content[:2000]}"
            }]
        )
        
        print(response.choices[0].message.content)


def example_11_advanced_config():
    """Advanced configuration options"""
    with Scraper(
        cache_ttl=24,        # Cache for 24 hours
        req_per_min=10,      # Max 10 requests/min (avoid blocking)
        headless=True        # Run in background
    ) as scraper:
        result = scraper.scrape(
            url="https://example.com",
            wait_for=".dynamic-content",  # Wait for this element
            scroll=True,                   # Scroll to load lazy content
            extract_all=True,              # Extract everything
            use_cache=True                 # Use caching
        )
        
        print(result)


def example_12_error_handling():
    """Handle errors gracefully"""
    result = scrape("https://example.com/nonexistent")
    
    if result['status'] == 'error':
        print(f"Error: {result['message']}")
    else:
        print(f"Success: {result['data']['metadata']['title']}")


# ============================================================================
# REAL-WORLD EXAMPLES
# ============================================================================

def example_market_research():
    """Scrape competitor pricing"""
    with Scraper() as scraper:
        competitors = [
            "https://shop1.com/products",
            "https://shop2.com/products",
            "https://shop3.com/products"
        ]
        
        results = scraper.scrape_multiple(competitors, selectors={
            "names": ".product-name",
            "prices": ".price",
            "reviews": ".review-count"
        })
        
        # Analyze pricing
        for result in results:
            domain = result['url'].split('/')[2]
            custom = result['custom']
            print(f"{domain}: {len(custom['names'])} products")
        
        scraper.export(results, "competitor_analysis.json")


def example_news_aggregation():
    """Aggregate articles from multiple news sources"""
    news_sources = [
        "https://techcrunch.com/",
        "https://theverge.com/",
        "https://arstechnica.com/"
    ]
    
    with Scraper() as scraper:
        articles = scraper.scrape_multiple(
            news_sources,
            selectors={"headlines": "h2.headline", "snippets": ".snippet"},
            extract_all=False
        )
        
        for article in articles:
            print(f"\nSource: {article['url']}")
            print(f"Headlines: {article['custom']['headlines']}")


def example_prediction_market_feed():
    """Create prediction market feed from events"""
    # This combines with url_scraper_agent.py for market creation
    
    from scraper import scrape
    
    # Scrape event article
    result = scrape("https://techcrunch.com/2024/01/15/openai-releases-gpt5/")
    
    article = result['data']['article']
    
    # Create prediction event
    event = {
        "title": article['title'],
        "description": article['body'][:500],
        "source": result['data']['metadata']['domain'],
        "url": result['url'],
        "extracted_at": result['scraped_at'],
        "market_options": ["Yes", "No", "Delayed"]
    }
    
    print(f"Event ready for market: {event['title']}")
    # Pass to url_scraper_agent.py for blockchain market creation
    return event


# ============================================================================
# RUN EXAMPLES
# ============================================================================

if __name__ == "__main__":
    import sys
    
    examples = {
        "1": ("Basic scraping", example_1_basic),
        "2": ("Custom selectors", example_2_custom_selectors),
        "3": ("Batch scraping", example_3_batch_scraping),
        "4": ("Extract tables", example_4_extract_tables),
        "5": ("Extract metadata", example_5_metadata),
        "6": ("Structured data (JSON-LD)", example_6_structured_data),
        "7": ("Extract links", example_7_links),
        "8": ("Export data", example_8_export),
        "9": ("Caching", example_9_with_caching),
        "10": ("AI analysis", example_10_ai_analysis),
        "11": ("Advanced config", example_11_advanced_config),
        "12": ("Error handling", example_12_error_handling),
        "market_research": ("Market research", example_market_research),
        "news": ("News aggregation", example_news_aggregation),
        "prediction": ("Prediction market feed", example_prediction_market_feed),
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in examples:
        name, func = examples[sys.argv[1]]
        print(f"\n{'='*60}")
        print(f"Example: {name}")
        print(f"{'='*60}\n")
        try:
            func()
        except Exception as e:
            print(f"Error: {e}")
            print("\nNote: Some examples need real URLs or API keys")
    else:
        print(f"\n{'='*60}")
        print("Universal Web Scraper - Examples")
        print(f"{'='*60}\n")
        print("Available examples:")
        for key, (name, _) in examples.items():
            print(f"  python examples.py {key:<15} # {name}")
        print("\nExample:")
        print("  python examples.py 1          # Run basic scraping")
