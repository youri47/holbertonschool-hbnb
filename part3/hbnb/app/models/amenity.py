#!/usr/bin/python3

"""Defines the Amenity model for the application."""
from app import db
import uuid
from app.models.base_model import BaseModel

class Amenity(BaseModel):
    """Represents an amenity that can be associated with places.
    
    Attributes:
        name (str): The name of the amenity (e.g., 'WiFi', 'Pool', 'Parking')
    """
    __tablename__ = 'amenities'
    
    name = db.Column(db.String(120), nullable=False)
    
    def __init__(self, name: str, **kwargs):
        """Initialize a new Amenity instance.
        
        Args:
            name (str): The name of the amenity
            **kwargs: Additional attributes from BaseModel
        """
        super().__init__(**kwargs)
        self.name = name
        
    def to_dict(self):
        """Return a dictionary representation of the Amenity instance.
        
        Returns:
            dict: Dictionary containing the amenity's attributes
        """
        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
