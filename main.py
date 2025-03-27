import os
import sys
import logging
import nltk
from flask import send_from_directory

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Download NLTK data required for sentiment analysis
try:
    nltk.download('vader_lexicon')
    logging.info("NLTK Vader lexicon downloaded successfully")
except Exception as e:
    logging.error(f"Error downloading NLTK data: {str(e)}")

# Import the Flask app from app.py in the root directory
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