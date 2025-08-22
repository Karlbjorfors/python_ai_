"""
Browser management utilities for Playwright automation.
"""

from typing import Tuple, Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from config.settings import settings
from config.logging_config import logger

class BrowserManager:
    """Manages browser lifecycle and configuration."""
    
    def __init__(
        self, 
        headless: Optional[bool] = None, 
        timeout: Optional[int] = None
    ):
        """
        Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Page timeout in milliseconds
        """
        self.headless = headless if headless is not None else settings.BROWSER_HEADLESS
        self.timeout = timeout if timeout is not None else settings.BROWSER_TIMEOUT
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def __enter__(self) -> Page:
        """Context manager entry."""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def start(self) -> Page:
        """
        Start the browser and return a page instance.
        
        Returns:
            Configured page instance
        """
        try:
            logger.info(f"Starting browser (headless={self.headless})")
            
            # Start Playwright
            self.playwright = sync_playwright().start()
            
            # Launch browser
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            
            # Create context with timeout settings
            self.context = self.browser.new_context()
            self.context.set_default_timeout(self.timeout)
            
            # Create page
            self.page = self.context.new_page()
            
            logger.info("Browser started successfully")
            return self.page
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            self.stop()  # Cleanup on failure
            raise
    
    def stop(self):
        """Stop the browser and cleanup resources."""
        try:
            if self.page:
                logger.debug("Closing page")
                self.page.close()
                self.page = None
            
            if self.context:
                logger.debug("Closing browser context")
                self.context.close()
                self.context = None
            
            if self.browser:
                logger.debug("Closing browser")
                self.browser.close()
                self.browser = None
            
            if self.playwright:
                logger.debug("Stopping Playwright")
                self.playwright.stop()
                self.playwright = None
            
            logger.info("Browser stopped successfully")
            
        except Exception as e:
            logger.warning(f"Error during browser cleanup: {e}")
    
    def restart(self) -> Page:
        """
        Restart the browser session.
        
        Returns:
            New page instance
        """
        logger.info("Restarting browser")
        self.stop()
        return self.start()
    
    def is_running(self) -> bool:
        """Check if browser is currently running."""
        return all([
            self.playwright is not None,
            self.browser is not None,
            self.context is not None,
            self.page is not None
        ])

def create_browser_session(headless: Optional[bool] = None) -> BrowserManager:
    """
    Create a new browser session.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        BrowserManager instance
    """
    return BrowserManager(headless=headless)
