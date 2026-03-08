from app.services.repositories.user_repository import UserRepository
from app.services.repositories.place_repository import PlaceRepository
from app.services.repositories.review_repository import ReviewRepository
from app.services.repositories.amenity_repository import AmenityRepository
from app.models.user import User
from app.models.amenitiy import Amenity
from app.models.place import Place
from app.models.review import Review



class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.amenity_repo = AmenityRepository()
        self.place_repo = PlaceRepository()
        self.reviews_repo = ReviewRepository()

    def create_user(self, user_data):
        user = User(**user_data)
        user.hash_password(user_data['password'])
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None

        self.user_repo.update(user_id, user_data)  # Передаем user_data (словарь), а не user
        return user

#-----------------------------------------------------------------------------------------------------------------------

    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get_amenity_by_id(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None

        self.amenity_repo.update(amenity_id, amenity_data)
        return amenity

#-----------------------------------------------------------------------------------------------------------------------

    def create_place(self, place_data):
        owner = self.get_user(place_data['owner_id'])
        if not owner:
            raise ValueError("Owner Didn't Found")

        new_place = Place(
            title=place_data['title'],
            description=place_data.get('description'),
            price=place_data['price'],
            latitude=place_data['latitude'],
            longitude=place_data['longitude'],
            owner=owner
        )

        amenity_ids = place_data.get('amenities', [])
        if isinstance(amenity_ids, list):
            for aid in amenity_ids:
                checker = self.get_amenity(aid)
                if checker:
                    new_place.amenities.append(checker)
                else:
                    raise ValueError(f"Amenity {aid} didn't found in list of amenities")

        self.place_repo.add(new_place)
        return new_place

    def get_place(self, place_id):
        return self.place_repo.get_place_by_id(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.get_place(place_id)
        if not place:
            return None

        update_dict = {}
        for field in ['title', 'description', 'price', 'latitude', 'longitude']:
            if field in place_data:
                update_dict[field] = place_data[field]
                # Сразу обновляем объект в памяти для возврата корректного ответа
                setattr(place, field, place_data[field])

        self.place_repo.update(place_id, update_dict)

        return place

# ----------------------------------------------------------------------------------------------------------------------

    def create_review(self, review_data):
        # Получаем данные безопасно
        text = review_data.get('text')
        rating = review_data.get('rating')
        user_id = review_data.get('user_id')
        place_id = review_data.get('place_id')

        # Логируем для отладки (потом можно удалить)
        print(f"DEBUG: received text={text}, rating={rating}, user_id={user_id}")

        if not text:
            raise ValueError("Review text is required")

        user = self.get_user(user_id)
        place = self.get_place(place_id)

        if not user or not place:
            raise ValueError('User or Place not found')

        new_review = Review(
            text=text,
            rating=rating,
            author=user,  # Убедись, что в модели Review связь называется author
            place=place
        )

        self.reviews_repo.add(new_review)
        return new_review

    def get_review(self, review_id):
        return self.reviews_repo.get_review_by_id(review_id)

    def get_all_reviews(self):
        return self.reviews_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return self.reviews_repo.get(place_id
                                     )
    def update_review(self, review_id, review_data):
        review = self.reviews_repo.get(review_id)
        if not review:
            raise ValueError('ValueError')

        review.text = review_data.get('text', review.text)
        review.rating = review_data.get('rating', review.rating)

        self.reviews_repo.update(review_id, review_data)
        return review

    def delete_review(self, review_id):
        review = self.reviews_repo.get(review_id)

        if not review:
            raise ValueError('ValueError')

        self.reviews_repo.delete(review_id)