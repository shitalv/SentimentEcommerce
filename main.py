import os
import sys
import logging
from flask import send_from_directory

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Import the Flask app from backend
sys.path.append('./backend')
from app import app

# Serve React frontend static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend static files"""
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

if __name__ == "__main__":
    # Run the backend Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)