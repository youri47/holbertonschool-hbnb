#!/usr/bin/python3

"""Amenity service module for handling amenity-related business logic.

This module provides the AmenityService class which encapsulates all business logic
related to amenity management, including creation, retrieval, and updates.
"""

from typing import List, Optional
from app.models.amenity import Amenity
from app.persistence.repository import Repository
from app.persistence.amenity_repository import AmenityRepository

class AmenityService:
    """Service class for handling amenity-related operations.
    
    This class provides methods for creating, retrieving, updating, and deleting
    amenities, which represent features or services offered by places.
    """
    
    def __init__(self, repository: Repository = None):
        """Initialize the AmenityService with a repository.
        
        Args:
            repository: The repository to use for data access. If not provided,
                     an InMemoryRepository will be used by default.
        """
        self.repository = repository or AmenityRepository()
    
    def create_amenity(self, name: str) -> Amenity:
        """Create a new amenity with the provided name.
        
        Args:
            name: The name of the amenity to create
            
        Returns:
            The newly created Amenity instance, or existing one if it already exists
            
        Raises:
            ValueError: If the name is empty or None
        """
        if not name:
            raise ValueError("Amenity name cannot be empty")
            
        # Check if an amenity with this name already exists
        existing = self.get_amenity_by_name(name)
        if existing:
            return existing
            
        amenity = Amenity(name=name)
        self.repository.add(amenity)
        return amenity
    
    def get_amenity(self, amenity_id: str) -> Optional[Amenity]:
        """Retrieve an amenity by its ID.
        
        Args:
            amenity_id: The unique identifier of the amenity
            
        Returns:
            The Amenity instance if found, None otherwise
        """
        return self.repository.get(amenity_id)
    
    def get_amenity_by_name(self, name: str) -> Optional[Amenity]:
        """Retrieve an amenity by its name.
        
        Args:
            name: The name of the amenity to find
            
        Returns:
            The Amenity instance if found, None otherwise
        """
        amenities = self.repository.get_all()
        for amenity in amenities:
            if hasattr(amenity, 'name') and amenity.name == name:
                return amenity
        return None
    
    def get_all_amenities(self) -> List[Amenity]:
        """Retrieve all amenities in the system.
        
        Returns:
            A list of all Amenity instances
        """
        return self.repository.get_all()
    
    def update_amenity(self, amenity_id: str, **updates) -> Optional[Amenity]:
        """Update an amenity's information.
        
        Args:
            amenity_id: The ID of the amenity to update
            **updates: Dictionary of fields to update
            
        Returns:
            The updated Amenity instance if successful, None if amenity not found
            
        Raises:
            ValueError: If the name is being set to an empty string
        """
        if 'name' in updates and not updates['name']:
            raise ValueError("Amenity name cannot be empty")
        return self.repository.update(amenity_id, updates)
    
    def delete_amenity(self, amenity_id: str) -> bool:
        """Delete an amenity from the system.
        
        Args:
            amenity_id: The ID of the amenity to delete
            
        Returns:
            True if the amenity was deleted, False if not found
        """
        if self.repository.get(amenity_id):
            self.repository.delete(amenity_id)
            return True
        return False


# Singleton instance of the AmenityService
amenity_service = AmenityService()