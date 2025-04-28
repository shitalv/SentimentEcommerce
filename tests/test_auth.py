"""
Authentication Test Module

This module contains tests for user authentication functionality.
"""

import unittest
from flask import url_for
from app_factory import create_app
from models_mongo import User
import json

class AuthTestCase(unittest.TestCase):
    """Test case for authentication functionality"""
    
    def setUp(self):
        """Set up test client and app context"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SERVER_NAME'] = 'localhost.localdomain'  # Prevent port conflicts
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
        
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': self.username, 'password': self.password}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Login successful')
        self.assertEqual(data['user']['username'], self.username)
        
    def test_login_invalid_password(self):
        """Test login with invalid password"""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': self.username, 'password': 'wrongpassword'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Invalid username or password')
        
    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'nonexistentuser', 'password': 'password'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Invalid username or password')
        
    def test_register_success(self):
        """Test successful registration"""
        # Delete test user first to ensure we can register it
        User.delete_by_username(self.username)
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': self.username,
                'email': self.email,
                'password': self.password
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User registered successfully')
        self.assertEqual(data['user']['username'], self.username)
        
    def test_register_existing_username(self):
        """Test registration with existing username"""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': self.username,
                'email': 'another@example.com',
                'password': self.password
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Username already exists')
        
    def test_register_existing_email(self):
        """Test registration with existing email"""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'anotheruser',
                'email': self.email,
                'password': self.password
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Email already exists')
        
    def test_logout(self):
        """Test logout functionality"""
        # First login
        self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': self.username, 'password': self.password}),
            content_type='application/json'
        )
        
        # Then logout via API
        response = self.client.post('/api/auth/logout')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Logged out successfully')
        
        # Test UI logout
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out successfully', response.data)

if __name__ == '__main__':
    unittest.main()