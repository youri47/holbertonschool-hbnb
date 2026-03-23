#!/usr/bin/python3

"""Defines the Place model for the application."""
from sqlalchemy.orm import relationship, validates
from app import db
import uuid
from app.models.base_model import BaseModel
from typing import List, Optional
from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity

class Place(BaseModel):
    __tablename__ = 'places'
    """Represents a property listing in the application.
    
    Attributes:
        title (str): Title of the place
        description (str): Detailed description
        price (float): Price per night
        latitude (float): Geographic latitude
        longitude (float): Geographic longitude
        owner_id (str): ID of the user who owns this place
        reviews (List[Review]): List of reviews for this place
        amenities (List[Amenity]): List of amenities available at this place
    """

    place_amenity = db.Table('place_amenity',
        db.Column('place_id', db.String(60), db.ForeignKey('places.id'), primary_key=True),
        db.Column('amenity_id', db.String(60), db.ForeignKey('amenities.id'), primary_key=True)
    )
    
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='places', lazy=True)
    reviews = db.relationship('Review', backref='place', lazy=True)
    amenities = db.relationship('Amenity', secondary=place_amenity, backref='places', lazy=True)
    
    def __init__(self,
                title: str,
                description: str,
                price: float,
                latitude: float,
                longitude: float,
                owner_id: str,
                **kwargs):
        """Initialize a new Place instance.
        
        Args:
            title (str): Title of the place
            description (str): Detailed description
            price (float): Price per night
            latitude (float): Geographic latitude
            longitude (float): Geographic longitude
            owner_id (str): ID of the user who owns this place
            **kwargs: Additional attributes from BaseModel
        """
        super().__init__(**kwargs)
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id
        self.reviews: List['Review'] = []
        self.amenities: List['Amenity'] = []

    @validates('price')
    def validate_price(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("price must be a number")
        if value < 0:
            raise ValueError("price must be non-negative")
        return value

    @validates('latitude')
    def validate_latitude(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("latitude must be a number")
        if not -90 <= value <= 90:
            raise ValueError("latitude must be between -90 and 90")
        return value

    @validates('longitude')
    def validate_longitude(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("longitude must be a number")
        if not -180 <= value <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return value