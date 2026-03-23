#!/usr/bin/python3

"""Place service module for handling place-related business logic.

This module provides the PlaceService class which encapsulates all business logic
related to place management, including creation, retrieval, and updates.
"""

from typing import List, Optional
from http import HTTPStatus
from flask_restx import abort

from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review
from app.models.user import User
from app.persistence.repository import Repository
from app.persistence.place_repository import PlaceRepository
from app.services.user_service import user_service as global_user_service

class PlaceService:
    """Service class for handling place-related operations.
    
    This class provides methods for creating, retrieving, updating, and deleting
    places, as well as managing place amenities and reviews.
    """
    
    def __init__(self, repository: Optional[Repository] = None, user_service=None):
        """Initialize the PlaceService with a repository and services.
        
        Args:
            repository: The repository to use for data access. If not provided,
                     an InMemoryRepository will be used by default.
            user_service: The user service to use for user-related operations.
        """
        self.repository = repository or PlaceRepository()
        self.user_service = user_service or global_user_service
    
    def _validate_user_exists(self, user_id: str) -> None:
        """Check if a user with the given ID exists.
        
        Args:
            user_id: The ID of the user to check
            
        Raises:
            ValueError: If user doesn't exist
        """
        if not self.user_service.get_user(user_id):
            raise ValueError(f"User with id {user_id} does not exist")

    def _validate_amenities_exist(self, amenity_ids: List[str]) -> None:
        """Check if all amenity IDs in the list exist.
        
        Args:
            amenity_ids: List of amenity IDs to validate
            
        Raises:
            ValueError: If any amenity doesn't exist
        """
        from app.services.facade import hbnb_facade as facade
        for amenity_id in amenity_ids:
            if not facade.amenity_service.get_amenity(amenity_id):
                raise ValueError(f"Amenity with id {amenity_id} does not exist")

    def create_place(self, title: str, description: str, price: float,
                   latitude: float, longitude: float, owner_id: str,
                   amenities: Optional[List[str]] = None) -> Optional[Place]:
        """Create a new place with the provided information.
        
        Args:
            title: The title of the place
            description: A detailed description of the place
            price: The price per night
            latitude: The geographical latitude of the place
            longitude: The geographical longitude of the place
            owner_id: The ID of the user who owns this place
            amenities: List of amenity IDs to associate with this place
            
        Returns:
            The newly created Place instance, or None if creation failed
            
        Raises:
            ValueError: If the user or any amenity doesn't exist, or if input validation fails
        """
        # Validate user exists
        self._validate_user_exists(owner_id)
        
        # Validate amenities if provided
        if amenities:
            self._validate_amenities_exist(amenities)

        # Create the place
        place = Place(
            title=title,
            description=description,
            price=price,
            latitude=latitude,
            longitude=longitude,
            owner_id=owner_id
        )
        place.reviews = []
        
        # Associate amenities if provided
        if amenities:
            from app.services.facade import hbnb_facade as facade
            for amenity_id in amenities:
                amenity = facade.amenity_service.get_amenity(amenity_id)
                if amenity:
                    place.amenities.append(amenity)
    
        self.repository.add(place)
    
        # Update user's places list
        self.user_service.add_user_place(owner_id, place.id)
    
        return place
    
    
    def get_place(self, place_id: str) -> Optional[Place]:
        """Retrieve a place by its ID.
        
        Args:
            place_id: The unique identifier of the place
            
        Returns:
            The Place instance if found, None otherwise
        """
        return self.repository.get(place_id)
    
    def get_all_places(self) -> List[Place]:
        """Retrieve all places in the system.
        
        Returns:
            A list of all Place instances
        """
        return self.repository.get_all()
    
    def update_place(self, place_id: str, **updates) -> Optional[Place]:
        """Update a place's information.
        
        Args:
            place_id: The ID of the place to update
            **updates: Dictionary of fields to update
            
        Returns:
            The updated Place instance if successful, None if place not found
            
        Raises:
            ValueError: If any amenity doesn't exist or if validation fails
        """
        # Validate amenities if they're being updated
        if 'amenities' in updates:
            self._validate_amenities_exist(updates['amenities'])
            
        # Get the current place to preserve existing fields
        place = self.get_place(place_id)
        if not place:
            return None
            
        # Update the place attributes
        for key, value in updates.items():
            if hasattr(place, key):
                setattr(place, key, value)
                
        # Save the updated place
        self.repository.add(place)
        return place
    
    def search_places(self, **filters) -> List[Place]:
        """Search for places based on filter criteria.
        
        Args:
            **filters: Keyword arguments for filtering places (e.g., min_price, max_price)
            
        Returns:
            A list of Place instances matching the filter criteria
        """
        all_places = self.get_all_places()
        
        # Apply filters
        filtered_places = all_places
        if 'min_price' in filters:
            filtered_places = [p for p in filtered_places 
                            if p.price >= float(filters['min_price'])]
        if 'max_price' in filters:
            filtered_places = [p for p in filtered_places 
                            if p.price <= float(filters['max_price'])]
            
        return filtered_places
    
    def add_review(self, place_id: str, review: Review) -> bool:
        """Ajoute un avis à la place"""
        place = self.get_place(place_id)
        if not place:
            return False
            
        if review not in place.reviews:
            place.reviews.append(review)
            if review.place_id != place_id:
                review.place_id = place_id
            return True
        return False
    
    def get_place_reviews(self, place_id: str) -> List[Review]:
        """Récupère tous les avis d'une place"""
        place = self.get_place(place_id)
        return place.reviews if place else []
    
    def add_amenity(self, place_id: str, amenity: Amenity) -> bool:
        """Ajoute un équipement à la place"""
        place = self.get_place(place_id)
        if not place:
            return False
            
        if amenity not in place.amenities:
            place.amenities.append(amenity)
            return True
        return False
    
    def get_place_amenities(self, place_id: str) -> List[Amenity]:
        """Récupère tous les équipements d'une place"""
        place = self.get_place(place_id)
        return place.amenities if place else []
    
    def remove_amenity(self, place_id: str, amenity: Amenity) -> bool:
        """Supprime un équipement de la place"""
        place = self.get_place(place_id)
        if not place or amenity not in place.amenities:
            return False
            
        place.amenities.remove(amenity)
        return True


# Singleton instance of the PlaceService
place_service = PlaceService()