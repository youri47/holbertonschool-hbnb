#!/usr/bin/python3

"""User service module for handling user-related business logic.

This module provides the UserService class which encapsulates all business logic
related to user management, including creation, retrieval, and updates.
"""

from typing import List, Optional
from app.models.user import User
from app.persistence.repository import Repository
from app.persistence.user_repository import UserRepository

class UserService:
    """Service class for handling user-related operations.
    
    This class provides methods for creating, retrieving, updating, and deleting
    users, as well as other user-related business logic.
    """
    
    def __init__(self, repository: Repository = None):
        """Initialize the UserService with a repository.
        
        Args:
            repository: The repository to use for data access. If not provided,
                     an InMemoryRepository will be used by default.
        """
        self.repository = repository or UserRepository()
    
    def create_user(self, email: str, first_name: str, last_name: str, password: str, is_admin: bool = False) -> User:
        """Create a new user with the provided information.
        
        Args:
            email: The user's email address (must be unique)
            first_name: The user's first name
            last_name: The user's last name
            password: The user's password
            is_admin: Whether the user should have admin privileges
            
        Returns:
            The newly created User instance
            
        Raises:
            ValueError: If a user with the given email already exists
        """
        if self.get_user_by_email(email):
            raise ValueError(f"A user with email {email} already exists.")
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_admin=is_admin
        )
        
        self.repository.add(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            The User instance if found, None otherwise
        """
        return self.repository.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            The User instance if found, None otherwise
        """
        return self.repository.get_user_by_email(email)
    
    def get_all_users(self) -> List[User]:
        """Retrieve all users in the system.
        
        Returns:
            A list of all User instances
        """
        return self.repository.get_all()
    
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
        if 'email' in updates and updates['email']:
            existing = self.get_user_by_email(updates['email'])
            if existing and existing.id != user_id:
                raise ValueError(f"A user with email {updates['email']} already exists.")
        
        return self.repository.update(user_id, updates)
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user from the system.
        
        Args:
            user_id: The ID of the user to delete
            
        Returns:
            True if the user was deleted, False if not found
        """
        if self.repository.get(user_id):
            self.repository.delete(user_id)
            return True
        return False
    

    
    def add_user_place(self, user_id: str, place_id: str) -> bool:
        """Add a place to the user's list of properties.
        
        Args:
            user_id: The ID of the user to update
            place_id: The ID of the place to add
            
        Returns:
            True if the place was added, False if the user was not found
        """
        user = self.get_user(user_id)
        if not user:
            return False
        # Import ici pour éviter les imports circulaires
        from app.models.place import Place
        place = Place.query.get(place_id)
        if not place:
            return False
        if place not in user.places:
            user.places.append(place)
            return True
        return False
    
    def get_user_places(self, user_id: str) -> List[str]:
        """Retrieve the list of place IDs owned by the user.
        
        Args:
            user_id: The ID of the user to retrieve places for
            
        Returns:
            A list of place IDs if the user was found, an empty list otherwise
        """
        user = self.get_user(user_id)
        return user.places if user else []


# Singleton instance of the UserService
user_service = UserService()
