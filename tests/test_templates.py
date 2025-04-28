"""
Template Integration Test Module

This module contains tests for template rendering functionality.
"""

import unittest
from flask import url_for
from app_factory import create_app

class TemplateTestCase(unittest.TestCase):
    """Test case for template rendering functionality"""
    
    def setUp(self):
        """Set up test client and app context"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SERVER_NAME'] = 'localhost.localdomain'  # Prevent port conflicts
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
        
    def test_login_page_renders(self):
        """Test login page renders properly"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        
    def test_logout_page_redirects(self):
        """Test logout page redirects properly"""
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out successfully', response.data)

if __name__ == '__main__':
    unittest.main()