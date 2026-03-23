#!/usr/bin/python3

"""Defines the base model class for all models in the application."""
from app import db
import uuid
from datetime import datetime


class BaseModel(db.Model):
    """Base class for all models with common attributes and methods."""
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self):
        """Initialize a new model instance with unique ID and timestamps."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now()

    def update(self, data):
        """
        Update model attributes with provided dictionary.
        
        Args:
            data (dict): Dictionary of attributes to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()  # Update the updated_at timestamp

    def to_dict(self):
        """Return a dictionary representation of the model instance."""
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
