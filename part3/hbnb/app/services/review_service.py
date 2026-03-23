#!/usr/bin/python3

"""Review service module for handling review-related business logic.

This module provides the ReviewService class which encapsulates all business logic
related to review management, including creation, retrieval, and updates.
"""

from typing import List, Optional
from flask_restx import abort
from http import HTTPStatus
from app.models.review import Review
from app.persistence.repository import Repository
from app.persistence.review_repository import ReviewRepository

class ReviewService:
    """Service class for handling review-related operations.
    
    This class provides methods for creating, retrieving, updating, and deleting
    reviews, as well as querying reviews by place or user.
    """
    
    def __init__(self, repository: Repository = None, user_service=None, place_service=None):
        """Initialize the ReviewService with a repository and optional dependencies.
        
        Args:
            repository: The repository to use for data access. If not provided,
                     an InMemoryRepository will be used by default.
            user_service: Service for user-related operations
            place_service: Service for place-related operations
        """
        self.repository = repository or ReviewRepository()
        self.user_service = user_service
        self.place_service = place_service
        
    def _validate_user_exists(self, user_id: str) -> None:
        """Check if a user with the given ID exists.
        
        Args:
            user_id: The ID of the user to check
            
        Raises:
            HTTPException: 404 if user doesn't exist
        """
        if self.user_service and not self.user_service.get_user(user_id):
            abort(HTTPStatus.NOT_FOUND, f"User with id {user_id} does not exist")
    
    def _validate_place_exists(self, place_id: str) -> None:
        """Check if a place with the given ID exists.
        
        Args:
            place_id: The ID of the place to check
            
        Raises:
            HTTPException: 404 if place doesn't exist
        """
        if self.place_service and not self.place_service.get_place(place_id):
            abort(HTTPStatus.NOT_FOUND, f"Place with id {place_id} does not exist")
    
    def create_review(self, text: str, rating: int, 
                     place_id: str, user_id: str) -> Optional[Review]:
        """Create a new review with the provided information.
        
        Args:
            text: The review content
            rating: The rating given (typically 1-5)
            place_id: The ID of the place being reviewed
            user_id: The ID of the user writing the review
            
        Returns:
            The newly created Review instance, or None if validation fails
            
        Raises:
            ValueError: If user_id or place_id doesn't exist
        """
        # Validate user and place exist
        self._validate_user_exists(user_id)
        self._validate_place_exists(place_id)
            
        # Validate rating is between 1 and 5
        if not 1 <= rating <= 5:
            abort(HTTPStatus.BAD_REQUEST, "Rating must be between 1 and 5")
            
        review = Review(
            text=text,
            rating=rating,
            place_id=place_id,
            user_id=user_id
        )
        self.repository.add(review)
        return review
    
    def get_review(self, review_id: str) -> Optional[Review]:
        """Retrieve a review by its ID.
        
        Args:
            review_id: The unique identifier of the review
            
        Returns:
            The Review instance if found, None otherwise
        """
        return self.repository.get(review_id)
    
    def get_all_reviews(self) -> List[Review]:
        """Retrieve all reviews in the system.
        
        Returns:
            A list of all Review instances
        """
        return self.repository.get_all()
    
    def get_reviews_by_place(self, place_id: str) -> List[Review]:
        """Retrieve all reviews for a specific place.
        
        Args:
            place_id: The ID of the place to get reviews for
            
        Returns:
            A list of Review instances for the specified place
        """
        return [r for r in self.repository.get_all() 
                if getattr(r, 'place_id', None) == place_id]
    
    def get_reviews_by_user(self, user_id: str) -> List[Review]:
        """Retrieve all reviews written by a specific user.
        
        Args:
            user_id: The ID of the user whose reviews to retrieve
            
        Returns:
            A list of Review instances written by the specified user
        """
        return [r for r in self.repository.get_all() 
                if getattr(r, 'user_id', None) == user_id]
    
    def update_review(self, review_id: str, **updates) -> Optional[Review]:
        """Update a review's information.
        
        Args:
            review_id: The ID of the review to update
            **updates: Dictionary of fields to update
            
        Returns:
            The updated Review instance if successful, None if review not found
            
        Raises:
            HTTPException: With appropriate status code if validation fails
        """
        # Check if user_id is being updated and validate it exists
        if 'user_id' in updates:
            self._validate_user_exists(updates['user_id'])
            
        # Check if place_id is being updated and validate it exists
        if 'place_id' in updates:
            self._validate_place_exists(updates['place_id'])
            
        # Validate rating is between 1 and 5 if being updated
        if 'rating' in updates and not 1 <= updates['rating'] <= 5:
            abort(HTTPStatus.BAD_REQUEST, "Rating must be between 1 and 5")
            
        return self.repository.update(review_id, updates)
    
    def delete_review(self, review_id: str) -> bool:
        """Delete a review from the system.
        
        Args:
            review_id: The ID of the review to delete
            
        Returns:
            True if the review was deleted, False if not found
        """
        if self.repository.get(review_id):
            self.repository.delete(review_id)
            return True
        return False


# Singleton instance of the ReviewService
review_service = ReviewService()