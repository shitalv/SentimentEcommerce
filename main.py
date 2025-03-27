import os
import sys
import logging
import subprocess
import signal
import threading
from flask import Flask, send_from_directory

# Import the Flask app from backend
sys.path.append('./backend')
from app import app as backend_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Serve React frontend static files
@backend_app.route('/', defaults={'path': ''})
@backend_app.route('/<path:path>')
def serve(path):
    """Serve React frontend static files"""
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

if __name__ == "__main__":
    # Run the backend Flask app
    backend_app.run(host="0.0.0.0", port=5000, debug=True)