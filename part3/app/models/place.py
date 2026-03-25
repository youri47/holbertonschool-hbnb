from app import db
from app.models.base_model import BaseModel
from sqlalchemy.orm import validates

place_amenity = db.Table('place_amenity',
    db.Column('place_id', db.String(36), db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True)
)


class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    reviews = db.relationship('Review', backref='place', lazy=True, cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary=place_amenity, lazy='subquery',
                                backref=db.backref('places', lazy=True))

    @validates('title')
    def validate_title(self, key, value):
        if not value or not value.strip():
            raise ValueError("Title is required.")
        if len(value) > 100:
            raise ValueError("Title must be at most 100 characters.")
        return value.strip()

    @validates('price')
    def validate_price(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Price must be a number.")
        if value <= 0:
            raise ValueError("Price must be a positive value.")
        return value

    @validates('latitude')
    def validate_latitude(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Latitude must be a number.")
        if not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90.")
        return value

    @validates('longitude')
    def validate_longitude(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Longitude must be a number.")
        if not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180.")
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner_id,
            'amenities': [a.to_dict() for a in self.amenities] if self.amenities else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }