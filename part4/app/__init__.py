from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS



bcrypt = Bcrypt()
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)
    bcrypt.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

       # Initialize database on start
    with app.app_context():
        from app.models.user import User
        from app.models.place import Place
        from app.models.review import Review
        from app.models.amenity import Amenity
        db.create_all()

        # Seed initial data if DB is empty
        if not User.query.first():
            hashed_admin = bcrypt.generate_password_hash('admin1234').decode('utf-8')
            admin = User(first_name='Admin', last_name='HBnB',
                        email='admin@hbnb.io', password=hashed_admin, is_admin=True)
            db.session.add(admin)
            db.session.flush()

            hashed_user = bcrypt.generate_password_hash('password123').decode('utf-8')
            user = User(first_name='John', last_name='Doe',
                       email='john@test.com', password=hashed_user, is_admin=False)
            db.session.add(user)
            db.session.flush()

            p1 = Place(title='Beautiful Beach House', price=150.0,
                      latitude=48.85, longitude=2.35,
                      description='A beautiful beach house with amazing views...')
            p1.owner_id = user.id
            p2 = Place(title='Cozy Cabin', price=100.0,
                      latitude=45.0, longitude=3.0,
                      description='A cozy cabin in the mountains.')
            p2.owner_id = user.id
            p3 = Place(title='Modern Apartment', price=200.0,
                      latitude=43.0, longitude=5.0,
                      description='A sleek modern apartment in the city center.')
            p3.owner_id = user.id
            db.session.add_all([p1, p2, p3])
            db.session.commit()
            
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Enter: Bearer <your_token>'
            }
        },
        security='Bearer'
    )
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    return app