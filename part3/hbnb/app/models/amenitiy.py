from app import db
from .baseclass import BaseModel

class Amenity(BaseModel):
    __tablename__ = 'amenities'
    name = db.Column(db.String(40), nullable=False)
    #relationship
    places = db.relationship('Place', secondary="place_amenity", back_populates="amenities")