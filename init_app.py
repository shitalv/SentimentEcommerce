"""
Initialization module for the Flask application.

This module contains functions to create and configure the Flask app.
It helps avoid circular imports by centralizing app creation.
"""

import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask app"""
    # Create the Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Set app configuration
    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "default_secret_key")
    app.config["MONGO_URI"] = os.environ.get("MONGODB_URI", "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    app.config["MONGO_DBNAME"] = os.environ.get("MONGODB_NAME", "sentiment_ecommerce")
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    return app, login_manager