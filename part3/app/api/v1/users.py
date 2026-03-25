from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='User password'),
    'is_admin': fields.Boolean(description='Admin flag', default=False)
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'email': fields.String(description='Email address'),
    'password': fields.String(description='User password')
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @jwt_required()
    def post(self):
        """Register a new user (Admin only)"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        user_data = api.payload
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400
        try:
            new_user = facade.create_user(user_data)
        except ValueError as e:
            return {'error': str(e)}, 400
        return {
            'id': new_user.id,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'email': new_user.email
        }, 201

    @api.doc('list_users')
    def get(self):
        """Retrieve list of all users"""
        users = facade.get_all_users()
        return [user.to_dict() for user in users], 200


@api.route('/<string:user_id>')
class UserResource(Resource):
    def get(self, user_id):
        """Get a user by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @api.expect(user_update_model)
    @jwt_required()
    def put(self, user_id):
        """Update a user's information"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        if is_admin:
            data = api.payload
            email = data.get('email')
            if email:
                existing_user = facade.get_user_by_email(email)
                if existing_user and existing_user.id != user_id:
                    return {'error': 'Email already in use'}, 400
            if 'password' in data:
                user = facade.get_user(user_id)
                if not user:
                    return {'error': 'User not found'}, 404
                user.hash_password(data.pop('password'))
            user = facade.update_user(user_id, data)
            if not user:
                return {'error': 'User not found'}, 404
            return user.to_dict(), 200

        if current_user_id != user_id:
            return {'error': 'Unauthorized action'}, 403
        data = api.payload
        if 'email' in data or 'password' in data:
            return {'error': 'You cannot modify email or password'}, 400
        user = facade.update_user(user_id, data)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200