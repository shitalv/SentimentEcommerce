"""
Main entry point for the Sentiment E-commerce Application

This module sets up the application and serves as the entry point.
"""

import os
import sys
import logging
import nltk

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download NLTK data required for sentiment analysis
logger.info("Downloading VADER lexicon for sentiment analysis")
try:
    nltk.download('vader_lexicon')
    logger.info("NLTK Vader lexicon downloaded successfully")
except Exception as e:
    logger.error(f"Error downloading NLTK data: {str(e)}")

# Import the Flask app from app.py in the root directory
# The app itself handles frontend routes
from app import app

if __name__ == "__main__":
    # Run the backend Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)