from app import db
from .baseclass import BaseModel
from sqlalchemy import CheckConstraint

class Review(BaseModel):
    __tablename__ = 'reviews'

    text = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    # relationship
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    place = db.relationship('Place', back_populates='reviews')
    author = db.relationship('User', back_populates='reviews')

    __table_args__ = (
        CheckConstraint('rating <= 5 AND rating >= 1', name='rating_range'),
    )