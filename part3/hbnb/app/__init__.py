from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.config import DevelopmentConfig

# Initialiser les extensions sans les configurer
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Configuration par défaut si aucune n'est fournie
    if config_class is None:
        config_class = DevelopmentConfig
    
    app.config.from_object(config_class)
    app.config['DEBUG'] = True

    # Initialiser les extensions avec l'application
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Créer les tables dans le contexte de l'application
    with app.app_context():
        # Importer TOUS les modèles pour que SQLAlchemy les connaisse
        from app.models.user import User
        from app.models.place import Place
        from app.models.review import Review
        from app.models.amenity import Amenity
        # Créer toutes les tables
        db.create_all()

    # Importer les routes après l'initialisation de db
    from .api.v1.users import api as users_ns
    from .api.v1.amenities import api as amenities_ns
    from .api.v1.reviews import api as reviews_ns
    from .api.v1.places import api as places_ns
    from .api.v1.auth import api as auth_ns

    # Configurer l'API
    api = Api(
        title='HBnB API', 
        description='HBnB Application API',
        doc='/',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'JWT token (prefix with "Bearer ")'
            }
        },
        security='Bearer'
    )
    
    # Enregistrer les namespaces
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    
    api.init_app(app)
    
    return app