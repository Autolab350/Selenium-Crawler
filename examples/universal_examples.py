#!/usr/bin/env python3
"""
Universal Web Scraper Examples
================================

Demonstrates the "master key" web scraping capabilities.
Works on any website - news, e-commerce, forums, documentation, etc.
"""

from core.universal_scraper import UniversalWebScraper, OutputFormat
import json


def example_1_news_article():
    """Extract article content from any news website"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Extract News Article")
    print("="*60)
    
    url = "https://news.ycombinator.com/item?id=38000000"
    
    with UniversalWebScraper(use_cache=True, headless=True) as scraper:
        result = scraper.scrape(
            url=url,
            extract_all=True,
            wait_for_selector=".titleline"  # Wait for content to load
        )
        
        # Extract article data
        if result.get("status") == "success":
            article = result["data"]["article"]
            print(f"\nTitle: {article['title']}")
            print(f"Word Count: {article['word_count']}")
            print(f"Read Time: {article['estimated_read_time']}")
            print(f"\nBody (first 500 chars):\n{article['body'][:500]}...")


def example_2_ecommerce_products():
    """Extract product listings from e-commerce site"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Extract E-Commerce Products")
    print("="*60)
    
    url = "https://example-shop.com/products"
    
    # Custom selectors for product data
    selectors = {
        "product_names": ".product-name",
        "prices": ".price",
        "ratings": ".rating",
        "product_urls": "a.product-link"
    }
    
    with UniversalWebScraper(use_cache=True) as scraper:
        result = scraper.scrape(
            url=url,
            selectors=selectors,
            extract_all=False,
            scroll=True  # Scroll to load lazy-loaded products
        )
        
        print(f"\nExtracted from: {result['url']}")
        print(f"Custom Data: {json.dumps(result['custom_data'], indent=2)[:500]}...")


def example_3_metadata_extraction():
    """Extract page metadata (SEO, social, etc.)"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Extract Page Metadata")
    print("="*60)
    
    url = "https://techcrunch.com/2024/01/15/openai-releases-gpt5/"
    
    with UniversalWebScraper() as scraper:
        result = scraper.scrape(url=url, extract_all=True)
        
        metadata = result["data"]["metadata"]
        print(f"\nTitle: {metadata['title']}")
        print(f"Description: {metadata['description']}")
        print(f"Author: {metadata['author']}")
        print(f"Published: {metadata['published_date']}")
        print(f"Language: {metadata['language']}")
        print(f"Domain: {metadata['domain']}")
        print(f"Keywords: {', '.join(metadata['keywords'][:5])}")
        
        if metadata['og_image']:
            print(f"OG Image: {metadata['og_image']}")


def example_4_table_extraction():
    """Extract all tables from page"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Extract Tables")
    print("="*60)
    
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    
    with UniversalWebScraper() as scraper:
        result = scraper.scrape(url=url, extract_all=True)
        
        tables = result["data"]["tables"]
        print(f"\nFound {len(tables)} tables on page")
        
        if tables:
            print("\nFirst table (first 3 rows):")
            import pandas as pd
            df = pd.DataFrame(tables[0])
            print(df.head(3).to_string())


def example_5_multiple_urls():
    """Scrape multiple URLs in batch"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Batch Scrape Multiple URLs")
    print("="*60)
    
    urls = [
        "https://github.com/topics/web-scraping",
        "https://github.com/topics/web-crawling",
        "https://github.com/topics/data-extraction"
    ]
    
    with UniversalWebScraper(use_cache=True) as scraper:
        results = scraper.scrape_multiple(urls, extract_all=True)
        
        for result in results:
            metadata = result["data"]["metadata"]
            print(f"\n{metadata['title']}")
            print(f"Description: {metadata['description'][:100]}...")


def example_6_structured_data():
    """Extract JSON-LD structured data"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Extract Structured Data (JSON-LD)")
    print("="*60)
    
    url = "https://www.imdb.com/title/tt0111161/"
    
    with UniversalWebScraper() as scraper:
        result = scraper.scrape(url=url, extract_all=True)
        
        json_ld = result["data"]["json_ld"]
        print(f"\nFound {len(json_ld)} JSON-LD blocks")
        
        if json_ld:
            print(f"\nStructured Data (first block):\n{json.dumps(json_ld[0], indent=2)[:500]}...")


def example_7_links_extraction():
    """Extract all links from page"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Extract All Links")
    print("="*60)
    
    url = "https://www.python.org/"
    
    with UniversalWebScraper() as scraper:
        result = scraper.scrape(url=url, extract_all=True)
        
        links = result["data"]["links"]
        print(f"\nInternal Links: {len(links['internal'])}")
        print(f"External Links: {len(links['external'])}")
        print(f"Anchors: {len(links['anchors'])}")
        
        print(f"\nFirst 5 Internal Links:")
        for link in links['internal'][:5]:
            print(f"  - {link}")


def example_8_custom_selectors():
    """Use custom CSS selectors for targeted extraction"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Custom CSS Selectors")
    print("="*60)
    
    url = "https://example.com/blog"
    
    selectors = {
        "post_titles": "h2.post-title",
        "post_dates": ".post-meta .date",
        "post_authors": ".post-meta .author",
        "featured_image": "img.featured"
    }
    
    with UniversalWebScraper() as scraper:
        result = scraper.scrape(
            url=url,
            selectors=selectors,
            extract_all=False
        )
        
        print(f"\nCustom Data from {url}:")
        print(json.dumps(result['custom_data'], indent=2)[:500])


def example_9_export_data():
    """Scrape and export data to files"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Scrape & Export Data")
    print("="*60)
    
    url = "https://example.com/products"
    
    with UniversalWebScraper(use_cache=True) as scraper:
        # Scrape
        result = scraper.scrape(
            url=url,
            extract_all=True,
            scroll=True
        )
        
        # Export as JSON
        scraper.export(
            result,
            "output/scraped_data.json",
            format=OutputFormat.JSON
        )
        
        # Export tables as CSV
        tables = result["data"]["tables"]
        if tables:
            scraper.export(
                tables[0],
                "output/table_data.csv",
                format=OutputFormat.CSV
            )
        
        print(f"✓ Exported to output/")
        print(f"✓ Stats: {scraper.get_stats()}")


def example_10_ai_powered():
    """AI-powered analysis of extracted content (requires OpenAI)"""
    print("\n" + "="*60)
    print("EXAMPLE 10: AI-Powered Content Analysis")
    print("="*60)
    
    print("\nNote: Requires OpenAI API key in .env")
    print("This example shows how to integrate AI analysis with scraping.")
    print("""
    from openai import OpenAI
    
    client = OpenAI()
    
    with UniversalWebScraper() as scraper:
        result = scraper.scrape(url="https://example.com/article")
        
        # Use AI to analyze content
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Summarize this: {result['data']['article']['body']}"
            }]
        )
        
        print(f"AI Summary: {response.choices[0].message.content}")
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("UNIVERSAL WEB SCRAPER - USAGE EXAMPLES")
    print("Master Key for Web Data Extraction")
    print("="*60)
    
    # Uncomment examples to run (note: requires actual URLs to work)
    
    # example_1_news_article()
    # example_2_ecommerce_products()
    # example_3_metadata_extraction()
    # example_4_table_extraction()
    # example_5_multiple_urls()
    # example_6_structured_data()
    # example_7_links_extraction()
    # example_8_custom_selectors()
    # example_9_export_data()
    example_10_ai_powered()
    
    print("\n✓ Examples complete!")
