from app.models.baseModel import BaseModel
from app import db, bcrypt
from sqlalchemy.orm import validates
import re

class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name  = db.Column(db.String(50), nullable=False)
    email      = db.Column(db.String(120), nullable=False, unique=True)
    password   = db.Column(db.String(128), nullable=False)
    is_admin   = db.Column(db.Boolean, default=False)

    places  = db.relationship('Place', back_populates='owner_rel', lazy=True)
    reviews = db.relationship('Review', back_populates='user_rel', lazy=True)

    emails = set()

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name  = last_name
        self.email      = email
        self.is_admin   = is_admin
        self.password   = password

    @validates('first_name')
    def validate_first_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("First name must be a string")
        if len(value) > 50:
            raise ValueError("First name must be 50 characters max.")
        return value

    @validates('last_name')
    def validate_last_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Last name must be a string")
        if len(value) > 50:
            raise ValueError("Last name must be 50 characters max.")
        return value

    @validates('email')
    def validate_email(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Email must be a string")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        if value in User.emails:
            raise ValueError("Email already exists")
        if hasattr(self, 'email') and self.email:
            User.emails.discard(self.email)
        User.emails.add(value)
        return value

    @validates('is_admin')
    def validate_is_admin(self, key, value):
        if not isinstance(value, bool):
            raise TypeError("Is Admin must be a boolean")
        return value

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id':         self.id,
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'email':      self.email
        }