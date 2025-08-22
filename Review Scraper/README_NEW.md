# 🚀 Review Scraper - Modular Architecture

A clean, modular, and future-proof Google Maps review scraper built with Python and Playwright.

## 🏗️ Architecture Overview

The application has been refactored into a clean, modular structure:

```
review_scraper/
├── main.py                  # Main entry point
├── examples.py              # Usage examples
├── config/                  # Configuration management
│   ├── settings.py          # Application settings
│   └── logging_config.py    # Logging configuration
├── scraper/                 # Core scraping functionality
│   ├── browser_manager.py   # Browser lifecycle management
│   ├── google_maps.py       # Google Maps navigation
│   └── review_extractor.py  # Review extraction logic
├── utils/                   # Utility functions
│   ├── text_processor.py    # Text cleaning & translation
│   └── data_exporter.py     # Data export functionality
└── models/                  # Data models
    └── review.py            # Review and result data classes
```

## ✨ Key Features

### 🎯 **Modular Design**

- **Separation of Concerns**: Each module has a single responsibility
- **Reusable Components**: Components can be used independently
- **Easy Testing**: Each module can be tested in isolation
- **Future-Proof**: Easy to extend and modify

### 🔧 **Configuration Management**

- **Centralized Settings**: All configuration in `config/settings.py`
- **Environment-Specific**: Easy to configure for different environments
- **Business-Specific**: Custom settings per business

### 📊 **Data Models**

- **Type Safety**: Strongly typed data models using dataclasses
- **Validation**: Built-in data validation and error handling
- **Serialization**: Easy conversion to/from dictionaries and JSON

### 🌐 **Translation Support**

- **Automatic Detection**: Detects source language automatically
- **Smart Translation**: Only translates non-English content
- **Error Resilience**: Falls back to original text if translation fails

### 📁 **Multiple Export Formats**

- **CSV**: Standard spreadsheet format
- **JSON**: Complete data with metadata
- **Summary Reports**: Human-readable summaries

### 🛡️ **Error Handling**

- **Graceful Degradation**: Continues processing even if some reviews fail
- **Detailed Logging**: Comprehensive logging for debugging
- **Error Reporting**: Collects and reports all errors

## 🚀 Quick Start

### Basic Usage

```python
from main import ReviewScraperApp

# Create scraper instance
app = ReviewScraperApp(
    business_name="Your Restaurant Name",
    max_reviews=100,
    enable_translation=True,
    headless=False
)

# Run scraping
result = app.run()

# Save results
saved_files = app.save_results(result, formats=['csv', 'summary'])
```

### Advanced Usage

```python
from main_new import ReviewScraperApp
from config.settings import settings

# Customize settings
settings.SCROLL_ATTEMPTS = 20
settings.DEFAULT_MAX_REVIEWS = 200

# Create app with custom configuration
app = ReviewScraperApp(
    business_name="High Volume Restaurant",
    max_reviews=200,
    enable_translation=True,
    headless=True,  # Run without browser window
    output_dir="./results"
)

result = app.run()
app.save_results(result, formats=['csv', 'json', 'summary'])
```

## 📋 Configuration Options

### Application Settings (`config/settings.py`)

```python
# Browser settings
BROWSER_HEADLESS = False
BROWSER_TIMEOUT = 30000

# Scraping settings
DEFAULT_MAX_REVIEWS = 100
SCROLL_ATTEMPTS = 15
SCROLL_DISTANCE = 3000

# Translation settings
ENABLE_TRANSLATION = True
TARGET_LANGUAGE = 'en'

# Output settings
DEFAULT_OUTPUT_FORMAT = 'csv'
OUTPUT_DIRECTORY = '.'
```

### Business-Specific Configuration

```python
from config.settings import settings

config = settings.get_business_config("Your Business Name")
# Returns:
# {
#     'name': 'Your Business Name',
#     'max_reviews': 100,
#     'translate': True,
#     'output_filename': 'your_business_name_reviews.csv'
# }
```

## 📊 Data Models

### Review Model

