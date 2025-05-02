"""
Main entry point for the Sentiment E-commerce Application

This module sets up the application and serves as the entry point.
"""

import os
import sys
import logging
from flask import redirect

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Flask app factory
from app_factory import create_app

# Create the application
app = create_app()

# Add a direct reports route at the application level
@app.route('/reports-direct')
def reports_direct():
    """Direct access to reports without authentication"""
    return redirect('/reports')
    
# Add a root redirect to our emergency navigation
@app.route('/')
def root_page():
    """Root page redirects to emergency navigation during navigation issues"""
    return redirect('/emergency')

if __name__ == "__main__":
    # Get the port from environment or use a different default
    port = int(os.environ.get("FLASK_PORT", 5001))
    
    # Run the backend Flask app
    app.run(host="0.0.0.0", port=port, debug=True)