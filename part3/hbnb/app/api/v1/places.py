#!/usr/bin/python3

"""Place resource module for handling place-related operations."""

from flask_restx import Namespace, Resource, fields, abort
from flask import request
from http import HTTPStatus
from app.services.facade import hbnb_facade as facade
from flask_jwt_extended import jwt_required, get_jwt_identity


def format_place_response(place, include_owner: bool = False):
    """Standardize place JSON response format"""
    from app.services.facade import hbnb_facade as facade
    
    # Build amenity details when needed
    amenities = []
    if include_owner:
        for amenity in getattr(place, 'amenities', []):
            amenities.append({
                'id': amenity.id,
                'name': amenity.name
            })
    
    base = {
        'id': place.id,
        'title': place.title,
        'description': place.description,
        'price': place.price,
        'latitude': place.latitude,
        'longitude': place.longitude,
    }
    if include_owner:
        base['owner'] = _get_owner_details(place.owner_id)
        base['amenities'] = amenities
    else:
        base['owner_id'] = place.owner_id
    return base



def _get_owner_details(owner_id: str):
    """Return detailed information about the owner (user) for embedding."""
    owner = facade.get_user(owner_id)
    if not owner:
        return None
    return {
        'id': owner.id,
        'first_name': owner.first_name,
        'last_name': owner.last_name,
        'email': owner.email
    }


api = Namespace('places', description='Place operations')

# Model for creating a place (no owner_id - taken from JWT)
place_create_model = api.model('PlaceCreate', {
    'title': fields.String(
        required=True,
        min_length=1,
        max_length=100,
        description='Title of the place',
        example='Cozy Studio in Paris'
    ),
    'description': fields.String(
        required=True,
        min_length=1,
        max_length=500,
        description='Detailed description of the place',
        example='A lovely studio apartment located in the heart of the city.'
    ),
    'price': fields.Float(
        required=True,
        description='Price per night (must be positive)',
        example=85.0,
    ),
    'latitude': fields.Float(
        required=True,
        description='Geographic latitude',
        example=48.8566
    ),
    'longitude': fields.Float(
        required=True,
        description='Geographic longitude',
        example=2.3522
    ),
    'amenities': fields.List(
        fields.String,
        required=False,
        description="List of amenities ID's",
        example=['wifi', 'tv', 'piscine']
    )
})

# Model for updating a place (no owner_id modification allowed)
place_update_model = api.model('PlaceUpdate', {
    'title': fields.String(
        required=False,
        min_length=1,
        max_length=100,
        description='Title of the place',
        example='Updated Studio in Paris'
    ),
    'description': fields.String(
        required=False,
        min_length=1,
        max_length=500,
        description='Detailed description of the place',
        example='An updated description of the apartment.'
    ),
    'price': fields.Float(
        required=False,
        description='Price per night (must be positive)',
        example=95.0,
    ),
    'latitude': fields.Float(
        required=False,
        description='Geographic latitude',
        example=48.8566
    ),
    'longitude': fields.Float(
        required=False,
        description='Geographic longitude',
        example=2.3522
    ),
    'amenities': fields.List(
        fields.String,
        required=False,
        description="List of amenities ID's",
        example=['wifi', 'tv', 'piscine']
    )
})

def format_place_summary(place):
    """Return minimal representation for listing all places."""
    return {
        'id': place.id,
        'title': place.title,
        'latitude': place.latitude,
        'longitude': place.longitude
    }

# Model for amenity representation
amenity_model = api.model('AmenityResponse', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

# Model for owner details
owner_model = api.model('OwnerResponse', {
    'id': fields.String(description='Owner ID'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'email': fields.String(description='Email')
})

# Basic place response (used for creation)
place_response_model = api.model('PlaceResponse', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Detailed description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude'),
    'owner_id': fields.String(description='Owner user ID')
})

# Detailed place response with embedded owner (used for GET /places/<id>)
place_detail_model = api.model('PlaceDetailResponse', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Detailed description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude'),
    'owner': fields.Nested(owner_model, description='Owner details'),
    'amenities': fields.List(
        fields.Nested(amenity_model),
        description='List of amenities with their details'
    )
})


@api.route('/')
class PlaceList(Resource):
    
    @api.response(200, 'Success')
    def get(self):
        """
        Retrieve all places
        
        Returns a list of all available places in the system.
        For detailed information about a specific place, use GET /places/{id}
        """
        places = facade.place_service.get_all_places()
        return [format_place_summary(p) for p in places], 200

    @api.expect(place_create_model, validate=True)
    @api.marshal_with(place_response_model, code=HTTPStatus.CREATED.value)  # type: ignore
    @api.response(201, 'Place registered successfully')
    @api.response(400, 'Invalid input')
    @api.response(500, 'Internal server error')
    @jwt_required()
    def post(self):
        """
        Register a new place
        
        Create a new place with the provided information.
        The owner is automatically set to the authenticated user.
        You can associate 0 to multiple amenities by including their IDs in the 'amenities' array.
        """
        try:
            data = api.payload.copy()
            # Add owner_id from JWT token
            data['owner_id'] = get_jwt_identity()
            
            # Basic validation for price
            if data['price'] < 0:
                abort(HTTPStatus.BAD_REQUEST.value, 'Price must be non-negative')  # type: ignore
            new_place = facade.create_place(**data)
            return format_place_response(new_place, include_owner=False), HTTPStatus.CREATED
        except ValueError as e:
            abort(HTTPStatus.NOT_FOUND.value, str(e))  # type: ignore
        except Exception:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR.value, 'An unexpected error occurred')  # type: ignore


@api.route('/<place_id>')
@api.param('place_id', 'The place identifier')
class AdminPlaceModify(Resource):
    @api.marshal_with(place_detail_model)
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """
        Get place details by ID
        
        Retrieve detailed information about a specific place,
        including owner details and associated amenities.
        """
        place = facade.get_place(place_id)
        if not place:
            abort(404, 'Place not found')  # type: ignore
        return format_place_response(place, include_owner=True), 200

    @api.expect(place_update_model, validate=True)
    @api.response(200, 'Place updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, place_id):
        """
        Update an existing place
        
        Update the details of an existing place. Only the fields provided
        in the request will be updated. The owner cannot be changed.
        
        - Regular users can only update their own places
        - Admins can update any place (bypass ownership restrictions)
        """
        current_user_id = get_jwt_identity()
        current_user = facade.get_user(current_user_id)
        is_admin = current_user and getattr(current_user, 'is_admin', False)
        user_id = current_user_id

        # Check if place exists first
        place = facade.get_place(place_id)
        if not place:
            abort(HTTPStatus.NOT_FOUND.value, 'Place not found')  # type: ignore
        
        # Assert pour le type checker
        assert place is not None
            
        # Check authorization: admins can update any place, users only their own
        if not is_admin and place.owner_id != user_id:
            return {'error': 'Unauthorized action'}, HTTPStatus.FORBIDDEN

        # Update the place (owner_id cannot be changed)
        updates = api.payload.copy()
        if 'owner_id' in updates:
            del updates['owner_id']  # Remove owner_id if somehow present
            
        updated_place = facade.place_service.update_place(place_id, **updates)
        if not updated_place:
            abort(HTTPStatus.NOT_FOUND.value, 'Place not found')  # type: ignore
            
        return {'message': 'Place updated successfully'}, HTTPStatus.OK
