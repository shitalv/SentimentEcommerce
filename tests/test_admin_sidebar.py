"""
Admin Sidebar Navigation Test

This module focuses specifically on testing the admin sidebar
navigation functionality with a mocked MongoDB to avoid timeouts.
"""

import unittest
from flask import Flask
from flask_testing import TestCase
import time
from unittest.mock import patch, MagicMock

class AdminSidebarTestCase(TestCase):
    """Test case specifically for admin sidebar functionality"""
    
    def create_app(self):
        """Create and configure a Flask app for testing"""
        app = Flask(__name__, template_folder='../templates')
        app.config['TESTING'] = True
        app.config['SERVER_NAME'] = 'localhost.localdomain'
        app.secret_key = 'test_secret_key'
        
        # Register simplified routes for testing
        @app.route('/admin')
        def admin_dashboard():
            from flask import render_template
            return render_template('admin/dashboard.html')
            
        @app.route('/admin/products')
        def admin_products():
            from flask import render_template
            return render_template('admin/products.html')
        
        @app.route('/admin/direct-access')
        def admin_direct_access():
            from flask import render_template
            return render_template('admin_direct_access.html')
            
        return app
        
    @patch('models_mongo.get_db')
    def test_admin_dashboard_sidebar(self, mock_get_db):
        """Test that admin sidebar renders correctly in dashboard"""
        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Access admin dashboard
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        
        # Check for sidebar elements
        html = response.data.decode('utf-8')
        self.assertIn('sidebarMenu', html, "Sidebar menu div not found")
        self.assertIn('Dashboard', html, "Dashboard link not found")
        self.assertIn('Products', html, "Products link not found")
        self.assertIn('Reviews', html, "Reviews link not found")
    
    @patch('models_mongo.get_db')
    def test_admin_direct_access_page(self, mock_get_db):
        """Test the admin direct access page loads correctly"""
        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Access direct access page
        response = self.client.get('/admin/direct-access')
        self.assertEqual(response.status_code, 200)
        
        # Check for direct access elements
        html = response.data.decode('utf-8')
        self.assertIn('Admin Direct Access Portal', html, "Direct access title not found")
        self.assertIn('Dashboard', html, "Dashboard link not found")
        self.assertIn('Products', html, "Products link not found")
        self.assertIn('Reviews', html, "Reviews link not found")
        
    @patch('models_mongo.get_db')
    def test_admin_products_sidebar(self, mock_get_db):
        """Test that admin sidebar renders correctly in products page"""
        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        
        # Access products page
        response = self.client.get('/admin/products')
        self.assertEqual(response.status_code, 200)
        
        # Check for sidebar elements
        html = response.data.decode('utf-8')
        self.assertIn('sidebarMenu', html, "Sidebar menu div not found")
        self.assertIn('Dashboard', html, "Dashboard link not found")
        self.assertIn('Products', html, "Products link not found")
        self.assertIn('Reviews', html, "Reviews link not found")
        self.assertIn('active', html, "Active class not found for current page")

if __name__ == '__main__':
    unittest.main()