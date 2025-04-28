"""
Main entry point for the Sentiment E-commerce Application

This module sets up the application and serves as the entry point.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Flask app factory
from app_factory import create_app

# Create the application
app = create_app()

if __name__ == "__main__":
    # Get the port from environment or use a different default
    port = int(os.environ.get("FLASK_PORT", 5001))
    
    # Run the backend Flask app
    app.run(host="0.0.0.0", port=port, debug=True)