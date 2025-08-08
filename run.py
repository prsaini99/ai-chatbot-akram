#!/usr/bin/env python3
"""
AI Chatbot with Knowledge Base
Run script for local development
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import flask
        import flask_cors
        import openai
        import numpy
        import tiktoken
        import PyPDF2
        import docx
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment configuration"""
    env_file = Path('.env')
    if not env_file.exists():
        print("✗ .env file not found")
        print("Please copy .env.example to .env and configure your settings")
        return False
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Note: python-dotenv not installed. Using system environment variables.")
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("✗ OPENAI_API_KEY not set in environment")
        print("Please add your OpenAI API key to .env file")
        return False
    
    print("✓ Environment configuration looks good")
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['knowledge_base', 'embeddings_cache']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created/verified directory: {dir_name}")

def main():
    """Main entry point"""
    print("🚀 Starting AI Chatbot with Knowledge Base...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Import and run the app
    try:
        from app import app
        print("\n✓ Application loaded successfully")
        print("🌐 Starting server...")
        print("📁 Access the chat interface at: http://localhost:5000")
        print("📋 Add documents to the 'knowledge_base' folder")
        print("⚠️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run the Flask app
        app.run()
        
    except Exception as e:
        print(f"✗ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()