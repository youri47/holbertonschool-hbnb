#!/usr/bin/python3

"""Defines the User model for the application."""
from app import db
import uuid
from app.models.base_model import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    """Represents a user in the application.
    
    Attributes:
        email (str): The user's email address (must be unique)
        first_name (str): The user's first name
        last_name (str): The user's last name
        password (str): The user's hashed password
        is_admin (bool): Whether the user has admin privileges
        places (list): List of place IDs owned by this user
    """
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def __init__(self, email: str, first_name: str, last_name: str, 
                 password: str, is_admin: bool = False, **kwargs):
        """Initialize a new User instance.
        
        Args:
            email: The user's email address
            first_name: The user's first name
            last_name: The user's last name
            password: The user's hashed password (should be pre-hashed)
            is_admin: Whether the user has admin privileges
            **kwargs: Additional attributes from BaseModel
        """
        super().__init__(**kwargs)
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password  # Already hashed password
        self.is_admin = is_admin

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using Flask-Bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password as string
        """
        from app import bcrypt
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        from app import bcrypt
        return bcrypt.check_password_hash(self.password, password)