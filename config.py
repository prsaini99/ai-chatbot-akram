import os
from pathlib import Path

class Config:
    """Application configuration from environment variables"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 500))
    TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.7))
    TOP_P = float(os.environ.get('TOP_P', 1.0))
    FREQUENCY_PENALTY = float(os.environ.get('FREQUENCY_PENALTY', 0))
    PRESENCE_PENALTY = float(os.environ.get('PRESENCE_PENALTY', 0))
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_DIR = os.environ.get('KNOWLEDGE_BASE_DIR', './knowledge_base')
    EMBEDDINGS_CACHE_DIR = os.environ.get('EMBEDDINGS_CACHE_DIR', './embeddings_cache')
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 500))
    CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', 50))
    MAX_CONTEXT_LENGTH = int(os.environ.get('MAX_CONTEXT_LENGTH', 2000))
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', 0.7))
    
    # Server Configuration
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            # In Vercel, allow empty API key during build time
            if not os.environ.get('VERCEL'):
                raise ValueError("OPENAI_API_KEY environment variable is required")
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        Path(cls.KNOWLEDGE_BASE_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.EMBEDDINGS_CACHE_DIR).mkdir(parents=True, exist_ok=True)