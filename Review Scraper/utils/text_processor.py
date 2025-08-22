"""
Text processing utilities for cleaning and translating review text.
"""

import re
import emoji
from typing import Optional, Tuple
from deep_translator import GoogleTranslator
from config.logging_config import logger

class TextProcessor:
    """Handles text cleaning and translation operations."""
    
    def __init__(self, enable_translation: bool = True, target_language: str = 'en'):
        """
        Initialize the text processor.
        
        Args:
            enable_translation: Whether to enable translation functionality
            target_language: Target language for translations
        """
        self.enable_translation = enable_translation
        self.target_language = target_language
        self._translator = None
    
    @property
    def translator(self) -> Optional[GoogleTranslator]:
        """Lazy initialization of translator."""
        if self._translator is None and self.enable_translation:
            self._translator = GoogleTranslator(source='auto', target=self.target_language)
        return self._translator
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing emojis and extra whitespace.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove emojis
        text = emoji.replace_emoji(text, replace='')
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def translate_text(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """
        Translate text to target language if needed.
        
        Args:
            text: Text to translate
            
        Returns:
            Tuple of (translated_text, was_translated, original_language)
        """
        if not self.enable_translation or not text or text.strip() == "" or text == "No review text":
            return text, False, None
        
        try:
            if not self.translator:
                return text, False, None
                
            translated = self.translator.translate(text)
            
            # Check if translation actually changed the text
            if translated != text:
                logger.info(f"Translated text to {self.target_language}")
                return translated, True, 'auto'  # GoogleTranslator doesn't provide source language
            else:
                return text, False, self.target_language
                
        except Exception as e:
            logger.warning(f"Translation failed for text: {text[:50]}... Error: {e}")
            return text, False, None
    
    def process_text(self, text: str) -> Tuple[str, bool, Optional[str]]:
        """
        Complete text processing: clean and translate.
        
        Args:
            text: Input text to process
            
        Returns:
            Tuple of (processed_text, was_translated, original_language)
        """
        # First clean the text
        cleaned_text = self.clean_text(text)
        
        # Then translate if enabled
        if self.enable_translation:
            translated_text, was_translated, original_lang = self.translate_text(cleaned_text)
            return translated_text, was_translated, original_lang
        else:
            return cleaned_text, False, None

# Global instance for convenience
text_processor = TextProcessor()
