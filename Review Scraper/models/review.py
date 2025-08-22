"""
Data models for the Review Scraper application.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Review:
    """Data class representing a single review."""
    
    reviewer: str
    rating: str
    review_text: str
    business_name: Optional[str] = None
    scraped_at: Optional[datetime] = None
    translated: bool = False
    original_language: Optional[str] = None
    
    def __post_init__(self):
        """Set default values after initialization."""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert review to dictionary format."""
        return {
            'Reviewer': self.reviewer,
            'Rating': self.rating,
            'Review': self.review_text,
            'Business': self.business_name,
            'Scraped_At': self.scraped_at.isoformat() if self.scraped_at else None,
            'Translated': self.translated,
            'Original_Language': self.original_language
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Review':
        """Create Review instance from dictionary."""
        return cls(
            reviewer=data.get('Reviewer', 'Unknown'),
            rating=data.get('Rating', 'No rating'),
            review_text=data.get('Review', 'No review text'),
            business_name=data.get('Business'),
            translated=data.get('Translated', False),
            original_language=data.get('Original_Language')
        )

@dataclass
class ScrapingResult:
    """Data class representing the result of a scraping operation."""
    
    business_name: str
    reviews: List[Review]
    total_found: int
    total_extracted: int
    errors: List[str]
    scraped_at: datetime
    
    def __post_init__(self):
        """Set default values after initialization."""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of extraction."""
        if self.total_found == 0:
            return 0.0
        return (self.total_extracted / self.total_found) * 100
    
    def to_dict(self) -> dict:
        """Convert scraping result to dictionary format."""
        return {
            'business_name': self.business_name,
            'total_found': self.total_found,
            'total_extracted': self.total_extracted,
            'success_rate': self.success_rate,
            'errors': self.errors,
            'scraped_at': self.scraped_at.isoformat(),
            'reviews': [review.to_dict() for review in self.reviews]
        }
