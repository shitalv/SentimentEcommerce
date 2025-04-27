"""
Main Flask application for Sentiment E-commerce Platform

This file imports the app from the app_factory to avoid circular imports.
"""

# Import the application from the factory
from app_factory import create_app

# Create the application
app = create_app()

# Development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)