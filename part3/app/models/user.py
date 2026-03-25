import re
from app import db, bcrypt
from app.models.base_model import BaseModel
from sqlalchemy.orm import validates


class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    places = db.relationship('Place', backref='owner', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    @validates('first_name')
    def validate_first_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("First name is required.")
        if len(value) > 50:
            raise ValueError("First name must be at most 50 characters.")
        return value.strip()

    @validates('last_name')
    def validate_last_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Last name is required.")
        if len(value) > 50:
            raise ValueError("Last name must be at most 50 characters.")
        return value.strip()

    @validates('email')
    def validate_email(self, key, value):
        if not value or not value.strip():
            raise ValueError("Email is required.")
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, value):
            raise ValueError("Invalid email format.")
        return value.strip()

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        if self.password is None:
            return False
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }