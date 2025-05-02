"""
Simple Python HTTP Server for emergencies

This script starts a Python HTTP server on port 8000
to serve static files as a backup when the main app is not working.
"""

import os
import sys
import http.server
import socketserver

PORT = 8000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    # Override to serve index.html from frontend/public
    def translate_path(self, path):
        # Redirect root to frontend/public
        if path == '/' or path == '/index.html':
            return os.path.join(os.getcwd(), 'frontend/public/index.html')
        return super().translate_path(path)

Handler = SimpleHTTPRequestHandler

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving at http://0.0.0.0:{PORT}")
    httpd.serve_forever()