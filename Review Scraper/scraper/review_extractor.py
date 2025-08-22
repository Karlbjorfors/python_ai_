"""
Review extraction functionality for parsing individual review elements.
"""

from typing import List, Optional, Tuple
from playwright.sync_api import Page, Locator
from datetime import datetime

from models.review import Review, ScrapingResult
from utils.text_processor import TextProcessor
from config.settings import settings
from config.logging_config import logger

class ReviewExtractor:
    """Extracts individual reviews from Google Maps review elements."""
    
    def __init__(self, page: Page, text_processor: Optional[TextProcessor] = None):
        """
        Initialize review extractor.
        
        Args:
            page: Playwright page instance
            text_processor: Text processor for cleaning and translation
        """
        self.page = page
        self.text_processor = text_processor or TextProcessor()
    
    def extract_single_review(
        self, 
        element: Locator, 
        business_name: str,
        index: int
    ) -> Optional[Review]:
        """
        Extract a single review from a review element.
        
        Args:
            element: Playwright locator for the review element
            business_name: Name of the business being reviewed
            index: Index of the review for logging
            
        Returns:
            Review object or None if extraction failed
        """
        try:
            # Get reviewer name with timeout
            reviewer_element = element.locator(settings.REVIEWER_NAME_SELECTOR)
            reviewer = (
                reviewer_element.inner_text(timeout=5000) 
                if reviewer_element.count() > 0 
                else "Unknown"
            )
            
            # Get rating with timeout
            rating_element = element.locator(settings.RATING_SELECTOR)
            rating = (
                rating_element.get_attribute("aria-label", timeout=5000) 
                if rating_element.count() > 0 
                else "No rating"
            )
            
            # Get review text with timeout (some reviews might not have text)
            review_text_element = element.locator(settings.REVIEW_TEXT_SELECTOR)
            review_text = (
                review_text_element.inner_text(timeout=5000) 
                if review_text_element.count() > 0 
                else "No review text"
            )
            
            # Process the text (clean and potentially translate)
            processed_reviewer, _, _ = self.text_processor.process_text(reviewer)
            processed_review_text, was_translated, original_lang = self.text_processor.process_text(review_text)
            
            # Create Review object
            review = Review(
                reviewer=processed_reviewer,
                rating=rating or "No rating",
                review_text=processed_review_text,
                business_name=business_name,
                translated=was_translated,
                original_language=original_lang
            )
            
            logger.debug(f"Successfully extracted review {index + 1}")
            return review
            
        except Exception as e:
            logger.warning(f"Failed to extract review {index + 1}: {e}")
            return None
    
    def extract_all_reviews(
        self, 
        business_name: str, 
        max_reviews: Optional[int] = None
    ) -> ScrapingResult:
        """
        Extract all available reviews from the page.
        
        Args:
            business_name: Name of the business being scraped
            max_reviews: Maximum number of reviews to extract
            
        Returns:
            ScrapingResult containing all extracted reviews and metadata
        """
        if max_reviews is None:
            max_reviews = settings.DEFAULT_MAX_REVIEWS
        
        logger.info(f"Starting review extraction for: {business_name}")
        
        reviews: List[Review] = []
        errors: List[str] = []
        
        try:
            # Get all review elements
            review_elements = self.page.locator(settings.REVIEW_ELEMENTS_SELECTOR)
            total_found = review_elements.count()
            
            logger.info(f"Found {total_found} review elements")
            
            if total_found == 0:
                error_msg = "No review elements found on the page"
                logger.error(error_msg)
                errors.append(error_msg)
                return ScrapingResult(
                    business_name=business_name,
                    reviews=[],
                    total_found=0,
                    total_extracted=0,
                    errors=errors,
                    scraped_at=datetime.now()
                )
            
            # Extract reviews up to the maximum limit
            elements_to_process = min(total_found, max_reviews)
            logger.info(f"Processing {elements_to_process} reviews...")
            
            for i, element in enumerate(review_elements.all()[:elements_to_process]):
                try:
                    review = self.extract_single_review(element, business_name, i)
                    if review:
                        reviews.append(review)
                        
                        # Log progress every 10 reviews
                        if (i + 1) % 10 == 0:
                            logger.info(f"Extracted {i + 1}/{elements_to_process} reviews")
                    else:
                        error_msg = f"Failed to extract review {i + 1}"
                        errors.append(error_msg)
                        
                except Exception as e:
                    error_msg = f"Error extracting review {i + 1}: {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
            
            logger.info(f"Extraction completed. Successfully extracted {len(reviews)} out of {total_found} reviews")
            
            return ScrapingResult(
                business_name=business_name,
                reviews=reviews,
                total_found=total_found,
                total_extracted=len(reviews),
                errors=errors,
                scraped_at=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Critical error during review extraction: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            return ScrapingResult(
                business_name=business_name,
                reviews=reviews,
                total_found=0,
                total_extracted=len(reviews),
                errors=errors,
                scraped_at=datetime.now()
            )
    
    def get_review_statistics(self) -> dict:
        """
        Get statistics about reviews on the current page.
        
        Returns:
            Dictionary with review statistics
        """
        try:
            review_elements = self.page.locator(settings.REVIEW_ELEMENTS_SELECTOR)
            total_reviews = review_elements.count()
            
            # Try to get more detailed statistics if possible
            stats = {
                'total_reviews': total_reviews,
                'page_url': self.page.url,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.debug(f"Review statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting review statistics: {e}")
            return {
                'total_reviews': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
