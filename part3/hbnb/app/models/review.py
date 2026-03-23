#!/usr/bin/python3

"""Defines the Review model for the application."""
from app import db
import uuid
from app.models.base_model import BaseModel
from sqlalchemy.orm import validates

class Review(BaseModel):
    """Represents a user review for a place.
    
    Attributes:
        text (str): The review content
        rating (int): Rating from 1 to 5
        place_id (str): ID of the reviewed place
        user_id (str): ID of the user who wrote the review
    """
    __tablename__ = 'reviews'
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(60), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self,
                text: str,
                rating: int,
                place_id: str,
                user_id: str,
                **kwargs):
        """Initialize a new Review instance.
        
        Args:
            text (str): The review content
            rating (int): Rating from 1 to 5
            place_id (str): ID of the reviewed place
            user_id (str): ID of the user who wrote the review
            **kwargs: Additional attributes from BaseModel
        """
        super().__init__(**kwargs)
        self.text = text
        self.rating = rating
        self.place_id = place_id
        self.user_id = user_id

    @validates('rating')
    def validate_rating(self, key, value):
        value = int(value)
        if not (1 <= value <= 5):
            raise ValueError("rating must be between 1 and 5")
        return value