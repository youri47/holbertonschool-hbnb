from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
})

admin_update_model = api.model('AdminUserUpdate', {
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
    'email': fields.String(description='Email of the user'),
    'password': fields.String(description='Password of the user')
})

@api.route('/')
class UserList(Resource):
    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(403, 'Admin privileges required')
    @api.response(400, 'Email already registered')
    def post(self):
        """Create a new user — admin only"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        user_data = api.payload
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400
        try:
            new_user = facade.create_user(user_data)
            return new_user.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve a list of users — public"""
        users = facade.get_users()
        return [user.to_dict() for user in users], 200

@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID — public"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @jwt_required()
    @api.response(200, 'User updated successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(400, 'Cannot modify email or password')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update user — own account or admin"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        user_data = api.payload

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        if is_admin:
            # Admin can modify anyone including email and password
            if 'email' in user_data:
                existing = facade.get_user_by_email(user_data['email'])
                if existing and existing.id != user_id:
                    return {'error': 'Email already in use'}, 400
            try:
                facade.update_user(user_id, user_data)
                return user.to_dict(), 200
            except Exception as e:
                return {'error': str(e)}, 400
        else:
            # Regular user — can only modify own account
            if user_id != current_user_id:
                return {'error': 'Unauthorized action'}, 403
            if 'email' in user_data or 'password' in user_data:
                return {'error': 'You cannot modify email or password'}, 400
            try:
                facade.update_user(user_id, user_data)
                return user.to_dict(), 200
            except Exception as e:
                return {'error': str(e)}, 400