from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text': fields.String(required=True, description='Review text'),
    'rating': fields.Integer(required=True, description='Rating (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

review_update_model = api.model('ReviewUpdate', {
    'text': fields.String(description='Review text'),
    'rating': fields.Integer(description='Rating (1-5)')
})


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model, validate=True)
    @jwt_required()
    def post(self):
        """Create a new review"""
        current_user_id = get_jwt_identity()
        review_data = api.payload
        place = facade.get_place(review_data['place_id'])
        if not place:
            return {'error': 'Place not found'}, 404
        if place.owner_id == current_user_id:
            return {'error': 'You cannot review your own place'}, 400
        existing_reviews = facade.get_reviews_by_place(review_data['place_id'])
        for review in existing_reviews:
            if review.user_id == current_user_id:
                return {'error': 'You have already reviewed this place'}, 400
        review_data['user_id'] = current_user_id
        try:
            new_review = facade.create_review(review_data)
        except ValueError as e:
            return {'error': str(e)}, 400
        return new_review.to_dict(), 201

    def get(self):
        """Retrieve all reviews"""
        reviews = facade.get_all_reviews()
        return [review.to_dict() for review in reviews], 200


@api.route('/<string:review_id>')
class ReviewResource(Resource):
    def get(self, review_id):
        """Get a review by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review.to_dict(), 200

    @api.expect(review_update_model)
    @jwt_required()
    def put(self, review_id):
        """Update a review"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if not is_admin and review.user_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403
        data = api.payload
        try:
            updated_review = facade.update_review(review_id, data)
        except ValueError as e:
            return {'error': str(e)}, 400
        return updated_review.to_dict(), 200

    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if not is_admin and review.user_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403
        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200


@api.route('/places/<string:place_id>/reviews')
class PlaceReviewList(Resource):
    def get(self, place_id):
        """Get all reviews for a place"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        reviews = facade.get_reviews_by_place(place_id)
        return [review.to_dict() for review in reviews], 200