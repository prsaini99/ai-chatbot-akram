#!/usr/bin/env python3
"""
AI Chatbot with Knowledge Base
Main Flask application entry point
"""

import logging
from flask import Flask
from flask_cors import CORS
import openai

from config import Config
from models.knowledge_base import KnowledgeBase
from routes.chat_routes import chat_bp, init_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Validate and load configuration
    try:
        Config.validate()
        Config.create_directories()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    # Configure OpenAI
    openai.api_key = Config.OPENAI_API_KEY
    
    # Initialize Knowledge Base
    logger.info("Initializing knowledge base...")
    knowledge_base = KnowledgeBase(
        knowledge_base_dir=Config.KNOWLEDGE_BASE_DIR,
        embeddings_cache_dir=Config.EMBEDDINGS_CACHE_DIR,
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        similarity_threshold=Config.SIMILARITY_THRESHOLD
    )
    
    # Initialize routes with knowledge base
    init_routes(knowledge_base)
    
    # Register blueprints
    app.register_blueprint(chat_bp)
    
    logger.info("Application initialized successfully")
    return app

# Create the application
app = create_app()

if __name__ == '__main__':
    # Run the application
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )