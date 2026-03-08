from app.models.amenitiy import Amenity
from app import db
from app.persistence.repository import SQLAlchemyRepository

class AmenityRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Amenity)

    def get_amenity_by_id(self, id):
        return self.model.query.filter_by(id=id).first()