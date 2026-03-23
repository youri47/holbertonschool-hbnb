"""Facade module providing a unified interface to the HBnB application services.

This module implements the Facade pattern to provide a simplified interface
to the complex subsystem of services and repositories in the application.
"""

from typing import Dict, Optional, List
from .user_service import UserService
from .place_service import PlaceService
from .review_service import ReviewService
from .amenity_service import AmenityService
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from app.persistence.repository import SQLAlchemyRepository
from app.persistence.user_repository import UserRepository

class HBnBFacade:
    """Main facade for the HBnB application.
    
    This class provides a unified interface to access all the application's
    functionality, abstracting away the complexity of the underlying services
    and repositories.
    """
    
    def __init__(self):
        """Initialize the HBnB facade with all required services and repositories.
        
        Sets up in-memory repositories and initializes the corresponding services.
        """
        # Initialize repositories
        user_repo = UserRepository()
        place_repo = SQLAlchemyRepository(Place)
        review_repo = SQLAlchemyRepository(Review)
        amenity_repo = SQLAlchemyRepository(Amenity)
        
        # Initialize services with their respective repositories
        self.user_service = UserService(user_repo)
        
        # Initialize place service with user service for validation
        self.place_service = PlaceService(
            repository=place_repo,
            user_service=self.user_service
        )
        
        # Initialize review service with both user and place services for validation
        self.review_service = ReviewService(
            repository=review_repo,
            user_service=self.user_service,
            place_service=self.place_service
        )
        self.amenity_service = AmenityService(amenity_repo)
    
    # User methods
    def create_user(self, email: str, first_name: str, last_name: str, password: str, is_admin: bool = False) -> User:
        """Create a new user with the provided information.
        
        Args:
            email: The user's email address (must be unique)
            first_name: The user's first name
            last_name: The user's last name
            is_admin: Whether the user should have admin privileges
            
        Returns:
            The newly created User instance
            
        Raises:
            ValueError: If a user with the given email already exists
        """
        return self.user_service.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_admin=is_admin
        )
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            The User instance if found, None otherwise
        """
        return self.user_service.get_user(user_id)
    
    def get_all_users(self) -> List[User]:
        """Retrieve all users in the system.
        
        Returns:
            A list of all User instances
        """
        return self.user_service.get_all_users()
        
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            The User instance if found, None otherwise
        """
        return self.user_service.get_user_by_email(email)

    # Place methods
    def create_place(self, **kwargs) -> Place:
        """Create a new place.
        
        Args:
            **kwargs: Keyword arguments for place creation
            
        Returns:
            The newly created Place instance
        """
        return self.place_service.create_place(**kwargs)
    
    def get_place(self, place_id: str) -> Optional[Place]:
        """Retrieve a place by its ID.
        
        Args:
            place_id: The unique identifier of the place
            
        Returns:
            The Place instance if found, None otherwise
        """
        return self.place_service.get_place(place_id)
    
    # Review methods
    def create_review(self, **kwargs) -> Review:
        """Create a new review.
        
        Args:
            **kwargs: Keyword arguments for review creation
            
        Returns:
            The newly created Review instance
        """
        return self.review_service.create_review(**kwargs)

    def get_review(self, review_id: str) -> Optional[Review]:
        """Retrieve a review by its ID.
        
        Args:
            review_id: The unique identifier of the review
            
        Returns:
            The Review instance if found, None otherwise
        """
        return self.review_service.get_review(review_id)
    
    def get_all_reviews(self) -> List[Review]:
        """Retrieve all reviews in the system.
        
        Returns:
            A list of all Review instances
        """
        return self.review_service.get_all_reviews()
    
    def update_review(self, review_id: str, **updates) -> Optional[Review]:
        """Update a review's information.
        
        Args:
            review_id: The ID of the review to update
            **updates: Dictionary of fields to update
            
        Returns:
            The updated Review instance if successful, None if review not found
        """
        return self.review_service.update_review(review_id, **updates)
    
    def delete_review(self, review_id: str) -> bool:
        """Delete a review from the system.
        
        Args:
            review_id: The ID of the review to delete
            
        Returns:
            True if the review was deleted, False if not found
        """
        return self.review_service.delete_review(review_id)

    def get_reviews_by_place(self, place_id: str) -> List[Review]:
        """Retrieve all reviews for a specific place.
        
        Args:
            place_id: The unique identifier of the place
            
        Returns:
            A list of Review instances matching the place ID
        """
        return self.review_service.get_reviews_by_place(place_id)
    
    # Amenity methods
    def get_amenities(self) -> List[Amenity]:
        """Retrieve all amenities.
        
        Returns:
            A list of all Amenity instances
        """
        return self.amenity_service.get_all_amenities()
    
    def search_places(self, **filters) -> List[Place]:
        """Search for places based on filters.
        
        Args:
            **filters: Keyword arguments for filtering places
            
        Returns:
            A list of Place instances matching the filters
        """
        return self.place_service.search_places(**filters)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            The User instance if found, None otherwise
        """
        return self.user_service.get_user_by_email(email)



    def update_user(self, user_id: str, **updates) -> Optional[User]:
        """Update a user's information.
        
        Args:
            user_id: The ID of the user to update
            **updates: Dictionary of fields to update
            
        Returns:
            The updated User instance if successful, None if user not found
            
        Raises:
            ValueError: If the update would result in a duplicate email
        """
        return self.user_service.update_user(user_id, **updates)

    def create_amenity(self, amenity_data):
        """Create a new amenity.
    
        Args:   
            amenity_data: Dictionary containing amenity data with a 'name' key
        
        Returns:
            The newly created Amenity instance
        
        Raises:
            ValueError: If the name is invalid (handled by the service)
        """
        return self.amenity_service.create_amenity(amenity_data['name'])

    def get_amenity(self, amenity_id):
        """Retrieve an amenity by its ID.
        
        Args:
            amenity_id: The unique identifier of the amenity
            
        Returns:
            The Amenity instance if found, None otherwise
        """
        return self.amenity_service.get_amenity(amenity_id)

    def get_all_amenities(self):
        """Retrieve all amenities.
        
        Returns:
            A list of all Amenity instances
        """
        return self.amenity_service.get_all_amenities()

    def update_amenity(self, amenity_id, **amenity_data):
        """Update an amenity's information.
        
        Args:
            amenity_id: The ID of the amenity to update
            **amenity_data: Keyword arguments containing amenity data to update
            
        Returns:
            The updated Amenity instance if successful, None if amenity not found
            
        Raises:
            ValueError: If the update would result in a duplicate name
        """
        return self.amenity_service.update_amenity(amenity_id, **amenity_data)

# Singleton instance of the facade
hbnb_facade = HBnBFacade()