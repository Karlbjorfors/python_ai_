"""
Main application entry point for the Review Scraper.

"""

import sys
from pathlib import Path
from typing import Optional, List

# Add project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from config.logging_config import setup_logging
from scraper.browser_manager import BrowserManager
from scraper.google_maps import GoogleMapsScraper
from scraper.review_extractor import ReviewExtractor
from utils.text_processor import TextProcessor
from utils.data_exporter import DataExporter
from models.review import ScrapingResult

class ReviewScraperApp:
    """Main application class for the Review Scraper."""
    
    def __init__(
        self, 
        business_name: str,
        max_reviews: Optional[int] = None,
        enable_translation: bool = True,
        headless: bool = False,
        output_dir: str = "."
    ):
        """
        Initialize the Review Scraper application.
        
        Args:
            business_name: Name of the business to scrape reviews for
            max_reviews: Maximum number of reviews to extract
            enable_translation: Whether to enable translation to English
            headless: Whether to run browser in headless mode
            output_dir: Directory to save output files
        """
        self.business_name = business_name
        self.max_reviews = max_reviews or settings.DEFAULT_MAX_REVIEWS
        self.enable_translation = enable_translation
        self.headless = headless
        
        # Initialize components
        self.logger = setup_logging()
        self.browser_manager = BrowserManager(headless=headless)
        self.text_processor = TextProcessor(enable_translation=enable_translation)
        self.data_exporter = DataExporter(output_directory=output_dir)
        
        # These will be initialized when browser starts
        self.google_maps_scraper: Optional[GoogleMapsScraper] = None
        self.review_extractor: Optional[ReviewExtractor] = None
    
    def _initialize_scrapers(self, page):
        """Initialize scraper components with the page instance."""
        self.google_maps_scraper = GoogleMapsScraper(page)
        self.review_extractor = ReviewExtractor(page, self.text_processor)
    
    def run(self) -> ScrapingResult:
        """
        Run the complete scraping process.
        
        Returns:
            ScrapingResult containing all extracted data and metadata
        """
        self.logger.info(f"Starting review scraping for: {self.business_name}")
        self.logger.info(f"Configuration: max_reviews={self.max_reviews}, translation={self.enable_translation}, headless={self.headless}")
        
        try:
            # Start browser session
            with self.browser_manager as page:
                self._initialize_scrapers(page)
                
                # Ensure scrapers are initialized
                assert self.google_maps_scraper is not None
                assert self.review_extractor is not None
                
                # Step 1: Navigate to Google Maps
                if not self.google_maps_scraper.navigate_to_maps():
                    raise Exception("Failed to navigate to Google Maps")
                
                # Step 2: Search for the business
                if not self.google_maps_scraper.search_business(self.business_name):
                    raise Exception(f"Failed to search for business: {self.business_name}")
                
                # Step 3: Navigate to reviews section
                if not self.google_maps_scraper.navigate_to_reviews():
                    raise Exception("Failed to navigate to reviews section")
                
                # Step 4: Load more reviews by scrolling
                total_reviews_loaded = self.google_maps_scraper.scroll_to_load_reviews()
                self.logger.info(f"Loaded {total_reviews_loaded} reviews by scrolling")
                
                # Step 5: Extract all reviews
                scraping_result = self.review_extractor.extract_all_reviews(
                    business_name=self.business_name,
                    max_reviews=self.max_reviews
                )
                
                self.logger.info(f"Scraping completed successfully. Extracted {scraping_result.total_extracted} reviews")
                return scraping_result
                
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            # Return empty result with error
            from datetime import datetime
            return ScrapingResult(
                business_name=self.business_name,
                reviews=[],
                total_found=0,
                total_extracted=0,
                errors=[str(e)],
                scraped_at=datetime.now()
            )
    
    def save_results(self, scraping_result: ScrapingResult, formats: Optional[List[str]] = None) -> dict:
        """
        Save scraping results in specified formats.
        
        Args:
            scraping_result: The scraping result to save
            formats: List of formats to save ('csv', 'json', 'summary')
            
        Returns:
            Dictionary with paths to saved files
        """
        if formats is None:
            formats = ['csv', 'summary']
        
        saved_files = {}
        
        try:
            if 'csv' in formats and scraping_result.reviews:
                csv_path = self.data_exporter.export_to_csv(
                    reviews=scraping_result.reviews,
                    filename=f"{self.business_name.lower().replace(' ', '_')}_reviews.csv"
                )
                saved_files['csv'] = csv_path
            
            if 'json' in formats:
                json_path = self.data_exporter.export_to_json(scraping_result)
                saved_files['json'] = json_path
            
            if 'summary' in formats:
                summary_path = self.data_exporter.export_summary_report(scraping_result)
                saved_files['summary'] = summary_path
            
            self.logger.info(f"Results saved to: {list(saved_files.values())}")
            return saved_files
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            return {}

def main():
    """Main function to run the scraper."""
    
    # Configuration - you can modify these values
    BUSINESS_NAME = "Rex"
    MAX_REVIEWS = 100
    ENABLE_TRANSLATION = False
    HEADLESS = False  # Set to True to hide browser window
    
    # Create and run the scraper
    app = ReviewScraperApp(
        business_name=BUSINESS_NAME,
        max_reviews=MAX_REVIEWS,
        enable_translation=ENABLE_TRANSLATION,
        headless=HEADLESS
    )
    
    # Run the scraping process
    result = app.run()
    
    # Save results in multiple formats
    saved_files = app.save_results(result, formats=['csv', 'json', 'summary'])
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"SCRAPING SUMMARY")
    print(f"{'='*50}")
    print(f"Business: {result.business_name}")
    print(f"Reviews found: {result.total_found}")
    print(f"Reviews extracted: {result.total_extracted}")
    print(f"Success rate: {result.success_rate:.1f}%")
    
    if result.errors:
        print(f"Errors: {len(result.errors)}")
    
    if saved_files:
        print(f"\nFiles saved:")
        for format_type, path in saved_files.items():
            print(f"  - {format_type.upper()}: {path}")
    
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
