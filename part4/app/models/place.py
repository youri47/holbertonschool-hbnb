from app.models.baseModel import BaseModel
from app import db
from app.models.place_amenity import place_amenity
from sqlalchemy.orm import validates

class Place(BaseModel):
    __tablename__ = 'places'

    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price       = db.Column(db.Float, nullable=False)
    latitude    = db.Column(db.Float, nullable=False)
    longitude   = db.Column(db.Float, nullable=False)
    owner_id    = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    owner_rel = db.relationship('User', back_populates='places')
    reviews   = db.relationship('Review', back_populates='place_rel', lazy=True)
    amenities = db.relationship('Amenity', secondary=place_amenity, lazy='subquery',
                                backref=db.backref('places', lazy=True))

    def __init__(self, title, price, latitude, longitude, description=None):
        super().__init__()
        self.title       = title
        self.description = description
        self.price       = price
        self.latitude    = latitude
        self.longitude   = longitude

    @validates('title')
    def validate_title(self, key, value):
        if not value:
            raise ValueError("Title cannot be empty")
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        if len(value) > 100:
            raise ValueError("Title must be 100 characters max.")
        return value

    @validates('price')
    def validate_price(self, key, value):
        if not isinstance(value, (float, int)):
            raise TypeError("Price must be a number")
        if value < 0:
            raise ValueError("Price must be positive.")
        return value

    @validates('latitude')
    def validate_latitude(self, key, value):
        if not isinstance(value, float):
            raise TypeError("Latitude must be a float")
        if not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90.")
        return value

    @validates('longitude')
    def validate_longitude(self, key, value):
        if not isinstance(value, float):
            raise TypeError("Longitude must be a float")
        if not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180.")
        return value

    def to_dict(self):
        return {
            'id':          self.id,
            'title':       self.title,
            'description': self.description,
            'price':       self.price,
            'latitude':    self.latitude,
            'longitude':   self.longitude,
            'owner_id':    self.owner_id
        }

    def to_dict_list(self):
        return {
            'id':          self.id,
            'title':       self.title,
            'description': self.description,
            'price':       self.price,
            'latitude':    self.latitude,
            'longitude':   self.longitude,
            'owner_id':    self.owner_id,
            'owner':       self.owner_rel.to_dict() if self.owner_rel else None,
            'amenities':   [a.to_dict() for a in self.amenities],
            'reviews':     [r.to_dict() for r in self.reviews]
        }