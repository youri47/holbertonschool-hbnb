"""Defines the abstract base class for all repository implementations.

This module provides the abstract interface that all concrete repository
implementations must follow to ensure consistent data access patterns.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from app import db

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Abstract base class defining the repository pattern interface.
    
    This class serves as a contract for all repository implementations,
    ensuring consistent data access operations across different storage backends.
    """
    
    @abstractmethod
    def add(self, obj: T) -> T:
        """Add a new object to the repository.
        
        Args:
            obj: The object to add to the repository
            
        Returns:
            The added object, possibly with generated fields populated
        """
        pass

    @abstractmethod
    def get(self, obj_id: str) -> Optional[T]:
        """Retrieve an object by its ID.
        
        Args:
            obj_id: The unique identifier of the object
            
        Returns:
            The object if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all objects in the repository.
        
        Returns:
            A list of all objects in the repository
        """
        pass

    @abstractmethod
    def update(self, obj_id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update an existing object.
        
        Args:
            obj_id: The ID of the object to update
            data: Dictionary of attributes to update
            
        Returns:
            The updated object if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, obj_id: str) -> bool:
        """Delete an object from the repository.
        
        Args:
            obj_id: The ID of the object to delete
            
        Returns:
            True if the object was deleted, False otherwise
        """
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name: str, attr_value: Any) -> List[T]:
        """Find objects by a specific attribute value.
        
        Args:
            attr_name: Name of the attribute to search by
            attr_value: Value to match against
            
        Returns:
            A list of matching objects, empty if none found
        """
        pass

class SQLAlchemyRepository(Repository):
    def __init__(self, model):
        self.model = model

    def add(self, obj):
        db.session.add(obj)
        db.session.commit()
        return obj

    def get(self, obj_id):
        return self.model.query.get(obj_id)

    def get_all(self):
        return self.model.query.all()

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()
        return obj

    def delete(self, obj_id):
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        return self.model.query.filter_by(**{attr_name: attr_value}).first()
