"""
Configuration settings for the Review Scraper application.
"""

import os
from typing import Dict, Any

class Settings:
    """Application settings and configuration."""
    
    # Browser settings
    BROWSER_HEADLESS: bool = False
    BROWSER_TIMEOUT: int = 30000
    PAGE_LOAD_TIMEOUT: int = 5000
    
    # Scraping settings
    DEFAULT_MAX_REVIEWS: int = 100
    SCROLL_ATTEMPTS: int = 15
    SCROLL_DISTANCE: int = 3000
    SCROLL_WAIT_TIME: int = 2000
    
    # Translation settings
    ENABLE_TRANSLATION: bool = True
    TARGET_LANGUAGE: str = 'en'
    
    # Output settings
    DEFAULT_OUTPUT_FORMAT: str = 'csv'
    DEFAULT_ENCODING: str = 'utf-8'
    OUTPUT_DIRECTORY: str = os.getcwd()
    
    # Google Maps selectors
    SEARCH_BOX_SELECTOR: str = "input[id='searchboxinput']"
    REVIEWS_TAB_SELECTOR: str = "Reviews"
    REVIEW_ELEMENTS_SELECTOR: str = "div[class*='jJc9Ad']"
    REVIEWER_NAME_SELECTOR: str = "div[class*='d4r55']"
    RATING_SELECTOR: str = "span[aria-label]"
    REVIEW_TEXT_SELECTOR: str = "span[class*='wiI7pd']"
    
    # Cookie consent selectors
    COOKIE_SELECTORS: list = [
        "button:has-text('Reject all')",
        "button:has-text('I disagree')",
        "button[aria-label*='Reject']",
        "button:has-text('Alla avvisa')",  # Swedish
        "div[role='button']:has-text('Reject')",
        "[data-value='0']",
    ]
    
    @classmethod
    def get_business_config(cls, business_name: str) -> Dict[str, Any]:
        """Get business-specific configuration."""
        return {
            'name': business_name,
            'max_reviews': cls.DEFAULT_MAX_REVIEWS,
            'translate': cls.ENABLE_TRANSLATION,
            'output_filename': f"{business_name.lower().replace(' ', '_')}_reviews.csv"
        }

# Global settings instance
settings = Settings()
