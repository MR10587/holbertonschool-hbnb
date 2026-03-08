from app import db
from .baseclass import BaseModel
from sqlalchemy import CheckConstraint

# The association table
place_amenity = db.Table('place_amenity',
    db.Column('place_id', db.Integer, db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id'), primary_key=True)
)

class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(70), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    # relationships
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='places')
    reviews = db.relationship('Review', back_populates='place', lazy='dynamic', cascade="all, delete-orphan")
    amenities = db.relationship('Amenity', secondary=place_amenity, back_populates='places')

    __table_args__ = (
        CheckConstraint('latitude >= -90 AND latitude <= 90', name='latitude_range'),
        CheckConstraint('longitude >= -180 AND longitude <= 180', name='longitude_range'),
    )