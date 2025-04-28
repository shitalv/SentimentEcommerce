"""
End-to-End Test Module

This module contains tests for full end-to-end functionality.
"""

import unittest
from flask import session
from app_factory import create_app
from models_mongo import User

class E2ETestCase(unittest.TestCase):
    """Test case for end-to-end functionality"""
    
    def setUp(self):
        """Set up test client and app context"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SERVER_NAME'] = 'localhost.localdomain'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create a test user
        self.username = "testuser"
        self.password = "testpassword"
        self.email = "test@example.com"
        
        # Remove existing test user if any
        User.delete_by_username(self.username)
        
        # Create new test user
        user = User(username=self.username, email=self.email)
        user.set_password(self.password)
        user.save()
        
    def tearDown(self):
        """Clean up after tests"""
        # Delete test user
        User.delete_by_username(self.username)
        self.app_context.pop()
    
    def test_full_auth_flow(self):
        """Test the full authentication flow"""
        # Step 1: Visit login page
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        
        # Step 2: Login via API
        login_response = self.client.post(
            '/api/auth/login',
            json={'username': self.username, 'password': self.password}
        )
        self.assertEqual(login_response.status_code, 200)
        
        # Step 3: Check that we are authenticated
        user_response = self.client.get('/api/auth/user')
        self.assertEqual(user_response.status_code, 200)
        data = user_response.get_json()
        self.assertIsNotNone(data.get('user'))
        self.assertEqual(data['user']['username'], self.username)
        
        # Step 4: Logout via API
        logout_response = self.client.post('/api/auth/logout')
        self.assertEqual(logout_response.status_code, 200)
        
        # Step 5: Check that we are logged out
        user_response_after_logout = self.client.get('/api/auth/user')
        self.assertEqual(user_response_after_logout.status_code, 200)
        data = user_response_after_logout.get_json()
        self.assertIsNone(data.get('user'))
        
        # Step 6: Visit logout page directly
        logout_page_response = self.client.get('/logout')
        self.assertEqual(logout_page_response.status_code, 200)
        self.assertIn(b'You have been logged out successfully', logout_page_response.data)

if __name__ == '__main__':
    unittest.main()