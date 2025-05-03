"""
Main Flask application for Sentiment E-commerce Platform

This file imports the app from the app_factory to avoid circular imports.
"""

# Import necessary libraries
from flask import Flask
import os
from app_factory import create_app
from mongo_config import get_mongo_client


# Create the application
app = create_app()

# Configure MongoDB connection
mongo_client, db = get_mongo_client()
if not mongo_client or not db:
    print("Error: Could not connect to MongoDB")

# Enable debug mode for development
app.debug = True

# Development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)