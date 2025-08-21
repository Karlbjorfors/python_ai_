# STEP 1 Import the libraries and configure the logging messages
from playwright.sync_api import sync_playwright
import pandas as pd
import re
import emoji
import logging
import time
from googletrans import Translator


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# STEP 2 Setting Up Playwright

def initialize_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    return playwright, browser, page

# Step 3: Handle cookie consent and navigate to Google Maps

def handle_cookie_consent(page):
    """Handle cookie consent popup if it appears"""
    try:
        # Wait a bit for the page to load
        page.wait_for_timeout(2000)
        
        # Common cookie rejection button selectors for Google
        cookie_selectors = [
            "button:has-text('Reject all')",
            "button:has-text('I disagree')",
            "button[aria-label*='Reject']",
            "button:has-text('Avvisa alla')",  # Italian
            "button:has-text('Rechazar todo')",  # Spanish
            "button:has-text('Tout refuser')",  # French
            "button:has-text('Alla avvisa')",  # Swedish
            "div[role='button']:has-text('Reject')",
            "[data-value='0']",  # Sometimes Google uses data-value for reject
        ]
        
        for selector in cookie_selectors:
            try:
                reject_button = page.locator(selector).first
                if reject_button.is_visible(timeout=3000):
                    logger.info(f"Found cookie reject button with selector: {selector}")
                    reject_button.click()
                    page.wait_for_timeout(1000)
                    return True
            except:
                continue
                
        logger.info("No cookie consent popup found or already handled")
        return False
        
    except Exception as e:
        logger.warning(f"Error handling cookie consent: {e}")
        return False

def search_google_maps(page, business_name):
    page.goto("https://www.google.com/maps")
    
    # Handle cookie consent
    handle_cookie_consent(page)
    
    search_box = page.locator("input[id='searchboxinput']")
    search_box.fill(business_name)
    search_box.press("Enter")
    page.wait_for_timeout(5000)

# Step 4: Clean the reviews text function (whitespace & emojis)

def clean_text(text):
    # Remove Emojis
    text = emoji.replace_emoji(text, replace='')

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Step 5: Extracting Reviews (scrolling is necessary to load additional content)

def scrape_reviews(page, max_reviews=100):
    reviews = []
    try:
        # Wait for details to load
        page.wait_for_timeout(5000)

        # Locate and click the reviews section
        logger.info("Searching for reviews section")
        review_section = page.get_by_role('tab', name="Reviews")
        review_section.click()
        page.wait_for_timeout(3000)

        # Scroll to load more reviews
        logger.info("Loading reviews...")
        previous_count = 0
        for scroll_attempt in range(15):  # Increased scroll attempts
            page.mouse.wheel(0, 3000)  # Reduced scroll distance for better loading
            page.wait_for_timeout(2000)
            
            # Check if new reviews loaded
            current_count = page.locator("div[class*='jJc9Ad']").count()
            if current_count == previous_count:
                # No new reviews loaded, try a few more times
                if scroll_attempt > 5:
                    logger.info(f"No new reviews loaded after {scroll_attempt} attempts, stopping scroll")
                    break
            else:
                logger.info(f"Loaded {current_count} reviews so far...")
                previous_count = current_count

        # Extract reviews
        review_elements = page.locator("div[class*='jJc9Ad']")
        logger.info(f"Found {review_elements.count()} reviews")

        for i, element in enumerate(review_elements.all()[:max_reviews]):
            try:
                # Get reviewer name with timeout
                reviewer_element = element.locator("div[class*='d4r55']")
                reviewer = reviewer_element.inner_text(timeout=5000) if reviewer_element.count() > 0 else "Unknown"
                
                # Get rating with timeout
                rating_element = element.locator("span[aria-label]")
                rating = rating_element.get_attribute("aria-label", timeout=5000) if rating_element.count() > 0 else "No rating"
                
                # Get review text with timeout (some reviews might not have text)
                review_text_element = element.locator("span[class*='wiI7pd']")
                review_text = review_text_element.inner_text(timeout=5000) if review_text_element.count() > 0 else "No review text"

                reviews.append({
                    "Reviewer": clean_text(reviewer),
                    "Rating": rating,
                    "Review": clean_text(review_text)
                })
                
                logger.info(f"Extracted review {i+1}/{max_reviews}")
                
            except Exception as element_error:
                logger.warning(f"Skipping review {i+1} due to error: {element_error}")
                continue

    except Exception as e:
        logger.error(f"Error during scraping: {e}")

    return reviews

# Step 6: Saving Data

def save_reviews_to_csv(reviews, filename="bellevue_falafel_och_pizza.csv"):
    df = pd.DataFrame(reviews)
    df.to_csv(filename, index=False, encoding='utf-8')
    logger.info(f"Reviews saved to {filename}")

# Step 7: Running the Script

def main():
    business_name = "Bellevue Falafel och Pizza"
    
    # Initialize browser
    playwright, browser, page = initialize_browser()
    
    try:
        # Search and scrape reviews
        search_google_maps(page, business_name)
        reviews = scrape_reviews(page, max_reviews=100)
        
        # Save results
        save_reviews_to_csv(reviews)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    finally:
        # Add a longer wait before closing
        page.wait_for_timeout(5000)
        browser.close()
        playwright.stop()

if __name__ == "__main__":
    main()