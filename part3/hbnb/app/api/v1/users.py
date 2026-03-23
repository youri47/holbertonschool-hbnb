from re import I
from flask_restx import Namespace, Resource
from app.services.facade import hbnb_facade as facade
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import request
from flask_restx import fields


def format_user_response(user):
    """Format standard pour les réponses utilisateur"""
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_admin': user.is_admin
    }

api = Namespace('users', description='User operations')

# User model for request documentation
user_model = api.model('User', {
    'first_name': fields.String(
        required=True,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Zà-ÿÀ-Ÿ\s\-']+$",
        description="User first name (letters, accents, spaces, hyphens and apostrophes only)",
        example='Marie-Louise'
    ),
    'last_name': fields.String(
        required=True,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Zà-ÿÀ-Ÿ\s\-']+$",
        description="User last name (letters, accents, spaces, hyphens and apostrophes only)",
        example="O'Connor"
    ),
    'email': fields.String(
        required=True,
        description='User email address',
        pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
        example="marie-louise.oconnor@example.com"
    ),
    'password': fields.String(
        required=True,
        min_length=8,
        max_length=128,
        description='User password (at least 8 characters, not returned in response)',
        example='MySecurePassword123!'
    ),
    'is_admin': fields.Boolean(
        required=False,
        description='User admin status',
        example=False
    )
})

# User update model - includes all modifiable fields
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(
        required=False,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Zà-ÿÀ-Ÿ\s\-']+$",
        description="User first name (letters, accents, spaces, hyphens and apostrophes only)",
        example='Marie-Louise'
    ),
    'last_name': fields.String(
        required=False,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Zà-ÿÀ-Ÿ\s\-']+$",
        description="User last name (letters, accents, spaces, hyphens and apostrophes only)",
        example="O'Connor"
    ),
    'email': fields.String(
        required=False,
        description='New email address (admins only)',
        pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
        example="new.email@example.com"
    ),
    'password': fields.String(
        required=False,
        min_length=8,
        max_length=128,
        description='New password (admins only, at least 8 characters)',
        example='NewSecurePassword123!'
    ),
    'is_admin': fields.Boolean(
        required=False,
        description='Admin status (admins only)',
        example=False
    )
})

# User response model for response documentation
user_response_model = api.model('UserResponse', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='User first name'),
    'last_name': fields.String(description='User last name'),
    'email': fields.String(description='User email address'),
    'is_admin': fields.Boolean(description='User admin status')
    # Password volontairement omis pour la sécurité
})

# Registration response model
user_registration_response_model = api.model('UserRegistrationResponse', {
    'id': fields.String(description='User ID'),
    'message': fields.String(description='Registration success message')
})

@api.route('/')
class UserList(Resource):
    @api.marshal_list_with(user_response_model)
    @api.response(200, 'Success')
    def get(self):
        """
        Retrieve all users
        
        Returns a list of all users with their basic information.
        For detailed user information, use GET /users/{user_id}
        """
        users = facade.get_all_users()
        return [format_user_response(user) for user in users], 200

    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_registration_response_model)
    @api.response(201, 'User created successfully')
    @api.response(400, 'Invalid input or email already registered')
    @api.response(403, 'Admin privileges required')
    @api.response(500, 'Internal server error')
    def post(self):
        """
        Create a new user (Admin only)
        
        Create a new user account. This endpoint is restricted to administrators only.
        The password will be automatically hashed before storage.
        """
        # Récupérer l'ID de l'utilisateur depuis le token JWT
        current_user_id = get_jwt_identity()
        
        # Vérifier si l'utilisateur est admin
        current_user = facade.get_user(current_user_id)
        
        if not current_user or not getattr(current_user, 'is_admin', False):
            api.abort(403, 'Admin privileges required')

        user_data = api.payload
        email = user_data.get('email')

        # Vérifier si l'email est déjà utilisé
        if facade.get_user_by_email(email):
            api.abort(400, 'Email already registered')

        try:
            data = api.payload
            # Hash the password before creating the user
            password_hash = User.hash_password(data['password'])
            
            # 🔒 Sécurité : Supprimer le password plain text de la mémoire
            data.pop('password', None)
            
            # Create user with hashed password
            new_user = facade.create_user(
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=password_hash
            )
            return {'id': new_user.id, 'message': 'User registered successfully'}, 201
        except ValueError as e:
            api.abort(400, str(e) or 'Invalid input data')
        except Exception as e:
            api.abort(500, 'An unexpected error occurred')


@api.route('/<user_id>')
class UserResource(Resource):
    @api.marshal_with(user_response_model)
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """
        Get user details by ID
        
        Retrieve detailed information about a specific user,
        including their first name, last name, and email.
        """
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        return format_user_response(user), 200
        
    @api.expect(user_update_model, validate=True)
    @api.marshal_with(user_response_model)
    @api.response(200, 'User successfully updated')
    @api.response(400, 'Invalid request')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    @api.response(409, 'Email already in use')
    @jwt_required()
    def put(self, user_id):
        """
        Update an existing user
        
        Update user information. 
        - Regular users can only update their own first_name and last_name
        - Admins can update any user's information including is_admin status
        - Email and password can only be modified by admins
        """
        current_user_id = get_jwt_identity()
        current_user = facade.get_user(current_user_id)
        is_admin = current_user and current_user.is_admin
        
        # Récupérer l'utilisateur à modifier d'abord
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        
        # Assert pour le type checker
        assert user is not None
            
        # Vérifier que l'utilisateur modifie son propre compte ou est admin
        if current_user_id != user_id and not is_admin:
            api.abort(403, 'Unauthorized action')
            
        user_data = api.payload.copy()
        
        # Traitement et vérification du mot de passe
        password_changed = False
        if 'password' in user_data and user_data['password']:
            # Vérifier si le password a vraiment changé
            if user.verify_password(user_data['password']):
                # Password identique, pas de modification réelle
                user_data.pop('password', None)
                password_changed = False
            else:
                # Password différent, c'est une vraie modification
                password_changed = True
                user_data['password'] = User.hash_password(user_data['password'])
        
        # Vérification des modifications interdites pour les non-admins
        if not is_admin:
            # Vérifier si l'email a vraiment été modifié
            if 'email' in user_data and user_data['email'] and user_data['email'] != user.email:
                api.abort(403, 'Admin privileges required to modify email')
            
            # Vérifier si le password a vraiment été modifié
            if password_changed:
                api.abort(403, 'Admin privileges required to modify password')
            
            # Vérifier si is_admin a vraiment été modifié
            if 'is_admin' in user_data and user_data['is_admin'] != user.is_admin:
                api.abort(403, 'Admin privileges required to modify is_admin')
            
            # Vérifier les autres champs strictement interdits (seul 'id' reste vraiment interdit)
            if 'id' in user_data:
                api.abort(403, 'Admin privileges required to modify id')
        
        # Vérification de l'unicité de l'email si modification
        if 'email' in user_data and user_data['email'] != user.email:
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user and existing_user.id != user_id:
                api.abort(409, 'Email already in use')
        
        # Mise à jour des champs fournis
        for field, value in user_data.items():
            if hasattr(user, field) and value is not None:
                # Pour les booléens comme is_admin, on accepte explicitement False
                if isinstance(getattr(user, field), bool):
                    setattr(user, field, value)
                # Pour les chaînes, on ne met à jour que si la valeur n'est pas vide
                elif value != '':
                    setattr(user, field, value)
        
        # Sauvegarder les modifications
        facade.update_user(user.id, **{k: v for k, v in user_data.items() 
                                    if hasattr(user, k) and v is not None and v != ''})
        
        return format_user_response(user), 200


