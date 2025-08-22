"""
Google Maps specific scraping functionality.
"""

from typing import List, Tuple, Optional
from playwright.sync_api import Page
from config.settings import settings
from config.logging_config import logger

class GoogleMapsScraper:
    """Handles Google Maps navigation and cookie consent."""
    
    def __init__(self, page: Page):
        """
        Initialize Google Maps scraper.
        
        Args:
            page: Playwright page instance
        """
        self.page = page
    
    def handle_cookie_consent(self) -> bool:
        """
        Handle cookie consent popup if it appears.
        
        Returns:
            True if cookie consent was handled, False otherwise
        """
        try:
            # Wait a bit for the page to load
            self.page.wait_for_timeout(2000)
            
            logger.debug("Checking for cookie consent popup")
            
            for selector in settings.COOKIE_SELECTORS:
                try:
                    reject_button = self.page.locator(selector).first
                    if reject_button.is_visible(timeout=3000):
                        logger.info(f"Found cookie reject button with selector: {selector}")
                        reject_button.click()
                        self.page.wait_for_timeout(1000)
                        return True
                except Exception:
                    continue
                    
            logger.debug("No cookie consent popup found or already handled")
            return False
            
        except Exception as e:
            logger.warning(f"Error handling cookie consent: {e}")
            return False
    
    def navigate_to_maps(self) -> bool:
        """
        Navigate to Google Maps.
        
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            logger.info("Navigating to Google Maps")
            self.page.goto("https://www.google.com/maps")
            
            # Handle cookie consent
            self.handle_cookie_consent()
            
            # Wait for the page to load
            self.page.wait_for_timeout(2000)
            
            # Verify we're on the correct page
            if "maps" not in self.page.url.lower():
                logger.error("Failed to navigate to Google Maps")
                return False
            
            logger.info("Successfully navigated to Google Maps")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to Google Maps: {e}")
            return False
    
    def search_business(self, business_name: str) -> bool:
        """
        Search for a business on Google Maps.
        
        Args:
            business_name: Name of the business to search for
            
        Returns:
            True if search was successful, False otherwise
        """
        try:
            logger.info(f"Searching for business: {business_name}")
            
            # Find and fill search box
            search_box = self.page.locator(settings.SEARCH_BOX_SELECTOR)
            
            if not search_box.is_visible(timeout=5000):
                logger.error("Search box not found")
                return False
            
            search_box.fill(business_name)
            search_box.press("Enter")
            
            # Wait for search results
            self.page.wait_for_timeout(settings.PAGE_LOAD_TIMEOUT)
            
            logger.info("Search completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error searching for business: {e}")
            return False
    
    def navigate_to_reviews(self) -> bool:
        """
        Navigate to the reviews section of a business.
        
        Returns:
            True if navigation to reviews was successful, False otherwise
        """
        try:
            logger.info("Navigating to reviews section")
            
            # Wait for business details to load
            self.page.wait_for_timeout(3000)
            
            # Find and click reviews tab
            review_section = self.page.get_by_role('tab', name=settings.REVIEWS_TAB_SELECTOR)
            
            if not review_section.is_visible(timeout=10000):
                logger.error("Reviews section not found")
                return False
            
            review_section.click()
            self.page.wait_for_timeout(3000)
            
            logger.info("Successfully navigated to reviews section")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to reviews: {e}")
            return False
    
    def scroll_to_load_reviews(self, max_attempts: Optional[int] = None) -> int:
        """
        Scroll to load more reviews.
        
        Args:
            max_attempts: Maximum number of scroll attempts
            
        Returns:
            Number of reviews loaded
        """
        if max_attempts is None:
            max_attempts = settings.SCROLL_ATTEMPTS
        
        logger.info("Starting to load reviews by scrolling")
        
        previous_count = 0
        
        for scroll_attempt in range(max_attempts):
            try:
                # Scroll down
                self.page.mouse.wheel(0, settings.SCROLL_DISTANCE)
                self.page.wait_for_timeout(settings.SCROLL_WAIT_TIME)
                
                # Check if new reviews loaded
                current_count = self.page.locator(settings.REVIEW_ELEMENTS_SELECTOR).count()
                
                if current_count == previous_count:
                    # No new reviews loaded
                    if scroll_attempt > 5:  # Give it a few tries before giving up
                        logger.info(f"No new reviews loaded after {scroll_attempt} attempts, stopping scroll")
                        break
                else:
                    logger.debug(f"Loaded {current_count} reviews so far...")
                    previous_count = current_count
                
            except Exception as e:
                logger.warning(f"Error during scroll attempt {scroll_attempt}: {e}")
                continue
        
        logger.info(f"Finished scrolling. Total reviews found: {previous_count}")
        return previous_count
    
    def get_review_count(self) -> int:
        """
        Get the total number of review elements on the page.
        
        Returns:
            Number of review elements found
        """
        try:
            count = self.page.locator(settings.REVIEW_ELEMENTS_SELECTOR).count()
            logger.debug(f"Found {count} review elements")
            return count
        except Exception as e:
            logger.error(f"Error getting review count: {e}")
            return 0
