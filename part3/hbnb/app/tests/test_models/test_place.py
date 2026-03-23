#!/usr/bin/python3

"""Unit tests for the Place model and its relationships."""

import unittest
from app.models.place import Place
from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity

class TestPlace(unittest.TestCase):
    """Test cases for the Place model"""

    def setUp(self):
        """Set up test fixtures"""
        self.owner = User(
            email="owner@example.com",
            password_hash="owner_pass",
            first_name="Place",
            last_name="Owner"
        )
        
        self.place = Place(
            title="Cozy Apartment",
            description="A nice place to stay",
            price=100.0,
            latitude=37.7749,
            longitude=-122.4194,
            owner_id=self.owner.id
        )
    
    def test_place_creation(self):
        """Test creating a new place with required fields"""
        self.assertEqual(self.place.title, "Cozy Apartment")
        self.assertEqual(self.place.description, "A nice place to stay")
        self.assertEqual(self.place.price, 100.0)
        self.assertEqual(self.place.latitude, 37.7749)
        self.assertEqual(self.place.longitude, -122.4194)
        self.assertEqual(self.place.owner_id, self.owner.id)
        self.assertEqual(self.place.reviews, [])
        self.assertEqual(self.place.amenities, [])
        self.assertIsNotNone(self.place.id)
        self.assertIsNotNone(self.place.created_at)
        self.assertIsNotNone(self.place.updated_at)
    
    def test_add_review(self):
        """Test adding a review to a place"""
        review = Review(
            text="Great stay!",
            rating=5,
            place_id=self.place.id,
            user_id=self.owner.id
        )
        
        self.place.reviews.append(review)
        
        self.assertEqual(len(self.place.reviews), 1)
        self.assertEqual(self.place.reviews[0].text, "Great stay!")
        self.assertEqual(self.place.reviews[0].rating, 5)
        self.assertEqual(self.place.reviews[0].place_id, self.place.id)
    
    def test_add_amenity(self):
        """Test adding an amenity to a place"""
        amenity = Amenity(name="Wi-Fi")
        self.place.amenities.append(amenity)
        
        self.assertEqual(len(self.place.amenities), 1)
        self.assertEqual(self.place.amenities[0].name, "Wi-Fi")

if __name__ == '__main__':
    unittest.main()