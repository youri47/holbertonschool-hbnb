from app.persistence.repository import SQLAlchemyRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

class HBnBFacade:
    def __init__(self):
        self.user_repo    = UserRepository()
        self.amenity_repo = SQLAlchemyRepository(Amenity)
        self.place_repo   = SQLAlchemyRepository(Place)
        self.review_repo  = SQLAlchemyRepository(Review)

    # USER
    def create_user(self, user_data):
        user = User(**user_data)
        user.hash_password(user_data['password'])
        self.user_repo.add(user)
        return user

    def get_users(self):
        return self.user_repo.get_all()

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def update_user(self, user_id, user_data):
        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)

    # AMENITY
    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        self.amenity_repo.update(amenity_id, amenity_data)
        return self.amenity_repo.get(amenity_id)

    # PLACE
    def create_place(self, place_data):
        owner_id = place_data.pop('owner_id', None)
        amenities = place_data.pop('amenities', None)

        user = self.user_repo.get(owner_id)
        if not user:
            raise KeyError('Invalid input data')

        place = Place(**place_data)
        place.owner_id = owner_id
        self.place_repo.add(place)

        if amenities:
            for amenity_id in amenities:
                amenity = self.amenity_repo.get(amenity_id)
                if amenity:
                    place.amenities.append(amenity)
            from app import db
            db.session.commit()

        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        self.place_repo.update(place_id, place_data)
        return self.place_repo.get(place_id)

    # REVIEWS
    def create_review(self, review_data):
        user_id  = review_data.pop('user_id')
        place_id = review_data.pop('place_id')

        user = self.user_repo.get(user_id)
        if not user:
            raise KeyError('Invalid input data')

        place = self.place_repo.get(place_id)
        if not place:
            raise KeyError('Invalid input data')

        review = Review(**review_data)
        review.user_id  = user_id
        review.place_id = place_id
        self.review_repo.add(review)
        return review

    def get_review_by_user_and_place(self, user_id, place_id):
        return Review.query.filter_by(
            user_id=user_id,
            place_id=place_id
        ).first()

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            raise KeyError('Place not found')
        return place.reviews

    def update_review(self, review_id, review_data):
        self.review_repo.update(review_id, review_data)
        return self.review_repo.get(review_id)

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        self.review_repo.delete(review_id)