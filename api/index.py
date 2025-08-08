import os
import sys
from flask import Flask

# Add the parent directory to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the Flask app
from app import app

# This is the entry point for Vercel
# Vercel will automatically handle the WSGI interface