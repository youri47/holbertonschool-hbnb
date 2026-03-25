from app import db
from app.models.base_model import BaseModel
from sqlalchemy.orm import validates


class Review(BaseModel):
    __tablename__ = 'reviews'

    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'place_id', name='unique_user_place_review'),
    )

    @validates('text')
    def validate_text(self, key, value):
        if not value or not value.strip():
            raise ValueError("Review text is required.")
        return value.strip()

    @validates('rating')
    def validate_rating(self, key, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Rating must be an integer.")
        if not 1 <= value <= 5:
            raise ValueError("Rating must be between 1 and 5.")
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'rating': self.rating,
            'place_id': self.place_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }