"""
Admin Routes Test Module

This module contains tests specifically for admin routes functionality.
"""

import unittest
from flask import session, url_for
from app_factory import create_app
from models_mongo import User

class AdminRoutesTestCase(unittest.TestCase):
    """Test case for admin routes functionality"""
    
    def setUp(self):
        """Set up test client and app context"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SERVER_NAME'] = 'localhost.localdomain'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create a test admin user
        self.admin_username = "testadmin"
        self.admin_password = "testpassword"
        self.admin_email = "testadmin@example.com"
        
        # Remove existing test admin if any
        User.delete_by_username(self.admin_username)
        
        # Create new test admin user
        admin_user = User(username=self.admin_username, email=self.admin_email, is_admin=True)
        admin_user.set_password(self.admin_password)
        admin_user.save()
        
    def tearDown(self):
        """Clean up after tests"""
        # Delete test user
        User.delete_by_username(self.admin_username)
        self.app_context.pop()
    
    def login_admin(self):
        """Helper method to log in as admin"""
        return self.client.post(
            '/api/auth/login',
            json={'username': self.admin_username, 'password': self.admin_password}
        )
    
    def test_admin_dashboard_access(self):
        """Test access to admin dashboard"""
        # First try without login
        response = self.client.get('/admin')
        self.assertIn(response.status_code, [302, 401, 403])  # Should redirect or deny
        
        # Login as admin
        login_response = self.login_admin()
        self.assertEqual(login_response.status_code, 200)
        
        # Now try to access admin dashboard
        dashboard_response = self.client.get('/admin')
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn(b'Admin Dashboard', dashboard_response.data)
    
    def test_admin_reports_access(self):
        """Test access to admin reports pages"""
        # Login as admin
        self.login_admin()
        
        # Try to access each reports page
        report_paths = [
            '/admin/reports/sentiment',
            '/admin/reports/products',
            '/admin/reports/hype-reality'
        ]
        
        for path in report_paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Reports', response.data)
    
    def test_admin_nav_helper(self):
        """Test the admin navigation helper page"""
        # This page should be accessible without login
        response = self.client.get('/admin/nav-helper')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard Navigation', response.data)
    
    def test_admin_direct_access(self):
        """Test the admin direct access page"""
        # First make sure the route is registered
        with self.app.test_request_context():
            url = url_for('admin_direct_access')
            self.assertIsNotNone(url)
        
        # Login as admin
        self.login_admin()
        
        # Access the page
        response = self.client.get('/admin/direct-access')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Direct Access Portal', response.data)
    
    def test_sidebar_presence(self):
        """Test that admin sidebar is present in admin pages"""
        # Login as admin
        self.login_admin()
        
        # Access admin dashboard
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        
        # Check for sidebar
        self.assertIn(b'sidebarMenu', response.data)
        self.assertIn(b'Dashboard', response.data)
        self.assertIn(b'Products', response.data)
        self.assertIn(b'Reviews', response.data)
        self.assertIn(b'Users', response.data)
        self.assertIn(b'Reports', response.data)

if __name__ == '__main__':
    unittest.main()