```python
@dataclass
class Review:
    reviewer: str
    rating: str
    review_text: str
    business_name: Optional[str] = None
    scraped_at: Optional[datetime] = None
    translated: bool = False
    original_language: Optional[str] = None
```

### Scraping Result Model

```python
@dataclass
class ScrapingResult:
    business_name: str
    reviews: List[Review]
    total_found: int
    total_extracted: int
    errors: List[str]
    scraped_at: datetime

    @property
    def success_rate(self) -> float:
        return (self.total_extracted / self.total_found) * 100
```

## 🔧 Individual Components

### Browser Manager

```python
from scraper.browser_manager import BrowserManager

with BrowserManager(headless=True) as page:
    page.goto("https://example.com")
    # Your automation code here
```

### Text Processor

```python
from utils.text_processor import TextProcessor

processor = TextProcessor(enable_translation=True)
cleaned_text, was_translated, original_lang = processor.process_text("Hola mundo!")
# Returns: ("Hello world!", True, "auto")
```

### Data Exporter

```python
from utils.data_exporter import DataExporter

exporter = DataExporter(output_directory="./results")
csv_path = exporter.export_to_csv(reviews, filename="reviews.csv")
json_path = exporter.export_to_json(scraping_result)
summary_path = exporter.export_summary_report(scraping_result)
```

## 🎯 Best Practices

### 1. **Use Context Managers**

```python
# Good: Automatic cleanup
with BrowserManager() as page:
    # scraping code

# Avoid: Manual cleanup required
browser_manager = BrowserManager()
page = browser_manager.start()
# ... scraping code ...
browser_manager.stop()  # Easy to forget!
```

### 2. **Configure Logging**

```python
from config.logging_config import setup_logging

logger = setup_logging(level='DEBUG', log_file='scraper.log')
```

### 3. **Handle Errors Gracefully**

```python
try:
    result = app.run()
    if result.errors:
        logger.warning(f"Scraping completed with {len(result.errors)} errors")
    app.save_results(result)
except Exception as e:
    logger.error(f"Scraping failed: {e}")
```

### 4. **Batch Processing**

```python
businesses = ["Restaurant A", "Restaurant B", "Restaurant C"]

for business in businesses:
    app = ReviewScraperApp(business_name=business, headless=True)
    result = app.run()
    app.save_results(result)
```

## 🆚 Migration from Old Code

### Old vs New Comparison

| Old Approach              | New Approach                 | Benefits            |
| ------------------------- | ---------------------------- | ------------------- |
| Single large file         | Modular structure            | Easier maintenance  |
| Global variables          | Configuration classes        | Better organization |
| Basic error handling      | Comprehensive error tracking | Better reliability  |
| Simple CSV output         | Multiple output formats      | More flexibility    |
| Manual browser management | Context managers             | Automatic cleanup   |
| Hardcoded settings        | Configurable settings        | Easy customization  |

### Migration Steps

1. **Replace old main.py**: Use `main.py` as your entry point
2. **Update imports**: Use the new modular imports
3. **Configure settings**: Set your preferences in `config/settings.py`
4. **Test functionality**: Run examples to ensure everything works
5. **Customize as needed**: Extend the modules for your specific needs

## 🧪 Testing

Run the examples to test the new structure:

```bash
python examples.py
```

## 🔮 Future Enhancements

The modular structure makes it easy to add new features:

- **Multiple Review Sources**: Add support for Yelp, TripAdvisor, etc.
- **Advanced Analytics**: Add sentiment analysis, rating trends
- **Database Storage**: Add support for PostgreSQL, MongoDB
- **API Integration**: Create REST API endpoints
- **Scheduling**: Add automated scraping schedules
- **Notifications**: Email/Slack notifications for completed scrapes

## 🏆 Benefits of This Architecture

### For Developers

- **Clean Code**: Easy to read and understand
- **Maintainable**: Changes are isolated to specific modules
- **Testable**: Each component can be tested independently
- **Extensible**: Easy to add new features

### For Users

- **Reliable**: Better error handling and recovery
- **Flexible**: Multiple output formats and configurations
- **Fast**: Optimized for performance
- **User-Friendly**: Clear logging and progress tracking

---

**Happy Scraping! 🎉**
