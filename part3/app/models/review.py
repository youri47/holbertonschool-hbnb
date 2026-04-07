from app.models.baseModel import BaseModel
from app import db
from sqlalchemy.orm import validates

class Review(BaseModel):
    __tablename__ = 'reviews'

    text     = db.Column(db.String(500), nullable=False)
    rating   = db.Column(db.Integer, nullable=False)
    user_id  = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)

    user_rel  = db.relationship('User', back_populates='reviews')
    place_rel = db.relationship('Place', back_populates='reviews')

    def __init__(self, text, rating):
        super().__init__()
        self.text   = text
        self.rating = rating

    @validates('text')
    def validate_text(self, key, value):
        if not value:
            raise ValueError("Text cannot be empty")
        if not isinstance(value, str):
            raise TypeError("Text must be a string")
        return value

    @validates('rating')
    def validate_rating(self, key, value):
        if not isinstance(value, int):
            raise TypeError("Rating must be an integer")
        if not 1 <= value <= 5:
            raise ValueError("Rating must be between 1 and 5.")
        return value

    def to_dict(self):
        return {
            'id':       self.id,
            'text':     self.text,
            'rating':   self.rating,
            'place_id': self.place_id,
            'user_id':  self.user_id
        }