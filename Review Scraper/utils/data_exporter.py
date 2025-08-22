"""
Data export utilities for saving scraped reviews in various formats.
"""

import pandas as pd
import json
import csv
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

from models.review import Review, ScrapingResult
from config.logging_config import logger

class DataExporter:
    """Handles exporting scraped data to various formats."""
    
    def __init__(self, output_directory: str = "."):
        """
        Initialize the data exporter.
        
        Args:
            output_directory: Directory to save exported files
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
    
    def export_to_csv(
        self, 
        reviews: List[Review], 
        filename: Optional[str] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export reviews to CSV format.
        
        Args:
            reviews: List of Review objects to export
            filename: Optional custom filename
            include_metadata: Whether to include metadata columns
            
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reviews_{timestamp}.csv"
        
        filepath = self.output_directory / filename
        
        # Convert reviews to dictionaries
        data: List[Dict[str, Any]] = []
        for review in reviews:
            review_dict: Dict[str, Any] = {
                'Reviewer': review.reviewer,
                'Rating': review.rating,
                'Review': review.review_text
            }
            
            if include_metadata:
                review_dict['Business'] = review.business_name
                review_dict['Scraped_At'] = review.scraped_at.isoformat() if review.scraped_at else None
                review_dict['Translated'] = review.translated
                review_dict['Original_Language'] = review.original_language
            
            data.append(review_dict)
        
        # Create DataFrame and save
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"Exported {len(reviews)} reviews to {filepath}")
        return str(filepath)
    
    def export_to_json(
        self, 
        scraping_result: ScrapingResult, 
        filename: Optional[str] = None,
        pretty_print: bool = True
    ) -> str:
        """
        Export scraping result to JSON format.
        
        Args:
            scraping_result: ScrapingResult object to export
            filename: Optional custom filename
            pretty_print: Whether to format JSON for readability
            
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_business_name = scraping_result.business_name.replace(' ', '_').lower()
            filename = f"{safe_business_name}_result_{timestamp}.json"
        
        filepath = self.output_directory / filename
        
        # Convert to dictionary
        data = scraping_result.to_dict()
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty_print:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        logger.info(f"Exported scraping result to {filepath}")
        return str(filepath)
    
    def export_summary_report(
        self, 
        scraping_result: ScrapingResult, 
        filename: Optional[str] = None
    ) -> str:
        """
        Export a summary report of the scraping operation.
        
        Args:
            scraping_result: ScrapingResult object to summarize
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_business_name = scraping_result.business_name.replace(' ', '_').lower()
            filename = f"{safe_business_name}_summary_{timestamp}.txt"
        
        filepath = self.output_directory / filename
        
        # Create summary content
        summary_lines = [
            f"Review Scraping Summary Report",
            f"=" * 40,
            f"Business: {scraping_result.business_name}",
            f"Scraped at: {scraping_result.scraped_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"Results:",
            f"  - Reviews found: {scraping_result.total_found}",
            f"  - Reviews extracted: {scraping_result.total_extracted}",
            f"  - Success rate: {scraping_result.success_rate:.1f}%",
            f"",
        ]
        
        if scraping_result.errors:
            summary_lines.extend([
                f"Errors encountered:",
                *[f"  - {error}" for error in scraping_result.errors],
                f""
            ])
        
        # Add review statistics
        if scraping_result.reviews:
            translated_count = sum(1 for review in scraping_result.reviews if review.translated)
            summary_lines.extend([
                f"Review Statistics:",
                f"  - Total reviews: {len(scraping_result.reviews)}",
                f"  - Translated reviews: {translated_count}",
                f"  - Original language reviews: {len(scraping_result.reviews) - translated_count}",
            ])
        
        # Write summary file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        
        logger.info(f"Exported summary report to {filepath}")
        return str(filepath)

# Global instance for convenience
data_exporter = DataExporter()
