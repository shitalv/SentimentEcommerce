"""
Main entry point for the Sentiment E-commerce Application

This module sets up the application and serves as the entry point.
"""

import os
import sys
import logging
from flask import redirect, render_template, Flask, jsonify

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Flask app factory
from app_factory import create_app

# Create the application
app = create_app()

# Import MongoDB connection here to avoid circular imports
from mongo_config import get_mongo_client

# Import the direct reports blueprint
from direct_reports import direct_reports

# Register the direct reports blueprint
app.register_blueprint(direct_reports)

# Ensure app is also available as a global variable for gunicorn
# This is what Replit expects for deployment - BOTH names are needed
application = app
# Make sure both 'app' and 'application' are defined for compatibility

# Add direct routes to access reports without authentication
@app.route('/reports-direct')
def reports_direct():
    """Direct access to reports without authentication"""
    return redirect('/reports')

@app.route('/sentiment-direct')
def sentiment_direct():
    """Direct access to sentiment reports without authentication"""
    return redirect('/admin/reports/sentiment', code=307)  # Use 307 to preserve HTTP method

@app.route('/hype-reality-direct')
def hype_reality_direct():
    """Direct access to hype-reality reports without authentication"""
    return redirect('/admin/reports/hype-reality', code=307)  # Use 307 to preserve HTTP method

# Root URL handler - ensure there's something at the root path
@app.route('/')
def root_page():
    """Root page - single source of truth for root URL handling

    Serve a static emergency page with links to all important sections.
    This ensures something is always visible at the root URL.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentiment E-commerce Platform</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { padding: 20px; }
            .btn { margin: 5px; }
            .container { max-width: 900px; margin: 0 auto; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sentiment E-commerce Platform</h1>
            <p>AI-powered product insights based on customer sentiment analysis</p>

            <div class="card bg-primary text-white mb-4 p-4">
                <h2>Direct Navigation</h2>
                <div class="grid">
                    <a href="/admin" class="btn btn-light">Admin Dashboard</a>
                    <a href="/admin/products" class="btn btn-light">Products</a>
                    <a href="/admin/reviews" class="btn btn-light">Reviews</a>
                    <a href="/admin/reports/sentiment" class="btn btn-light">Sentiment Reports</a>
                    <a href="/admin/reports/hype-reality" class="btn btn-light">Hype vs Reality</a>
                    <a href="/emergency" class="btn btn-light">Emergency Navigation</a>
                </div>
                
                <h3 class="mt-4 text-light">Direct Access Links (No Login Required)</h3>
                <div class="grid">
                    <a href="/direct/sentiment" class="btn btn-success">Sentiment Reports (Direct)</a>
                    <a href="/direct/hype-reality" class="btn btn-success">Hype vs Reality (Direct)</a>
                    <a href="/direct/products" class="btn btn-success">Products Report (Direct)</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# Admin direct access routes - ensure all of these work
@app.route('/admin-portal')
def admin_portal():
    """Direct access to admin portal without authentication"""
    return redirect('/admin')

@app.route('/admin/dashboard')
def admin_dashboard_redirect():
    """Ensure /admin/dashboard redirects to /admin for consistency"""
    return redirect('/admin')

# Direct route to admin dashboard that doesn't require template inheritance
@app.route('/admin_dashboard_direct')
def admin_dashboard_direct():
    """Direct access to admin dashboard without template inheritance"""
    try:
        return render_template('admin_dashboard_direct.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return redirect('/')

# API status is already defined in app_factory.py, no need to redefine it here

# Emergency navigation with direct HTML (no templates)
@app.route('/emergency')
def emergency_direct():
    """Super simple emergency navigation with no template dependencies"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emergency Navigation</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body { padding: 20px; }
            .nav-link { display: block; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-warning">
                        <h1>Emergency Navigation</h1>
                        <p>Direct access links to all important sections of the application.</p>
                    </div>

                    <div class="list-group mt-4">
                        <a href="/" class="list-group-item list-group-item-action list-group-item-primary">Home</a>
                        <a href="/admin" class="list-group-item list-group-item-action">Admin Dashboard</a>
                        <a href="/admin/products" class="list-group-item list-group-item-action">Products Management</a>
                        <a href="/admin/reviews" class="list-group-item list-group-item-action">Reviews Management</a>
                        <a href="/admin/users" class="list-group-item list-group-item-action">Users Management</a>
                        <a href="/admin/reports/sentiment" class="list-group-item list-group-item-action">Sentiment Reports</a>
                        <a href="/admin/reports/hype-reality" class="list-group-item list-group-item-action">Hype vs Reality</a>
                        <a href="/api/status" class="list-group-item list-group-item-action">API Status Check</a>
                    </div>
                    
                    <h3 class="mt-4">Direct Access (No Auth Required)</h3>
                    <div class="list-group mt-2">
                        <a href="/direct/sentiment" class="list-group-item list-group-item-action list-group-item-success">Sentiment Reports (Direct)</a>
                        <a href="/direct/hype-reality" class="list-group-item list-group-item-action list-group-item-success">Hype vs Reality (Direct)</a>
                        <a href="/direct/products" class="list-group-item list-group-item-action list-group-item-success">Products Report (Direct)</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    # Check if we need to run a simple HTTP server for emergency access
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "emergency":
        import http.server
        import socketserver

        class EmergencyHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/' or self.path == '/index.html':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    emergency_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Emergency Access - Sentiment Platform</title>
                        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            body {{ padding: 20px; }}
                            .btn {{ margin: 5px; }}
                        </style>
                    </head>
                    <body class="bg-dark text-white">
                        <div class="container">
                            <div class="alert alert-danger">
                                <h1>Emergency Access Mode</h1>
                                <p>This is a direct access page bypassing the main application.</p>
                            </div>

                            <div class="card bg-secondary mb-4">
                                <div class="card-body">
                                    <h2>Direct Access Links</h2>
                                    <div class="d-grid gap-2">
                                        <a href="/admin" class="btn btn-primary">Admin Dashboard</a>
                                        <a href="/admin/reports/sentiment" class="btn btn-info">Sentiment Reports</a>
                                        <a href="/admin/reports/hype-reality" class="btn btn-warning">Hype vs. Reality</a>
                                        <a href="/admin/products" class="btn btn-success">Products</a>
                                        <a href="/admin/reviews" class="btn btn-danger">Reviews</a>
                                    </div>
                                </div>
                            </div>

                            <p>Server is running on port 8000</p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(emergency_html.encode())
                else:
                    super().do_GET()

        # Run a simple HTTP server on port 8000 for emergency access
        print("Starting emergency HTTP server on port 8000")
        handler = EmergencyHandler
        with socketserver.TCPServer(("0.0.0.0", 8000), handler) as httpd:
            print("Emergency server started at http://0.0.0.0:8000")
            httpd.serve_forever()
    else:
        # Always use port 5000 for consistency with Gunicorn
        port = int(os.environ.get("PORT", 5000))

        # Run the backend Flask app
        app.run(host="0.0.0.0", port=port, debug=True)