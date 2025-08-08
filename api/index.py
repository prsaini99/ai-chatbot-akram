import os
import sys

# Add the parent directory to Python path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import app

# Vercel serverless function handler
def handler(event, context):
    return app

# For testing locally
if __name__ == "__main__":
    app.run(debug=True)