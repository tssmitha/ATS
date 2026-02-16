import spacy
import nltk
from nltk.corpus import stopwords
from typing import Optional, Set

class NLPModels:
    """Singleton class to load and manage NLP models"""
    _instance = None
    _nlp = None
    _stop_words = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
    
    def _initialize_models(self):
        """Load NLP models once at startup"""
        # Load spaCy model
        try:
            self._nlp = spacy.load("en_core_web_sm")
            print("✓ Spacy model loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load Spacy model: {e}")
            self._nlp = None
        
        # Download and load NLTK stopwords
        try:
            nltk.download('stopwords', quiet=True)
            self._stop_words = set(stopwords.words('english'))
            print("✓ NLTK stopwords loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load NLTK stopwords: {e}")
            self._stop_words = set()
    
    @property
    def nlp(self) -> Optional[spacy.Language]:
        """Get spaCy NLP model"""
        return self._nlp
    
    @property
    def stop_words(self) -> Set[str]:
        """Get NLTK stopwords"""
        return self._stop_words if self._stop_words else set()
    
    def is_ready(self) -> bool:
        """Check if models are loaded"""
        return self._nlp is not None and self._stop_words is not None

# Create global instance
nlp_models = NLPModels()