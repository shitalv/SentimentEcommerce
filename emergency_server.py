"""
Emergency HTTP Server

This script provides a simple HTTP server that serves an emergency access page.
Use this when the main application is not accessible.
"""

import http.server
import socketserver

PORT = 8000

class EmergencyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            emergency_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Emergency Access - Sentiment Platform</title>
                <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { padding: 20px; background-color: #212529; color: white; }
                    .btn { margin: 5px; }
                    .container { max-width: 900px; margin: 0 auto; }
                    .card { background-color: #2b3035; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
                    .alert { background-color: #721c24; color: white; padding: 15px; border-radius: 5px; margin-bottom: 15px; }
                    h1, h2 { margin-top: 0; }
                    .btn { display: block; text-decoration: none; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold; }
                    .btn-primary { background-color: #0d6efd; }
                    .btn-info { background-color: #0dcaf0; }
                    .btn-warning { background-color: #ffc107; color: black; }
                    .btn-success { background-color: #198754; }
                    .btn-danger { background-color: #dc3545; }
                    .btn:hover { opacity: 0.9; }
                    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="alert">
                        <h1>Emergency Access Mode</h1>
                        <p>This is a direct access page bypassing the main application.</p>
                    </div>
                    
                    <div class="card">
                        <h2>Direct Access Links</h2>
                        <div class="grid">
                            <a href="/admin/dashboard" class="btn btn-primary">Admin Dashboard</a>
                            <a href="/admin/reports/sentiment" class="btn btn-info">Sentiment Reports</a>
                            <a href="/admin/reports/hype-reality" class="btn btn-warning">Hype vs. Reality</a>
                            <a href="/admin/products" class="btn btn-success">Products</a>
                            <a href="/admin/reviews" class="btn btn-danger">Reviews</a>
                            <a href="/emergency" class="btn btn-primary">Emergency Navigation</a>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Access by Port</h2>
                        <p>If you can't access the application through the main URL, try these direct ports:</p>
                        <div class="grid">
                            <a href="http://0.0.0.0:5000/" class="btn btn-primary">Main App (Port 5000)</a>
                            <a href="http://0.0.0.0:5001/" class="btn btn-info">Dev Server (Port 5001)</a>
                            <a href="http://0.0.0.0:8000/" class="btn btn-warning">Emergency Server (Port 8000)</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(emergency_html.encode())
        else:
            super().do_GET()

print("Starting emergency HTTP server on port 8000")
handler = EmergencyHandler
with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
    print(f"Emergency server started at http://0.0.0.0:{PORT}")
    httpd.serve_forever()