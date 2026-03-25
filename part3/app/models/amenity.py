from app import db
from app.models.base_model import BaseModel
from sqlalchemy.orm import validates


class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False, unique=True)

    @validates('name')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Amenity name is required.")
        if len(value) > 50:
            raise ValueError("Amenity name must be at most 50 characters.")
        return value.strip()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }