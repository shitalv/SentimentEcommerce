"""
App Factory Module

This module contains functions to create and configure the Flask app
and all its dependencies to avoid circular imports.
"""

import os
import logging
import nltk
from flask import Flask, jsonify, send_from_directory, render_template
from flask_login import LoginManager
from flask_cors import CORS
from mongo_config import init_mongo, setup_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask app and all its dependencies"""
    # Download NLTK data
    logger.info("Downloading VADER lexicon for sentiment analysis")
    nltk.download('vader_lexicon')
    logger.info("NLTK Vader lexicon downloaded successfully")
    
    # Create the Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Set app configuration
    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "default_secret_key")
    app.config["MONGO_URI"] = os.environ.get("MONGODB_URI")
    app.config["MONGO_DBNAME"] = os.environ.get("MONGODB_NAME", "sentiment_ecommerce")
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login_page'
    
    # Initialize MongoDB
    with app.app_context():
        init_mongo(app)
        setup_db()
        logger.info("MongoDB setup completed")
    
    # Import models after MongoDB initialization
    from models_mongo import User
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    
    # Register routes
    register_routes(app)
    
    # Setup error handlers
    register_error_handlers(app)
    
    return app

def register_routes(app):
    """Register all routes with the app"""
    # Define and create the backend blueprint
    from flask import Blueprint, jsonify, request, session
    from flask_login import login_user, logout_user, login_required, current_user
    import logging
    
    # Create the backend routes blueprint
    backend_bp = Blueprint('backend', __name__, url_prefix='/api')
    
    # Import backend routes functions
    from backend.routes import (
        home, register, login, logout, get_user,
        api_get_products, api_get_product, 
        api_analyze_sentiment, api_get_recommendations,
        api_get_top_rated
    )
    
    # Register route functions with the blueprint
    backend_bp.route('/')(home)
    backend_bp.route('/auth/register', methods=['POST'])(register)
    backend_bp.route('/auth/login', methods=['POST'])(login)
    backend_bp.route('/auth/logout', methods=['POST'])(logout)
    backend_bp.route('/auth/user', methods=['GET'])(get_user)
    backend_bp.route('/products', methods=['GET'])(api_get_products)
    backend_bp.route('/products/<product_id>', methods=['GET'])(api_get_product)
    backend_bp.route('/analyze', methods=['POST'])(api_analyze_sentiment)
    backend_bp.route('/recommendations/<product_id>', methods=['GET'])(api_get_recommendations)
    backend_bp.route('/top-rated', methods=['GET'])(api_get_top_rated)
    
    # Register the blueprint with the app
    app.register_blueprint(backend_bp)
    
    # Import and register admin routes
    try:
        from backend.admin import admin_bp, add_admin_field_to_users
        app.register_blueprint(admin_bp)
        
        # Add admin field to users
        with app.app_context():
            add_admin_field_to_users()
        logger.info("Admin routes registered successfully")
    except Exception as e:
        logger.error(f"Failed to register admin routes: {str(e)}")
    
    logger.info("Backend routes registered successfully")
    
    # Login and logout page routes
    @app.route('/login')
    def login_page():
        """Serve login page"""
        return render_template('login.html')
        
    @app.route('/logout')
    def logout_page():
        """Handle GET logout requests from UI links"""
        from flask_login import logout_user
        logout_user()
        return render_template('login.html', message="You have been logged out successfully.")
        
    # Serve React frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Serve React frontend static files"""
        # Skip login and logout routes as they're handled separately
        if path == 'login':
            return login_page()
        elif path == 'logout':
            return logout_page()
            
        if path != "" and os.path.exists(os.path.join('frontend/public', path)):
            return send_from_directory('frontend/public', path)
        else:
            return send_from_directory('frontend/public', 'index.html')
    
    # Basic API endpoints
    @app.route('/api/status')
    def api_status():
        """API status check endpoint"""
        return jsonify({
            "status": "ok",
            "database": "mongodb",
            "message": "Sentiment E-commerce API is running"
        })

def register_error_handlers(app):
    """Register error handlers with the app"""
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Server error"}), 500