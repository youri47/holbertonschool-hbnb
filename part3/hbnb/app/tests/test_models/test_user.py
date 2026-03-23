#!/usr/bin/python3

import unittest
from app.models.user import User

class TestUser(unittest.TestCase):
    """Test cases for the User model"""

    def test_user_creation(self):
        """Test creating a new user with required fields"""
        user = User(
            email="john.doe@example.com",
            password_hash="hashed_password_123",
            first_name="John",
            last_name="Doe"
        )
        
        self.assertEqual(user.email, "john.doe@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.is_admin, False)  # Default value
        self.assertEqual(user.places, [])  # Should be initialized as empty list
        self.assertIsNotNone(user.id)  # ID should be auto-generated
        self.assertIsNotNone(user.created_at)  # Timestamp should be set
        self.assertIsNotNone(user.updated_at)  # Timestamp should be set

    def test_user_creation_with_admin(self):
        """Test creating an admin user"""
        admin = User(
            email="admin@example.com",
            password_hash="admin_hashed_pass",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        
        self.assertTrue(admin.is_admin)

    '''def test_user_str_representation(self):
        """Test the string representation of User"""
        user = User(
            email="test@example.com",
            password_hash="test_pass",
            first_name="Test",
            last_name="User"
        )
        
        self.assertIn("User", str(user))
        self.assertIn(user.id, str(user))
        self.assertIn(user.email, str(user))'''

if __name__ == '__main__':
    unittest.main()