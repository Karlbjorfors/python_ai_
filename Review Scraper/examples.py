"""
Example usage of the modular Review Scraper.

This file demonstrates different ways to use the new modular architecture.
"""

from main import ReviewScraperApp
from config.settings import settings

def example_basic_usage():
    """Example of basic usage."""
    print("=== Basic Usage Example ===")
    
    app = ReviewScraperApp(
        business_name="Pizzeria Example Stockholm",
        max_reviews=50,
        enable_translation=True,
        headless=False
    )
    
    result = app.run()
    saved_files = app.save_results(result)
    
    print(f"Extracted {result.total_extracted} reviews")
    print(f"Files saved: {saved_files}")

def example_headless_batch():
    """Example of running multiple businesses in headless mode."""
    print("=== Headless Batch Processing Example ===")
    
    businesses = [
        "Restaurant ABC Stockholm",
        "Cafe XYZ Malmö",
        "Pizzeria 123 Göteborg"
    ]
    
    for business in businesses:
        print(f"\nProcessing: {business}")
        
        app = ReviewScraperApp(
            business_name=business,
            max_reviews=30,
            enable_translation=True,
            headless=True  # Run without showing browser
        )
        
        result = app.run()
        app.save_results(result, formats=['csv', 'summary'])
        
        print(f"Completed: {result.total_extracted} reviews extracted")

def example_custom_configuration():
    """Example with custom configuration."""
    print("=== Custom Configuration Example ===")
    
    # Override default settings
    settings.DEFAULT_MAX_REVIEWS = 200
    settings.SCROLL_ATTEMPTS = 20
    settings.ENABLE_TRANSLATION = False
    
    app = ReviewScraperApp(
        business_name="High-volume Restaurant",
        max_reviews=settings.DEFAULT_MAX_REVIEWS,
        enable_translation=settings.ENABLE_TRANSLATION,
        headless=True,
        output_dir="./custom_output"
    )
    
    result = app.run()
    saved_files = app.save_results(result, formats=['csv', 'json', 'summary'])
    
    print(f"Results: {result.total_extracted} reviews")
    print(f"Saved to: {saved_files}")

if __name__ == "__main__":
    # Run the basic example
    # Uncomment the example you want to test:
    
    example_basic_usage()
    # example_headless_batch()
    # example_custom_configuration()
