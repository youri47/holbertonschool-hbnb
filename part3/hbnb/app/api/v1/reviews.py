from flask_restx import Namespace, Resource, fields, abort
from http import HTTPStatus
from app.services.facade import hbnb_facade as facade
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.place import Place

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_create_model = api.model('ReviewCreate', {
    'text': fields.String(
        required=True,
        description='Text of the review',
        example='The place was great!',
        min_length=1,
        max_length=1000,
        pattern=r'^[\w\s\-\'\.,!?()\[\]{}@#$%^&*+=:;"\u00C0-\u017F]+$',
    ),
    'rating': fields.Integer(required=True,
        description='Rating of the place (1-5)',
        example=5,
        min=1,
        max=5),
    'place_id': fields.String(required=True,
        description='ID of the place',
        example='place_12345')
})

# Define the review update model (no user_id or place_id modification allowed)
review_update_model = api.model('ReviewUpdate', {
    'text': fields.String(
        required=False,
        description='Text of the review',
        example='Updated review text!',
        min_length=1,
        max_length=1000,
        pattern=r'^[\w\s\-\'\.,!?()\[\]{}@#$%^&*+=:;"\u00C0-\u017F]+$',
    ),
    'rating': fields.Integer(required=False,
        description='Rating of the place (1-5)',
        example=4,
        min=1,
        max=5)
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_create_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'User or Place not found')
    @jwt_required()
    def post(self):
        """
        Register a new review
        
        Create a new review for a place. The user_id is automatically 
        set from the authenticated user. The place_id must reference an existing place.
        Rating must be between 1 and 5.
        """
        try:
            review_data = api.payload
            user_id = get_jwt_identity()
            place_id = review_data['place_id']
            
            # Vérifier si l'utilisateur a déjà posté un avis pour ce lieu
            existing_reviews = facade.get_reviews_by_place(place_id)
            for review in existing_reviews:
                if review.user_id == user_id:
                    abort(HTTPStatus.BAD_REQUEST.value, 'You have already reviewed this place')  # type: ignore
            
            new_review = facade.create_review(
                text=review_data['text'],
                rating=review_data['rating'],
                user_id=user_id,
                place_id=place_id
            )
            if not new_review:
                abort(HTTPStatus.BAD_REQUEST.value, 'Invalid input data')  # type: ignore
            place = facade.get_place(place_id)
            if place and place.owner_id == get_jwt_identity():
                abort(HTTPStatus.FORBIDDEN.value, 'You are not authorized to create this review')  # type: ignore
            return {
                'id': new_review.id,
                'text': new_review.text,
                'rating': new_review.rating,
                'user_id': new_review.user_id,
                'place_id': new_review.place_id
            }, 201
        except Exception as e:
            # Validation errors are already handled by the service
            # Let the exception propagate so it can be handled by the Flask-RestX error handler
            raise

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """
        Retrieve all reviews
        
        Returns a list of all reviews in the system.
        For reviews of a specific place, use GET /places/{place_id}/reviews
        """
        reviews = facade.get_all_reviews()
        return [{'id': review.id, 'text': review.text, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id} for review in reviews], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """
        Get review details by ID
        
        Retrieve detailed information about a specific review,
        including the review text, rating, and associated user and place.
        """
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return {'id': review.id, 'text': review.text, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id}, 200

    @api.expect(review_update_model, validate=True)
    @api.response(200, 'Review updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review, User or Place not found')
    @jwt_required()
    def put(self, review_id):
        """
        Update a review
        
        Update the details of an existing review. Only the fields provided
        in the request will be updated. The rating must be between 1 and 5.
        
        - Regular users can only update their own reviews
        - Admins can update any review (bypass ownership restrictions)
        """
        try:
            current_user_id = get_jwt_identity()
            current_user = facade.get_user(current_user_id)
            is_admin = current_user and getattr(current_user, 'is_admin', False)
            
            # Get the review first to check ownership
            review = facade.get_review(review_id)
            if not review:
                abort(HTTPStatus.NOT_FOUND.value, 'Review not found')  # type: ignore
            
            # Assert pour le type checker
            assert review is not None
                
            # Check authorization: admins can update any review, users only their own
            if not is_admin and review.user_id != current_user_id:
                abort(HTTPStatus.FORBIDDEN.value, 'You are not authorized to update this review')  # type: ignore
            
            review_data = api.payload
            updated_review = facade.update_review(review_id, **review_data)
            if not updated_review:
                abort(HTTPStatus.NOT_FOUND.value, 'Review not found')  # type: ignore
            
            # Assert pour le type checker
            assert updated_review is not None
                
            return {
                'id': updated_review.id,
                'text': updated_review.text,
                'rating': updated_review.rating,
                'user_id': updated_review.user_id,
                'place_id': updated_review.place_id
            }, 200
        except Exception as e:
            # Validation errors are already handled by the service
            # Let the exception propagate so it can be handled by the Flask-RestX error handler
            raise

    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        """
        Delete a review
        
        Permanently remove a review from the system.
        This action cannot be undone.
        
        - Regular users can only delete their own reviews
        - Admins can delete any review (bypass ownership restrictions)
        """
        current_user_id = get_jwt_identity()
        current_user = facade.get_user(current_user_id)
        is_admin = current_user and getattr(current_user, 'is_admin', False)
        
        # Get the review first
        review = facade.get_review(review_id)
        if not review:
            abort(HTTPStatus.NOT_FOUND.value, 'Review not found')  # type: ignore
        
        # Assert pour le type checker
        assert review is not None
            
        # Check authorization: admins can delete any review, users only their own
        if not is_admin and review.user_id != current_user_id:
            abort(HTTPStatus.FORBIDDEN.value, 'You are not authorized to delete this review')  # type: ignore
            
        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200

@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """
        Get reviews for a place
        
        Retrieve all reviews associated with a specific place,
        including user information and ratings.
        """
        # First check if the place exists
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        
        # Get reviews for the place (can be empty list)
        reviews = facade.get_reviews_by_place(place_id)
        return [{'id': review.id, 'text': review.text, 'rating': review.rating, 'user_id': review.user_id, 'place_id': review.place_id} for review in reviews], 200
